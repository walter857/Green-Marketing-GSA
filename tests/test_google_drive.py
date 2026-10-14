from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gm_gsa.google_drive import (  # noqa: E402
    CANONICAL_TEMPLATE_ID,
    DOCUMENT_MIME_TYPE,
    DRIVE_SCOPES,
    FORBIDDEN_SCOPES,
    FOLDER_MIME_TYPE,
    MASTER_TEMPLATE_NAME,
    MY_DRIVE_ROOT,
    PICKER_AUTH_URI,
    PICKER_SCOPES,
    TEMP_SCRUB_NAME,
    DriveAmbiguityError,
    DriveAuthorizationError,
    DriveSettings,
    PartialWriteError,
    PickerSelectionError,
    UnscrubbedMasterError,
    apply_plan,
    assert_not_main_token_path,
    assert_not_unscrubbed_master,
    build_picker_authorization_params,
    validate_picked_file_ids,
    classify_api_error,
    drive_url,
    escape_query_value,
    find_children_by_exact_name,
    load_drive_settings,
    plan_as_json,
    plan_landing_page_drive,
    record_verified_ids,
    redact_error_text,
    redact_oauth_payload,
    resolve_unique_child,
)
from gm_gsa.config import ConfigurationError  # noqa: E402

# ---------------------------------------------------------------------------
# Fake Drive service
#
# The fake parses the real query string the module builds, so these tests exercise query
# construction rather than trusting it.
# ---------------------------------------------------------------------------

NAME_RE = re.compile(r"name = '((?:[^'\\]|\\.)*)'")
PARENT_RE = re.compile(r"'((?:[^'\\]|\\.)*)' in parents")
MIME_RE = re.compile(r"mimeType = '((?:[^'\\]|\\.)*)'")


def _unescape(value: str) -> str:
    return value.replace("\\'", "'").replace("\\\\", "\\")


class _Request:
    def __init__(self, result):
        self._result = result

    def execute(self):
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


class FakeFiles:
    def __init__(self, store, fail_on_create=None):
        self.store = store
        self.fail_on_create = fail_on_create or set()
        self.created = []
        self.copied = []
        self.list_queries = []

    def list(self, **kwargs):
        query = kwargs["q"]
        self.list_queries.append(query)
        if "trashed = false" not in query:
            raise AssertionError("every lookup must exclude trashed files")
        name_match = NAME_RE.search(query)
        parent_match = PARENT_RE.search(query)
        mime_match = MIME_RE.search(query)
        name = _unescape(name_match.group(1)) if name_match else None
        parent = _unescape(parent_match.group(1)) if parent_match else None
        mime = _unescape(mime_match.group(1)) if mime_match else None

        files = []
        for item in self.store:
            if item.get("trashed"):
                continue
            if name is not None and item["name"] != name:
                continue
            if parent is not None and parent not in item.get("parents", []):
                continue
            if mime is not None and item.get("mimeType") != mime:
                continue
            files.append(dict(item))
        return _Request({"files": files})

    def create(self, **kwargs):
        body = kwargs["body"]
        if body["name"] in self.fail_on_create:
            return _Request(RuntimeError(f"simulated failure creating {body['name']}"))
        new = {
            "id": f"folder-{len(self.created) + 1}",
            "name": body["name"],
            "mimeType": body.get("mimeType", FOLDER_MIME_TYPE),
            "parents": list(body.get("parents", [])),
            "webViewLink": "https://drive.google.com/drive/folders/x",
            "trashed": False,
        }
        self.created.append(new)
        self.store.append(new)
        return _Request(new)

    def copy(self, **kwargs):
        source_id = kwargs["fileId"]
        body = kwargs["body"]
        if body["name"] in self.fail_on_create:
            return _Request(RuntimeError(f"simulated failure copying to {body['name']}"))
        new = {
            "id": f"doc-{len(self.copied) + 1}",
            "name": body["name"],
            "mimeType": DOCUMENT_MIME_TYPE,
            "parents": list(body.get("parents", [])),
            "webViewLink": "https://docs.google.com/document/d/x/edit",
            "trashed": False,
            "copied_from": source_id,
        }
        self.copied.append(new)
        self.store.append(new)
        return _Request(new)

    def get(self, **kwargs):
        file_id = kwargs["fileId"]
        for item in self.store:
            if item["id"] == file_id:
                return _Request(dict(item))
        return _Request(RuntimeError(f"file not found: {file_id}"))


