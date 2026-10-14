# 04 — GTM: current state, minimal delta, acceptance cases, blockers

Plan file: `clients/apogee-lawns/plans/APG-0928-GTM-LID.yaml` (**DRAFT, no fingerprint**). No workspace edit, version or
publication was made. Workspace Changes read **0** before and after the view-only browsing.

## Published versus workspace (read 2026-09-28, ≈21:15–21:20 UTC)

| Item | Published v3 (`gtm.js`, SHA-256 prefix 894a8c6178df4a02) | Workspace 5 (current; 0 pending) | Match |
|---|---|---|---|
| Google tag | tag 6, AW-18453077620, Initialization | same | ✓ |
| Form conversion | tag 7, 18453077620 / KOL7CImirvocEPS8jt9E, transaction ID `{{DLV \| lead_id}}`, once per event, no exceptions | same | ✓ |
| Website calls | tag 9, 402-526-5754, lp3jCKf5vPocEPS8jt9E, LP page view | same | ✓ |
| Conversion Linker | tag 10, cross-domain on, no domains, Initialization, Unfiled, edited ≈2 h before the read | same | ✓ |
| Custom-event trigger | event `apg_permanent_lights_lead` (regex off); hostname equals `offer.apogeelawns.com`; path `^/thank-you/permanent-christmas-lights/?$`; `DLV \| lead_id` matches `.+` | same | ✓ |
| LP page-view trigger | hostname + path `^/permanent-christmas-lights-lincoln-ne/?$` | same | ✓ |
| Variable | `DLV \| lead_id` id 4, v2, default "" | same | ✓ |
| Consent | no tag-level consent settings; no consent-default command | same | — |
| Paused tags | none (4 tags in the version = 4 in `gtm.js`) | — | ✓ |

**IDs:** tags 6, 7, 9 and 10 and variable 4 were confirmed in the UI. The custom-event trigger is historical ID 5 (09-17
receipt), name-matched now. The GTM UI does not display trigger IDs, so the ID must be confirmed in the editor before any
edit. The page-view trigger's ID is not recorded anywhere and is not guessed. Historical workspace 3 no longer exists;
creating version 2 consumed it.

## Version history (platform versus repository versus approval)

| Version | Platform observation | Repository record | Approval evidence |
|---|---|---|---|
| 1 "Empty Container" | 2026-09-16, published by the agency login | GTM-K receipt mentions it | n/a (container default) |
| 2 "Apogee \| PPC Tracking \| 2026-09" | created and published 2026-09-17, agency login; content = tags 6, 7, 9 + 2 triggers + DLV | **none** (the GTM-P receipt says 0 publishes; the publication gate was recorded BLOCKED) | **not found** |
| 3 "Add Conversion Linker tag" | created and published 2026-09-28; `gtm.js` Last-Modified 19:38:53 GMT (14:38:53 CDT); only change = tag 10 added | **none** | **not found** |

The agency login is shared, so the person is not identified. Missing repository records are missing evidence, not proof of
unauthorized activity.

## Minimal delta

| # | Change | Before | After | Readiness |
|---|---|---|---|---|
| 1 | Custom-event trigger, condition 3 | `DLV \| lead_id` matches RegEx `.+` | matches RegEx **(ignore case)** `^(?!(?:undefined\|null\|nan\|none\|false\|true\|0\|lead_?id\|entry_?id\|test\|example\|placeholder\|sample)$)[^\s"'<>{}\[\]%]{1,128}$` | **Fully specified.** Format-independent; tested in Python (3 tests) and JavaScript (26 invalid values rejected, 8 valid accepted) |
| 2 | Same condition, format-specific | guard from #1 | the developer's exact format (for example `^[1-9][0-9]{0,11}$` **only** if the ID is a Gravity Forms entry ID) | **Depends on D-Q3** |
| — | Event name, hostname, path, tag 7 ID/label/transaction ID | — | unchanged | Correct as built. **Not widened** to fit the current site |
| — | Conversion Linker tag 10 | — | unchanged | Redundant with the Google tag's linking. No observed issue: one `_gcl_au` cookie, and no link decoration because no domains are listed. Removal is not proposed |

**Why the path is not changed to `/thank-you/`:** that page receives visits the site cannot tie to an accepted lead.
Pointing the trigger there would count page views, not accepted leads.

## GTM acceptance cases (run in Preview after the developer fix)

| Case | Expectation |
|---|---|
| G01 | Tag 6 fires on every page (Initialization) |
| G02 | Tag 7 fires **once** on F01 with `transaction_id` = the accepted entry ID |
| G03 | Tag 7 does **not** fire for F02–F05 or F09, or on `/thank-you/` |
| G04 | Tag 9 loads on the LP only; a non-ad visitor still sees 402-526-5754 |
| G05 | Tag 10 fires at Initialization with no errors; exactly one `_gcl_au` |
| G06 | The workspace diff shows only the condition change(s) above |
| G07 | No new tag, trigger or variable; nothing in the Unfiled folder beyond tag 10 |

## What blocks production QA or publication

1. The developer repair (D1–D5) is not deployed, so tag 7 has nothing to fire on.
2. The ID format (D-Q3) is unknown, so change #2 cannot be finalized. Change #1 can ship before or with it.
3. A publication plan with its own fingerprint and approval, issued only after G01–G07 pass in Preview.

## Consent and administration (observed; no change authorized)

- **Measurement:** no consent settings exist, so every tag fires for every visitor. That is functionally complete for
  measurement.
- **Governance:** GTM's container-quality panel flags "Add another administrator" (fewer than two admins).
- **Owner and legal:** whether a consent banner or consent mode is required for this Nebraska audience is **not
  determined here**. The absence of consent settings is neither a compliance pass nor a proven problem.
