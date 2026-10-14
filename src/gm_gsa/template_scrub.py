"""Scrubbing engine for the Green Marketing landing-page master template.

The canonical document is a completed client example. It is treated here as a protected,
read-only formatting and structural source. Every write helper in this module refuses to
operate on it, so a copy is the only thing that can ever be modified.

Design notes:

- Bulk text substitution uses Docs ``replaceAllText``, which preserves paragraph styles,
  headings, lists, tables, and spacing, and which reaches headers, footers, footnotes, and
  table cells automatically. The document is never rebuilt from scratch.
- Rich-link chips and hyperlinked text cannot be changed by ``replaceAllText``, so those are
  handled by explicit range operations. Range edits shift indices, so they are emitted in
  descending index order and executed in their own batch BEFORE the text batch.
- Nothing in this module deletes, trashes, moves, or shares a Drive resource.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from .config import ConfigurationError, load_yaml
# MASTER_TEMPLATE_NAME and TEMP_SCRUB_NAME are defined in google_drive so that the
# "never create an unscrubbed master" guard and the rename that earns the final name share
# one definition. They are re-exported here because callers import them from this module.
from .google_drive import (  # noqa: F401
    CANONICAL_TEMPLATE_ID,
    MASTER_TEMPLATE_NAME,
    TEMP_SCRUB_NAME,
    DriveError,
)

# Any file ID here is permanently read-only for this repository.
PROTECTED_DOCUMENT_IDS: frozenset[str] = frozenset({CANONICAL_TEMPLATE_ID})

WRITE_OPERATIONS = (
    "documents.batchUpdate",
    "files.update",
    "files.delete",
    "files.trash",
    "files.move",
    "files.copy:destination",
    "permissions.create",
    "permissions.update",
    "permissions.delete",
)


class CanonicalTemplateWriteError(DriveError):
    """Raised on any attempt to write to, move, share, or delete the canonical template."""


class ScrubValidationError(DriveError):
    """Raised when a scrubbed document still contains source-client facts."""


# ---------------------------------------------------------------------------
# Hard write guard
# ---------------------------------------------------------------------------


def assert_writable_target(file_id: str | None, operation: str) -> None:
    """Refuse any write-shaped operation aimed at a protected document ID."""
    normalized = str(file_id or "").strip()
    if normalized in PROTECTED_DOCUMENT_IDS:
        raise CanonicalTemplateWriteError(
            f"Refusing {operation} on protected canonical template {normalized}. "
            "The canonical document is a read-only structural source; scrub a copy instead."
        )


def assert_requests_do_not_target_canonical(requests: Any) -> None:
    """Second line of defense: reject a protected ID nested anywhere inside a payload."""
    if isinstance(requests, dict):
        for key, value in requests.items():
            if isinstance(value, str) and value.strip() in PROTECTED_DOCUMENT_IDS:
                raise CanonicalTemplateWriteError(
                    f"Refusing a request whose {key!r} targets the protected canonical template."
                )
            assert_requests_do_not_target_canonical(value)
    elif isinstance(requests, (list, tuple)):
        for item in requests:
            assert_requests_do_not_target_canonical(item)


def guarded_batch_update(docs_service: Any, document_id: str, requests: list[dict]) -> dict:
    assert_writable_target(document_id, "documents.batchUpdate")
    assert_requests_do_not_target_canonical(requests)
    if not requests:
        return {}
    return (
        docs_service.documents()
        .batchUpdate(documentId=document_id, body={"requests": requests})
        .execute()
    )


def guarded_files_update(drive_service: Any, file_id: str, body: dict, **kwargs: Any) -> dict:
    assert_writable_target(file_id, "files.update")
    assert_requests_do_not_target_canonical(body)
    for parent_key in ("addParents", "removeParents"):
        if kwargs.get(parent_key):
            assert_writable_target(file_id, "files.move")
    return (
        drive_service.files()
        .update(fileId=file_id, body=body, supportsAllDrives=True, **kwargs)
        .execute()
    )


def guarded_rename(drive_service: Any, file_id: str, new_name: str) -> dict:
    assert_writable_target(file_id, "files.update")
    return guarded_files_update(drive_service, file_id, {"name": new_name}, fields="id, name")


def guarded_delete(drive_service: Any, file_id: str) -> None:
    """Present only to enforce the refusal. This repository never deletes Drive resources."""
    assert_writable_target(file_id, "files.delete")
    raise CanonicalTemplateWriteError(
        "Deletion is not permitted from the landing-page workflow. "
        "A destructive-action approval is required."
    )


def guarded_trash(drive_service: Any, file_id: str) -> None:
    assert_writable_target(file_id, "files.trash")
    raise CanonicalTemplateWriteError(
        "Trashing is not permitted from the landing-page workflow. "
        "A destructive-action approval is required."
    )


def guarded_move(drive_service: Any, file_id: str, add_parents: str, remove_parents: str) -> None:
    assert_writable_target(file_id, "files.move")
    raise CanonicalTemplateWriteError(
        "Moving existing Drive resources is not permitted from the landing-page workflow."
    )


def guarded_permission_change(drive_service: Any, file_id: str, operation: str = "permissions.create") -> None:
    assert_writable_target(file_id, operation)
    raise CanonicalTemplateWriteError(
        "Sharing and permission changes are not permitted from the landing-page workflow."
    )


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReplacementRule:
    find: str
    replace: str
    category: str
    note: str = ""
    match_case: bool = True

    def occurrences(self, text: str) -> int:
        if not self.find:
            return 0
        haystack = text if self.match_case else text.casefold()
        needle = self.find if self.match_case else self.find.casefold()
        return haystack.count(needle)


@dataclass
class ScrubManifest:
    source_document_id: str
    rules: list[ReplacementRule] = field(default_factory=list)
    forbidden_after_scrub: list[str] = field(default_factory=list)
    link_replacements: dict[str, str] = field(default_factory=dict)

    def sorted_rules(self) -> list[ReplacementRule]:
        """Longest find-string first so specific phrases win over their own substrings."""
        return sorted(self.rules, key=lambda r: (-len(r.find), r.find))


def load_scrub_manifest(path: str | Path) -> ScrubManifest:
    document = load_yaml(path)
    source_id = str(document.get("source_document_id") or "").strip()
    if not source_id:
        raise ConfigurationError(f"source_document_id is required in {path}")

    rules: list[ReplacementRule] = []
    seen: set[str] = set()
    for raw in document.get("replacements") or []:
        if not isinstance(raw, dict):
            raise ConfigurationError(f"Each replacement must be a mapping in {path}")
        find = str(raw.get("find", ""))
        if not find:
            raise ConfigurationError(f"A replacement is missing 'find' in {path}")
        if find in seen:
            raise ConfigurationError(f"Duplicate replacement find value {find!r} in {path}")
        seen.add(find)
        rules.append(
            ReplacementRule(
                find=find,
                replace=str(raw.get("replace", "")),
                category=str(raw.get("category", "uncategorized")),
                note=str(raw.get("note", "")),
                match_case=bool(raw.get("match_case", True)),
            )
        )

    return ScrubManifest(
        source_document_id=source_id,
        rules=rules,
        forbidden_after_scrub=[str(t) for t in (document.get("forbidden_after_scrub") or [])],
        link_replacements={
            str(k): str(v) for k, v in (document.get("link_replacements") or {}).items()
        },
    )


# ---------------------------------------------------------------------------
# Document traversal
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TextSegment:
    tab_id: str
    segment_kind: str  # body | header | footer | footnote
    segment_id: str
    path: str
    text: str
    style: str


@dataclass(frozen=True)
class LinkTarget:
    tab_id: str
    segment_kind: str
    segment_id: str
    kind: str  # richLink | hyperlink | inlineImage
    start_index: int
    end_index: int
    url: str
    title: str = ""
    description: str = ""


def iter_tabs(document: dict) -> Iterator[tuple[str, dict]]:
    """Yield (tab_id, tab_content) for tabbed and untabbed documents alike."""
    tabs = document.get("tabs")
    if not tabs:
        yield ("", document)
        return

    def walk(nodes: list[dict]) -> Iterator[tuple[str, dict]]:
        for node in nodes or []:
            tab_id = (node.get("tabProperties") or {}).get("tabId", "")
            content = node.get("documentTab") or {}
            yield (tab_id, content)
            yield from walk(node.get("childTabs") or [])

    yield from walk(tabs)


def _iter_structural(content: list[dict] | None, path: str) -> Iterator[tuple[dict, str]]:
    for element in content or []:
        if "paragraph" in element:
            yield (element["paragraph"], path)
        elif "table" in element:
            table = element["table"]
            for r, row in enumerate(table.get("tableRows") or []):
                for c, cell in enumerate(row.get("tableCells") or []):
                    yield from _iter_structural(cell.get("content"), f"{path}/table[r{r}c{c}]")
        elif "tableOfContents" in element:
            yield from _iter_structural(element["tableOfContents"].get("content"), f"{path}/toc")


def _segments_of_tab(tab_id: str, tab: dict) -> Iterator[tuple[str, str, list[dict] | None]]:
    yield ("body", "", (tab.get("body") or {}).get("content"))
    for kind, key in (("header", "headers"), ("footer", "footers"), ("footnote", "footnotes")):
        for segment_id, segment in (tab.get(key) or {}).items():
            yield (kind, segment_id, segment.get("content"))


def iter_text_segments(document: dict) -> Iterator[TextSegment]:
    """Every paragraph of text in the document, including headers, footers and tables."""
    for tab_id, tab in iter_tabs(document):
        for kind, segment_id, content in _segments_of_tab(tab_id, tab):
            for paragraph, path in _iter_structural(content, kind):
                text = "".join(
                    (el.get("textRun") or {}).get("content", "")
                    for el in paragraph.get("elements") or []
                )
                if not text.strip():
                    continue
                yield TextSegment(
                    tab_id=tab_id,
                    segment_kind=kind,
                    segment_id=segment_id,
                    path=path,
                    text=text,
                    style=(paragraph.get("paragraphStyle") or {}).get("namedStyleType", ""),
                )


def iter_link_targets(document: dict) -> Iterator[LinkTarget]:
    """Rich-link chips, hyperlinked text runs, and inline images with their alt text."""
    for tab_id, tab in iter_tabs(document):
        inline_objects = tab.get("inlineObjects") or {}
        for kind, segment_id, content in _segments_of_tab(tab_id, tab):
            for paragraph, _path in _iter_structural(content, kind):
                for element in paragraph.get("elements") or []:
                    start = element.get("startIndex", 0)
                    end = element.get("endIndex", 0)
                    rich = element.get("richLink")
                    if rich:
                        props = rich.get("richLinkProperties") or {}
                        yield LinkTarget(
                            tab_id, kind, segment_id, "richLink", start, end,
                            url=props.get("uri", ""), title=props.get("title", ""),
                        )
                        continue
                    text_run = element.get("textRun")
                    if text_run:
                        link = (text_run.get("textStyle") or {}).get("link") or {}
                        if link.get("url"):
                            yield LinkTarget(
                                tab_id, kind, segment_id, "hyperlink", start, end,
                                url=link["url"], title=text_run.get("content", "").strip(),
                            )
                        continue
                    inline = element.get("inlineObjectElement")
                    if inline:
                        obj = inline_objects.get(inline.get("inlineObjectId"), {})
                        embedded = (
                            (obj.get("inlineObjectProperties") or {}).get("embeddedObject") or {}
                        )
                        yield LinkTarget(
                            tab_id, kind, segment_id, "inlineImage", start, end,
                            url=(embedded.get("imageProperties") or {}).get("sourceUri", ""),
                            title=embedded.get("title", ""),
                            description=embedded.get("description", ""),
                        )


def document_structure_fingerprint(document: dict) -> dict[str, Any]:
    """Structural signature used to prove scrubbing did not alter the document's shape."""
    styles: list[str] = []
    bullets = 0
    tables: list[str] = []

    def has_content(paragraph: dict) -> bool:
        """A paragraph counts if it carries text, a rich link, or an inline image.

        Rich-link-only paragraphs must count both before and after scrubbing, otherwise
        turning a link chip into placeholder text would look like a structural change.
        """
        for element in paragraph.get("elements") or []:
            if (element.get("textRun") or {}).get("content", "").strip():
                return True
            if element.get("richLink") or element.get("inlineObjectElement"):
                return True
        return False

    for tab_id, tab in iter_tabs(document):
        for kind, segment_id, content in _segments_of_tab(tab_id, tab):
            for element in content or []:
                if "table" in element:
                    table = element["table"]
                    tables.append(f"{table.get('rows')}x{table.get('columns')}")
            for paragraph, _path in _iter_structural(content, kind):
                if not has_content(paragraph):
                    continue
                styles.append((paragraph.get("paragraphStyle") or {}).get("namedStyleType", ""))
                if paragraph.get("bullet"):
                    bullets += 1
    return {
        "paragraph_styles": styles,
        "paragraph_count": len(styles),
        "bullet_count": bullets,
        "tables": tables,
        "tab_count": len(list(iter_tabs(document))),
    }


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


