# Ambient Cooling - Live (2401959466) — 2026-09-10 session D — Commercial HVAC build

**Identity gate:** PASS before the write — `Ambient Cooling - Live`, 2401959466, non-manager,
non-test, America/New_York, USD, Green Marketing 3373711342 ACTIVE, ClickCease 2815082755 ACTIVE.

**Mutations executed: 3** (one package). Local Services Ads are out of scope and are not
analysed anywhere in this report.

---

## 1. Created

### `AMB-0910-COMM-1` · `A9173FADBA82` · 3 operations · EXECUTED

Fingerprint recomputed from the on-disk plan and matched `A9173FADBA82` before the write.
`EXECUTED_OK: 3 results returned` · one atomic mutate · `partial_failure=False`.

| Resource | ID | State |
|---|---|---|
| Ad group `SKAG \| Commercial HVAC Installation` | **199748801029** | **PAUSED**, SEARCH_STANDARD, cpc_bid 10000 |
| Keyword `"commercial hvac installation"` | — | PHRASE, ENABLED |
| Keyword `[commercial hvac installation]` | — | EXACT, ENABLED |

Created inside existing campaign 24132507747. **No separate campaign.** No Broad keyword.
Zero ads. Zero ad-group negatives.

### Readback — 0 FAIL

Campaign 24132507747 now holds 2 ad groups: the new one (PAUSED, 0 ads, 2 keywords, 0
negatives) and residential 202339087634 (ENABLED, retaining ads 821319509197 and 821319509200
ENABLED+APPROVED, unedited).

**Unrelated resources verified unchanged:** campaigns 23 · ad groups **69** (68 + the one
created, expected) · geo criteria 375 on the five · IP blocks 2,796 · shared sets 17 ·
conversion actions 16 · campaign negatives on the five 6,158 · account-level negatives 271 ·
ClickCease tracking template intact · all five ENABLED, PRESENCE geo, Search Partners off,
Display off.

**CPC ceilings preserved:** AC Repair $25 · Gas Boiler $25 · HVAC Installation $30 · HVAC
Repair $25 · HVAC Replacement $30.
**Budgets preserved:** $421.55/day × 30.4 = **$12,815.12**, headroom **$184.88**.

Keywords are `UNDER_REVIEW`, which is normal for newly created criteria.

---

## 2. Phone configuration — resolved before touching anything

Measured from 272 WhatConverts lead records and the live Google Ads asset graph. **No
WhatConverts configuration was changed.**

| Number | Role (measured) | Evidence |
|---|---|---|
| **(410) 705-6354** | **Tracking number for `google` paid traffic** | 11 leads, all `lead_source=google` (cpc 6, organic 5). Also the single Google Ads CALL asset **407995613637** linked to all five campaigns |
| (410) 761-0932 | **DESTINATION** — the line every tracking number rings to | Appears as `destination_number` on **233** leads. Never a tracking number |
| **(410) 914-1456** | **A real tracking number — but mixed-source** | 12 leads: `google` 4, `GBP` 4, `(direct)` 3, site referral 1. Routes correctly to 410-761-0932 |

Other tracking numbers: 410-449-4021 (2nd GBP Traffic, 119) · 410-429-7280 (GBP Traffic, 66) ·
410-429-7756 (LSA Severn, 40) · 410-498-4240 · 410-513-9803.

### Verdict on (410) 914-1456

It is **not rogue** — it is intentionally configured and routes correctly. But it is **not a
paid-source number**: it collects GBP, direct and organic calls too. Hard-coding it on a paid
landing page pollutes paid call attribution. It currently sits as `tel:+14109141456` "Call Now"
on all five existing paid pages — a defect to fix there and not to reproduce on the commercial
page.

**Per your instruction it is treated as unapproved as the static paid-page number, and it is
not used anywhere in this build.** Routing is untouched.

### One discrepancy to confirm

You specified WhatConverts profile **"GSA Cooling Traffic"**. **No profile by that name is
visible on this login.** The only profile carrying Ambient leads is **"Ambient Cooling &
Heating" (profile_id 105803)**. The `/accounts` endpoint also lists unrelated clients (Pristine
Lawn Care, JT's, Emerald Oasis, Perfect Edge, Greenway), which were not touched.
`/profiles` returns HTTP 400 with and without `account_id`; `tracking-numbers`, `phone-numbers`
and `numbers` all return 404 — so number roles were derived from lead records instead.

