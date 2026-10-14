"""The one safe sequence that turns the canonical client example into the master template.

This module is the ONLY place in the repository that copies a Google Doc. The destination
name of that copy is hard-coded to ``TEMP_SCRUB_NAME``, so an unscrubbed document can never
exist under the final master name. The final name is reached only by renaming a copy that
has already been re-read from the API and passed both validations.

Apply sequence, each step gated by the one before it:

  1. Reuse or create ``Green Marketing Landing Pages`` (exact name, stop on duplicates).
  2. Reuse or create ``Templates`` under that root (exact name, stop on duplicates).
  3. Copy the canonical document into Templates as ``TEMP - Master Template Scrub In Progress``.
  4. Scrub ONLY that copy: the rich-link/hyperlink range batch first, then replaceAllText.
  5. Re-read the copy from the API. The in-memory request list is never trusted as proof.
  6. Confirm zero forbidden source-client facts remain.
  7. Confirm the structural fingerprint still matches the canonical source.
  8. Rename to ``Landing Page Content Template - Master`` only after 6 and 7 both pass.
  9. Record the verified root folder ID and master document ID in config/google-drive.yaml.

Idempotency and refusal rules:

- A validated final master that already exists is reused; nothing is copied or scrubbed.
- A TEMP copy with no final master stops the run. It is reported, never re-copied over,
  never renamed sight unseen, and never deleted.
- Duplicate root folders, Templates folders, TEMP copies, or master documents stop the run.
- No failure path deletes, trashes, moves, shares, or re-permissions anything. A partial run
  leaves the TEMP copy in place under its TEMP name and reports its ID and URL.
- The canonical document is read-only throughout. It is only ever fetched and copied FROM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .google_drive import (
    DOCUMENT_MIME_TYPE,
    FOLDER_MIME_TYPE,
    MASTER_TEMPLATE_NAME,
    MY_DRIVE_ROOT,
    TEMP_SCRUB_NAME,
    DriveError,
    DriveSettings,
    PartialWriteError,
    apply_plan,
    assert_not_unscrubbed_master,
    drive_url,
    plan_landing_page_drive,
    read_back,
    record_verified_ids,
    resolve_unique_child,
)
from .template_scrub import (
    ScrubManifest,
    ScrubValidationError,
    assert_structure_preserved,
    assert_writable_target,
    document_structure_fingerprint,
    guarded_batch_update,
    guarded_rename,
    plan_scrub,
    validate_scrubbed,
)

# Plan statuses.
STATUS_CREATE_MASTER = "create_master"
STATUS_REUSE_MASTER = "reuse_master"
STATUS_BLOCKED_TEMP_EXISTS = "blocked_temp_exists"


class MasterTemplateBlockedError(DriveError):
    """Raised when the pipeline must stop for human review instead of writing."""


@dataclass
class PipelineStep:
    """One line of the sequence, printable in a dry run and executed in the same order."""

    key: str
    action: str  # create | reuse | copy | scrub | validate | rename | record | stop | skip
    target: str
    detail: str
    existing_id: str | None = None
    existing_url: str | None = None

    def as_row(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "action": self.action,
            "target": self.target,
            "detail": self.detail,
            "existing_id": self.existing_id,
            "url": self.existing_url,
        }


@dataclass
class MasterTemplatePlan:
    status: str
    steps: list[PipelineStep] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    folder_plan: Any = None
    root_id: str | None = None
    templates_id: str | None = None
    final_master_id: str | None = None
    temp_id: str | None = None

    @property
    def blocked(self) -> bool:
        return self.status == STATUS_BLOCKED_TEMP_EXISTS

    @property
    def will_write(self) -> bool:
        """True when applying this plan would create, modify, or rename anything."""
        return any(
            step.action in {"create", "copy", "scrub", "rename", "record"} for step in self.steps
        )

    def summary(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "steps": len(self.steps),
            "creates": len([s for s in self.steps if s.action in {"create", "copy"}]),
            "reuses": len([s for s in self.steps if s.action == "reuse"]),
            "blocked": self.blocked,
        }


# ---------------------------------------------------------------------------
# Planning (read-only)
# ---------------------------------------------------------------------------


def plan_master_template(drive_service: Any, settings: DriveSettings) -> MasterTemplatePlan:
    """Read-only plan for the full sequence. Issues lookups only; writes nothing.

    Duplicate exact-name matches raise ``DriveAmbiguityError`` out of
    ``resolve_unique_child`` rather than being guessed at.
    """
    folder_plan = plan_landing_page_drive(drive_service, settings)
    by_key = {resource.key: resource for resource in folder_plan.resources}
    root = by_key["root"]
    templates = by_key["templates"]

    steps: list[PipelineStep] = [
        PipelineStep(
            key="root",
            action=root.action,
            target=settings.root_folder_name,
            detail=(
                "Exact-name match under My Drive."
                if root.action != "reuse"
                else "Exact existing root folder is reused; nothing is created."
            ),
            existing_id=root.existing_id,
            existing_url=root.existing_url,
        ),
        PipelineStep(
            key="templates",
            action=templates.action,
            target=settings.templates_folder_name,
            detail=(
                f"Exact-name match under {settings.root_folder_name!r}."
                if templates.action != "reuse"
                else "Exact existing Templates folder is reused; nothing is created."
            ),
            existing_id=templates.existing_id,
            existing_url=templates.existing_url,
        ),
    ]

    plan = MasterTemplatePlan(
        status=STATUS_CREATE_MASTER,
        steps=steps,
        notes=list(folder_plan.notes),
        folder_plan=folder_plan,
        root_id=root.existing_id,
        templates_id=templates.existing_id,
    )

    existing_master: dict[str, Any] | None = None
    existing_temp: dict[str, Any] | None = None
    if templates.existing_id:
        existing_master = resolve_unique_child(
            drive_service, templates.existing_id, MASTER_TEMPLATE_NAME, DOCUMENT_MIME_TYPE
        )
        existing_temp = resolve_unique_child(
            drive_service, templates.existing_id, TEMP_SCRUB_NAME, DOCUMENT_MIME_TYPE
        )

    if existing_master:
        plan.status = STATUS_REUSE_MASTER
        plan.final_master_id = str(existing_master["id"])
        steps.append(
            PipelineStep(
                key="master_template",
                action="reuse",
                target=MASTER_TEMPLATE_NAME,
                detail=(
                    "A validated master already exists. No copy, no scrub, no rename. "
                    "The canonical document is not read for writing."
                ),
                existing_id=plan.final_master_id,
                existing_url=drive_url(plan.final_master_id, DOCUMENT_MIME_TYPE),
            )
        )
        if existing_temp:
            plan.temp_id = str(existing_temp["id"])
            plan.notes.append(
                f"A leftover {TEMP_SCRUB_NAME!r} copy also exists (ID {plan.temp_id}, "
                f"{drive_url(plan.temp_id, DOCUMENT_MIME_TYPE)}). It is reported for manual "
                "review only. This workflow will not rename, move, share, or delete it."
            )
    elif existing_temp:
        plan.status = STATUS_BLOCKED_TEMP_EXISTS
        plan.temp_id = str(existing_temp["id"])
        steps.append(
            PipelineStep(
                key="master_template",
                action="stop",
                target=TEMP_SCRUB_NAME,
                detail=(
                    "A TEMP copy exists with no validated master. A previous run stopped "
                    "part-way. Review that document by hand before anything else happens; "
                    "a second TEMP copy is never created blindly."
                ),
                existing_id=plan.temp_id,
                existing_url=drive_url(plan.temp_id, DOCUMENT_MIME_TYPE),
            )
        )
        plan.notes.append(
            f"BLOCKED: {TEMP_SCRUB_NAME!r} exists (ID {plan.temp_id}). Nothing will be "
            "copied, scrubbed, renamed, moved, or deleted until a person reviews it."
        )
    else:
        canonical = settings.canonical_source_template_id
        steps.extend(
            [
                PipelineStep(
                    key="copy_temp",
                    action="copy",
                    target=TEMP_SCRUB_NAME,
                    detail=(
                        f"files.copy FROM canonical {canonical} INTO Templates. The "
                        "destination name is hard-coded to the TEMP name. The canonical "
                        "document is a copy source only and is never modified."
                    ),
                ),
                PipelineStep(
                    key="scrub",
                    action="scrub",
                    target=TEMP_SCRUB_NAME,
                    detail=(
                        "documents.batchUpdate on the TEMP copy only: link/rich-link range "
                        "batch first, then the replaceAllText batch."
                    ),
                ),
                PipelineStep(
                    key="reread",
                    action="validate",
                    target=TEMP_SCRUB_NAME,
                    detail="Re-read the TEMP copy from the Docs API. Request lists are not proof.",
                ),
                PipelineStep(
                    key="validate_content",
                    action="validate",
                    target=TEMP_SCRUB_NAME,
                    detail=(
                        "Confirm zero forbidden Ambient Cooling & Heating facts remain. "
                        "Any residue stops the run before the rename."
                    ),
                ),
                PipelineStep(
                    key="validate_structure",
                    action="validate",
                    target=TEMP_SCRUB_NAME,
                    detail=(
                        "Confirm the structural fingerprint (tabs, paragraph styles, "
                        "bullets, tables) matches the canonical source exactly."
                    ),
                ),
                PipelineStep(
                    key="rename",
                    action="rename",
                    target=MASTER_TEMPLATE_NAME,
                    detail=(
                        "Rename TEMP to the final master name. This is the only way the "
                        "final name can ever be reached, and it runs only after both "
                        "validations pass."
                    ),
                ),
                PipelineStep(
                    key="record_ids",
                    action="record",
                    target="config/google-drive.yaml",
                    detail=(
                        "Record landing_page_root_folder_id and master_template_document_id. "
                        "Non-secret Drive IDs only, written only after validation succeeds."
                    ),
                ),
            ]
        )
    return plan


# ---------------------------------------------------------------------------
# Applying
# ---------------------------------------------------------------------------


def _fetch_document(docs_service: Any, document_id: str) -> dict[str, Any]:
    """Read-only Docs fetch. Used for the canonical source and for the TEMP copy."""
    return (
        docs_service.documents()
        .get(documentId=document_id, includeTabsContent=True)
        .execute()
    )


def copy_canonical_to_temp(
    drive_service: Any, canonical_id: str, templates_folder_id: str
) -> dict[str, Any]:
    """The only files.copy in this repository. Its destination name cannot be overridden.

    ``assert_writable_target`` is deliberately applied to the *destination folder*, not to
    the canonical ID: ``files.copy`` reads the source and writes a new file, so guarding the
    source ID here would only ever produce a false failure.
    """
    assert_not_unscrubbed_master(TEMP_SCRUB_NAME, "files.copy")
    assert_writable_target(templates_folder_id, "files.copy:destination")
    return (
        drive_service.files()
        .copy(
            fileId=canonical_id,
            body={"name": TEMP_SCRUB_NAME, "parents": [templates_folder_id]},
            fields="id, name, mimeType, parents, trashed",
            supportsAllDrives=True,
        )
        .execute()
    )


def apply_master_template(
    drive_service: Any,
    docs_service: Any,
    settings: DriveSettings,
    manifest: ScrubManifest,
    plan: MasterTemplatePlan,
    *,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Execute the planned sequence. The only function here that writes to Drive or Docs.

    Raises ``MasterTemplateBlockedError`` when the plan says stop, and ``PartialWriteError``
    carrying a full inventory when a step fails after something was already created.
    """
    if plan.blocked:
        raise MasterTemplateBlockedError(
            f"Refusing to apply: {TEMP_SCRUB_NAME!r} already exists (ID {plan.temp_id}, "
            f"{drive_url(str(plan.temp_id), DOCUMENT_MIME_TYPE)}) with no validated master. "
            "Review it by hand. Nothing was copied, scrubbed, renamed, moved, or deleted."
        )

    canonical_id = settings.canonical_source_template_id
    if manifest.source_document_id != canonical_id:
        raise ScrubValidationError(
            "The scrub manifest's source_document_id does not match the configured canonical "
            "template ID. Refusing to scrub against a mismatched manifest."
        )

    created: list[dict[str, Any]] = []
    report: dict[str, Any] = {"status": plan.status, "created": created, "steps": []}

    def note(key: str, outcome: str, **extra: Any) -> None:
        report["steps"].append({"key": key, "outcome": outcome, **extra})

    # --- Steps 1 and 2: folders. apply_plan creates folders only and inventories failures.
    try:
        folder_results = apply_plan(drive_service, plan.folder_plan)
    except PartialWriteError as exc:
        created.extend(exc.inventory())
        raise PartialWriteError(str(exc), created, exc.failed_key) from exc

    resolved = {item["key"]: str(item["id"]) for item in folder_results}
    created.extend([item for item in folder_results if item["status"] == "created"])
    root_id = resolved["root"]
    templates_id = resolved["templates"]
    note("root", next(r["status"] for r in folder_results if r["key"] == "root"), id=root_id)
    note(
        "templates",
        next(r["status"] for r in folder_results if r["key"] == "templates"),
        id=templates_id,
    )

    if plan.status == STATUS_REUSE_MASTER:
        master_id = str(plan.final_master_id)
        note("master_template", "reused", id=master_id)
    else:
        try:
            master_id = _create_validated_master(
                drive_service,
                docs_service,
                settings,
                manifest,
                templates_id=templates_id,
                created=created,
                note=note,
            )
        except MasterTemplateBlockedError:
            # A blocked run that already created folders must still hand back an inventory,
            # otherwise those folders would be invisible to whoever reviews the failure.
            if created:
                raise PartialWriteError(
                    f"Stopped for review before copying. {TEMP_SCRUB_NAME!r} or "
                    f"{MASTER_TEMPLATE_NAME!r} appeared in Templates after planning.",
                    created,
                    "copy_temp",
                ) from None
            raise

    # --- Step 9: record the two verified, non-secret IDs.
    try:
        recorded = record_verified_ids(root_id, master_id, config_path=config_path)
    except Exception as exc:  # noqa: BLE001 - re-raised with the full inventory
        raise PartialWriteError(
            f"The master template is valid but recording its IDs failed: {exc}",
            created,
            "record_ids",
        ) from exc
    note("record_ids", "recorded", **recorded)

    report["root_folder_id"] = root_id
    report["master_template_document_id"] = master_id
    report["master_template_url"] = drive_url(master_id, DOCUMENT_MIME_TYPE)
    return report