@dataclass
class Detection:
    rule: ReplacementRule
    occurrences: int
    locations: list[str] = field(default_factory=list)
    samples: list[str] = field(default_factory=list)


def detect_client_facts(document: dict, manifest: ScrubManifest) -> list[Detection]:
    """Count every manifest rule against all text, link URLs, titles, and alt text."""
    segments = list(iter_text_segments(document))
    links = list(iter_link_targets(document))

    detections: list[Detection] = []
    for rule in manifest.sorted_rules():
        total = 0
        locations: list[str] = []
        samples: list[str] = []
        for segment in segments:
            hits = rule.occurrences(segment.text)
            if hits:
                total += hits
                where = f"{segment.segment_kind}:{segment.path}"
                if where not in locations:
                    locations.append(where)
                if len(samples) < 2:
                    samples.append(segment.text.strip()[:160])
        for link in links:
            haystack = " ".join([link.url, link.title, link.description])
            hits = rule.occurrences(haystack)
            if hits:
                total += hits
                where = f"{link.segment_kind}:{link.kind}"
                if where not in locations:
                    locations.append(where)
        if total:
            detections.append(
                Detection(rule=rule, occurrences=total, locations=locations, samples=samples)
            )

    # Image links are replaced by range operations rather than by text rules, so they must
    # be reported here too or the manifest summary would understate what is being changed.
    for url, placeholder in manifest.link_replacements.items():
        hits = [link for link in links if link.url == url]
        if not hits:
            continue
        detections.append(
            Detection(
                rule=ReplacementRule(
                    find=url, replace=placeholder, category="image_link",
                    note="Replaced by a range operation, not by replaceAllText.",
                ),
                occurrences=len(hits),
                locations=sorted({f"{h.segment_kind}:{h.kind}" for h in hits}),
                samples=[h.title for h in hits if h.title][:2],
            )
        )
    return detections