class FakeDrive:
    def __init__(self, store=None, fail_on_create=None):
        self._files = FakeFiles(list(store or []), fail_on_create)

    def files(self):
        return self._files


def make_settings(**overrides) -> DriveSettings:
    base = {
        "credentials_file": Path("D:/MG/secrets/green-marketing-drive-client.json"),
        "token_file": Path("D:/MG/secrets/green-marketing-drive-token.json"),
        "scopes": DRIVE_SCOPES,
        "root_folder_name": "Green Marketing Landing Pages",
        "root_folder_id": None,
        "templates_folder_name": "Templates",
        "master_template_name": "Landing Page Content Template - Master",
        "master_template_document_id": None,
        "canonical_source_template_id": "1bQR5wLIF47fd-wNOaNxtjlun1ch8Fc5kmfCA93vuFuc",
        "create_clients_folder": False,
        "clients_folder_name": "Clients",
    }
    base.update(overrides)
    return DriveSettings(**base)


def folder(file_id: str, name: str, parent: str) -> dict:
    return {
        "id": file_id,
        "name": name,
        "mimeType": FOLDER_MIME_TYPE,
        "parents": [parent],
        "webViewLink": f"https://drive.google.com/drive/folders/{file_id}",
        "trashed": False,
    }


def master_doc(file_id: str, parent: str) -> dict:
    return {
        "id": file_id,
        "name": "Landing Page Content Template - Master",
        "mimeType": DOCUMENT_MIME_TYPE,
        "parents": [parent],
        "webViewLink": f"https://docs.google.com/document/d/{file_id}/edit",
        "trashed": False,
    }


class ExactNameLookupTests(unittest.TestCase):
    def test_ignores_partial_and_case_variants(self):
        drive = FakeDrive(
            [
                folder("a", "Templates", "root-id"),
                folder("b", "Templates Archive", "root-id"),
                folder("c", "templates", "root-id"),
            ]
        )
        matches = find_children_by_exact_name(drive, "root-id", "Templates", FOLDER_MIME_TYPE)
        self.assertEqual([m["id"] for m in matches], ["a"])

    def test_is_scoped_to_the_expected_parent(self):
        drive = FakeDrive(
            [
                folder("a", "Templates", "root-id"),
                folder("b", "Templates", "some-other-folder"),
            ]
        )
        matches = find_children_by_exact_name(drive, "root-id", "Templates", FOLDER_MIME_TYPE)
        self.assertEqual([m["id"] for m in matches], ["a"])

    def test_excludes_trashed_resources(self):
        trashed = folder("a", "Templates", "root-id")
        trashed["trashed"] = True
        drive = FakeDrive([trashed])
        self.assertEqual(
            find_children_by_exact_name(drive, "root-id", "Templates", FOLDER_MIME_TYPE), []
        )

    def test_quotes_in_names_are_escaped(self):
        self.assertEqual(escape_query_value("Bob's Yard"), "Bob\\'s Yard")
        drive = FakeDrive([folder("a", "Bob's Yard", "root-id")])
        matches = find_children_by_exact_name(drive, "root-id", "Bob's Yard", FOLDER_MIME_TYPE)
        self.assertEqual([m["id"] for m in matches], ["a"])

    def test_missing_resource_resolves_to_none(self):
        self.assertIsNone(
            resolve_unique_child(FakeDrive([]), "root-id", "Templates", FOLDER_MIME_TYPE)
        )


