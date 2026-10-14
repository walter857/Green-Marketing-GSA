"""Least-privilege Google Drive and Google Docs integration for landing-page delivery.

Safety contract for this module:

- It never reads, prints, logs, or returns the contents of the OAuth client JSON or the
  stored token. Client secrets are handed to ``google-auth-oauthlib`` by file path only.
- It reports whether a configured path exists, never what is inside it.
- Every write is planned first. ``plan_landing_page_drive`` performs read-only lookups and
  ``apply_plan`` is the only function in this module that mutates Google Drive.
- ``apply_plan`` creates folders and nothing else. There is no ``files.copy`` call in this
  module, so the initializer physically cannot produce an unscrubbed master template. The
  master document is produced only by ``gm_gsa.master_template``, which copies the canonical
  example under a TEMP name, scrubs it, validates it, and only then renames it.
- All lookups are exact-name lookups scoped to one expected parent. Duplicates and
  ambiguity raise instead of guessing.
- Nothing here deletes, moves, trashes, or shares a Drive resource, and no permission or
  sharing call exists in this module.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, ConfigurationError, load_yaml

DRIVE_SCOPES: tuple[str, ...] = (
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
)

#: Scopes this repository must never request. ``drive`` and ``drive.appdata``-adjacent full
#: grants give read/write over the user's entire Drive; every durable write here belongs to
#: ``drive.file``. ``drive.readonly`` is deliberately NOT listed: it is read-only, and it is
#: the narrowest way to inspect client-owned files the app did not create.
FORBIDDEN_SCOPES: frozenset[str] = frozenset(
    {
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.metadata",
    }
)

CANONICAL_TEMPLATE_ID = "1bQR5wLIF47fd-wNOaNxtjlun1ch8Fc5kmfCA93vuFuc"

# The two document names live here, not in template_scrub, so that the "never create an
# unscrubbed master" guard and the code that performs the rename share one definition.
TEMP_SCRUB_NAME = "TEMP - Master Template Scrub In Progress"
MASTER_TEMPLATE_NAME = "Landing Page Content Template - Master"

FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
DOCUMENT_MIME_TYPE = "application/vnd.google-apps.document"

MY_DRIVE_ROOT = "root"

DEFAULT_CREDENTIALS_FILE = Path(r"D:\MG\secrets\green-marketing-drive-client.json")
DEFAULT_TOKEN_FILE = Path(r"D:\MG\secrets\green-marketing-drive-token.json")

DRIVE_CONFIG_PATH = PROJECT_ROOT / "config" / "google-drive.yaml"

FILE_FIELDS = "id, name, mimeType, parents, webViewLink, trashed"
LIST_FIELDS = f"nextPageToken, files({FILE_FIELDS})"

OAUTH_SECRET_KEY_PATTERN = re.compile(
    r"(token|secret|password|api[_-]?key|authorization|client[_-]?id|private[_-]?key"
    r"|code[_-]?verifier|auth[_-]?uri|id[_-]?token)",
    re.IGNORECASE,
)


# One-time desktop Picker grant.
#
# Google's desktop/mobile Picker flow (trigger_onepick=true) is the least-privilege way to
# give this OAuth app access to a pre-existing file without widening the stored scopes.
# Google permits ONLY drive.file in this request and forbids combining it with any other
# scope, so the documents scope must never appear here.
PICKER_SCOPES: tuple[str, ...] = ("https://www.googleapis.com/auth/drive.file",)
PICKER_AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"


class DriveError(RuntimeError):
    """Base class for Drive workflow failures."""


class DriveAmbiguityError(DriveError):
    """Raised when an exact-name lookup matches more than one resource."""


class DriveAuthorizationError(DriveError):
    """Raised when the local Drive authorization is missing, stale, or wrong."""


class PickerSelectionError(DriveError):
    """Raised when the Picker returned something other than the one expected file."""


class UnscrubbedMasterError(DriveError):
    """Raised when an operation would create a document under the final master name.

    The final name is a *promise* that the document has been scrubbed of the source
    client's facts and structurally verified. Only a rename of an already validated TEMP
    copy is allowed to make that promise, so creating or copying straight to the final name
    is refused everywhere.
    """


class PartialWriteError(DriveError):
    """Raised when a plan fails part-way through, carrying an inventory of what was created."""

    def __init__(self, message: str, created: list[dict[str, Any]], failed_key: str) -> None:
        super().__init__(message)
        self.created = created
        self.failed_key = failed_key

    def inventory(self) -> list[dict[str, Any]]:
        return list(self.created)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DriveSettings:
    credentials_file: Path
    token_file: Path
    scopes: tuple[str, ...]
    root_folder_name: str
    root_folder_id: str | None
    templates_folder_name: str
    master_template_name: str
    master_template_document_id: str | None
    canonical_source_template_id: str
    create_clients_folder: bool
    clients_folder_name: str

    def describe(self) -> dict[str, Any]:
        """Non-secret description of the configuration, safe to print."""
        return {
            "credentials_file": str(self.credentials_file),
            "credentials_file_present": self.credentials_file.exists(),
            "token_file": str(self.token_file),
            "token_file_present": self.token_file.exists(),
            "scopes": list(self.scopes),
            "root_folder_name": self.root_folder_name,
            "root_folder_id": self.root_folder_id,
            "templates_folder_name": self.templates_folder_name,
            "master_template_name": self.master_template_name,
            "master_template_document_id": self.master_template_document_id,
            "canonical_source_template_id": self.canonical_source_template_id,
            "create_clients_folder": self.create_clients_folder,
        }


def _env_path(name: str, fallback: Path) -> Path:
    value = os.getenv(name)
    return Path(value) if value else fallback


def load_drive_settings(config_path: str | Path | None = None) -> DriveSettings:
    """Resolve non-secret Drive settings from config/google-drive.yaml plus env overrides.

    This deliberately does not load ``.env``. The only environment variables consulted are
    the four documented Drive names, so unrelated Google Ads configuration is never read.
    """
    path = Path(config_path) if config_path else DRIVE_CONFIG_PATH
    document = load_yaml(path)
    drive = document.get("drive") or {}
    oauth = document.get("oauth") or {}
    if not isinstance(drive, dict) or not isinstance(oauth, dict):
        raise ConfigurationError(f"Expected 'drive' and 'oauth' mappings in {path}")

    scopes = tuple(oauth.get("scopes") or DRIVE_SCOPES)
    if not scopes:
        raise ConfigurationError("At least one OAuth scope must be configured.")
    forbidden = sorted(set(scopes) & FORBIDDEN_SCOPES)
    if forbidden:
        raise ConfigurationError(
            f"Refusing the full read/write Drive scope(s) {', '.join(forbidden)} in {path}. "
            "Writes must stay on drive.file; use drive.readonly for inspecting pre-existing "
            "client files. Removing this guard requires separate written approval."
        )

    # The rename that earns the final name uses the MASTER_TEMPLATE_NAME constant, and the
    # "never create this name" guard checks that same constant. A config file naming
    # something different would describe a document the guard does not actually protect.
    configured_master_name = str(drive.get("master_template_name") or "").strip()
    if configured_master_name and configured_master_name != MASTER_TEMPLATE_NAME:
        raise ConfigurationError(
            f"master_template_name in {path} is {configured_master_name!r} but the protected "
            f"final name is {MASTER_TEMPLATE_NAME!r}. They must match."
        )

    root_id = os.getenv("GOOGLE_DRIVE_LANDING_PAGE_ROOT_FOLDER_ID") or drive.get(
        "landing_page_root_folder_id"
    )
    template_id = os.getenv("GOOGLE_DOC_LANDING_PAGE_TEMPLATE_ID") or drive.get(
        "master_template_document_id"
    )

    return DriveSettings(
        credentials_file=_env_path("GOOGLE_DRIVE_CREDENTIALS_FILE", DEFAULT_CREDENTIALS_FILE),
        token_file=_env_path("GOOGLE_DRIVE_TOKEN_FILE", DEFAULT_TOKEN_FILE),
        scopes=scopes,
        root_folder_name=str(drive.get("landing_page_root_folder_name") or "").strip(),
        root_folder_id=str(root_id).strip() or None if root_id else None,
        templates_folder_name=str(drive.get("templates_folder_name") or "").strip(),
        master_template_name=str(drive.get("master_template_name") or "").strip(),
        master_template_document_id=str(template_id).strip() or None if template_id else None,
        canonical_source_template_id=str(
            drive.get("canonical_source_template_id") or CANONICAL_TEMPLATE_ID
        ).strip(),
        create_clients_folder=bool(drive.get("create_clients_folder", False)),
        clients_folder_name=str(drive.get("clients_folder_name") or "Clients").strip(),
    )


# ---------------------------------------------------------------------------
# Final-master name guard
# ---------------------------------------------------------------------------


def assert_not_unscrubbed_master(name: str | None, operation: str) -> None:
    """Refuse to bring a *new* resource into existence under the final master name.

    Copying the canonical example straight to ``Landing Page Content Template - Master``
    would publish a document that still carries the source client's name, phone number,
    reviews, and image links under a name that claims it is a clean template. The final
    name may only ever be reached by renaming a copy that has already passed the content
    and structure validations in ``gm_gsa.master_template``.
    """
    if str(name or "").strip() == MASTER_TEMPLATE_NAME:
        raise UnscrubbedMasterError(
            f"Refusing {operation}: a resource may never be created or copied under the "
            f"name {MASTER_TEMPLATE_NAME!r}. Copy the canonical document to "
            f"{TEMP_SCRUB_NAME!r}, scrub it, validate it, and rename it only after every "
            "validation passes."
        )


# ---------------------------------------------------------------------------
# Recording verified, non-secret IDs
# ---------------------------------------------------------------------------

DRIVE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{10,120}$")

RECORDED_ID_KEYS = ("landing_page_root_folder_id", "master_template_document_id")


def _assert_recordable_id(key: str, value: str) -> str:
    """Only a bare Drive resource ID may be written into the non-secret config file."""
    candidate = str(value or "").strip()
    if not DRIVE_ID_PATTERN.match(candidate):
        raise ConfigurationError(
            f"Refusing to record {key}: {candidate[:12]!r}... is not a plain Drive resource ID. "
            "Only non-secret Drive IDs belong in config/google-drive.yaml."
        )
    return candidate


def record_verified_ids(
    root_folder_id: str,
    master_template_document_id: str,
    config_path: str | Path | None = None,
) -> dict[str, str]:
    """Write the two verified, non-secret IDs into config/google-drive.yaml.

    Call this only after the master template has been scrubbed, re-read, and validated.
    The file is edited line by line so its comments survive, and the values are checked to
    be bare Drive IDs so no token or secret can ever be written here.
    """
    path = Path(config_path) if config_path else DRIVE_CONFIG_PATH
    values = {
        "landing_page_root_folder_id": _assert_recordable_id(
            "landing_page_root_folder_id", root_folder_id
        ),
        "master_template_document_id": _assert_recordable_id(
            "master_template_document_id", master_template_document_id
        ),
    }
    if values["master_template_document_id"] == CANONICAL_TEMPLATE_ID:
        raise ConfigurationError(
            "Refusing to record the canonical source document as the master template. "
            "The master template must be a scrubbed copy, never the protected original."
        )
    if values["landing_page_root_folder_id"] == values["master_template_document_id"]:
        raise ConfigurationError(
            "Refusing to record the same ID as both the root folder and the master template."
        )

    text = path.read_text(encoding="utf-8")
    for key, value in values.items():
        pattern = re.compile(rf"^([ \t]*){re.escape(key)}:[^\r\n]*$", re.MULTILINE)
        if not pattern.search(text):
            raise ConfigurationError(f"Key {key!r} was not found in {path}.")
        text = pattern.sub(lambda m, k=key, v=value: f'{m.group(1)}{k}: "{v}"', text, count=1)
    path.write_text(text, encoding="utf-8")
    return values


# ---------------------------------------------------------------------------
# Redaction
# ---------------------------------------------------------------------------


def redact_oauth_payload(value: Any) -> Any:
    """Redact anything that looks like an OAuth identifier or secret.

    Used so that a caught exception or a debug dump can never surface client secrets,
    refresh tokens, access tokens, or the OAuth client ID.
    """
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            if OAUTH_SECRET_KEY_PATTERN.search(str(key)):
                clean[key] = "[REDACTED]"
            else:
                clean[key] = redact_oauth_payload(item)
        return clean
    if isinstance(value, list):
        return [redact_oauth_payload(item) for item in value]
    return value


def redact_error_text(text: str) -> str:
    """Strip long opaque tokens out of an error string before it is shown."""
    cleaned = re.sub(r"[A-Za-z0-9_\-]{40,}", "[REDACTED]", str(text))
    cleaned = re.sub(
        r"(client_secret|refresh_token|access_token|client_id)=[^&\s\"']+",
        r"\1=[REDACTED]",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned


# ---------------------------------------------------------------------------
# Credentials and services
# ---------------------------------------------------------------------------


def load_stored_credentials(settings: DriveSettings) -> Any:
    """Load and refresh the separate Drive token. Never returns or logs token material."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise ConfigurationError(
            "Google auth libraries are not installed. Run: "
            "python -m pip install google-api-python-client google-auth-httplib2 "
            "google-auth-oauthlib"
        ) from exc

    if not settings.token_file.exists():
        raise DriveAuthorizationError(
            f"No Drive token found at {settings.token_file}. "
            "Run scripts/setup_google_drive_oauth.py first."
        )

    credentials = Credentials.from_authorized_user_file(
        str(settings.token_file), list(settings.scopes)
    )
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            save_credentials(credentials, settings.token_file)
        else:
            raise DriveAuthorizationError(
                "The stored Drive token is not valid and cannot be refreshed. "
                "Re-run scripts/setup_google_drive_oauth.py."
            )
    return credentials


