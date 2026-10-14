"""Regression tests for the reusable folder, review, image and placeholder rules.

Each test pins a defect found in the EKG Lawn Services packages on 2026-08-15 so the same
mistake cannot silently recur for a future client.
"""

from __future__ import annotations

import pytest

from gm_gsa.landing_page_rules import (
    BANNED_PLACEHOLDER,
    GENERAL_SERVICE_POSITIONS,
    PROJECT_GALLERY_POSITIONS,
    SOURCING_PRIORITY,
    ImageRecord,
    LandingPageRuleError,
    PagePackage,
    ReviewCard,
    count_repeated_instructions,
    expected_page_path,
    images_needing_generation,
    validate_filename_extension,
    validate_image_instruction,
    validate_image_record,
    validate_no_public_sharing,
    validate_page_packages,
    validate_review_card,
)

SHARED = "shared-landing-pages-folder"


def pkg(name, page="pf", images="if", doc="doc", parents=None, images_parent=None):
    return PagePackage(
        page_name=name,
        page_folder_id=page,
        images_folder_id=images,
        doc_id=doc,
        doc_parents=tuple(parents if parents is not None else (page,)),
        images_folder_parent=images_parent if images_parent is not None else page,
    )


# ---------------------------------------------------------------------------
# Folder rules
# ---------------------------------------------------------------------------


class TestFolderLayout:
    def test_correct_layout_has_no_violations(self):
        packages = [
            pkg("Lawn Aeration", "pf-a", "if-a", "doc-a"),
            pkg("Aeration & Overseeding", "pf-b", "if-b", "doc-b"),
        ]
        assert validate_page_packages(packages, SHARED) == []

    def test_expected_path_has_a_page_level_and_no_clients_level(self):
        path = expected_page_path("Green Marketing Landing Pages", "EKG Lawn Services LLC",
                                  "Lawn Aeration")
        assert path == ["Green Marketing Landing Pages", "EKG Lawn Services LLC",
                        "Landing Pages", "Lawn Aeration"]
        assert "Clients" not in path

    def test_doc_loose_in_shared_landing_pages_folder_is_flagged(self):
        """The exact EKG defect: both Docs sat directly in 'Landing Pages'."""
        packages = [
            pkg("Lawn Aeration", "pf-a", "if-a", "doc-a", parents=(SHARED,)),
            pkg("Aeration & Overseeding", "pf-b", "if-b", "doc-b", parents=(SHARED,)),
        ]
        violations = validate_page_packages(packages, SHARED)
        assert len(violations) == 2
        assert all("needs its own page folder" in v for v in violations)

    def test_doc_with_two_parents_is_flagged(self):
        violations = validate_page_packages(
            [pkg("Lawn Aeration", "pf-a", "if-a", "doc-a", parents=("pf-a", SHARED))], SHARED
        )
        assert any("expected exactly 1" in v for v in violations)

    def test_missing_images_subfolder_is_flagged(self):
        violations = validate_page_packages([pkg("Lawn Aeration", "pf-a", "", "doc-a")], SHARED)
        assert any("no Images subfolder" in v for v in violations)

    def test_two_pages_sharing_one_images_folder_is_flagged(self):
        packages = [
            pkg("Lawn Aeration", "pf-a", "shared-images", "doc-a"),
            pkg("Aeration & Overseeding", "pf-b", "shared-images", "doc-b"),
        ]
        packages[1] = PagePackage("Aeration & Overseeding", "pf-b", "shared-images", "doc-b",
                                  ("pf-b",), "pf-b")
        violations = validate_page_packages(packages, SHARED)
        assert any("shares its Images folder" in v for v in violations)

    def test_same_document_registered_twice_is_flagged(self):
        """Guards against a duplicate Doc being created instead of the original moved."""
        packages = [
            pkg("Lawn Aeration", "pf-a", "if-a", "same-doc"),
            pkg("Aeration & Overseeding", "pf-b", "if-b", "same-doc", parents=("pf-b",),
                images_parent="pf-b"),
        ]
        violations = validate_page_packages(packages, SHARED)
        assert any("shares its document" in v for v in violations)

    def test_images_folder_parented_elsewhere_is_flagged(self):
        violations = validate_page_packages(
            [pkg("Lawn Aeration", "pf-a", "if-a", "doc-a", images_parent=SHARED)], SHARED
        )
        assert any("not to its own page folder" in v for v in violations)


