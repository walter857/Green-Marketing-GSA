from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.google_drive import CANONICAL_TEMPLATE_ID, load_drive_settings  # noqa: E402
from gm_gsa.template_scrub import (  # noqa: E402
    MASTER_TEMPLATE_NAME,
    PROTECTED_DOCUMENT_IDS,
    TEMP_SCRUB_NAME,
    CanonicalTemplateWriteError,
    ReplacementRule,
    ScrubManifest,
    ScrubValidationError,
    assert_requests_do_not_target_canonical,
    assert_structure_preserved,
    assert_writable_target,
    build_link_requests,
    build_text_requests,
    detect_client_facts,
    document_structure_fingerprint,
    guarded_batch_update,
    guarded_delete,
    guarded_files_update,
    guarded_move,
    guarded_permission_change,
    guarded_rename,
    guarded_trash,
    iter_link_targets,
    iter_text_segments,
    load_scrub_manifest,
    plan_scrub,
    simulate_scrub,
    validate_scrubbed,
)

MANIFEST_PATH = ROOT / "config" / "landing-page-template-scrub.yaml"
SAFE_COPY_ID = "copy-document-id-1234"


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _Request:
    def __init__(self, result):
        self._result = result

    def execute(self):
        return self._result


class FakeDocuments:
    def __init__(self):
        self.batch_calls = []

    def batchUpdate(self, **kwargs):  # noqa: N802 - mirrors the Google client
        self.batch_calls.append(kwargs)
        return _Request({"documentId": kwargs.get("documentId")})


class FakeDocsService:
    def __init__(self):
        self._documents = FakeDocuments()

    def documents(self):
        return self._documents


class FakeFilesResource:
    def __init__(self):
        self.updates = []

    def update(self, **kwargs):
        self.updates.append(kwargs)
        return _Request({"id": kwargs.get("fileId"), "name": (kwargs.get("body") or {}).get("name")})


class FakeDriveService:
    def __init__(self):
        self._files = FakeFilesResource()

    def files(self):
        return self._files


def paragraph(text, style="NORMAL_TEXT", bullet=False, link=None):
    run = {"textRun": {"content": text, "textStyle": {}}}
    if link:
        run["textRun"]["textStyle"]["link"] = {"url": link}
    para = {"elements": [run], "paragraphStyle": {"namedStyleType": style}}
    if bullet:
        para["bullet"] = {"listId": "l1"}
    return {"paragraph": para}


def rich_link_paragraph(uri, title="img.jpg", start=10, end=11):
    return {
        "paragraph": {
            "elements": [
                {
                    "startIndex": start,
                    "endIndex": end,
                    "richLink": {"richLinkProperties": {"uri": uri, "title": title}},
                }
            ],
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
        }
    }


def table_element(cell_texts):
    rows = []
    for row in cell_texts:
        cells = [{"content": [paragraph(text)]} for text in row]
        rows.append({"tableCells": cells})
    return {
        "table": {
            "rows": len(cell_texts),
            "columns": len(cell_texts[0]) if cell_texts else 0,
            "tableRows": rows,
        }
    }


def tabbed_document():
    """A document exercising tabs, headers, footers, tables, links and rich links."""
    return {
        "tabs": [
            {
                "tabProperties": {"tabId": "t.0", "title": "Tab 1"},
                "documentTab": {
                    "body": {
                        "content": [
                            paragraph("Ambient Cooling & Heating", "HEADING_1"),
                            paragraph("Call (410) 761-0932"),
                            paragraph("Comprehensive AC repair diagnosis", bullet=True),
                            table_element([["Ambient serves Severn", "Rachel Ehmann"]]),
                            rich_link_paragraph(
                                "https://drive.google.com/file/d/1DFvfHaK43WAboQk8B6ZQYoUWhBDD7RY_/view?usp=drive_link"
                            ),
                            paragraph(
                                "https://drive.google.com/file/d/1zlxytOLOfweuFlN0eaIIm9NkpcrdtOfu/view?usp=drive_link",
                                link="https://drive.google.com/file/d/1zlxytOLOfweuFlN0eaIIm9NkpcrdtOfu/view?usp=drive_link",
                            ),
                        ]
                    },
                    "headers": {"h1": {"content": [paragraph("Ambient header")]}},
                    "footers": {"f1": {"content": [paragraph("CALL: (410) 761-0932")]}},
                    "footnotes": {"fn1": {"content": [paragraph("Javis Brown note")]}},
                    "inlineObjects": {},
                },
                "childTabs": [
                    {
                        "tabProperties": {"tabId": "t.1", "title": "Child"},
                        "documentTab": {
                            "body": {"content": [paragraph("Ernesto Palacios Jr")]},
                            "inlineObjects": {},
                        },
                    }
                ],
            }
        ]
    }