class DuplicateDetectionTests(unittest.TestCase):
    def test_duplicate_names_raise_instead_of_guessing(self):
        drive = FakeDrive(
            [folder("a", "Templates", "root-id"), folder("b", "Templates", "root-id")]
        )
        with self.assertRaises(DriveAmbiguityError) as ctx:
            resolve_unique_child(drive, "root-id", "Templates", FOLDER_MIME_TYPE)
        self.assertIn("a", str(ctx.exception))
        self.assertIn("b", str(ctx.exception))

    def test_plan_surfaces_duplicate_root_folders(self):
        drive = FakeDrive(
            [
                folder("r1", "Green Marketing Landing Pages", MY_DRIVE_ROOT),
                folder("r2", "Green Marketing Landing Pages", MY_DRIVE_ROOT),
            ]
        )
        with self.assertRaises(DriveAmbiguityError):
            plan_landing_page_drive(drive, make_settings())

    def test_plan_surfaces_duplicate_templates_folders(self):
        drive = FakeDrive(
            [
                folder("r1", "Green Marketing Landing Pages", MY_DRIVE_ROOT),
                folder("t1", "Templates", "r1"),
                folder("t2", "Templates", "r1"),
            ]
        )
        with self.assertRaises(DriveAmbiguityError):
            plan_landing_page_drive(drive, make_settings())


class DryRunTests(unittest.TestCase):
    def test_planning_writes_nothing(self):
        drive = FakeDrive([])
        plan = plan_landing_page_drive(drive, make_settings())
        self.assertEqual(drive.files().created, [])
        self.assertEqual(drive.files().copied, [])
        self.assertEqual(plan.summary(), {"total": 2, "create": 2, "copy": 0, "reuse": 0})

    def test_plan_covers_folders_only_and_never_the_master_document(self):
        plan = plan_landing_page_drive(FakeDrive([]), make_settings())
        self.assertEqual([r.key for r in plan.resources], ["root", "templates"])
        self.assertEqual([r.action for r in plan.resources], ["create", "create"])
        self.assertTrue(all(r.kind == "folder" for r in plan.resources))
        self.assertTrue(all(r.action != "copy" for r in plan.resources))

    def test_no_resource_is_planned_under_the_final_master_name(self):
        for settings in (make_settings(), make_settings(create_clients_folder=True)):
            plan = plan_landing_page_drive(FakeDrive([]), settings)
            self.assertNotIn(MASTER_TEMPLATE_NAME, [r.name for r in plan.resources])

    def test_no_client_folder_is_ever_planned(self):
        plan = plan_landing_page_drive(FakeDrive([]), make_settings())
        self.assertFalse(any("client" in r.key.lower() for r in plan.resources))

    def test_clients_folder_only_when_explicitly_enabled(self):
        plan = plan_landing_page_drive(FakeDrive([]), make_settings(create_clients_folder=True))
        self.assertEqual([r.key for r in plan.resources], ["root", "templates", "clients"])


class IdempotencyTests(unittest.TestCase):
    def test_existing_scaffold_plans_zero_creates(self):
        drive = FakeDrive(
            [
                folder("root-1", "Green Marketing Landing Pages", MY_DRIVE_ROOT),
                folder("tpl-1", "Templates", "root-1"),
                master_doc("doc-1", "tpl-1"),
            ]
        )
        plan = plan_landing_page_drive(drive, make_settings())
        self.assertEqual(plan.summary(), {"total": 2, "create": 0, "copy": 0, "reuse": 2})
        self.assertEqual(plan.creates, [])

        results = apply_plan(drive, plan)
        self.assertEqual([r["status"] for r in results], ["reused"] * 2)
        self.assertEqual(drive.files().created, [])
        self.assertEqual(drive.files().copied, [])

    def test_apply_twice_creates_nothing_the_second_time(self):
        drive = FakeDrive([])
        first = apply_plan(drive, plan_landing_page_drive(drive, make_settings()))
        self.assertEqual([r["status"] for r in first], ["created"] * 2)

        second_plan = plan_landing_page_drive(drive, make_settings())
        self.assertEqual(second_plan.summary()["create"], 0)
        self.assertEqual(second_plan.summary()["copy"], 0)
        second = apply_plan(drive, second_plan)
        self.assertEqual([r["status"] for r in second], ["reused"] * 2)
        self.assertEqual(len(drive.files().created), 2)
        self.assertEqual(drive.files().copied, [])


