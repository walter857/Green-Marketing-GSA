"""Reusable landing-page rules: folder layout, image provenance, placeholders, sharing.

These encode the corrections made on 2026-08-15 so that every future client inherits them
automatically rather than depending on a per-task instruction:

* one page-specific folder per landing-page document, each with its own ``Images`` subfolder;
* first-party image research before stock, and stock before generated imagery;
* pixel-level visual inspection and a provenance record before any image is approved;
* specific ``IMAGE SUGGESTION`` briefs instead of generic developer placeholders;
* no stock or generated imagery presented as the client's own project work;
* no public-sharing workaround for a private image.

Every function here is pure so it can be unit tested without touching Drive.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Placeholders
# ---------------------------------------------------------------------------

BANNED_PLACEHOLDER = "[DEVELOPER TODO:"
IMAGE_SUGGESTION_PREFIX = "IMAGE SUGGESTION:"

#: Every image brief must answer all of these.
REQUIRED_BRIEF_ELEMENTS = (
    "subject",
    "composition",
    "orientation",
    "must show",
    "real",  # "Real <client> photo - required / not required"
    "avoid",
    "alt text",
)

VAGUE_PHRASES = (
    "insert an image",
    "add a project photo",
    "add an image",
    "insert image here",
    "image here",
    "tbd",
    "to be decided",
    "placeholder image",
)

# ---------------------------------------------------------------------------
# Image positions
# ---------------------------------------------------------------------------

#: Positions that may carry client-owned, licensed stock, or generated service imagery.
GENERAL_SERVICE_POSITIONS = (1, 2, 3, 4, 5)
#: Positions that may carry ONLY authentic client project photographs.
PROJECT_GALLERY_POSITIONS = (6, 7, 8, 9)

SOURCING_PRIORITY = (
    "client_project_photo",
    "client_website_or_gbp",
    "licensed_stock",
    "generated",
)

#: Provenance classes that may never occupy a project-gallery position.
NON_PROJECT_PROVENANCE = frozenset({"licensed_stock", "generated", "unknown"})

EXTENSION_BY_FORMAT = {
    "jpeg": {".jpg", ".jpeg"},
    "jpg": {".jpg", ".jpeg"},
    "png": {".png"},
    "webp": {".webp"},
    "gif": {".gif"},
}


class LandingPageRuleError(ValueError):
    """Raised when a caller supplies input the rules cannot evaluate."""


# ---------------------------------------------------------------------------
# Drive folder layout
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PagePackage:
    """One landing page's Drive resources."""

    page_name: str
    page_folder_id: str
    images_folder_id: str
    doc_id: str
    doc_parents: tuple[str, ...]
    images_folder_parent: str


def expected_page_path(root_name: str, client_name: str, page_name: str) -> list[str]:
    """The approved Drive path for a landing-page package."""
    return [root_name, client_name, "Landing Pages", page_name]


def validate_page_packages(
    packages: list[PagePackage], shared_parent_id: str
) -> list[str]:
    """Return every folder-layout violation. An empty list means the layout is correct.

    ``shared_parent_id`` is the client's ``Landing Pages`` folder. A document parented
    directly there has not been given its own page folder.
    """
    violations: list[str] = []
    seen_page_folders: dict[str, str] = {}
    seen_images_folders: dict[str, str] = {}
    seen_docs: dict[str, str] = {}

    for pkg in packages:
        if len(pkg.doc_parents) != 1:
            violations.append(
                f"{pkg.page_name}: document has {len(pkg.doc_parents)} parents, expected exactly 1"
            )
        elif pkg.doc_parents[0] == shared_parent_id:
            violations.append(
                f"{pkg.page_name}: document sits directly in the shared 'Landing Pages' folder; "
                "it needs its own page folder"
            )
        elif pkg.doc_parents[0] != pkg.page_folder_id:
            violations.append(
                f"{pkg.page_name}: document parent {pkg.doc_parents[0]} is not its page folder "
                f"{pkg.page_folder_id}"
            )

        if not pkg.images_folder_id:
            violations.append(f"{pkg.page_name}: page folder has no Images subfolder")
        elif pkg.images_folder_parent != pkg.page_folder_id:
            violations.append(
                f"{pkg.page_name}: Images folder is parented to {pkg.images_folder_parent}, "
                f"not to its own page folder {pkg.page_folder_id}"
            )

        for value, registry, label in (
            (pkg.page_folder_id, seen_page_folders, "page folder"),
            (pkg.images_folder_id, seen_images_folders, "Images folder"),
            (pkg.doc_id, seen_docs, "document"),
        ):
            if not value:
                continue
            if value in registry:
                violations.append(
                    f"{pkg.page_name}: shares its {label} {value} with {registry[value]}; "
                    "each page needs its own"
                )
            else:
                registry[value] = pkg.page_name

    return violations