# ---------------------------------------------------------------------------
# Image provenance rules
# ---------------------------------------------------------------------------


def img(**kw):
    base = dict(
        page_name="Lawn Aeration",
        position=5,
        filename="05-aerated-turf-detail.jpg",
        provenance="client_website_or_gbp",
        source_url="https://example.com/photo.jpg",
        visually_inspected=True,
        observed_content="core-aerated turf with soil plugs",
        actual_format="jpeg",
        client_owned=False,
    )
    base.update(kw)
    return ImageRecord(**base)


class TestImageProvenance:
    def test_sourcing_priority_puts_first_party_before_stock_and_generated(self):
        assert SOURCING_PRIORITY.index("client_project_photo") == 0
        assert SOURCING_PRIORITY.index("client_website_or_gbp") < SOURCING_PRIORITY.index(
            "licensed_stock"
        )
        assert SOURCING_PRIORITY.index("licensed_stock") < SOURCING_PRIORITY.index("generated")

    def test_general_position_accepts_inspected_first_party_image(self):
        assert validate_image_record(img()) == []

    def test_image_approved_without_visual_inspection_is_flagged(self):
        violations = validate_image_record(img(visually_inspected=False))
        assert any("without pixel-level visual inspection" in v for v in violations)

    def test_image_without_recorded_source_is_flagged(self):
        violations = validate_image_record(img(source_url=""))
        assert any("no original source recorded" in v for v in violations)

    def test_stock_image_without_license_is_flagged(self):
        violations = validate_image_record(img(provenance="licensed_stock", license=""))
        assert any("without a recorded license" in v for v in violations)

    def test_watermarked_image_is_flagged(self):
        violations = validate_image_record(img(watermark_or_third_party_branding=True))
        assert any("watermark or third-party branding" in v for v in violations)

    @pytest.mark.parametrize("position", PROJECT_GALLERY_POSITIONS)
    @pytest.mark.parametrize("provenance", ["licensed_stock", "generated", "unknown"])
    def test_gallery_position_rejects_stock_and_generated(self, position, provenance):
        violations = validate_image_record(
            img(position=position, provenance=provenance, license="CC0",
                filename=f"0{position}-ekg-project.jpg")
        )
        assert any("project-gallery position cannot use" in v for v in violations)

    @pytest.mark.parametrize("position", PROJECT_GALLERY_POSITIONS)
    def test_gallery_position_requires_client_owned_photo(self, position):
        violations = validate_image_record(
            img(position=position, provenance="client_project_photo", client_owned=False,
                filename=f"0{position}-ekg-project.jpg")
        )
        assert any("requires an authentic client project photo" in v for v in violations)

    @pytest.mark.parametrize("position", PROJECT_GALLERY_POSITIONS)
    def test_gallery_position_accepts_authentic_client_photo(self, position):
        assert validate_image_record(
            img(position=position, provenance="client_project_photo", client_owned=True,
                presented_as_client_work=True, filename=f"0{position}-ekg-project.jpg")
        ) == []

    def test_stock_image_presented_as_client_work_is_flagged(self):
        """The headline rule: never describe stock or AI imagery as the client's work."""
        violations = validate_image_record(
            img(position=2, provenance="licensed_stock", license="Unsplash",
                presented_as_client_work=True, filename="02-core-aeration-service.jpg")
        )
        assert any("presented as client work" in v for v in violations)

    def test_generated_image_presented_as_client_work_is_flagged(self):
        violations = validate_image_record(
            img(position=1, provenance="generated", presented_as_client_work=True,
                filename="01-lawn-aeration-hero.png", actual_format="png")
        )
        assert any("presented as client work" in v for v in violations)

    def test_unknown_position_raises(self):
        with pytest.raises(LandingPageRuleError):
            validate_image_record(img(position=12))