def unmatched_rules(document: dict, manifest: ScrubManifest) -> list[ReplacementRule]:
    found = {d.rule.find for d in detect_client_facts(document, manifest)}
    return [rule for rule in manifest.sorted_rules() if rule.find not in found]


# ---------------------------------------------------------------------------
# Request building
# ---------------------------------------------------------------------------


def build_text_requests(manifest: ScrubManifest) -> list[dict]:
    """replaceAllText requests, longest match first, applied across every tab and segment."""
    return [
        {
            "replaceAllText": {
                "containsText": {"text": rule.find, "matchCase": rule.match_case},
                "replaceText": rule.replace,
            }
        }
        for rule in manifest.sorted_rules()
    ]


def build_link_requests(document: dict, manifest: ScrubManifest) -> list[dict]:
    """Range operations for rich links and hyperlinks, emitted in descending index order.

    replaceAllText cannot touch a rich-link chip or a link URL, so each is deleted and
    replaced with its placeholder text. Descending order keeps earlier indices valid.
    """
    targets = [
        target
        for target in iter_link_targets(document)
        if target.kind in {"richLink", "hyperlink"} and target.url
    ]
    targets.sort(key=lambda t: t.start_index, reverse=True)

    requests: list[dict] = []
    for target in targets:
        placeholder = manifest.link_replacements.get(target.url)
        if placeholder is None:
            continue
        requests.append(
            {"deleteContentRange": {"range": {"startIndex": target.start_index, "endIndex": target.end_index}}}
        )
        requests.append(
            {"insertText": {"location": {"index": target.start_index}, "text": placeholder}}
        )
    return requests