# ---------------------------------------------------------------------------
# Image provenance
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ImageRecord:
    """One image considered for one position on one page."""

    page_name: str
    position: int
    filename: str
    provenance: str  # one of SOURCING_PRIORITY, or "unknown"
    source_url: str
    visually_inspected: bool
    observed_content: str
    license: str = ""
    creator: str = ""
    client_owned: bool = False
    presented_as_client_work: bool = False
    actual_format: str = ""
    dimensions: tuple[int, int] | None = None
    alt_text: str = ""
    watermark_or_third_party_branding: bool = False
    notes: str = ""


def validate_image_record(record: ImageRecord) -> list[str]:
    """Return every provenance/placement violation for one image."""
    violations: list[str] = []
    where = f"{record.page_name} position {record.position}"

    if record.position not in GENERAL_SERVICE_POSITIONS + PROJECT_GALLERY_POSITIONS:
        raise LandingPageRuleError(f"{where}: unknown image position")

    if not record.visually_inspected:
        violations.append(f"{where}: approved without pixel-level visual inspection")
    if not record.observed_content.strip():
        violations.append(f"{where}: no record of what the image visibly shows")
    if not record.source_url.strip():
        violations.append(f"{where}: no original source recorded")
    if record.provenance not in SOURCING_PRIORITY and record.provenance != "unknown":
        raise LandingPageRuleError(f"{where}: unrecognized provenance {record.provenance!r}")
    if record.provenance == "licensed_stock" and not record.license.strip():
        violations.append(f"{where}: stock image without a recorded license")
    if record.watermark_or_third_party_branding:
        violations.append(f"{where}: carries a watermark or third-party branding")

    if record.position in PROJECT_GALLERY_POSITIONS:
        if record.provenance in NON_PROJECT_PROVENANCE:
            violations.append(
                f"{where}: project-gallery position cannot use "
                f"{record.provenance!r} imagery"
            )
        if not record.client_owned:
            violations.append(
                f"{where}: project-gallery position requires an authentic client project photo"
            )

    if record.presented_as_client_work and (
        record.provenance in NON_PROJECT_PROVENANCE or not record.client_owned
    ):
        violations.append(
            f"{where}: presented as client work but is not a verified client project photo"
        )

    violations.extend(validate_filename_extension(record.filename, record.actual_format, where))
    return violations


def validate_filename_extension(filename: str, actual_format: str, where: str = "") -> list[str]:
    """A file must not be renamed into a type it is not."""
    if not actual_format:
        return []
    fmt = actual_format.lower().lstrip(".")
    allowed = EXTENSION_BY_FORMAT.get(fmt)
    if allowed is None:
        raise LandingPageRuleError(f"unrecognized image format {actual_format!r}")
    suffix = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    if suffix not in allowed:
        label = f"{where}: " if where else ""
        return [
            f"{label}filename {filename!r} does not match the actual {fmt.upper()} format "
            f"(expected one of {sorted(allowed)})"
        ]
    return []


def images_needing_generation(
    records: list[ImageRecord], positions_per_page: int = 9
) -> dict[str, list[int]]:
    """Per page, the GENERAL-SERVICE positions with no approved image.

    Gallery positions are never included: generated imagery may not fill them.
    """
    filled: dict[str, set[int]] = {}
    for r in records:
        filled.setdefault(r.page_name, set())
        if not validate_image_record(r):
            filled[r.page_name].add(r.position)
    return {
        page: [p for p in GENERAL_SERVICE_POSITIONS if p not in got]
        for page, got in filled.items()
    }