class TestFilenameExtension:
    def test_matching_extension_passes(self):
        assert validate_filename_extension("05-aerated-turf-detail.jpg", "jpeg") == []
        assert validate_filename_extension("01-hero.png", "png") == []

    def test_jpeg_renamed_as_png_is_flagged(self):
        violations = validate_filename_extension("05-aerated-turf-detail.png", "jpeg")
        assert any("does not match the actual JPEG format" in v for v in violations)

    def test_missing_extension_is_flagged(self):
        assert validate_filename_extension("05-aerated-turf-detail", "jpeg")

    def test_unknown_format_raises(self):
        with pytest.raises(LandingPageRuleError):
            validate_filename_extension("x.tiff", "tiff")


class TestGenerationManifest:
    def test_only_general_positions_are_ever_requested_for_generation(self):
        records = [img(position=5, filename="05-aerated-turf-detail.jpg")]
        missing = images_needing_generation(records)
        assert missing["Lawn Aeration"] == [1, 2, 3, 4]
        assert not set(missing["Lawn Aeration"]) & set(PROJECT_GALLERY_POSITIONS)

    def test_gallery_positions_never_appear_even_when_totally_empty(self):
        missing = images_needing_generation([img(position=1, filename="01-hero.jpg")])
        assert all(p in GENERAL_SERVICE_POSITIONS for p in missing["Lawn Aeration"])


# ---------------------------------------------------------------------------
# Placeholder / image instruction rules
# ---------------------------------------------------------------------------

GOOD_BRIEF = (
    "IMAGE SUGGESTION: Subject - a commercial walk-behind core aerator on a residential lawn. "
    "Composition - three-quarter side view with plugs in the foreground. "
    "Orientation - landscape, 4:3, at least 1200x1000. "
    "Must show - the coring tines and soil plugs on the surface. "
    "Real client photo - not required. "
    "Avoid - manufacturer branding, farm tractors, watermarks. "
    'Alt text - "Core aerator pulling soil plugs from a residential lawn."'
)


class TestImageInstructions:
    def test_complete_brief_passes(self):
        assert validate_image_instruction(GOOD_BRIEF, position=2) == []

    def test_developer_todo_is_banned(self):
        text = f"{BANNED_PLACEHOLDER} insert a hero image]"
        violations = validate_image_instruction(text, position=1)
        assert any("banned" in v for v in violations)

    def test_missing_image_suggestion_marker_is_flagged(self):
        violations = validate_image_instruction("Subject - a lawn. Avoid - logos.", position=1)
        assert any("missing the 'IMAGE SUGGESTION:' marker" in v for v in violations)

    @pytest.mark.parametrize(
        "dropped", ["Subject", "Composition", "Orientation", "Must show", "Avoid", "Alt text"]
    )
    def test_brief_missing_a_required_element_is_flagged(self, dropped):
        stripped = " ".join(
            part for part in GOOD_BRIEF.split(". ") if dropped.lower() not in part.lower()
        )
        assert dropped.lower() not in stripped.lower()
        violations = validate_image_instruction(stripped, position=2)
        assert any("omits" in v for v in violations)

    @pytest.mark.parametrize("phrase", ["insert an image", "add a project photo", "TBD"])
    def test_vague_wording_is_flagged(self, phrase):
        violations = validate_image_instruction(
            f"IMAGE SUGGESTION: {phrase}. subject composition orientation must show real "
            'avoid alt text - "x"',
            position=1,
        )
        assert any("vague wording" in v for v in violations)

    @pytest.mark.parametrize("position", PROJECT_GALLERY_POSITIONS)
    def test_gallery_brief_must_state_a_real_photo_is_required(self, position):
        violations = validate_image_instruction(GOOD_BRIEF, position=position)
        assert any("must state that a real client photo is required" in v for v in violations)

    def test_repeated_instruction_inside_one_card_is_detectable(self):
        card = "TODO\vTODO\vTODO"
        assert count_repeated_instructions(card) == 3
        assert count_repeated_instructions("stars\vtext\vname\vlabel") == 1