Please confirm the intended profile name before any routing change is proposed.

---

## 3. Launch pack — read in full

Located at the repo root rather than `handoffs/…`; copied into the expected folder with a
SHA-256 manifest. Originals left in place.

```
handoffs/ambient-commercial-hvac-installation-2026-09-10/
  DEVELOPER_HANDOFF.md
  MANIFEST.json
  source/  Ambient_Commercial_HVAC_Installation_Launch_Pack.docx (1,503,462 B)
           CLAUDE_CODE_MASTER_PROMPT.md (16,053 B)
           COMMERCIAL_HVAC_COPY_PASTE.txt (5,255 B)
  images/  ambient-commercial-rooftop-hvac-installation-1200x628.jpg
           ambient-commercial-ground-unit-installation-1200x628.jpg
           ambient-commercial-mechanical-room-1200x1200.jpg
           ambient-commercial-rtu-ductwork-1200x1200.jpg
```

All 427 lines of the docx and all 211 lines of the copy-paste file were read. The four images
are **illustrative generated imagery** and the handoff forbids presenting them as completed
Ambient projects, including in alt text.

---

## 4. Landing page — still 404

`https://offer.ambientcoolingandheating.com/commercial-hvac-installation/` re-checked at the
end of this session: **HTTP 404**, title `404 Not Found | Ambient Cooling & Heating`.

The developer handoff is complete and covers: the phone-number rules above, the pack copy
verbatim, image usage limits, the required form fields, **unique DOM IDs** (the five existing
pages each render `gform_1` three times with 30+ tripled child IDs), GTM-PQTPQ436, WhatConverts,
**GCLID/GBRAID/WBRAID/UTM capture and persistence**, one conversion per submission, canonical,
Privacy and Terms links, and ten acceptance tests.

It also records the two standing blockers: **no approved non-production/test path exists**, so
form-submission and one-conversion-per-submit verification cannot be run without creating a real
lead and a real conversion; and **no Privacy or Terms link exists on any of the five current
paid pages** (the offer subdomain does have a Privacy Policy page — it appears in the 404 page
navigation — so this is a linking gap, not a missing document).

---

## 5. Negatives — conflict-tested, and one judgement call

Conflict testing against the pack's 22 BROAD ad-group negatives:

| Test | Result |
|---|---|
| Falls in a barred category (free, quote, estimate, cost, pricing, building, property manager, repair, maintenance) | **NONE** |
| Blocks the positive keyword `commercial hvac installation` | **NONE** |
| Blocks any converting search term (97 terms examined, 10 with conversions, 2026-06-01→09-09) | **NONE** |
| Equals one of the 75 targeted location names | **NONE** |
| Equals a supported manufacturer (20-name list) | **NONE** |

**But four of them can block genuine commercial buyers**, which the mechanical tests cannot
see. With PHRASE `commercial hvac installation` live, a query like *"commercial hvac
installation for schools"* **does** match — and would then be blocked:

| Term | Risk | Why |
|---|---|---|
| `school`, `schools` | **HIGH** | Schools and school districts are major commercial HVAC buyers |
| `rent`, `rental` | **HIGH** | Property managers run rental buildings — and the pack itself says to preserve `property manager` |
| `training`, `house`, `job`, `jobs` | MEDIUM | "training facility", "house of worship", "job site" are real commercial language, but non-buyer intent dominates. Shipping these. *(Note `warehouse` is a single token and is unaffected by a `house` negative.)* |

**Recommendation: `AMB-0910-COMM-NEG-1` `C4142D5D5DE0` — 18 of the 22 terms.** Holding four
back is still "only negatives from the supplied pack" — a subset, not an addition — and it is
the reversible direction: a missing negative can be added later from search-term evidence,
while a shipped negative silently destroys demand you never see.

The verbatim 22-term alternative is drafted as `AMB-0910-COMM-NEG-1-FULL` `A774B9C14896`, for
use only if schools and rental/managed properties are deliberately out of commercial scope.