class CreationAndCopyTests(unittest.TestCase):
    def test_folders_are_created_under_the_correct_parents(self):
        drive = FakeDrive([])
        apply_plan(drive, plan_landing_page_drive(drive, make_settings()))
        created = {f["name"]: f for f in drive.files().created}
        self.assertEqual(created["Green Marketing Landing Pages"]["parents"], [MY_DRIVE_ROOT])
        root_id = created["Green Marketing Landing Pages"]["id"]
        self.assertEqual(created["Templates"]["parents"], [root_id])

    def test_the_initializer_never_copies_a_document(self):
        """The unsafe path: copying the canonical example straight to its final name."""
        drive = FakeDrive([])
        apply_plan(drive, plan_landing_page_drive(drive, make_settings()))
        self.assertEqual(drive.files().copied, [])
        self.assertTrue(all(f["mimeType"] == FOLDER_MIME_TYPE for f in drive.files().created))
        self.assertNotIn(
            MASTER_TEMPLATE_NAME, [f["name"] for f in drive.files().created]
        )

    def test_google_drive_module_has_no_copy_helper_at_all(self):
        import gm_gsa.google_drive as module

        self.assertFalse(
            [name for name in dir(module) if "copy" in name.lower()],
            "google_drive must expose no copy helper; copying belongs to master_template",
        )
        source = (
            Path(__file__).resolve().parents[1] / "src" / "gm_gsa" / "google_drive.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn(".copy(", source)

    def test_configured_root_id_is_reused_without_scanning_my_drive(self):
        drive = FakeDrive([folder("tpl-1", "Templates", "known-root")])
        plan = plan_landing_page_drive(drive, make_settings(root_folder_id="known-root"))
        self.assertEqual(plan.resources[0].action, "reuse")
        self.assertEqual(plan.resources[0].existing_id, "known-root")
        my_drive_clause = f"'{MY_DRIVE_ROOT}' in parents"
        self.assertTrue(
            all(my_drive_clause not in q for q in drive.files().list_queries),
            "a configured root ID must not trigger a My Drive top-level scan",
        )


class PartialFailureTests(unittest.TestCase):
    def test_folder_failure_inventories_what_was_created(self):
        drive = FakeDrive([], fail_on_create={"Templates"})
        plan = plan_landing_page_drive(drive, make_settings())
        with self.assertRaises(PartialWriteError) as ctx:
            apply_plan(drive, plan)

        error = ctx.exception
        self.assertEqual(error.failed_key, "templates")
        inventory = error.inventory()
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0]["name"], "Green Marketing Landing Pages")
        self.assertTrue(inventory[0]["id"])
        # Nothing downstream of the failure may run.
        self.assertEqual(drive.files().copied, [])

    def test_clients_folder_failure_reports_both_created_folders(self):
        drive = FakeDrive([], fail_on_create={"Clients"})
        with self.assertRaises(PartialWriteError) as ctx:
            apply_plan(
                drive,
                plan_landing_page_drive(drive, make_settings(create_clients_folder=True)),
            )
        inventory = ctx.exception.inventory()
        self.assertEqual(
            [item["name"] for item in inventory],
            ["Green Marketing Landing Pages", "Templates"],
        )
        self.assertEqual(ctx.exception.failed_key, "clients")