# ---------------------------------------------------------------------------
# Image instructions
# ---------------------------------------------------------------------------


def validate_image_instruction(text: str, position: int | None = None) -> list[str]:
    """Return every violation for one image-placement instruction."""
    violations: list[str] = []
    where = f"position {position}: " if position is not None else ""
    lowered = text.lower()

    if BANNED_PLACEHOLDER.lower() in lowered:
        violations.append(f"{where}uses the banned '{BANNED_PLACEHOLDER}' placeholder")
    if IMAGE_SUGGESTION_PREFIX not in text:
        violations.append(f"{where}missing the '{IMAGE_SUGGESTION_PREFIX}' marker")

    missing = [e for e in REQUIRED_BRIEF_ELEMENTS if e not in lowered]
    if missing:
        violations.append(f"{where}brief omits {', '.join(missing)}")

    for phrase in VAGUE_PHRASES:
        if re.search(rf"\b{re.escape(phrase)}\b", lowered):
            violations.append(f"{where}uses vague wording {phrase!r}")

    if position in PROJECT_GALLERY_POSITIONS:
        # "not required" contains "required", so a substring test is not enough here.
        stance = re.search(
            r"real[^.\v]*?photo[^.\v]*?[-–—:]\s*(not\s+required|required)", lowered
        )
        if stance is None or stance.group(1).startswith("not"):
            violations.append(
                f"{where}gallery position must state that a real client photo is required"
            )
    return violations


def count_repeated_instructions(card_text: str) -> int:
    """How many times the longest repeated line occurs in one card."""
    lines = [line.strip() for line in re.split(r"[\v\n]", card_text) if line.strip()]
    if not lines:
        return 0
    return max(lines.count(line) for line in lines)


# ---------------------------------------------------------------------------
# Review cards
# ---------------------------------------------------------------------------

PROVENANCE_TERMS = (
    "http://",
    "https://",
    "google review",
    "google business profile",
    "gbp",
    "source:",
    "retrieved",
    "snapshot",
    "birdeye",
    "yelp",
)


@dataclass(frozen=True)
class ReviewCard:
    star_rating: str
    text: str
    reviewer_name: str
    attribution: str = ""
    lines: tuple[str, ...] = field(default_factory=tuple)


def validate_review_card(card: ReviewCard, official_text: str | None = None) -> list[str]:
    """Return every violation for one customer-facing review card."""
    violations: list[str] = []
    who = card.reviewer_name or "<unnamed>"

    if not card.star_rating.strip():
        violations.append(f"{who}: no displayed star rating")
    if not card.text.strip():
        violations.append(f"{who}: no review text")
    if not card.reviewer_name.strip():
        violations.append("review card has no displayed reviewer name")
    if BANNED_PLACEHOLDER.lower() in card.text.lower():
        violations.append(f"{who}: still holds a developer placeholder")

    if official_text is not None and card.text != official_text:
        if official_text.startswith(card.text.rstrip()) and card.text.rstrip() != official_text:
            violations.append(f"{who}: review text is TRUNCATED relative to the official source")
        else:
            violations.append(f"{who}: review text does not match the official source verbatim")

    joined = " ".join(filter(None, [card.text, card.reviewer_name, card.attribution])).lower()
    for term in PROVENANCE_TERMS:
        if term in joined:
            violations.append(f"{who}: customer-facing card leaks provenance term {term!r}")

    if card.lines:
        counts = {line.strip(): card.lines.count(line) for line in card.lines if line.strip()}
        repeated = [line for line, n in counts.items() if n >= 3]
        if repeated:
            violations.append(f"{who}: the same line is repeated three times inside the card")
    return violations


# ---------------------------------------------------------------------------
# Sharing
# ---------------------------------------------------------------------------


def validate_no_public_sharing(permissions: list[dict[str, str]], resource: str = "") -> list[str]:
    """A landing-page asset must never be shared with 'anyone with the link'."""
    label = f"{resource}: " if resource else ""
    bad = [p for p in permissions if p.get("type") in {"anyone", "domain"}]
    if bad:
        kinds = ", ".join(sorted({p.get("type", "?") for p in bad}))
        return [f"{label}shared publicly via '{kinds}'; private images must never be made public"]
    return []
