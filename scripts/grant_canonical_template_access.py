#!/usr/bin/env python3
"""One-time Google Picker grant for the canonical landing-page template.

Google's desktop Picker flow (trigger_onepick=true) lets the account owner hand this OAuth
app access to exactly one pre-existing file, without widening any stored scope. Reference:
https://developers.google.com/workspace/drive/picker/guides/desktop-mobile-picker

Hard constraints enforced here:

- The authorization request asks for https://www.googleapis.com/auth/drive.file and nothing
  else. Google forbids combining the Picker request with any other scope, so the documents
  scope never appears in it.
- The picker is filtered to the single canonical template ID and to Google Docs only.
  allow_multiple and allow_folder_selection are never sent, so one file is the maximum.
- The returned picked_file_ids must equal the canonical template ID exactly, or the run
  fails without taking any further action.
- The long-lived Drive token is never read, written, or overwritten by this script. The
  short-lived Picker credentials are held in memory only and are never written to disk.
- No authorization URL, client ID, authorization code, or token is ever printed.

This script grants access. It creates, copies, modifies, and deletes nothing.
"""
from __future__ import annotations

import argparse
import secrets
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.google_drive import (  # noqa: E402
    DOCUMENT_MIME_TYPE,
    PICKER_AUTH_URI,
    PICKER_SCOPES,
    PickerSelectionError,
    build_picker_authorization_params,
    load_drive_settings,
    redact_error_text,
    validate_picked_file_ids,
)

EXPECTED_EMAIL = "access@greenmarketingfl.com"

SUCCESS_HTML = b"""<!doctype html><html><body style="font-family:sans-serif;padding:40px">
<h2>Green Marketing template access granted</h2>
<p>You can close this tab and return to the terminal.</p></body></html>"""

FAILURE_HTML = b"""<!doctype html><html><body style="font-family:sans-serif;padding:40px">
<h2>Authorization was not completed</h2>
<p>You can close this tab and return to the terminal.</p></body></html>"""


class _CallbackHandler(BaseHTTPRequestHandler):
    result: dict[str, str] = {}

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        # Ignore stray probes (favicon, port scanners) that carry no OAuth parameters.
        if not any(key in params for key in ("code", "error", "picked_file_ids")):
            self.send_response(204)
            self.end_headers()
            return

        type(self).result = {k: v[0] for k, v in params.items()}
        body = FAILURE_HTML if "error" in params else SUCCESS_HTML
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:
        """Silence the default stderr logging; it would echo the query string."""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="One-time Picker grant for the canonical landing-page template."
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--expect-email", default=EXPECTED_EMAIL)
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=300,
        help="How long to wait for the browser callback.",
    )
    args = parser.parse_args()

    settings = load_drive_settings()
    template_id = settings.canonical_source_template_id

    if not settings.credentials_file.exists():
        print(f"FAIL: OAuth client file not found at {settings.credentials_file}")
        return 1

    try:
        from google_auth_oauthlib.flow import Flow
    except ImportError:
        print("FAIL: google-auth-oauthlib is not installed in this environment.")
        return 1

    redirect_uri = f"http://localhost:{args.port}/"
    flow = Flow.from_client_secrets_file(
        str(settings.credentials_file),
        scopes=list(PICKER_SCOPES),
        redirect_uri=redirect_uri,
    )
    # Use the v2 authorization endpoint documented for the desktop Picker flow.
    flow.client_config["auth_uri"] = PICKER_AUTH_URI

    picker_params = build_picker_authorization_params(
        template_id=template_id, expected_email=args.expect_email
    )
    state = secrets.token_urlsafe(24)
    authorization_url, _ = flow.authorization_url(state=state, **picker_params)

    print("=" * 78)
    print("ONE-TIME GOOGLE PICKER GRANT")
    print("=" * 78)
    print(f"Account to select   : {args.expect_email}")
    print(f"Requested scope     : {', '.join(PICKER_SCOPES)}")
    print(f"Picker filter       : file_ids={template_id}")
    print(f"                      mimetypes={DOCUMENT_MIME_TYPE}")
    print("Multiple selection  : disabled (allow_multiple not sent)")
    print("Folder selection    : disabled (allow_folder_selection not sent)")
    print(f"Callback            : {redirect_uri}")
    print("(The authorization URL is not printed; it embeds the OAuth client ID.)")

    server = HTTPServer(("localhost", args.port), _CallbackHandler)
    server.timeout = args.timeout_seconds
    _CallbackHandler.result = {}

    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("\nOpening your browser. Select the ONE listed template and approve access.")
    sys.stdout.flush()
    webbrowser.open(authorization_url)

    thread.join(timeout=args.timeout_seconds)
    server.server_close()

    result = _CallbackHandler.result
    if not result:
        print("\nFAIL: no callback received before the timeout. Nothing was granted.")
        print("If the callback port is busy, retry with --port <other port>.")
        return 1

    if "error" in result:
        print(f"\nFAIL: Google returned an error: {redact_error_text(result.get('error'))}")
        print("Nothing was granted.")
        return 1

    if result.get("state") != state:
        print("\nFAIL: OAuth state mismatch. Discarding this response.")
        return 1

    granted_scope = result.get("scope", "")
    print(f"\nScope returned by Google : {granted_scope}")
    if granted_scope and set(granted_scope.split()) - set(PICKER_SCOPES):
        print("FAIL: Google returned a scope beyond drive.file. Stopping.")
        return 1

    try:
        picked = validate_picked_file_ids(result.get("picked_file_ids"), template_id)
    except PickerSelectionError as exc:
        print(f"\nFAIL: {exc}")
        return 1

    print(f"Picked file ID           : {picked[0]}")
    print("Picked file matches the canonical template exactly: YES")

    # Redeem the code so Google finalizes the per-file grant. These credentials are held in
    # memory only, are never written to disk, and never touch the main Drive token file.
    try:
        flow.fetch_token(code=result["code"])
    except Exception as exc:  # noqa: BLE001
        print(f"\nFAIL: could not finalize the grant: {redact_error_text(exc)}")
        return 1

    print("\nGrant finalized. The temporary Picker credentials were kept in memory only")
    print(f"and were NOT written to disk. The main token at {settings.token_file}")
    print("was not read, modified, or overwritten by this script.")
    print("\nNext: python scripts/verify_google_drive_access.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