---

## 6. RSAs — resupplied from the pack

`AMB-0910-COMM-RSA-1` `30312BC45992` is **SUPERSEDED · DO_NOT_EXECUTE.** It was drafted before
the pack was located and had three defects: agency-draft copy instead of the pack copy (RSA A's
third pin was "Commercial HVAC in Maryland" rather than the pack's "HVAC Installation for
Business"); `path2` of `maryland`/`install` instead of `installation`; and it addressed the ad
group by name because it did not exist yet.

**`AMB-0910-COMM-RSA-2` · `41C183D15C93` · 2 operations · create-PAUSED · GATED.** Pack copy
verbatim, ad group **199748801029** by ID, paths `commercial-hvac` / `installation`.

- **RSA A** — pinned to HEADLINE_1: *Commercial HVAC Installation* (28) · *Commercial HVAC
  Installers* (26) · *HVAC Installation for Business* (30). Plus 12 unpinned, 4 descriptions.
- **RSA B** — 15 unpinned headlines, 4 descriptions, as the relevance/automation control.

All 30 headlines ≤30 chars, all 8 descriptions ≤90, zero duplicates, claim check **PASS** — no
Licensed & Insured, emergency, 24/7, financing, rebates, guarantees or #1.

Two RSAs in one ad group is **not** an evenly allocated A/B test; Google allocates unevenly and
a true test needs Experiments. No CTR, CPC, conversion or CPQL improvement is claimed.

---

## 7. Consolidated approval block

| Plan | Fingerprint | Ops | Status |
|---|---|---|---|
| `AMB-0910-COMM-NEG-1` | `C4142D5D5DE0` | 18 | **VALIDATED_OK — ready. RECOMMENDED** |
| `AMB-0910-COMM-NEG-1-FULL` | `A774B9C14896` | 22 | alternative, not recommended |
| `AMB-0910-RSA-ACR-2` | `1F166DE17017` | 1 | ready — AC Repair challenger, create-paused |
| `AMB-0910-COMM-RSA-2` | `41C183D15C93` | 2 | **GATED** — landing page is 404 |
| `AMB-0910-COMM-XNEG-1` | `A70260017DAD` | 1 | **GATED** — commercial group must serve first |

**Exact next approval line:**

```
APPROVE AMB-0910-COMM-NEG-1 C4142D5D5DE0 18 operations FOR 2401959466
```

Safe to run now: the ad group is PAUSED with no ads, so the negatives cannot affect delivery.

### Do not execute

`AMB-0909C-CPC-INST-2 5D57E0EF3B70` REJECTED · `AMB-0910-RSA-ACR-1 19E2F2FFC311` SUPERSEDED ·
`AMB-0910-COMM-RSA-1 30312BC45992` SUPERSEDED · `46C39C6B7091` · `D448BFDE4650` ·
`23BE8FF0F24C` · `CE289F3508A2` · `A435FA09AC97` · `DE376F91F449`

---

## 8. Still gated

1. **Commercial landing page 404** — blocks `41C183D15C93` and enabling the ad group.
2. **No approved test path** — blocks one-conversion-per-submission verification.
3. **Commercial ad group not serving** — blocks `A70260017DAD`.
4. **WhatConverts profile name discrepancy** — "GSA Cooling Traffic" not found.
5. **Claude in Chrome not connected** — the six-ad policy appeal and the August Auction
   Insights exports remain outstanding from session C.

## Evidence

```
receipts/live/AMB-0910-COMM-1-2026-09-10-EXECUTED.json
receipts/validate-only/AMB-0910-COMM-NEG-1-2026-09-10.json
reports/ambient-cooling-heating/evidence/
  2026-09-10d-comm1-readback.json           readback, 0 FAIL
  2026-09-10d-phone-configuration.json      number roles + Google Ads call assets
  2026-09-10d-number-source-map.json        tracking number x traffic source
  2026-09-10d-commercial-neg-and-rsa.json   conflict tests + drafts
handoffs/ambient-commercial-hvac-installation-2026-09-10/
  DEVELOPER_HANDOFF.md · MANIFEST.json · source/ · images/
```

No credential, token, secret, or unredacted lead PII appears in any artifact.