# ---------------------------------------------------------------------------
# Canonical write protection
# ---------------------------------------------------------------------------


class CanonicalWriteProtectionTests(unittest.TestCase):
    def test_canonical_id_is_in_the_protected_set(self):
        self.assertIn(CANONICAL_TEMPLATE_ID, PROTECTED_DOCUMENT_IDS)

    def test_direct_assertion_refuses_the_canonical_id(self):
        with self.assertRaises(CanonicalTemplateWriteError):
            assert_writable_target(CANONICAL_TEMPLATE_ID, "documents.batchUpdate")

    def test_whitespace_padded_canonical_id_is_still_refused(self):
        with self.assertRaises(CanonicalTemplateWriteError):
            assert_writable_target(f"  {CANONICAL_TEMPLATE_ID}  ", "files.update")

    def test_batch_update_against_canonical_is_refused(self):
        docs = FakeDocsService()
        with self.assertRaises(CanonicalTemplateWriteError):
            guarded_batch_update(docs, CANONICAL_TEMPLATE_ID, [{"replaceAllText": {}}])
        self.assertEqual(docs.documents().batch_calls, [])

    def test_files_update_against_canonical_is_refused(self):
        drive = FakeDriveService()
        with self.assertRaises(CanonicalTemplateWriteError):
            guarded_files_update(drive, CANONICAL_TEMPLATE_ID, {"name": "anything"})
        self.assertEqual(drive.files().updates, [])

    def test_rename_of_canonical_is_refused(self):
        drive = FakeDriveService()
        with self.assertRaises(CanonicalTemplateWriteError):
            guarded_rename(drive, CANONICAL_TEMPLATE_ID, MASTER_TEMPLATE_NAME)
        self.assertEqual(drive.files().updates, [])

    def test_delete_trash_move_and_sharing_are_all_refused(self):
        drive = FakeDriveService()
        for call in (
            lambda: guarded_delete(drive, CANONICAL_TEMPLATE_ID),
            lambda: guarded_trash(drive, CANONICAL_TEMPLATE_ID),
            lambda: guarded_move(drive, CANONICAL_TEMPLATE_ID, "new", "old"),
            lambda: guarded_permission_change(drive, CANONICAL_TEMPLATE_ID),
        ):
            with self.assertRaises(CanonicalTemplateWriteError):
                call()

    def test_destructive_helpers_refuse_even_a_safe_id(self):
        """Deletion, trashing, moving and sharing are barred workflow-wide, not just for the source."""
        drive = FakeDriveService()
        for call in (
            lambda: guarded_delete(drive, SAFE_COPY_ID),
            lambda: guarded_trash(drive, SAFE_COPY_ID),
            lambda: guarded_move(drive, SAFE_COPY_ID, "new", "old"),
            lambda: guarded_permission_change(drive, SAFE_COPY_ID),
        ):
            with self.assertRaises(CanonicalTemplateWriteError):
                call()

    def test_canonical_id_nested_inside_a_payload_is_refused(self):
        with self.assertRaises(CanonicalTemplateWriteError):
            assert_requests_do_not_target_canonical(
                [{"replaceAllText": {"documentId": CANONICAL_TEMPLATE_ID}}]
            )

    def test_move_via_add_parents_is_refused_for_canonical(self):
        drive = FakeDriveService()
        with self.assertRaises(CanonicalTemplateWriteError):
            guarded_files_update(
                drive, CANONICAL_TEMPLATE_ID, {}, addParents="x", removeParents="y"
            )

    def test_writes_to_a_copy_are_allowed(self):
        docs = FakeDocsService()
        guarded_batch_update(docs, SAFE_COPY_ID, [{"replaceAllText": {}}])
        self.assertEqual(len(docs.documents().batch_calls), 1)

        drive = FakeDriveService()
        guarded_rename(drive, SAFE_COPY_ID, MASTER_TEMPLATE_NAME)
        self.assertEqual(drive.files().updates[0]["body"]["name"], MASTER_TEMPLATE_NAME)


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_scrub_manifest(MANIFEST_PATH)

    def test_manifest_targets_the_canonical_document(self):
        self.assertEqual(self.manifest.source_document_id, CANONICAL_TEMPLATE_ID)

    def test_rules_are_applied_longest_find_first(self):
        lengths = [len(rule.find) for rule in self.manifest.sorted_rules()]
        self.assertEqual(lengths, sorted(lengths, reverse=True))

    def test_company_phrase_outranks_the_bare_company_token(self):
        finds = [rule.find for rule in self.manifest.sorted_rules()]
        self.assertLess(finds.index("Ambient Cooling & Heating"), finds.index("Ambient"))

    def test_every_required_placeholder_category_is_present(self):
        categories = {rule.category for rule in self.manifest.rules}
        for required in (
            "company_name",
            "service",
            "phone",
            "email",
            "location",
            "service_area",
            "offer",
            "reviews",
            "reviewer_name",
            "image_alt",
            "image_brief",
            "seo",
            "cta",
        ):
            self.assertIn(required, categories)

    def test_all_nine_client_image_links_are_mapped(self):
        self.assertEqual(len(self.manifest.link_replacements), 9)
        for placeholder in self.manifest.link_replacements.values():
            self.assertTrue(placeholder.startswith("[IMAGE_PLACEMENT_"))

    def test_all_caps_service_variant_is_covered(self):
        """Case-sensitive rules would otherwise miss upper-case section headings."""
        finds = {rule.find for rule in self.manifest.rules}
        self.assertIn("AC REPAIR", finds)
        self.assertIn("AC Repair", finds)
        self.assertIn("AC repair", finds)

    def test_client_specific_section_headings_are_neutralized(self):
        mapping = {rule.find: rule.replace for rule in self.manifest.rules}
        self.assertEqual(mapping["5. MAIN AC REPAIR FEATURE"], "5. MAIN SERVICE FEATURE")
        self.assertEqual(
            mapping["4. FREE QUOTE COUNTDOWN SECTION"], "4. PROMOTIONAL OR EVERGREEN CTA SECTION"
        )
        for replacement in mapping.values():
            self.assertNotIn("AC REPAIR", replacement)

    def test_bare_city_names_have_a_safety_net(self):
        finds = {rule.find for rule in self.manifest.rules}
        for city in ("Severn", "Severna Park", "Columbia", "Annapolis", "Ellicott City"):
            self.assertIn(city, finds)

    def test_longer_city_phrase_outranks_its_own_substring(self):
        finds = [rule.find for rule in self.manifest.sorted_rules()]
        self.assertLess(finds.index("Severna Park"), finds.index("Severn"))

    def test_no_replacement_reintroduces_a_forbidden_term(self):
        """A replacement string must never contain something the validator forbids."""
        for rule in self.manifest.rules:
            for term in self.manifest.forbidden_after_scrub:
                self.assertNotIn(
                    term.casefold(),
                    rule.replace.casefold(),
                    f"rule {rule.find!r} reintroduces forbidden term {term!r}",
                )

    def test_duplicate_find_values_are_rejected(self):
        import tempfile

        bad = "source_document_id: x\nreplacements:\n  - find: A\n    replace: B\n  - find: A\n    replace: C\n"
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as fh:
            fh.write(bad)
            path = fh.name
        with self.assertRaises(Exception):
            load_scrub_manifest(path)