def _create_validated_master(
    drive_service: Any,
    docs_service: Any,
    settings: DriveSettings,
    manifest: ScrubManifest,
    *,
    templates_id: str,
    created: list[dict[str, Any]],
    note: Any,
) -> str:
    """Steps 3-8: copy to TEMP, scrub, re-read, validate twice, then rename."""
    canonical_id = settings.canonical_source_template_id

    # Re-check immediately before writing. Planning may be minutes old, and a second TEMP
    # copy must never be created because a stale plan said the folder was empty.
    for name in (MASTER_TEMPLATE_NAME, TEMP_SCRUB_NAME):
        existing = resolve_unique_child(drive_service, templates_id, name, DOCUMENT_MIME_TYPE)
        if existing:
            raise MasterTemplateBlockedError(
                f"{name!r} appeared in Templates since the plan was built (ID "
                f"{existing['id']}). Stopping without copying. Review it by hand."
            )

    # Read the canonical document once, read-only, for the structural baseline.
    try:
        canonical = _fetch_document(docs_service, canonical_id)
        canonical_fingerprint = document_structure_fingerprint(canonical)
    except Exception as exc:  # noqa: BLE001 - re-raised with the folder inventory
        raise PartialWriteError(
            f"Could not read the canonical source: {exc}", created, "canonical_read"
        ) from exc

    try:
        copied = copy_canonical_to_temp(drive_service, canonical_id, templates_id)
    except Exception as exc:  # noqa: BLE001 - re-raised with the folder inventory
        raise PartialWriteError(
            f"The copy to {TEMP_SCRUB_NAME!r} failed: {exc}", created, "copy_temp"
        ) from exc

    temp_id = str(copied["id"])
    if copied.get("name") != TEMP_SCRUB_NAME:
        raise ScrubValidationError(
            f"The copy was created as {copied.get('name')!r} instead of {TEMP_SCRUB_NAME!r}."
        )
    record = {
        "key": "temp_copy",
        "name": TEMP_SCRUB_NAME,
        "id": temp_id,
        "mimeType": DOCUMENT_MIME_TYPE,
        "parent_id": templates_id,
        "status": "created",
        "url": drive_url(temp_id, DOCUMENT_MIME_TYPE),
    }
    created.append(record)
    note("copy_temp", "created", id=temp_id, name=TEMP_SCRUB_NAME)

    try:
        scrub_plan = plan_scrub(
            _fetch_document(docs_service, temp_id), manifest, document_id=temp_id
        )
        if scrub_plan.link_batch:
            guarded_batch_update(docs_service, temp_id, scrub_plan.link_batch)
        if scrub_plan.text_batch:
            guarded_batch_update(docs_service, temp_id, scrub_plan.text_batch)
        note(
            "scrub",
            "applied",
            link_requests=len(scrub_plan.link_batch),
            text_requests=len(scrub_plan.text_batch),
        )

        scrubbed = _fetch_document(docs_service, temp_id)
        note("reread", "ok", id=temp_id)

        violations = validate_scrubbed(scrubbed, manifest.forbidden_after_scrub)
        if violations:
            raise ScrubValidationError(
                f"{len(violations)} source-client fact(s) survived the scrub, first at "
                f"{violations[0].where}. The copy keeps its TEMP name."
            )
        note("validate_content", "clean", residual=0)

        assert_structure_preserved(
            canonical_fingerprint, document_structure_fingerprint(scrubbed)
        )
        note("validate_structure", "matches_canonical")
    except Exception as exc:  # noqa: BLE001 - re-raised with the TEMP copy inventoried
        raise PartialWriteError(
            f"Validation failed before the rename: {exc}", created, "scrub"
        ) from exc

    renamed = guarded_rename(drive_service, temp_id, MASTER_TEMPLATE_NAME)
    observed = read_back(drive_service, temp_id)
    if observed.get("name") != MASTER_TEMPLATE_NAME:
        raise PartialWriteError(
            f"Readback after the rename shows {observed.get('name')!r}, not "
            f"{MASTER_TEMPLATE_NAME!r}.",
            created,
            "rename",
        )
    record["name"] = MASTER_TEMPLATE_NAME
    record["key"] = "master_template"
    note("rename", "renamed", id=temp_id, name=renamed.get("name") or MASTER_TEMPLATE_NAME)
    return temp_id


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def format_pipeline(plan: MasterTemplatePlan) -> str:
    lines = [f"{'#':<3} {'ACTION':<9} {'TARGET':<46} EXISTING ID", "-" * 100]
    for index, step in enumerate(plan.steps, start=1):
        lines.append(
            f"{index:<3} {step.action:<9} {step.target[:45]:<46} {step.existing_id or '-'}"
        )
        lines.append(f"    {step.detail}")
    return "\n".join(lines)