def save_credentials(credentials: Any, token_file: Path) -> None:
    """Persist the token outside the repository with best-effort restrictive permissions."""
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(credentials.to_json(), encoding="utf-8")
    try:
        os.chmod(token_file, 0o600)
    except OSError:  # pragma: no cover - platform dependent
        pass


def granted_scopes(credentials: Any) -> list[str]:
    scopes = getattr(credentials, "granted_scopes", None) or getattr(credentials, "scopes", None)
    return sorted(scopes or [])


def build_drive_service(credentials: Any) -> Any:
    from googleapiclient.discovery import build

    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def build_docs_service(credentials: Any) -> Any:
    from googleapiclient.discovery import build

    return build("docs", "v1", credentials=credentials, cache_discovery=False)


def authorized_identity(drive_service: Any) -> dict[str, Any]:
    """Return the authorized account identity via the Drive about endpoint."""
    about = drive_service.about().get(fields="user(emailAddress,displayName)").execute()
    return about.get("user", {}) or {}


def classify_api_error(error: Exception) -> dict[str, Any]:
    """Turn a Google API error into a redacted, human-readable classification."""
    status = getattr(getattr(error, "resp", None), "status", None)
    raw = redact_error_text(getattr(error, "reason", "") or str(error))
    lowered = raw.lower()
    if "has not been used in project" in lowered or "accessnotconfigured" in lowered:
        kind = "api_not_enabled"
    elif status == 404:
        kind = "not_found_or_not_shared_with_this_oauth_app"
    elif status == 403 and "insufficient" in lowered:
        kind = "insufficient_scope"
    elif status == 403:
        kind = "forbidden"
    elif status == 401:
        kind = "unauthorized"
    else:
        kind = "error"
    return {"kind": kind, "status": status, "message": raw}