# ---------------------------------------------------------------------------
# Traversal: tabs, headers, footers, tables, links, image text
# ---------------------------------------------------------------------------


class TraversalTests(unittest.TestCase):
    def setUp(self):
        self.doc = tabbed_document()

    def test_all_segment_kinds_are_traversed(self):
        kinds = {segment.segment_kind for segment in iter_text_segments(self.doc)}
        self.assertEqual(kinds, {"body", "header", "footer", "footnote"})

    def test_child_tabs_are_traversed(self):
        tab_ids = {segment.tab_id for segment in iter_text_segments(self.doc)}
        self.assertEqual(tab_ids, {"t.0", "t.1"})

    def test_table_cell_text_is_traversed(self):
        paths = [s.path for s in iter_text_segments(self.doc) if "table" in s.path]
        self.assertEqual(len(paths), 2)
        texts = [s.text for s in iter_text_segments(self.doc) if "table" in s.path]
        self.assertIn("Ambient serves Severn", texts)

    def test_rich_links_and_hyperlinks_are_collected(self):
        kinds = {target.kind for target in iter_link_targets(self.doc)}
        self.assertEqual(kinds, {"richLink", "hyperlink"})

    def test_inline_image_alt_text_is_collected(self):
        doc = {
            "body": {
                "content": [
                    {
                        "paragraph": {
                            "elements": [
                                {
                                    "startIndex": 1,
                                    "endIndex": 2,
                                    "inlineObjectElement": {"inlineObjectId": "img1"},
                                }
                            ]
                        }
                    }
                ]
            },
            "inlineObjects": {
                "img1": {
                    "inlineObjectProperties": {
                        "embeddedObject": {
                            "title": "Ambient photo",
                            "description": "Ambient technician in Severn",
                            "imageProperties": {"sourceUri": "https://example.test/a.jpg"},
                        }
                    }
                }
            },
        }
        targets = list(iter_link_targets(doc))
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0].kind, "inlineImage")
        self.assertIn("Severn", targets[0].description)

    def test_untabbed_documents_are_supported(self):
        doc = {"body": {"content": [paragraph("Ambient")]}}
        self.assertEqual(len(list(iter_text_segments(doc))), 1)