class UnscrubbedMasterNameGuardTests(unittest.TestCase):
    """The final master name may only ever be reached by renaming a validated TEMP copy."""

    def test_the_final_name_is_refused_for_creation(self):
        with self.assertRaises(UnscrubbedMasterError) as ctx:
            assert_not_unscrubbed_master(MASTER_TEMPLATE_NAME, "files.create")
        self.assertIn(TEMP_SCRUB_NAME, str(ctx.exception))

    def test_padded_final_name_is_still_refused(self):
        with self.assertRaises(UnscrubbedMasterError):
            assert_not_unscrubbed_master(f"  {MASTER_TEMPLATE_NAME}  ", "files.copy")

    def test_the_temp_name_and_folder_names_are_allowed(self):
        for name in (TEMP_SCRUB_NAME, "Templates", "Green Marketing Landing Pages", ""):
            assert_not_unscrubbed_master(name, "files.create")

    def test_apply_plan_refuses_a_hand_built_copy_action(self):
        """Even a plan constructed by hand cannot smuggle a document copy through."""
        from gm_gsa.google_drive import DrivePlan, PlannedResource

        plan = DrivePlan(
            resources=[
                PlannedResource(
                    key="master_template",
                    name=MASTER_TEMPLATE_NAME,
                    kind="document",
                    mime_type=DOCUMENT_MIME_TYPE,
                    action="copy",
                    parent_id="tpl-1",
                    source_template_id=CANONICAL_TEMPLATE_ID,
                )
            ]
        )
        drive = FakeDrive([])
        with self.assertRaises(UnscrubbedMasterError):
            apply_plan(drive, plan)
        self.assertEqual(drive.files().copied, [])
        self.assertEqual(drive.files().created, [])

    def test_apply_plan_refuses_a_folder_named_like_the_master(self):
        from gm_gsa.google_drive import DrivePlan, PlannedResource

        plan = DrivePlan(
            resources=[
                PlannedResource(
                    key="root",
                    name=MASTER_TEMPLATE_NAME,
                    kind="folder",
                    mime_type=FOLDER_MIME_TYPE,
                    action="create",
                    parent_id=MY_DRIVE_ROOT,
                )
            ]
        )
        drive = FakeDrive([])
        with self.assertRaises(UnscrubbedMasterError):
            apply_plan(drive, plan)
        self.assertEqual(drive.files().created, [])


class RecordVerifiedIdsTests(unittest.TestCase):
    SAMPLE = (
        "drive:\n"
        '  landing_page_root_folder_name: "Green Marketing Landing Pages"\n'
        "  # a comment that must survive\n"
        "  landing_page_root_folder_id: null\n"
        "  master_template_document_id: null\n"
        f'  canonical_source_template_id: "{CANONICAL_TEMPLATE_ID}"\n'
    )

    def _write_sample(self) -> Path:
        import tempfile

        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".yaml", delete=False, encoding="utf-8"
        )
        handle.write(self.SAMPLE)
        handle.close()
        return Path(handle.name)

    def test_ids_are_written_and_comments_survive(self):
        path = self._write_sample()
        record_verified_ids("rootFolderId123", "masterDocId4567", config_path=path)
        text = path.read_text(encoding="utf-8")
        self.assertIn('landing_page_root_folder_id: "rootFolderId123"', text)
        self.assertIn('master_template_document_id: "masterDocId4567"', text)
        self.assertIn("# a comment that must survive", text)
        self.assertIn(CANONICAL_TEMPLATE_ID, text)

    def test_the_canonical_source_can_never_be_recorded_as_the_master(self):
        path = self._write_sample()
        before = path.read_text(encoding="utf-8")
        with self.assertRaises(ConfigurationError):
            record_verified_ids("rootFolderId123", CANONICAL_TEMPLATE_ID, config_path=path)
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_non_id_values_are_refused_so_no_secret_can_land_here(self):
        path = self._write_sample()
        before = path.read_text(encoding="utf-8")
        for bad in ("", "   ", "short", "1//0gRefreshTokenValue", 'x"\n  injected: true'):
            with self.assertRaises(ConfigurationError):
                record_verified_ids(bad, "masterDocId4567", config_path=path)
            with self.assertRaises(ConfigurationError):
                record_verified_ids("rootFolderId123", bad, config_path=path)
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_the_same_id_cannot_be_both_root_and_master(self):
        path = self._write_sample()
        with self.assertRaises(ConfigurationError):
            record_verified_ids("sameIdValue123", "sameIdValue123", config_path=path)