# ---------------------------------------------------------------------------
# Exact-name lookups
# ---------------------------------------------------------------------------


def escape_query_value(value: str) -> str:
    """Escape a literal for use inside a Drive query string."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_children_by_exact_name(
    drive_service: Any,
    parent_id: str,
    name: str,
    mime_type: str | None = None,
) -> list[dict[str, Any]]:
    """Return every non-trashed child of ``parent_id`` whose name matches ``name`` exactly.

    The Drive query narrows the result set; the final equality check is done locally so a
    case-insensitive backend match can never be mistaken for an exact match.
    """
    clauses = [
        f"name = '{escape_query_value(name)}'",
        f"'{escape_query_value(parent_id)}' in parents",
        "trashed = false",
    ]
    if mime_type:
        clauses.append(f"mimeType = '{escape_query_value(mime_type)}'")
    query = " and ".join(clauses)

    matches: list[dict[str, Any]] = []
    page_token: str | None = None
    while True:
        response = (
            drive_service.files()
            .list(
                q=query,
                spaces="drive",
                fields=LIST_FIELDS,
                pageSize=100,
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        for item in response.get("files", []) or []:
            if item.get("name") == name and not item.get("trashed", False):
                matches.append(item)
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return matches


def resolve_unique_child(
    drive_service: Any,
    parent_id: str,
    name: str,
    mime_type: str | None = None,
) -> dict[str, Any] | None:
    """Return the single exact match, ``None`` if absent, and raise on duplicates."""
    matches = find_children_by_exact_name(drive_service, parent_id, name, mime_type)
    if len(matches) > 1:
        ids = ", ".join(sorted(str(m.get("id")) for m in matches))
        raise DriveAmbiguityError(
            f"Found {len(matches)} resources named {name!r} under parent {parent_id!r} "
            f"(IDs: {ids}). Resolve the duplicates in Drive before continuing."
        )
    return matches[0] if matches else None


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------


@dataclass
class PlannedResource:
    key: str
    name: str
    kind: str  # "folder" or "document"
    mime_type: str
    action: str  # "create", "copy", or "reuse"
    parent_key: str | None = None
    parent_id: str | None = None
    existing_id: str | None = None
    existing_url: str | None = None
    source_template_id: str | None = None

    def as_row(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "kind": self.kind,
            "action": self.action,
            "parent": self.parent_id or self.parent_key or MY_DRIVE_ROOT,
            "existing_id": self.existing_id,
            "url": self.existing_url,
            "source_template_id": self.source_template_id,
        }


@dataclass
class DrivePlan:
    resources: list[PlannedResource] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def creates(self) -> list[PlannedResource]:
        return [r for r in self.resources if r.action in {"create", "copy"}]

    @property
    def reuses(self) -> list[PlannedResource]:
        return [r for r in self.resources if r.action == "reuse"]

    def summary(self) -> dict[str, int]:
        return {
            "total": len(self.resources),
            "create": len([r for r in self.resources if r.action == "create"]),
            "copy": len([r for r in self.resources if r.action == "copy"]),
            "reuse": len(self.reuses),
        }


def _plan_child(
    drive_service: Any,
    plan: DrivePlan,
    *,
    key: str,
    name: str,
    kind: str,
    mime_type: str,
    parent: PlannedResource | None,
    parent_id: str | None,
    source_template_id: str | None = None,
) -> PlannedResource:
    """Plan one resource under a parent that either already exists or is itself planned."""
    parent_exists = parent_id is not None
    create_action = "copy" if source_template_id else "create"

    if not parent_exists:
        # The parent does not exist yet, so no child can exist. No lookup is possible.
        resource = PlannedResource(
            key=key,
            name=name,
            kind=kind,
            mime_type=mime_type,
            action=create_action,
            parent_key=parent.key if parent else None,
            source_template_id=source_template_id,
        )
        plan.resources.append(resource)
        return resource

    existing = resolve_unique_child(drive_service, parent_id, name, mime_type)
    if existing:
        resource = PlannedResource(
            key=key,
            name=name,
            kind=kind,
            mime_type=mime_type,
            action="reuse",
            parent_key=parent.key if parent else None,
            parent_id=parent_id,
            existing_id=existing.get("id"),
            existing_url=existing.get("webViewLink"),
            source_template_id=source_template_id,
        )
    else:
        resource = PlannedResource(
            key=key,
            name=name,
            kind=kind,
            mime_type=mime_type,
            action=create_action,
            parent_key=parent.key if parent else None,
            parent_id=parent_id,
            source_template_id=source_template_id,
        )
    plan.resources.append(resource)
    return resource


def plan_landing_page_drive(drive_service: Any, settings: DriveSettings) -> DrivePlan:
    """Read-only plan for the approved landing-page *folder* scaffold.

    Plans exactly: the root folder, the Templates folder, and optionally a Clients folder
    when ``create_clients_folder`` is enabled. No client folders are ever planned here.

    The master template is deliberately NOT part of this plan. Copying the canonical client
    example straight to its final name would create an unscrubbed document claiming to be a
    clean template, so the document is owned by ``gm_gsa.master_template``, which copies to
    a TEMP name, scrubs, validates, and only then renames.
    """
    plan = DrivePlan()

    if settings.root_folder_id:
        root = PlannedResource(
            key="root",
            name=settings.root_folder_name,
            kind="folder",
            mime_type=FOLDER_MIME_TYPE,
            action="reuse",
            parent_id=None,
            existing_id=settings.root_folder_id,
        )
        plan.resources.append(root)
        plan.notes.append(
            f"Root folder ID supplied by configuration: {settings.root_folder_id}"
        )
    else:
        root = _plan_child(
            drive_service,
            plan,
            key="root",
            name=settings.root_folder_name,
            kind="folder",
            mime_type=FOLDER_MIME_TYPE,
            parent=None,
            parent_id=MY_DRIVE_ROOT,
        )

    _plan_child(
        drive_service,
        plan,
        key="templates",
        name=settings.templates_folder_name,
        kind="folder",
        mime_type=FOLDER_MIME_TYPE,
        parent=root,
        parent_id=root.existing_id,
    )

    if settings.create_clients_folder:
        _plan_child(
            drive_service,
            plan,
            key="clients",
            name=settings.clients_folder_name,
            kind="folder",
            mime_type=FOLDER_MIME_TYPE,
            parent=root,
            parent_id=root.existing_id,
        )

    plan.notes.append(
        "The master template is not planned here. It is produced only by the scrub "
        "pipeline (gm_gsa.master_template), which copies the canonical document to "
        f"{TEMP_SCRUB_NAME!r} and renames it to {MASTER_TEMPLATE_NAME!r} after validation."
    )

    if not plan.creates:
        plan.notes.append("Plan is idempotent: every folder already exists and will be reused.")
    return plan


# ---------------------------------------------------------------------------
# Applying
# ---------------------------------------------------------------------------


def _create_folder(drive_service: Any, name: str, parent_id: str) -> dict[str, Any]:
    assert_not_unscrubbed_master(name, "files.create")
    body = {"name": name, "mimeType": FOLDER_MIME_TYPE, "parents": [parent_id]}
    return (
        drive_service.files()
        .create(body=body, fields=FILE_FIELDS, supportsAllDrives=True)
        .execute()
    )


def read_back(drive_service: Any, file_id: str) -> dict[str, Any]:
    return (
        drive_service.files()
        .get(fileId=file_id, fields=FILE_FIELDS, supportsAllDrives=True)
        .execute()
    )


def apply_plan(drive_service: Any, plan: DrivePlan) -> list[dict[str, Any]]:
    """Create the planned folders in order. The only mutating function in this module.

    Folder creation and reuse are the only actions this function performs. A ``copy``
    action is refused outright: document copying belongs to ``gm_gsa.master_template``,
    where the copy is forced to land under the TEMP name and cannot skip the scrub.

    On any failure this raises ``PartialWriteError`` carrying every resource already
    created, so the caller can inventory instead of blindly rerunning.
    """
    resolved: dict[str, str] = {}
    created: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    for resource in plan.resources:
        parent_id = resource.parent_id or (
            resolved.get(resource.parent_key) if resource.parent_key else None
        )

        if resource.action == "reuse":
            resolved[resource.key] = str(resource.existing_id)
            results.append(
                {
                    "key": resource.key,
                    "name": resource.name,
                    "id": resource.existing_id,
                    "mimeType": resource.mime_type,
                    "parent_id": parent_id,
                    "status": "reused",
                }
            )
            continue

        if resource.action == "copy":
            raise UnscrubbedMasterError(
                f"Refusing to copy {resource.name!r} from this plan. Document copies are "
                "performed only by gm_gsa.master_template, which copies to the TEMP name "
                "and renames only after the scrub validations pass."
            )
        assert_not_unscrubbed_master(resource.name, f"apply_plan:{resource.action}")

        if parent_id is None and resource.key != "root":
            raise PartialWriteError(
                f"Cannot resolve a parent for {resource.key!r}.", created, resource.key
            )
        if resource.key == "root" and parent_id is None:
            parent_id = MY_DRIVE_ROOT

        try:
            created_file = _create_folder(drive_service, resource.name, parent_id)
        except Exception as exc:  # noqa: BLE001 - re-raised with an inventory
            classification = classify_api_error(exc)
            raise PartialWriteError(
                f"Failed while creating {resource.key!r} ({resource.name!r}): "
                f"{classification['kind']} - {classification['message']}",
                created,
                resource.key,
            ) from exc

        file_id = str(created_file.get("id"))
        resolved[resource.key] = file_id
        record = {
            "key": resource.key,
            "name": created_file.get("name"),
            "id": file_id,
            "mimeType": created_file.get("mimeType"),
            "parent_id": parent_id,
            "status": "created",
        }
        created.append(record)
        results.append(record)

    return results


def drive_url(file_id: str, mime_type: str) -> str:
    if mime_type == FOLDER_MIME_TYPE:
        return f"https://drive.google.com/drive/folders/{file_id}"
    if mime_type == DOCUMENT_MIME_TYPE:
        return f"https://docs.google.com/document/d/{file_id}/edit"
    return f"https://drive.google.com/file/d/{file_id}/view"


def check_template_access(
    drive_service: Any, docs_service: Any, template_id: str
) -> dict[str, Any]:
    """Probe the canonical template with both APIs without modifying it."""
    from googleapiclient.errors import HttpError

    report: dict[str, Any] = {"template_id": template_id}

    try:
        metadata = (
            drive_service.files()
            .get(fileId=template_id, fields="id, name, mimeType, capabilities(canCopy)")
            .execute()
        )
        report["drive"] = {
            "accessible": True,
            "name": metadata.get("name"),
            "mimeType": metadata.get("mimeType"),
            "is_native_google_doc": metadata.get("mimeType") == DOCUMENT_MIME_TYPE,
            "can_copy": (metadata.get("capabilities") or {}).get("canCopy"),
        }
    except HttpError as exc:
        report["drive"] = {"accessible": False, **classify_api_error(exc)}
    except Exception as exc:  # noqa: BLE001
        report["drive"] = {"accessible": False, **classify_api_error(exc)}

    try:
        document = (
            docs_service.documents()
            .get(documentId=template_id, fields="documentId,title")
            .execute()
        )
        report["docs"] = {
            "accessible": True,
            "documentId": document.get("documentId"),
            "title": document.get("title"),
        }
    except HttpError as exc:
        report["docs"] = {"accessible": False, **classify_api_error(exc)}
    except Exception as exc:  # noqa: BLE001
        report["docs"] = {"accessible": False, **classify_api_error(exc)}

    return report


# ---------------------------------------------------------------------------
# One-time Picker grant
# ---------------------------------------------------------------------------


def build_picker_authorization_params(
    *,
    template_id: str,
    expected_email: str,
    mime_type: str = DOCUMENT_MIME_TYPE,
) -> dict[str, str]:
    """Extra authorization-request parameters for the desktop Picker flow.

    ``scope`` is intentionally absent: it is supplied separately from ``PICKER_SCOPES`` so
    the drive.file-only rule is enforced in exactly one place. ``allow_multiple`` and
    ``allow_folder_selection`` are intentionally omitted, which limits the picker to a
    single file and forbids folder selection.
    """
    if not template_id.strip():
        raise PickerSelectionError("A canonical template ID is required for the Picker.")
    return {
        "trigger_onepick": "true",
        "file_ids": template_id.strip(),
        "mimetypes": mime_type,
        "prompt": "consent",
        "access_type": "offline",
        "login_hint": expected_email,
    }


def validate_picked_file_ids(raw: str | None, expected_template_id: str) -> list[str]:
    """Confirm the Picker returned exactly the one canonical template ID.

    Anything else - nothing picked, a different file, or more than one file - is a hard
    failure. The grant must never silently apply to an unintended document.
    """
    if raw is None or not str(raw).strip():
        raise PickerSelectionError(
            "The Picker returned no picked_file_ids. No file access was granted."
        )
    picked = [part.strip() for part in str(raw).split(",") if part.strip()]
    if len(picked) != 1:
        raise PickerSelectionError(
            f"Expected exactly one picked file, got {len(picked)}: {', '.join(picked)}"
        )
    if picked[0] != expected_template_id:
        raise PickerSelectionError(
            f"Picked file {picked[0]!r} does not match the canonical template "
            f"{expected_template_id!r}. No further action was taken."
        )
    return picked


def assert_not_main_token_path(candidate: str | Path, settings: DriveSettings) -> None:
    """Guard the long-lived Drive token against being overwritten by the Picker flow."""
    candidate_path = Path(candidate).expanduser()
    main_path = Path(settings.token_file).expanduser()
    try:
        same = candidate_path.resolve(strict=False) == main_path.resolve(strict=False)
    except OSError:  # pragma: no cover - platform dependent
        same = str(candidate_path) == str(main_path)
    if same:
        raise DriveAuthorizationError(
            f"Refusing to write the temporary Picker token over the main Drive token at "
            f"{main_path}."
        )


def format_plan_table(plan: DrivePlan) -> str:
    lines = [
        f"{'ACTION':<7} {'KIND':<9} {'NAME':<46} {'PARENT':<38} EXISTING ID",
        "-" * 130,
    ]
    for resource in plan.resources:
        row = resource.as_row()
        lines.append(
            f"{row['action']:<7} {row['kind']:<9} {row['name'][:45]:<46} "
            f"{str(row['parent'])[:37]:<38} {row['existing_id'] or '-'}"
        )
    return "\n".join(lines)


def plan_as_json(plan: DrivePlan) -> str:
    payload = {
        "summary": plan.summary(),
        "resources": [r.as_row() for r in plan.resources],
        "notes": plan.notes,
    }
    return json.dumps(redact_oauth_payload(payload), indent=2, sort_keys=True)