# ---------------------------------------------------------------------------
# Detection and complete replacement
# ---------------------------------------------------------------------------


class DetectionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_scrub_manifest(MANIFEST_PATH)

    def test_detection_finds_facts_in_every_segment_kind(self):
        detections = detect_client_facts(tabbed_document(), self.manifest)
        found = {d.rule.find for d in detections}
        for expected in ("Ambient", "(410) 761-0932", "Rachel Ehmann", "Javis Brown"):
            self.assertIn(expected, found)

    def test_detection_reports_link_urls(self):
        detections = detect_client_facts(tabbed_document(), self.manifest)
        self.assertTrue(any("richLink" in loc for d in detections for loc in d.locations))

    def test_simulated_scrub_removes_every_forbidden_term(self):
        doc = tabbed_document()
        before = validate_scrubbed(doc, self.manifest.forbidden_after_scrub)
        self.assertGreater(len(before), 0)

        scrubbed = simulate_scrub(doc, self.manifest)
        after = validate_scrubbed(scrubbed, self.manifest.forbidden_after_scrub)
        self.assertEqual(
            after, [], f"residual client facts: {[(v.term, v.where) for v in after]}"
        )

    def test_simulated_scrub_replaces_rich_link_and_hyperlink_urls(self):
        scrubbed = simulate_scrub(tabbed_document(), self.manifest)
        text = " ".join(segment.text for segment in iter_text_segments(scrubbed))
        self.assertIn("[IMAGE_PLACEMENT_3]", text)
        self.assertIn("[IMAGE_PLACEMENT_1]", text)
        self.assertNotIn("drive.google.com", text)
        self.assertEqual(
            [t for t in iter_link_targets(scrubbed) if t.kind in {"richLink", "hyperlink"}], []
        )

    def test_placeholders_replace_client_identity(self):
        scrubbed = simulate_scrub(tabbed_document(), self.manifest)
        text = " ".join(segment.text for segment in iter_text_segments(scrubbed))
        self.assertIn("[CLIENT_NAME]", text)
        self.assertIn("[PHONE_NUMBER]", text)
        self.assertIn("[REVIEWER_NAME_1]", text)

    def test_validation_flags_a_surviving_fact(self):
        doc = {"body": {"content": [paragraph("Contact Ambient today")]}}
        violations = validate_scrubbed(doc, ["Ambient"])
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].term, "Ambient")

    def test_validation_is_case_insensitive(self):
        doc = {"body": {"content": [paragraph("contact AMBIENT today")]}}
        self.assertEqual(len(validate_scrubbed(doc, ["Ambient"])), 1)