class RedactionTests(unittest.TestCase):
    def test_oauth_identifiers_and_secrets_are_masked(self):
        payload = {
            "installed": {
                "client_id": "1234-abc.apps.googleusercontent.com",
                "client_secret": "GOCSPX-supersecretvalue",
                "refresh_token": "1//0gSuperSecretRefreshToken",
                "access_token": "ya29.a0AfB_byRealAccessToken",
                "project_id": "green-marketing-drive",
                "redirect_uris": ["http://localhost"],
            }
        }
        rendered = str(redact_oauth_payload(payload))
        for secret in (
            "GOCSPX-supersecretvalue",
            "1//0gSuperSecretRefreshToken",
            "ya29.a0AfB_byRealAccessToken",
            "1234-abc.apps.googleusercontent.com",
        ):
            self.assertNotIn(secret, rendered)
        # Non-secret context survives so reports stay useful.
        self.assertEqual(
            redact_oauth_payload(payload)["installed"]["project_id"], "green-marketing-drive"
        )

    def test_redaction_does_not_mutate_the_original(self):
        payload = {"client_secret": "GOCSPX-original"}
        redact_oauth_payload(payload)
        self.assertEqual(payload["client_secret"], "GOCSPX-original")

    def test_error_text_strips_long_opaque_tokens(self):
        message = (
            "invalid_grant for refresh_token=1//0gABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop "
            "and client_secret=GOCSPX-abcdefghijklmnopqrstuvwx"
        )
        cleaned = redact_error_text(message)
        self.assertNotIn("1//0gABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop", cleaned)
        self.assertNotIn("GOCSPX-abcdefghijklmnopqrstuvwx", cleaned)
        self.assertIn("invalid_grant", cleaned)

    def test_plan_json_carries_no_secret_keys(self):
        rendered = plan_as_json(plan_landing_page_drive(FakeDrive([]), make_settings())).lower()
        for marker in ("client_secret", "refresh_token", "access_token"):
            self.assertNotIn(marker, rendered)

    def test_settings_describe_reports_presence_not_contents(self):
        described = make_settings().describe()
        self.assertEqual(set(described["scopes"]), set(DRIVE_SCOPES))
        self.assertIn(described["credentials_file_present"], (True, False))
        self.assertNotIn("client_secret", str(described).lower())


class ScopeAndErrorTests(unittest.TestCase):
    def test_default_scopes_are_least_privilege(self):
        self.assertEqual(
            DRIVE_SCOPES,
            (
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/documents",
            ),
        )
        self.assertNotIn("https://www.googleapis.com/auth/drive", DRIVE_SCOPES)

    def test_disabled_api_is_distinguished_from_missing_file(self):
        class _Resp:
            def __init__(self, status):
                self.status = status

        class _HttpError(Exception):
            def __init__(self, status, reason):
                super().__init__(reason)
                self.resp = _Resp(status)
                self.reason = reason

        disabled = classify_api_error(
            _HttpError(403, "Google Docs API has not been used in project 123 before")
        )
        self.assertEqual(disabled["kind"], "api_not_enabled")

        missing = classify_api_error(_HttpError(404, "File not found: abc"))
        self.assertEqual(missing["kind"], "not_found_or_not_shared_with_this_oauth_app")

    def test_drive_url_matches_resource_type(self):
        self.assertEqual(
            drive_url("abc", FOLDER_MIME_TYPE), "https://drive.google.com/drive/folders/abc"
        )
        self.assertEqual(
            drive_url("abc", DOCUMENT_MIME_TYPE), "https://docs.google.com/document/d/abc/edit"
        )


CANONICAL = "1bQR5wLIF47fd-wNOaNxtjlun1ch8Fc5kmfCA93vuFuc"