@dataclass
class ScrubPlan:
    document_id: str | None
    link_batch: list[dict] = field(default_factory=list)
    text_batch: list[dict] = field(default_factory=list)
    detections: list[Detection] = field(default_factory=list)
    unmatched: list[ReplacementRule] = field(default_factory=list)

    @property
    def total_requests(self) -> int:
        return len(self.link_batch) + len(self.text_batch)

    def summary(self) -> dict[str, int]:
        return {
            "link_requests": len(self.link_batch),
            "text_requests": len(self.text_batch),
            "detected_rules": len(self.detections),
            "detected_occurrences": sum(d.occurrences for d in self.detections),
            "unmatched_rules": len(self.unmatched),
        }


def plan_scrub(document: dict, manifest: ScrubManifest, document_id: str | None = None) -> ScrubPlan:
    """Build the full scrub plan. Read-only: issues no API call and mutates nothing."""
    return ScrubPlan(
        document_id=document_id,
        link_batch=build_link_requests(document, manifest),
        text_batch=build_text_requests(manifest),
        detections=detect_client_facts(document, manifest),
        unmatched=unmatched_rules(document, manifest),
    )


def simulate_scrub(document: dict, manifest: ScrubManifest) -> dict:
    """Apply the manifest to an in-memory copy of a document. Issues no API call.

    This mirrors what the two batches would do on the server so the scrub can be proven to
    reach zero residue before any Drive write happens. Rich links and hyperlinks become
    plain placeholder text, then rules are applied longest-find-first over the joined
    paragraph text, matching ``replaceAllText`` semantics across run boundaries.
    """
    import copy as _copy

    result = _copy.deepcopy(document)
    rules = manifest.sorted_rules()

    def scrub_paragraph(paragraph: dict) -> None:
        elements = paragraph.get("elements") or []
        pieces: list[str] = []
        for element in elements:
            rich = element.get("richLink")
            if rich:
                url = (rich.get("richLinkProperties") or {}).get("uri", "")
                pieces.append(manifest.link_replacements.get(url, url))
                continue
            text_run = element.get("textRun")
            if text_run:
                content = text_run.get("content", "")
                link = (text_run.get("textStyle") or {}).get("link") or {}
                url = link.get("url")
                if url and url in manifest.link_replacements:
                    trailing = "".join(c for c in content if c in "\n\v")
                    pieces.append(manifest.link_replacements[url] + trailing)
                else:
                    pieces.append(content)

        joined = "".join(pieces)
        for rule in rules:
            if rule.match_case:
                joined = joined.replace(rule.find, rule.replace)
            else:
                joined = re.sub(re.escape(rule.find), rule.replace, joined, flags=re.IGNORECASE)

        new_elements: list[dict] = []
        placed = False
        for element in elements:
            if element.get("richLink"):
                continue
            if element.get("textRun"):
                if not placed:
                    element = _copy.deepcopy(element)
                    element["textRun"]["content"] = joined
                    style = element["textRun"].get("textStyle") or {}
                    style.pop("link", None)
                    element["textRun"]["textStyle"] = style
                    placed = True
                    new_elements.append(element)
                continue
            new_elements.append(element)
        if not placed and joined:
            new_elements.insert(0, {"textRun": {"content": joined, "textStyle": {}}})
        paragraph["elements"] = new_elements

    for _tab_id, tab in iter_tabs(result):
        for _kind, _segment_id, content in _segments_of_tab(_tab_id, tab):
            for paragraph, _path in _iter_structural(content, _kind):
                scrub_paragraph(paragraph)

    return result


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@dataclass
class Violation:
    term: str
    where: str
    sample: str


def validate_scrubbed(document: dict, forbidden_terms: list[str]) -> list[Violation]:
    """Find any surviving source-client fact in text, link URLs, titles, or alt text."""
    violations: list[Violation] = []
    segments = list(iter_text_segments(document))
    links = list(iter_link_targets(document))

    for term in forbidden_terms:
        if not term.strip():
            continue
        needle = term.casefold()
        for segment in segments:
            if needle in segment.text.casefold():
                violations.append(
                    Violation(term, f"{segment.segment_kind}:{segment.path}", segment.text.strip()[:160])
                )
        for link in links:
            haystack = " ".join([link.url, link.title, link.description]).casefold()
            if needle in haystack:
                violations.append(
                    Violation(term, f"{link.segment_kind}:{link.kind}", link.url or link.title)
                )
    return violations


def assert_structure_preserved(before: dict[str, Any], after: dict[str, Any]) -> None:
    """Fail if scrubbing changed headings, section order, list counts, tables, or tabs."""
    for key in ("paragraph_styles", "paragraph_count", "bullet_count", "tables", "tab_count"):
        if before.get(key) != after.get(key):
            raise ScrubValidationError(
                f"Document structure changed during scrubbing: {key} differs. "
                "The copy must retain the canonical structure exactly."
            )