def expected_new_resources(plan: MasterTemplatePlan, settings: DriveSettings) -> list[str]:
    """Exactly what a future --apply would bring into existence, in order."""
    if plan.blocked:
        return []
    expected: list[str] = []
    for step in plan.steps:
        if step.key == "root" and step.action == "create":
            expected.append(f"Folder: {settings.root_folder_name} (in My Drive)")
        elif step.key == "templates" and step.action == "create":
            expected.append(
                f"Folder: {settings.templates_folder_name} (in {settings.root_folder_name})"
            )
        elif step.key == "copy_temp":
            expected.append(
                f"Google Doc: {TEMP_SCRUB_NAME} (in {settings.templates_folder_name}), "
                f"renamed to {MASTER_TEMPLATE_NAME} after validation"
            )
    return expected


def assert_no_forbidden_operations() -> tuple[str, ...]:
    """The operations this pipeline has no code path for. Used as a documented assertion."""
    return (
        "files.delete",
        "files.trash",
        "files.update:addParents",
        "files.update:removeParents",
        "permissions.create",
        "permissions.update",
        "permissions.delete",
        "files.copy:to-master-name",
        "files.create:document",
    )


__all__ = [
    "DOCUMENT_MIME_TYPE",
    "FOLDER_MIME_TYPE",
    "MASTER_TEMPLATE_NAME",
    "MY_DRIVE_ROOT",
    "STATUS_BLOCKED_TEMP_EXISTS",
    "STATUS_CREATE_MASTER",
    "STATUS_REUSE_MASTER",
    "TEMP_SCRUB_NAME",
    "MasterTemplateBlockedError",
    "MasterTemplatePlan",
    "PipelineStep",
    "apply_master_template",
    "assert_no_forbidden_operations",
    "copy_canonical_to_temp",
    "expected_new_resources",
    "format_pipeline",
    "plan_master_template",
]