class PickerParameterTests(unittest.TestCase):
    def params(self):
        return build_picker_authorization_params(
            template_id=CANONICAL, expected_email="access@greenmarketingfl.com"
        )

    def test_trigger_onepick_is_requested(self):
        self.assertEqual(self.params()["trigger_onepick"], "true")

    def test_picker_scope_is_drive_file_only(self):
        self.assertEqual(PICKER_SCOPES, ("https://www.googleapis.com/auth/drive.file",))
        self.assertNotIn("https://www.googleapis.com/auth/documents", PICKER_SCOPES)
        self.assertNotIn("https://www.googleapis.com/auth/drive", PICKER_SCOPES)
        self.assertNotIn("https://www.googleapis.com/auth/drive.readonly", PICKER_SCOPES)

    def test_picker_never_carries_a_scope_parameter_of_its_own(self):
        # Scope comes from PICKER_SCOPES alone, so drive.file cannot be widened here.
        self.assertNotIn("scope", self.params())

    def test_picker_is_filtered_to_the_canonical_template_only(self):
        params = self.params()
        self.assertEqual(params["file_ids"], CANONICAL)
        self.assertNotIn(",", params["file_ids"])

    def test_picker_is_limited_to_google_docs(self):
        self.assertEqual(self.params()["mimetypes"], DOCUMENT_MIME_TYPE)

    def test_multiple_and_folder_selection_are_never_enabled(self):
        params = self.params()
        self.assertNotIn("allow_multiple", params)
        self.assertNotIn("allow_folder_selection", params)

    def test_account_is_pinned_with_a_login_hint(self):
        self.assertEqual(self.params()["login_hint"], "access@greenmarketingfl.com")

    def test_offline_consent_is_requested(self):
        params = self.params()
        self.assertEqual(params["prompt"], "consent")
        self.assertEqual(params["access_type"], "offline")

    def test_documented_v2_authorization_endpoint_is_used(self):
        self.assertEqual(PICKER_AUTH_URI, "https://accounts.google.com/o/oauth2/v2/auth")

    def test_blank_template_id_is_rejected(self):
        with self.assertRaises(PickerSelectionError):
            build_picker_authorization_params(
                template_id="   ", expected_email="access@greenmarketingfl.com"
            )


class PickedFileValidationTests(unittest.TestCase):
    def test_exact_match_is_accepted(self):
        self.assertEqual(validate_picked_file_ids(CANONICAL, CANONICAL), [CANONICAL])

    def test_surrounding_whitespace_is_tolerated(self):
        self.assertEqual(validate_picked_file_ids(f"  {CANONICAL} ", CANONICAL), [CANONICAL])

    def test_a_different_file_is_rejected(self):
        with self.assertRaises(PickerSelectionError) as ctx:
            validate_picked_file_ids("someOtherFileId", CANONICAL)
        self.assertIn("does not match", str(ctx.exception))

    def test_multiple_files_are_rejected(self):
        with self.assertRaises(PickerSelectionError) as ctx:
            validate_picked_file_ids(f"{CANONICAL},otherFileId", CANONICAL)
        self.assertIn("exactly one", str(ctx.exception))

    def test_empty_selection_is_rejected(self):
        for value in (None, "", "   ", ","):
            with self.assertRaises(PickerSelectionError):
                validate_picked_file_ids(value, CANONICAL)

    def test_a_prefix_of_the_canonical_id_is_rejected(self):
        with self.assertRaises(PickerSelectionError):
            validate_picked_file_ids(CANONICAL[:-1], CANONICAL)


