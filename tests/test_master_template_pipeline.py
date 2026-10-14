"""Proofs for the one safe master-template sequence.

Every test here exists to make a specific unsafe outcome impossible rather than unlikely:
an unscrubbed document under the final master name, a write aimed at the canonical source,
a rename that outruns validation, a blind second TEMP copy, or a configuration write that
happens before the document was proven clean.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import ConfigurationError  # noqa: E402
from gm_gsa.google_drive import (  # noqa: E402
    CANONICAL_TEMPLATE_ID,
    DOCUMENT_MIME_TYPE,
    DRIVE_SCOPES,
    FOLDER_MIME_TYPE,
    MASTER_TEMPLATE_NAME,
    MY_DRIVE_ROOT,
    TEMP_SCRUB_NAME,
    DriveAmbiguityError,
    DriveSettings,
    PartialWriteError,
    UnscrubbedMasterError,
)
from gm_gsa.master_template import (  # noqa: E402
    STATUS_BLOCKED_TEMP_EXISTS,
    STATUS_CREATE_MASTER,
    STATUS_REUSE_MASTER,
    MasterTemplateBlockedError,
    apply_master_template,
    assert_no_forbidden_operations,
    copy_canonical_to_temp,
    expected_new_resources,
    format_pipeline,
    plan_master_template,
)
from gm_gsa.template_scrub import (  # noqa: E402
    CanonicalTemplateWriteError,
    load_scrub_manifest,
    simulate_scrub,
    validate_scrubbed,
)

MANIFEST_PATH = ROOT / "config" / "landing-page-template-scrub.yaml"

NAME_RE = re.compile(r"name = '((?:[^'\\]|\\.)*)'")
PARENT_RE = re.compile(r"'((?:[^'\\]|\\.)*)' in parents")
MIME_RE = re.compile(r"mimeType = '((?:[^'\\]|\\.)*)'")


def _unescape(value: str) -> str:
    return value.replace("\\'", "'").replace("\\\\", "\\")


# ---------------------------------------------------------------------------
# Document fixture
# ---------------------------------------------------------------------------


def paragraph(text, style="NORMAL_TEXT", bullet=False):
    para = {
        "elements": [{"textRun": {"content": text, "textStyle": {}}}],
        "paragraphStyle": {"namedStyleType": style},
    }
    if bullet:
        para["bullet"] = {"listId": "l1"}
    return {"paragraph": para}


def canonical_document():
    """A miniature of the canonical example: real client facts in a real structure."""
    return {
        "title": "AC Repair Landing Page Content",
        "body": {
            "content": [
                paragraph("Ambient Cooling & Heating", "HEADING_1"),
                paragraph("Call (410) 761-0932"),
                paragraph("Comprehensive AC repair diagnosis", bullet=True),
                paragraph("Rachel Ehmann"),
            ]
        },
    }


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _Request:
    def __init__(self, result):
        self._result = result

    def execute(self):
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


class FakeFiles:
    """Records every mutating call. Destructive verbs raise if they are ever reached."""

    def __init__(self, store, doc_store, fail_on_copy=False, fail_on_create=None):
        self.store = store
        self.doc_store = doc_store
        self.fail_on_copy = fail_on_copy
        self.fail_on_create = fail_on_create or set()
        self.created = []
        self.copied = []
        self.updates = []
        self.list_queries = []

    def list(self, **kwargs):
        query = kwargs["q"]
        self.list_queries.append(query)
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
            "id": f"1generatedFolderId{len(self.created) + 1:04d}AAAAAA",
            "name": body["name"],
            "mimeType": body.get("mimeType", FOLDER_MIME_TYPE),
            "parents": list(body.get("parents", [])),
            "trashed": False,
        }
        # Snapshot the record: the store entry is mutated by a later rename, and an
        # aliased history would hide the name a resource was actually born under.
        self.created.append(dict(new))
        self.store.append(new)
        return _Request(new)

    def copy(self, **kwargs):
        if self.fail_on_copy:
            return _Request(RuntimeError("simulated copy failure"))
        body = kwargs["body"]
        source_id = kwargs["fileId"]
        new = {
            "id": f"1generatedDocId{len(self.copied) + 1:04d}BBBBBBBBB",
            "name": body["name"],
            "mimeType": DOCUMENT_MIME_TYPE,
            "parents": list(body.get("parents", [])),
            "trashed": False,
            "copied_from": source_id,
        }
        self.copied.append(dict(new))
        self.store.append(new)
        # The real files.copy duplicates content as well as metadata, so the Docs-side
        # store must gain an independent copy. Sharing the object would let a write to the
        # copy silently mutate the canonical fixture and hide a real safety failure.
        if source_id in self.doc_store:
            self.doc_store[new["id"]] = deepcopy(self.doc_store[source_id])
        return _Request(new)

    def update(self, **kwargs):
        self.updates.append(kwargs)
        file_id = kwargs["fileId"]
        body = kwargs.get("body") or {}
        for item in self.store:
            if item["id"] == file_id:
                if body.get("name"):
                    item["name"] = body["name"]
                return _Request({"id": file_id, "name": item["name"]})
        return _Request(RuntimeError(f"file not found: {file_id}"))

    def get(self, **kwargs):
        for item in self.store:
            if item["id"] == kwargs["fileId"]:
                return _Request(dict(item))
        return _Request(RuntimeError(f"file not found: {kwargs['fileId']}"))

    # Destructive verbs the workflow must never reach.
    def delete(self, **kwargs):  # pragma: no cover - reaching this is the failure
        raise AssertionError("files.delete must never be called")

    def trash(self, **kwargs):  # pragma: no cover
        raise AssertionError("files.trash must never be called")


class FakeDrive:
    def __init__(self, store=None, doc_store=None, fail_on_copy=False, fail_on_create=None):
        self._files = FakeFiles(
            list(store or []), doc_store if doc_store is not None else {}, fail_on_copy,
            fail_on_create,
        )

    def files(self):
        return self._files

    def permissions(self):  # pragma: no cover - reaching this is the failure
        raise AssertionError("permissions must never be touched")


class FakeDocuments:
    def __init__(self, documents, manifest, mode="clean"):
        self.documents = documents
        self.manifest = manifest
        self.mode = mode  # clean | residue | structure_damage
        self.batch_calls = []
        self.get_calls = []

    def get(self, **kwargs):
        document_id = kwargs["documentId"]
        self.get_calls.append(document_id)
        if document_id not in self.documents:
            return _Request(RuntimeError(f"document not found: {document_id}"))
        return _Request(self.documents[document_id])

    def batchUpdate(self, **kwargs):  # noqa: N802 - mirrors the Google client
        self.batch_calls.append(kwargs)
        document_id = kwargs["documentId"]
        if self.mode == "residue":
            return _Request({"documentId": document_id})
        scrubbed = simulate_scrub(self.documents[document_id], self.manifest)
        if self.mode == "structure_damage":
            scrubbed["body"]["content"] = scrubbed["body"]["content"][:-1]
        self.documents[document_id] = scrubbed
        return _Request({"documentId": document_id})


class FakeDocs:
    def __init__(self, documents, manifest, mode="clean"):
        self._documents = FakeDocuments(documents, manifest, mode)

    def documents(self):
        return self._documents


def make_settings(**overrides) -> DriveSettings:
    base = {
        "credentials_file": Path("D:/MG/secrets/green-marketing-drive-client.json"),
        "token_file": Path("D:/MG/secrets/green-marketing-drive-token.json"),
        "scopes": DRIVE_SCOPES,
        "root_folder_name": "Green Marketing Landing Pages",
        "root_folder_id": None,
        "templates_folder_name": "Templates",
        "master_template_name": MASTER_TEMPLATE_NAME,
        "master_template_document_id": None,
        "canonical_source_template_id": CANONICAL_TEMPLATE_ID,
        "create_clients_folder": False,
        "clients_folder_name": "Clients",
    }
    base.update(overrides)
    return DriveSettings(**base)


def folder(file_id, name, parent):
    return {
        "id": file_id,
        "name": name,
        "mimeType": FOLDER_MIME_TYPE,
        "parents": [parent],
        "trashed": False,
    }


def document(file_id, name, parent):
    return {
        "id": file_id,
        "name": name,
        "mimeType": DOCUMENT_MIME_TYPE,
        "parents": [parent],
        "trashed": False,
    }


def scaffold():
    """Root and Templates already exist; the Templates folder is empty."""
    return [
        folder("1rootFolderIdAAAAAAAAAAAAAAAA", "Green Marketing Landing Pages", MY_DRIVE_ROOT),
        folder("1templatesFolderIdBBBBBBBBBBB", "Templates", "1rootFolderIdAAAAAAAAAAAAAAAA"),
    ]


class PipelineTestCase(unittest.TestCase):
    def setUp(self):
        self.manifest = load_scrub_manifest(MANIFEST_PATH)
        self.doc_store = {CANONICAL_TEMPLATE_ID: canonical_document()}
        handle = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False)
        handle.close()
        self.config_path = Path(handle.name)
        self.config_path.write_text(
            "drive:\n"
            "  landing_page_root_folder_id: null\n"
            "  master_template_document_id: null\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.config_path.unlink(missing_ok=True)

    def drive(self, store=None, **kwargs):
        """Drive and Docs fakes share one document store, as the real APIs do."""
        return FakeDrive(store, doc_store=self.doc_store, **kwargs)

    def docs(self, mode="clean"):
        return FakeDocs(self.doc_store, self.manifest, mode)

    def run_apply(self, drive, docs, settings=None, plan=None):
        settings = settings or make_settings()
        plan = plan or plan_master_template(drive, settings)
        return apply_master_template(
            drive, docs, settings, self.manifest, plan, config_path=self.config_path
        )

    def recorded(self) -> str:
        return self.config_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. No unscrubbed final master can be created
# ---------------------------------------------------------------------------


class UnscrubbedMasterIsImpossibleTests(PipelineTestCase):
    def test_the_only_copy_in_the_repository_lands_under_the_temp_name(self):
        drive = self.drive(scaffold())
        copy_canonical_to_temp(drive, CANONICAL_TEMPLATE_ID, "1templatesFolderIdBBBBBBBBBBB")
        self.assertEqual(len(drive.files().copied), 1)
        self.assertEqual(drive.files().copied[0]["name"], TEMP_SCRUB_NAME)

    def test_the_copy_helper_takes_no_name_argument(self):
        import inspect

        parameters = set(inspect.signature(copy_canonical_to_temp).parameters)
        self.assertEqual(parameters, {"drive_service", "canonical_id", "templates_folder_id"})

    def test_no_repository_source_copies_to_the_final_name(self):
        """A grep-level proof: no files.copy anywhere names the final master."""
        offenders = []
        for path in list((ROOT / "src").rglob("*.py")) + list((ROOT / "scripts").rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"\.copy\(", text):
                window = text[match.start() : match.start() + 400]
                if "MASTER_TEMPLATE_NAME" in window or MASTER_TEMPLATE_NAME in window:
                    offenders.append(str(path))
        self.assertEqual(offenders, [])

    def test_the_master_name_only_ever_appears_in_a_rename(self):
        source = (ROOT / "src" / "gm_gsa" / "master_template.py").read_text(encoding="utf-8")
        copy_body = source.split("def copy_canonical_to_temp", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("TEMP_SCRUB_NAME", copy_body)
        self.assertNotIn("MASTER_TEMPLATE_NAME", copy_body)

    def test_a_completed_run_leaves_exactly_one_document_correctly_named(self):
        drive = self.drive(scaffold())
        self.run_apply(drive, self.docs())
        documents = [f for f in drive.files().store if f["mimeType"] == DOCUMENT_MIME_TYPE]
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]["name"], MASTER_TEMPLATE_NAME)
        # And it was born under the TEMP name, not the final one.
        self.assertEqual(drive.files().copied[0]["name"], TEMP_SCRUB_NAME)


# ---------------------------------------------------------------------------
# 2. The canonical document can never be a write target
# ---------------------------------------------------------------------------


class CanonicalIsReadOnlyTests(PipelineTestCase):
    def test_the_canonical_document_is_never_updated_copied_over_or_renamed(self):
        drive = self.drive(scaffold())
        docs = self.docs()
        self.run_apply(drive, docs)
        for call in drive.files().updates:
            self.assertNotEqual(call["fileId"], CANONICAL_TEMPLATE_ID)
        for call in docs.documents().batch_calls:
            self.assertNotEqual(call["documentId"], CANONICAL_TEMPLATE_ID)
        self.assertNotIn(CANONICAL_TEMPLATE_ID, [f["id"] for f in drive.files().created])

    def test_the_canonical_document_is_only_ever_a_copy_source(self):
        drive = self.drive(scaffold())
        self.run_apply(drive, self.docs())
        self.assertEqual(drive.files().copied[0]["copied_from"], CANONICAL_TEMPLATE_ID)

    def test_a_templates_folder_equal_to_the_canonical_id_is_refused(self):
        """Defense in depth: the copy destination is checked against the protected set."""
        drive = self.drive(scaffold())
        with self.assertRaises(CanonicalTemplateWriteError):
            copy_canonical_to_temp(drive, CANONICAL_TEMPLATE_ID, CANONICAL_TEMPLATE_ID)
        self.assertEqual(drive.files().copied, [])

    def test_the_canonical_content_is_fetched_read_only(self):
        drive = self.drive(scaffold())
        docs = self.docs()
        self.run_apply(drive, docs)
        self.assertIn(CANONICAL_TEMPLATE_ID, docs.documents().get_calls)
        self.assertTrue(
            all(c["documentId"] != CANONICAL_TEMPLATE_ID for c in docs.documents().batch_calls)
        )


# ---------------------------------------------------------------------------
# 3. TEMP is used before scrubbing, rename comes last
# ---------------------------------------------------------------------------


class OrderOfOperationsTests(PipelineTestCase):
    def test_the_document_carries_the_temp_name_while_it_is_scrubbed(self):
        drive = self.drive(scaffold())
        docs = self.docs()
        observed = []

        original = docs.documents().batchUpdate

        def spy(**kwargs):
            match = next(
                f for f in drive.files().store if f["id"] == kwargs["documentId"]
            )
            observed.append(match["name"])
            return original(**kwargs)

        docs.documents().batchUpdate = spy
        self.run_apply(drive, docs)
        self.assertTrue(observed)
        self.assertEqual(set(observed), {TEMP_SCRUB_NAME})

    def test_the_rename_is_the_last_write_and_follows_both_validations(self):
        drive = self.drive(scaffold())
        docs = self.docs()
        report = self.run_apply(drive, docs)
        outcomes = [step["key"] for step in report["steps"]]
        self.assertLess(outcomes.index("validate_content"), outcomes.index("rename"))
        self.assertLess(outcomes.index("validate_structure"), outcomes.index("rename"))
        self.assertLess(outcomes.index("reread"), outcomes.index("validate_content"))
        self.assertEqual(len(drive.files().updates), 1)
        self.assertEqual(drive.files().updates[0]["body"]["name"], MASTER_TEMPLATE_NAME)

    def test_the_copy_is_re_read_from_the_api_before_it_is_judged(self):
        drive = self.drive(scaffold())
        docs = self.docs()
        self.run_apply(drive, docs)
        temp_id = drive.files().copied[0]["id"]
        # Once to build the scrub plan, once to re-read the scrubbed result.
        self.assertGreaterEqual(docs.documents().get_calls.count(temp_id), 2)

    def test_the_scrub_actually_removes_the_source_client_facts(self):
        drive = self.drive(scaffold())
        docs = self.docs()
        self.run_apply(drive, docs)
        temp_id = drive.files().copied[0]["id"]
        residue = validate_scrubbed(
            docs.documents().documents[temp_id], self.manifest.forbidden_after_scrub
        )
        self.assertEqual(residue, [])


# ---------------------------------------------------------------------------
# 4. Validation failure means zero renames
# ---------------------------------------------------------------------------


class ValidationFailureTests(PipelineTestCase):
    def test_surviving_client_facts_prevent_the_rename(self):
        drive = self.drive(scaffold())
        docs = self.docs(mode="residue")
        with self.assertRaises(PartialWriteError) as ctx:
            self.run_apply(drive, docs)
        self.assertEqual(drive.files().updates, [], "no rename may occur when content fails")
        self.assertEqual(drive.files().copied[0]["name"], TEMP_SCRUB_NAME)
        self.assertIn("survived the scrub", str(ctx.exception))

    def test_a_damaged_structure_prevents_the_rename(self):
        drive = self.drive(scaffold())
        docs = self.docs(mode="structure_damage")
        with self.assertRaises(PartialWriteError):
            self.run_apply(drive, docs)
        self.assertEqual(drive.files().updates, [])
        self.assertEqual(drive.files().copied[0]["name"], TEMP_SCRUB_NAME)

    def test_a_failed_validation_records_no_ids(self):
        drive = self.drive(scaffold())
        with self.assertRaises(PartialWriteError):
            self.run_apply(drive, self.docs(mode="residue"))
        self.assertIn("landing_page_root_folder_id: null", self.recorded())
        self.assertIn("master_template_document_id: null", self.recorded())

    def test_a_failed_validation_leaves_the_temp_document_in_place(self):
        drive = self.drive(scaffold())
        with self.assertRaises(PartialWriteError):
            self.run_apply(drive, self.docs(mode="residue"))
        survivors = [f["name"] for f in drive.files().store if f["mimeType"] == DOCUMENT_MIME_TYPE]
        self.assertEqual(survivors, [TEMP_SCRUB_NAME])


# ---------------------------------------------------------------------------
# 5. Idempotency: reuse, block, never duplicate
# ---------------------------------------------------------------------------


class IdempotencyTests(PipelineTestCase):
    def test_an_existing_validated_master_is_reused(self):
        store = scaffold() + [document("1masterDocIdCCCCCCCCCCCCCCCCC", MASTER_TEMPLATE_NAME, "1templatesFolderIdBBBBBBBBBBB")]
        drive = self.drive(store)
        plan = plan_master_template(drive, make_settings())
        self.assertEqual(plan.status, STATUS_REUSE_MASTER)
        self.assertEqual(plan.final_master_id, "1masterDocIdCCCCCCCCCCCCCCCCC")
        self.assertEqual(expected_new_resources(plan, make_settings()), [])

        self.run_apply(drive, self.docs(), plan=plan)
        self.assertEqual(drive.files().copied, [])
        self.assertEqual(drive.files().created, [])
        self.assertEqual(drive.files().updates, [])

    def test_reusing_an_existing_master_still_records_its_ids(self):
        store = scaffold() + [document("1masterDocIdCCCCCCCCCCCCCCCCC", MASTER_TEMPLATE_NAME, "1templatesFolderIdBBBBBBBBBBB")]
        report = self.run_apply(self.drive(store), self.docs())
        self.assertEqual(report["master_template_document_id"], "1masterDocIdCCCCCCCCCCCCCCCCC")
        self.assertIn('master_template_document_id: "1masterDocIdCCCCCCCCCCCCCCCCC"', self.recorded())

    def test_an_existing_temp_copy_blocks_the_whole_operation(self):
        store = scaffold() + [document("1tempDocIdDDDDDDDDDDDDDDDDDDD", TEMP_SCRUB_NAME, "1templatesFolderIdBBBBBBBBBBB")]
        drive = self.drive(store)
        plan = plan_master_template(drive, make_settings())
        self.assertEqual(plan.status, STATUS_BLOCKED_TEMP_EXISTS)
        self.assertTrue(plan.blocked)
        self.assertEqual(plan.temp_id, "1tempDocIdDDDDDDDDDDDDDDDDDDD")
        self.assertEqual(expected_new_resources(plan, make_settings()), [])

        with self.assertRaises(MasterTemplateBlockedError) as ctx:
            self.run_apply(drive, self.docs(), plan=plan)
        self.assertIn("1tempDocIdDDDDDDDDDDDDDDDDDDD", str(ctx.exception))
        self.assertEqual(drive.files().copied, [])
        self.assertEqual(drive.files().created, [])
        self.assertEqual(drive.files().updates, [])
        self.assertIn("landing_page_root_folder_id: null", self.recorded())

    def test_the_blocked_plan_reports_a_safe_url_for_review(self):
        store = scaffold() + [document("1tempDocIdDDDDDDDDDDDDDDDDDDD", TEMP_SCRUB_NAME, "1templatesFolderIdBBBBBBBBBBB")]
        plan = plan_master_template(self.drive(store), make_settings())
        step = next(s for s in plan.steps if s.key == "master_template")
        self.assertEqual(step.action, "stop")
        self.assertEqual(step.existing_url, "https://docs.google.com/document/d/1tempDocIdDDDDDDDDDDDDDDDDDDD/edit")

    def test_a_temp_appearing_after_planning_still_stops_the_copy(self):
        """A stale plan must never license a blind second TEMP copy."""
        drive = self.drive(scaffold())
        plan = plan_master_template(drive, make_settings())
        self.assertEqual(plan.status, STATUS_CREATE_MASTER)
        drive.files().store.append(
            document("1tempDocIdDDDDDDDDDDDDDDDDDDD", TEMP_SCRUB_NAME,
                     "1templatesFolderIdBBBBBBBBBBB")
        )
        with self.assertRaises(MasterTemplateBlockedError) as ctx:
            self.run_apply(drive, self.docs(), plan=plan)
        self.assertIn("appeared in Templates", str(ctx.exception))
        self.assertEqual(drive.files().copied, [])
        self.assertIn("landing_page_root_folder_id: null", self.recorded())

    def test_a_master_appearing_after_planning_still_stops_the_copy(self):
        drive = self.drive(scaffold())
        plan = plan_master_template(drive, make_settings())
        drive.files().store.append(
            document("1otherMasterIdEEEEEEEEEEEEEEE", MASTER_TEMPLATE_NAME,
                     "1templatesFolderIdBBBBBBBBBBB")
        )
        with self.assertRaises(MasterTemplateBlockedError):
            self.run_apply(drive, self.docs(), plan=plan)
        self.assertEqual(drive.files().copied, [])

    def test_a_late_temp_reports_folders_this_run_created(self):
        """Stopping for review must never hide resources the same run brought into being."""
        drive = self.drive([])
        plan = plan_master_template(drive, make_settings())
        files = drive.files()
        original_create = files.create

        def create_and_race(**kwargs):
            result = original_create(**kwargs)
            if kwargs["body"]["name"] == "Templates":
                folder_id = result.execute()["id"]
                files.store.append(
                    document("1tempDocIdDDDDDDDDDDDDDDDDDDD", TEMP_SCRUB_NAME, folder_id)
                )
            return result

        files.create = create_and_race
        with self.assertRaises(PartialWriteError) as ctx:
            self.run_apply(drive, self.docs(), plan=plan)
        inventory = ctx.exception.inventory()
        self.assertEqual(
            [item["name"] for item in inventory],
            ["Green Marketing Landing Pages", "Templates"],
        )
        self.assertEqual(ctx.exception.failed_key, "copy_temp")
        self.assertEqual(files.copied, [])

    def test_applying_twice_creates_nothing_the_second_time(self):
        drive = self.drive([])
        docs = self.docs()
        self.run_apply(drive, docs)
        self.assertEqual(len(drive.files().created), 2)
        self.assertEqual(len(drive.files().copied), 1)

        second_plan = plan_master_template(drive, make_settings())
        self.assertEqual(second_plan.status, STATUS_REUSE_MASTER)
        self.run_apply(drive, docs, plan=second_plan)
        self.assertEqual(len(drive.files().created), 2)
        self.assertEqual(len(drive.files().copied), 1)

    def test_a_leftover_temp_beside_a_valid_master_is_reported_not_touched(self):
        store = scaffold() + [
            document("1masterDocIdCCCCCCCCCCCCCCCCC", MASTER_TEMPLATE_NAME, "1templatesFolderIdBBBBBBBBBBB"),
            document("1tempDocIdDDDDDDDDDDDDDDDDDDD", TEMP_SCRUB_NAME, "1templatesFolderIdBBBBBBBBBBB"),
        ]
        drive = self.drive(store)
        plan = plan_master_template(drive, make_settings())
        self.assertEqual(plan.status, STATUS_REUSE_MASTER)
        self.assertEqual(plan.temp_id, "1tempDocIdDDDDDDDDDDDDDDDDDDD")
        self.assertTrue(any("leftover" in note for note in plan.notes))
        self.run_apply(drive, self.docs(), plan=plan)
        self.assertEqual(drive.files().updates, [])


# ---------------------------------------------------------------------------
# 6. Duplicates stop the operation
# ---------------------------------------------------------------------------


class DuplicateDetectionTests(PipelineTestCase):
    def test_duplicate_root_folders_stop_planning(self):
        drive = self.drive(
            [
                folder("1dupRootOneHHHHHHHHHHHHHHHHHH", "Green Marketing Landing Pages", MY_DRIVE_ROOT),
                folder("1dupRootTwoIIIIIIIIIIIIIIIIII", "Green Marketing Landing Pages", MY_DRIVE_ROOT),
            ]
        )
        with self.assertRaises(DriveAmbiguityError):
            plan_master_template(drive, make_settings())

    def test_duplicate_templates_folders_stop_planning(self):
        drive = self.drive(
            [
                folder("1dupRootOneHHHHHHHHHHHHHHHHHH", "Green Marketing Landing Pages", MY_DRIVE_ROOT),
                folder("1dupTplOneJJJJJJJJJJJJJJJJJJJ", "Templates", "1dupRootOneHHHHHHHHHHHHHHHHHH"),
                folder("1dupTplTwoKKKKKKKKKKKKKKKKKKK", "Templates", "1dupRootOneHHHHHHHHHHHHHHHHHH"),
            ]
        )
        with self.assertRaises(DriveAmbiguityError):
            plan_master_template(drive, make_settings())

    def test_duplicate_master_documents_stop_planning(self):
        store = scaffold() + [
            document("1dupDocIdOneFFFFFFFFFFFFFFFFF", MASTER_TEMPLATE_NAME, "1templatesFolderIdBBBBBBBBBBB"),
            document("1dupDocIdTwoGGGGGGGGGGGGGGGGG", MASTER_TEMPLATE_NAME, "1templatesFolderIdBBBBBBBBBBB"),
        ]
        with self.assertRaises(DriveAmbiguityError) as ctx:
            plan_master_template(self.drive(store), make_settings())
        self.assertIn("1dupDocIdOneFFFFFFFFFFFFFFFFF", str(ctx.exception))
        self.assertIn("1dupDocIdTwoGGGGGGGGGGGGGGGGG", str(ctx.exception))

    def test_duplicate_temp_documents_stop_planning(self):
        store = scaffold() + [
            document("1dupDocIdOneFFFFFFFFFFFFFFFFF", TEMP_SCRUB_NAME, "1templatesFolderIdBBBBBBBBBBB"),
            document("1dupDocIdTwoGGGGGGGGGGGGGGGGG", TEMP_SCRUB_NAME, "1templatesFolderIdBBBBBBBBBBB"),
        ]
        with self.assertRaises(DriveAmbiguityError):
            plan_master_template(self.drive(store), make_settings())


# ---------------------------------------------------------------------------
# 7. Partial resources are inventoried
# ---------------------------------------------------------------------------


class PartialFailureTests(PipelineTestCase):
    def test_a_failed_folder_creation_inventories_what_exists(self):
        drive = self.drive([], fail_on_create={"Templates"})
        with self.assertRaises(PartialWriteError) as ctx:
            self.run_apply(drive, self.docs())
        inventory = ctx.exception.inventory()
        self.assertEqual([item["name"] for item in inventory], ["Green Marketing Landing Pages"])
        self.assertTrue(inventory[0]["id"])
        self.assertEqual(drive.files().copied, [])

    def test_a_failed_validation_inventories_the_temp_document_with_a_url(self):
        drive = self.drive(scaffold())
        with self.assertRaises(PartialWriteError) as ctx:
            self.run_apply(drive, self.docs(mode="residue"))
        inventory = ctx.exception.inventory()
        temp = next(item for item in inventory if item["key"] == "temp_copy")
        self.assertEqual(temp["name"], TEMP_SCRUB_NAME)
        self.assertEqual(temp["url"], f"https://docs.google.com/document/d/{temp['id']}/edit")

    def test_a_failed_copy_inventories_the_folders_only(self):
        drive = self.drive([], fail_on_copy=True)
        with self.assertRaises(PartialWriteError) as ctx:
            self.run_apply(drive, self.docs())
        inventory = ctx.exception.inventory()
        self.assertEqual(
            [item["name"] for item in inventory],
            ["Green Marketing Landing Pages", "Templates"],
        )

    def test_a_partial_failure_never_deletes_moves_or_shares_anything(self):
        drive = self.drive(scaffold())
        with self.assertRaises(PartialWriteError):
            self.run_apply(drive, self.docs(mode="residue"))
        # FakeFiles.delete/trash and FakeDrive.permissions raise if reached; getting here
        # without an AssertionError is the proof.
        for call in drive.files().updates:
            self.assertNotIn("addParents", call)
            self.assertNotIn("removeParents", call)


# ---------------------------------------------------------------------------
# 8. IDs are recorded only after success
# ---------------------------------------------------------------------------


class IdRecordingTests(PipelineTestCase):
    def test_ids_are_recorded_after_a_successful_run(self):
        drive = self.drive(scaffold())
        report = self.run_apply(drive, self.docs())
        text = self.recorded()
        self.assertIn(f'landing_page_root_folder_id: "{report["root_folder_id"]}"', text)
        self.assertIn(
            f'master_template_document_id: "{report["master_template_document_id"]}"', text
        )

    def test_the_recorded_master_is_the_copy_not_the_canonical_source(self):
        drive = self.drive(scaffold())
        report = self.run_apply(drive, self.docs())
        self.assertNotEqual(report["master_template_document_id"], CANONICAL_TEMPLATE_ID)
        self.assertNotIn(CANONICAL_TEMPLATE_ID, self.recorded())

    def test_nothing_is_recorded_when_the_run_is_blocked(self):
        store = scaffold() + [document("1tempDocIdDDDDDDDDDDDDDDDDDDD", TEMP_SCRUB_NAME, "1templatesFolderIdBBBBBBBBBBB")]
        with self.assertRaises(MasterTemplateBlockedError):
            self.run_apply(self.drive(store), self.docs())
        self.assertNotIn('"', self.recorded())

    def test_a_recording_failure_is_reported_with_the_full_inventory(self):
        drive = self.drive(scaffold())
        self.config_path.write_text("drive:\n  unrelated: true\n", encoding="utf-8")
        with self.assertRaises(PartialWriteError) as ctx:
            self.run_apply(drive, self.docs())
        self.assertEqual(ctx.exception.failed_key, "record_ids")
        self.assertTrue(ctx.exception.inventory())

    def test_a_manifest_pointing_elsewhere_is_refused_before_any_write(self):
        from gm_gsa.template_scrub import ScrubValidationError

        drive = self.drive(scaffold())
        self.manifest.source_document_id = "someOtherDocumentId"
        with self.assertRaises(ScrubValidationError):
            self.run_apply(drive, self.docs())
        self.assertEqual(drive.files().copied, [])


# ---------------------------------------------------------------------------
# 9. Dry run writes nothing at all
# ---------------------------------------------------------------------------


class DryRunTests(PipelineTestCase):
    def test_planning_touches_no_drive_docs_or_local_state(self):
        drive = self.drive(scaffold())
        docs = self.docs()
        before = self.recorded()
        plan = plan_master_template(drive, make_settings())
        self.assertEqual(drive.files().created, [])
        self.assertEqual(drive.files().copied, [])
        self.assertEqual(drive.files().updates, [])
        self.assertEqual(docs.documents().batch_calls, [])
        self.assertEqual(docs.documents().get_calls, [])
        self.assertEqual(self.recorded(), before)
        self.assertTrue(plan.steps)

    def test_planning_on_an_empty_drive_shows_the_whole_sequence(self):
        plan = plan_master_template(self.drive([]), make_settings())
        self.assertEqual(
            [step.key for step in plan.steps],
            [
                "root",
                "templates",
                "copy_temp",
                "scrub",
                "reread",
                "validate_content",
                "validate_structure",
                "rename",
                "record_ids",
            ],
        )
        self.assertEqual(
            [step.action for step in plan.steps],
            [
                "create",
                "create",
                "copy",
                "scrub",
                "validate",
                "validate",
                "validate",
                "rename",
                "record",
            ],
        )

    def test_the_printed_sequence_names_temp_before_the_final_name(self):
        rendered = format_pipeline(plan_master_template(self.drive([]), make_settings()))
        self.assertLess(rendered.index(TEMP_SCRUB_NAME), rendered.index(MASTER_TEMPLATE_NAME))

    def test_expected_resources_list_the_temp_name_not_an_unscrubbed_master(self):
        settings = make_settings()
        expected = expected_new_resources(
            plan_master_template(self.drive([]), settings), settings
        )
        self.assertEqual(
            expected,
            [
                "Folder: Green Marketing Landing Pages (in My Drive)",
                "Folder: Templates (in Green Marketing Landing Pages)",
                f"Google Doc: {TEMP_SCRUB_NAME} (in Templates), renamed to "
                f"{MASTER_TEMPLATE_NAME} after validation",
            ],
        )

    def test_an_existing_scaffold_plans_only_the_document_work(self):
        settings = make_settings()
        plan = plan_master_template(self.drive(scaffold()), settings)
        self.assertEqual([s.action for s in plan.steps[:2]], ["reuse", "reuse"])
        self.assertEqual(
            expected_new_resources(plan, settings),
            [
                f"Google Doc: {TEMP_SCRUB_NAME} (in Templates), renamed to "
                f"{MASTER_TEMPLATE_NAME} after validation"
            ],
        )


# ---------------------------------------------------------------------------
# 10. Structural refusals
# ---------------------------------------------------------------------------


class ForbiddenOperationTests(PipelineTestCase):
    def test_no_clients_folder_appears_anywhere_in_the_sequence(self):
        plan = plan_master_template(self.drive([]), make_settings())
        rendered = format_pipeline(plan).lower()
        self.assertNotIn("clients", rendered)
        self.assertFalse(any("client" in step.key.lower() for step in plan.steps))

    def test_the_pipeline_source_contains_no_destructive_call(self):
        """Scan executable lines only; the module's prose names these to forbid them."""
        source = (ROOT / "src" / "gm_gsa" / "master_template.py").read_text(encoding="utf-8")
        code = source.split('__all__ = [', 1)[0]
        code = code.split('def assert_no_forbidden_operations', 1)[0]
        code = "\n".join(
            line for line in code.splitlines() if not line.lstrip().startswith("#")
        )
        for forbidden in (
            ".delete(",
            ".trash(",
            ".permissions(",
            "addParents=",
            "removeParents=",
            "anyoneWithLink",
            '"anyone"',
            "webContentLink",
            "publishedLink",
        ):
            self.assertNotIn(forbidden, code, f"{forbidden} must not exist in the pipeline")

    def test_the_documented_refusal_list_is_complete(self):
        forbidden = assert_no_forbidden_operations()
        for expected in (
            "files.delete",
            "files.trash",
            "permissions.create",
            "files.copy:to-master-name",
        ):
            self.assertIn(expected, forbidden)

    def test_no_script_can_reach_a_document_copy_outside_the_pipeline(self):
        import ast

        for path in (ROOT / "scripts").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                method = node.func
                if not isinstance(method, ast.Attribute) or method.attr != "copy":
                    continue
                # Google Drive's document copy is drive.files().copy(...), not
                # Pillow's img.copy() or Python's copy.copy(...).
                receiver = method.value
                is_drive_copy = (
                    isinstance(receiver, ast.Call)
                    and isinstance(receiver.func, ast.Attribute)
                    and receiver.func.attr == "files"
                )
                self.assertFalse(
                    is_drive_copy,
                    f"{path.name} must delegate Drive copying to master_template",
                )

    def test_a_folder_named_like_the_master_is_refused(self):
        settings = make_settings(root_folder_name=MASTER_TEMPLATE_NAME)
        drive = self.drive([])
        plan = plan_master_template(drive, settings)
        with self.assertRaises(UnscrubbedMasterError):
            self.run_apply(drive, self.docs(), settings=settings, plan=plan)
        self.assertEqual(drive.files().created, [])