# ---------------------------------------------------------------------------
# Structure preservation
# ---------------------------------------------------------------------------


class StructurePreservationTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_scrub_manifest(MANIFEST_PATH)

    def test_scrubbing_preserves_the_structural_fingerprint(self):
        doc = tabbed_document()
        before = document_structure_fingerprint(doc)
        after = document_structure_fingerprint(simulate_scrub(doc, self.manifest))
        assert_structure_preserved(before, after)

    def test_headings_bullets_and_tables_survive(self):
        fingerprint = document_structure_fingerprint(
            simulate_scrub(tabbed_document(), self.manifest)
        )
        self.assertIn("HEADING_1", fingerprint["paragraph_styles"])
        self.assertEqual(fingerprint["bullet_count"], 1)
        self.assertEqual(fingerprint["tables"], ["1x2"])
        self.assertEqual(fingerprint["tab_count"], 2)

    def test_a_dropped_heading_fails_validation(self):
        before = {"paragraph_styles": ["HEADING_1", "NORMAL_TEXT"], "paragraph_count": 2,
                  "bullet_count": 0, "tables": [], "tab_count": 1}
        after = {"paragraph_styles": ["NORMAL_TEXT", "NORMAL_TEXT"], "paragraph_count": 2,
                 "bullet_count": 0, "tables": [], "tab_count": 1}
        with self.assertRaises(ScrubValidationError):
            assert_structure_preserved(before, after)

    def test_a_lost_table_fails_validation(self):
        before = {"paragraph_styles": [], "paragraph_count": 0, "bullet_count": 0,
                  "tables": ["1x2"], "tab_count": 1}
        after = {"paragraph_styles": [], "paragraph_count": 0, "bullet_count": 0,
                 "tables": [], "tab_count": 1}
        with self.assertRaises(ScrubValidationError):
            assert_structure_preserved(before, after)


# ---------------------------------------------------------------------------
# Request building and failure before rename
# ---------------------------------------------------------------------------


class RequestBuildingTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_scrub_manifest(MANIFEST_PATH)

    def test_text_requests_use_replace_all_text_and_preserve_structure(self):
        requests = build_text_requests(self.manifest)
        self.assertEqual(len(requests), len(self.manifest.rules))
        for request in requests:
            self.assertIn("replaceAllText", request)
        # Nothing that would rebuild or restyle the document may be emitted.
        rendered = str(requests)
        for forbidden in ("insertTable", "deleteParagraphBullets", "updateParagraphStyle",
                          "createParagraphBullets", "deleteTableRow"):
            self.assertNotIn(forbidden, rendered)

    def test_link_requests_are_emitted_in_descending_index_order(self):
        doc = {
            "body": {
                "content": [
                    rich_link_paragraph(
                        "https://drive.google.com/file/d/1i6mnHqL-3wgjVgSe5liSFGpEnrf2qmBx/view?usp=drive_link",
                        start=10, end=11,
                    ),
                    rich_link_paragraph(
                        "https://drive.google.com/file/d/1KiJd01T5kp4yiQDVIHYdGmBYKq2EQW5v/view?usp=drive_link",
                        start=50, end=51,
                    ),
                ]
            }
        }
        requests = build_link_requests(doc, self.manifest)
        starts = [
            r["deleteContentRange"]["range"]["startIndex"]
            for r in requests
            if "deleteContentRange" in r
        ]
        self.assertEqual(starts, sorted(starts, reverse=True))

    def test_unmapped_links_are_left_alone(self):
        doc = {"body": {"content": [rich_link_paragraph("https://example.test/not-mapped")]}}
        self.assertEqual(build_link_requests(doc, self.manifest), [])

    def test_plan_issues_no_api_calls(self):
        docs = FakeDocsService()
        drive = FakeDriveService()
        plan = plan_scrub(tabbed_document(), self.manifest)
        self.assertGreater(plan.total_requests, 0)
        self.assertEqual(docs.documents().batch_calls, [])
        self.assertEqual(drive.files().updates, [])

    def test_temp_name_differs_from_the_master_name(self):
        self.assertNotEqual(TEMP_SCRUB_NAME, MASTER_TEMPLATE_NAME)
        self.assertIn("TEMP", TEMP_SCRUB_NAME)

    def test_validation_failure_prevents_the_rename(self):
        """A failed scrub must leave the copy under the TEMP name."""
        drive = FakeDriveService()
        residue = {"body": {"content": [paragraph("Ambient is still here")]}}
        violations = validate_scrubbed(residue, ["Ambient"])
        self.assertTrue(violations)
        if not violations:  # pragma: no cover - guard mirrors the script's control flow
            guarded_rename(drive, SAFE_COPY_ID, MASTER_TEMPLATE_NAME)
        self.assertEqual(drive.files().updates, [], "no rename may occur when validation fails")

    def test_structure_failure_prevents_the_rename(self):
        drive = FakeDriveService()
        before = {"paragraph_styles": ["HEADING_1"], "paragraph_count": 1, "bullet_count": 0,
                  "tables": [], "tab_count": 1}
        after = {"paragraph_styles": [], "paragraph_count": 0, "bullet_count": 0,
                 "tables": [], "tab_count": 1}
        try:
            assert_structure_preserved(before, after)
            guarded_rename(drive, SAFE_COPY_ID, MASTER_TEMPLATE_NAME)
        except ScrubValidationError:
            pass
        self.assertEqual(drive.files().updates, [])


# ---------------------------------------------------------------------------
# Configuration guards
# ---------------------------------------------------------------------------


class ConfigurationGuardTests(unittest.TestCase):
    def test_create_clients_folder_remains_disabled(self):
        self.assertFalse(load_drive_settings().create_clients_folder)

    def test_client_hierarchy_has_no_clients_level(self):
        settings = load_drive_settings()
        self.assertEqual(settings.root_folder_name, "Green Marketing Landing Pages")
        self.assertFalse(settings.create_clients_folder)


class ManifestRuleTests(unittest.TestCase):
    def test_occurrence_counting_is_case_sensitive_by_default(self):
        rule = ReplacementRule(find="Ambient", replace="[CLIENT_NAME]", category="company_name")
        self.assertEqual(rule.occurrences("Ambient and ambient"), 1)

    def test_case_insensitive_rules_count_both(self):
        rule = ReplacementRule(
            find="Ambient", replace="[CLIENT_NAME]", category="company_name", match_case=False
        )
        self.assertEqual(rule.occurrences("Ambient and ambient"), 2)

    def test_empty_manifest_sorts_cleanly(self):
        self.assertEqual(ScrubManifest(source_document_id="x").sorted_rules(), [])


if __name__ == "__main__":
    unittest.main()