class MainTokenProtectionTests(unittest.TestCase):
    def test_writing_over_the_main_token_is_refused(self):
        settings = make_settings()
        with self.assertRaises(DriveAuthorizationError) as ctx:
            assert_not_main_token_path(settings.token_file, settings)
        self.assertIn("Refusing", str(ctx.exception))

    def test_equivalent_path_spellings_are_still_refused(self):
        settings = make_settings()
        disguised = Path("D:/MG/secrets/../secrets/green-marketing-drive-token.json")
        with self.assertRaises(DriveAuthorizationError):
            assert_not_main_token_path(disguised, settings)

    def test_a_separate_temporary_path_is_allowed(self):
        settings = make_settings()
        assert_not_main_token_path(Path("D:/MG/secrets/picker-temp-token.json"), settings)

    def test_picker_grant_script_never_persists_a_token(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "grant_canonical_template_access.py"
        ).read_text(encoding="utf-8")
        # The Picker credentials must stay in memory only.
        self.assertNotIn("save_credentials", source)
        self.assertNotIn("to_json()", source)
        self.assertNotIn("write_text", source)

    def test_picker_grant_script_never_prints_the_authorization_url(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "grant_canonical_template_access.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("print(authorization_url", source)
        self.assertNotIn("{authorization_url}", source)


class PickerRedactionTests(unittest.TestCase):
    def test_authorization_code_and_tokens_are_redacted(self):
        payload = {
            "code": "4/0AeanS0abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGH",
            "access_token": "ya29.a0AfB_bySecretAccessTokenValue",
            "refresh_token": "1//0gSecretRefreshTokenValue",
            "client_id": "15566403719-abc.apps.googleusercontent.com",
            "picked_file_ids": CANONICAL,
        }
        rendered = str(redact_oauth_payload(payload))
        for secret in (
            "ya29.a0AfB_bySecretAccessTokenValue",
            "1//0gSecretRefreshTokenValue",
            "15566403719-abc.apps.googleusercontent.com",
        ):
            self.assertNotIn(secret, rendered)

    def test_a_callback_url_with_a_code_is_scrubbed(self):
        callback = (
            "http://localhost:8080/?state=abc&code="
            "4or0AeanS0abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGH"
            f"&scope=https://www.googleapis.com/auth/drive.file&picked_file_ids={CANONICAL}"
        )
        cleaned = redact_error_text(callback)
        self.assertNotIn("4or0AeanS0abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGH", cleaned)

    def test_picker_parameters_contain_no_secret_material(self):
        rendered = str(
            build_picker_authorization_params(
                template_id=CANONICAL, expected_email="access@greenmarketingfl.com"
            )
        ).lower()
        for marker in ("client_id", "client_secret", "code", "token"):
            self.assertNotIn(marker, rendered)


class TestForbiddenScopeGuard(unittest.TestCase):
    """The approved scope set may include drive.readonly, never full read/write drive."""

    @staticmethod
    def _write_config(tmp, scopes):
        path = Path(tmp) / "google-drive.yaml"
        lines = [
            "drive:",
            "  landing_page_root_folder_name: 'Green Marketing Landing Pages'",
            "  templates_folder_name: 'Templates'",
            f"  master_template_name: '{MASTER_TEMPLATE_NAME}'",
            "oauth:",
            "  scopes:",
        ]
        lines += [f"    - '{scope}'" for scope in scopes]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def test_drive_file_readonly_and_documents_are_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_config(
                tmp,
                [
                    "https://www.googleapis.com/auth/drive.file",
                    "https://www.googleapis.com/auth/drive.readonly",
                    "https://www.googleapis.com/auth/documents",
                ],
            )
            settings = load_drive_settings(path)
            self.assertIn("https://www.googleapis.com/auth/drive.readonly", settings.scopes)

    def test_full_read_write_drive_scope_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_config(
                tmp,
                [
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/documents",
                ],
            )
            with self.assertRaises(ConfigurationError) as ctx:
                load_drive_settings(path)
            self.assertIn("full read/write Drive scope", str(ctx.exception))

    def test_writes_still_target_drive_file_only(self):
        self.assertEqual(PICKER_SCOPES, ("https://www.googleapis.com/auth/drive.file",))
        self.assertIn("https://www.googleapis.com/auth/drive.file", DRIVE_SCOPES)

    def test_the_shipped_config_passes_the_guard(self):
        settings = load_drive_settings(
            Path(__file__).resolve().parents[1] / "config" / "google-drive.yaml"
        )
        self.assertFalse(set(settings.scopes) & FORBIDDEN_SCOPES)


if __name__ == "__main__":
    unittest.main()