class ConfigurationGuardTests(PipelineTestCase):
    def test_recording_rejects_a_non_id_value(self):
        from gm_gsa.google_drive import record_verified_ids

        with self.assertRaises(ConfigurationError):
            record_verified_ids("ok-root-id-1", "not an id", config_path=self.config_path)

    def test_the_repository_config_agrees_with_the_protected_final_name(self):
        from gm_gsa.google_drive import load_drive_settings

        settings = load_drive_settings()
        self.assertEqual(settings.master_template_name, MASTER_TEMPLATE_NAME)
        self.assertFalse(settings.create_clients_folder)

    def test_a_config_naming_a_different_master_is_refused(self):
        """Config drift must not describe a document the name guard does not protect."""
        from gm_gsa.google_drive import load_drive_settings

        self.config_path.write_text(
            "drive:\n"
            '  landing_page_root_folder_name: "Green Marketing Landing Pages"\n'
            '  templates_folder_name: "Templates"\n'
            '  master_template_name: "Landing Page Content Template - MASTER"\n'
            "oauth:\n"
            '  scopes: ["https://www.googleapis.com/auth/drive.file"]\n',
            encoding="utf-8",
        )
        with self.assertRaises(ConfigurationError):
            load_drive_settings(self.config_path)


if __name__ == "__main__":
    unittest.main()