# ---------------------------------------------------------------------------
# Review card rules
# ---------------------------------------------------------------------------

OFFICIAL = (
    "I've been using EKG Lawn Services for several years. They always do a great job at a "
    "fair price. The work is meticulous and well done. I give them my highest personal "
    "recommendation."
)


class TestReviewCards:
    def test_complete_card_passes(self):
        card = ReviewCard("*****", OFFICIAL, "RANDALL, L.", "EKG Lawn Customer",
                          ("*****", OFFICIAL, "RANDALL, L.", "EKG Lawn Customer"))
        assert validate_review_card(card, official_text=OFFICIAL) == []

    def test_truncated_review_is_flagged_as_truncated(self):
        """The exact EKG defect: two cards had their closing sentences dropped."""
        truncated = OFFICIAL.split(" The work is meticulous")[0]
        card = ReviewCard("*****", truncated, "RANDALL, L.", "EKG Lawn Customer")
        violations = validate_review_card(card, official_text=OFFICIAL)
        assert any("TRUNCATED" in v for v in violations)

    def test_paraphrased_review_is_flagged(self):
        card = ReviewCard("*****", "They do great work at fair prices.", "RANDALL, L.")
        violations = validate_review_card(card, official_text=OFFICIAL)
        assert any("does not match the official source verbatim" in v for v in violations)

    def test_missing_star_rating_is_flagged(self):
        card = ReviewCard("", OFFICIAL, "RANDALL, L.")
        assert any("no displayed star rating" in v for v in validate_review_card(card))

    def test_missing_reviewer_name_is_flagged(self):
        card = ReviewCard("*****", OFFICIAL, "")
        assert any("no displayed reviewer name" in v for v in validate_review_card(card))

    def test_placeholder_left_in_card_is_flagged(self):
        card = ReviewCard("*****", f"{BANNED_PLACEHOLDER} add a review]", "X")
        assert any("developer placeholder" in v for v in validate_review_card(card))

    @pytest.mark.parametrize(
        "leak",
        ["Source: https://ekglawn.com/reviews/", "Google Review", "retrieved from Birdeye"],
    )
    def test_provenance_leaking_into_a_card_is_flagged(self, leak):
        card = ReviewCard("*****", OFFICIAL, "RANDALL, L.", leak)
        assert any("leaks provenance term" in v for v in validate_review_card(card))

    def test_same_placeholder_repeated_three_times_in_a_card_is_flagged(self):
        card = ReviewCard("*****", "TODO", "TODO", "TODO", ("TODO", "TODO", "TODO"))
        assert any("repeated three times" in v for v in validate_review_card(card))


# ---------------------------------------------------------------------------
# Sharing rules
# ---------------------------------------------------------------------------


class TestSharing:
    def test_owner_only_permissions_pass(self):
        perms = [{"type": "user", "role": "owner"}, {"type": "user", "role": "writer"}]
        assert validate_no_public_sharing(perms, "05-aerated-turf-detail.jpg") == []

    def test_anyone_with_the_link_is_flagged(self):
        """No public-sharing workaround to force Google Docs image insertion."""
        perms = [{"type": "user", "role": "owner"}, {"type": "anyone", "role": "reader"}]
        violations = validate_no_public_sharing(perms, "05-aerated-turf-detail.jpg")
        assert any("must never be made public" in v for v in violations)

    def test_domain_wide_sharing_is_flagged(self):
        perms = [{"type": "domain", "role": "reader"}]
        assert validate_no_public_sharing(perms)
