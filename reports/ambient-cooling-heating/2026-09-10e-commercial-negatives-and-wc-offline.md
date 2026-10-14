# Ambient Cooling - Live (2401959466) — 2026-09-10 session E

**Identity gate:** PASS on every read and on the validate-only call.
**Google Ads mutations executed this session: 0.** `AMB-0910-COMM-1 / A9173FADBA82` is treated
as executed and complete; it was not replayed. Ad group **199748801029** remains **PAUSED**.
Local Services Ads are out of scope and appear nowhere in this analysis.

---

## 1. WhatConverts configuration finding

### Configuration of record — now written to `work-order.yaml`

| Field | Value |
|---|---|
| Profile | Ambient Cooling & Heating |
| Profile ID | 105803 |
| Paid tracking number | **410-705-6354** |
| Tracking-number name | **GSA Cooling Traffic** |
| Google Ads call asset | 407995613637 |
| Forwarding destination | 410-761-0932 — never public |
| Mixed-source number | 410-914-1456 — never static on paid pages |
| Routing | **PRESERVE_ALL_CURRENT_ROUTING** — nothing was changed |

> **Correction.** My session-D report stated that no WhatConverts profile named "GSA Cooling
> Traffic" exists. The finding was right but the label was wrong: *GSA Cooling Traffic is the
> name of the tracking number*, not a profile. Corrected in the work order and the handoff.

### Source = Offline — yes, it mislabels paid-search leads, in both directions

Measured across **371 lead records**, 2026-06-01 → 2026-09-10. Read-only; nothing altered.

All 13 leads on 410-705-6354 are calls or texts. **Zero carry a GCLID.**

| Label | n | With GCLID | With landing_url |
|---|---|---|---|
| `google / cpc` | 8 | **0** | **0** |
| `google / organic` | 5 | 0 | **5** |

That split is the proof:

- The 8 `cpc` leads have **no landing URL and no click ID** — there was no web session to read.
  The `cpc` label came from the number's own fixed source configuration, not from the visitor.
- The 5 `organic` leads **do** have a landing URL. Where a session *was* matched, the real
  source won — and it was organic.

Channel control across the whole profile:

| Channel | Leads | With GCLID |
|---|---|---|
| Phone Call / Text Message | 363 | **2 (0.6%)** |
| Web Form | 8 | **6 (75%)** |

The click ID survives to web forms and dies at the call boundary.

**Two failure modes:**

1. **Paid over-credited.** Every call to this number is stamped `google/cpc` regardless of true
   origin. Eight leads carry that label on zero evidence.
2. **Paid under-credited.** Outside the DNI pool, a genuine paid visitor's session is never
   bound to the call, so it can never be joined to a campaign, ad group or keyword.

**Consequence:** CPQL computed from GCLID joins counts only web-form leads, so the qualified-lead
denominator is understated and **every CPQL figure for this account is an upper bound.** The
`cpc` label on those calls cannot be trusted either, so they cannot simply be added back.

**Confidence:** this is inferred from lead-record behaviour, not read from the configuration
object. `/accounts` and `/leads` work; `/profiles` returns HTTP 400, and `tracking-numbers`,
`phone-numbers` and `numbers` all return 404 — there is no readable number-configuration
endpoint on this plan. Confirm on the settings screen before changing anything.

**Change plan drafted, not executed:** `clients/ambient-cooling-heating/plans/WC-0910-OFFLINE-SOURCE-1.md`.
It proposes moving the number from Offline to web-session/DNI, keeps routing untouched, states
that reported paid call volume will likely **fall** at first (a correction, not a regression),
and claims no improvement. It sits outside the Google Ads fingerprint system because no Google
Ads resource changes.

*Related, out of scope:* six enabled conversion actions touch calls, **four of them primary**
(`1068114183 AD_CALL`, `6640721230 Clicks to call`, `6885576934 WEBSITE_CALL`,
`7643656075 WC Calls`). That is a duplication risk against "exactly one conversion per
submission". Flagged for a separate plan; no conversion goal was changed.

---

## 2. Fresh 18-negative package

### `AMB-0910-COMM-NEG-2` · **`A9C9BCBDDD74`** · 18 operations · `VALIDATED_OK`

Exactly the 18 specified BROAD ad-group negatives, on ad group **199748801029 only**:

```
residential  homeowner  house     diy      job     jobs
career       careers    salary    salaries training course
courses      parts      used      wholesale supplier supply
```

**HELD as instructed:** `school` · `schools` · `rent` · `rental`

`VALIDATED_OK — 18 operations, validate_only=True, partial_failure=False`.
Receipt: `receipts/validate-only/AMB-0910-COMM-NEG-2-2026-09-10.json`.

### Conflict testing

| Test | Result |
|---|---|
| Both positive commercial keywords | **clear** |
| Every ENABLED positive keyword in campaign 24132507747 (4) | **clear** |
| All converting search terms, 2026-01-01→09-09 (97 examined, **28** with Primary or All conversions) | **clear** |
| Commercial property-manager intent (5 phrases) | **clear** |
| Institutional buyers — schools, universities, government, church, hospital, training facility, warehouse (8 phrases) | **1 conflict, see below** |
| Ordinary commercial intent (7 phrases) | **clear** |
| Equipment types (6 phrases) | **clear** |
| Manufacturers (6 phrases) | **clear** |
| Duplicates across campaign / ad-group / account / shared-list negatives | see below |

Testing was made **reachability-aware**: a negative only costs anything if the query could
match a positive keyword in the first place. `hvac installation for a training facility` is
blocked by `training` but cannot match PHRASE `commercial hvac installation` anyway, so it is
irrelevant. The reachable case is not.

### One residual risk, reported not overridden

**`training` blocks `commercial hvac installation for a training facility`** — a query that
*does* match the live PHRASE keyword. The 18 terms are specified by the approval owner, so the
package is delivered as specified rather than silently trimmed.

**Action:** monitor the commercial search-term report after launch. If a "training facility" or
"training center" query appears, remove `training` under a new fingerprint.

### The hold is validated by measurement

Holding the four terms preserves **two** buyer phrases that *do* match the live PHRASE keyword:

- `commercial hvac installation for schools` — would have been blocked by `schools`
- `commercial hvac installation for my rental building` — would have been blocked by `rental`

### Duplicate sweep

Of the 18, fifteen already exist as a negative somewhere — but this matters far less than the
raw count suggests:

- **Twelve** exist only in shared sets (10720232972, 11813144900, 12091293463, 12178646912,
  12021721179, 10664304544, 10667314427). **None of those sets is attached to any of the five
  campaigns** — verified, 0 links to 24132507747. They are inert.
- **Three** — `job`, `jobs`, `supplier` — exist as campaign-level **PHRASE** negatives on
  24132507747. For single-token negatives PHRASE and BROAD behave the same, so these three
  ad-group copies are genuinely redundant. Retained anyway so the commercial ad group is
  self-contained and portable.
- **None** of the 18 is on the account-level list 11252984411 (271 members), and `commercial` is
  confirmed absent from it.

**Scope:** ad-group level only. No campaign-level or account-level negative is created.

### Superseded / rejected

| Plan | Fingerprint | Status |
|---|---|---|
| `AMB-0910-COMM-NEG-1` | `C4142D5D5DE0` | **SUPERSEDED** by NEG-2 — same 18 terms, weaker testing |
| `AMB-0910-COMM-NEG-1-FULL` | `A774B9C14896` | **REJECTED — do not execute.** Contained school, schools, rent, rental |

---

## 3. Landing-page build status

`https://offer.ambientcoolingandheating.com/commercial-hvac-installation/` — **HTTP 404.**
Not built. Nothing published.

Developer handoff complete and updated this session at
`handoffs/ambient-commercial-hvac-installation-2026-09-10/` — source pack, four images,
SHA-256 `MANIFEST.json`, and `DEVELOPER_HANDOFF.md`.

Requirements carried into the handoff, matching the gate exactly:

HTTP 200 · **410-705-6354** for every static display and `tel:` link · WhatConverts and
GTM-PQTPQ436 preserved · **Privacy and Terms links** · **unique DOM and form IDs** · **GCLID,
GBRAID, WBRAID and UTM capture, persisted through submission** · **exactly one conversion per
approved test submission** · desktop and mobile · correct canonical · **commercial HVAC
installation and replacement messaging only** · no Licensed & Insured · **no LSA references of
any kind** (no badge, Google Guaranteed mark, LSA number or LSA review widget).

Added this session: the corrected WhatConverts configuration block, the Source = Offline defect
and why DNI alone will not fix call attribution if the page drops the parameters, and acceptance
tests 11 (no LSA) and 12 (commercial-only messaging).

**Two standing blockers:** no approved non-production/test path exists, so the
one-conversion-per-submission test cannot run without creating a real lead and a real
conversion; and no Privacy or Terms link exists on any of the five current paid pages (the
offer subdomain does have a Privacy Policy page — it appears in the 404 page navigation — so
this is a linking gap, not a missing document).

---

## 4. Commercial RSA status — GATED

| Plan | Fingerprint | Status |
|---|---|---|
| `AMB-0910-COMM-RSA-1` | `30312BC45992` | **SUPERSEDED · DO_NOT_EXECUTE** |
| `AMB-0910-COMM-RSA-2` | `41C183D15C93` | **GATED** on the 404 — 2 ops, create-PAUSED |

RSA-1 was drafted before the launch pack was located: agency-draft copy instead of the pack
copy, `path2` of `maryland`/`install` instead of `installation`, and it addressed the ad group
by name because it did not yet exist. RSA-2 carries the pack copy verbatim, addresses ad group
**199748801029** by ID, uses paths `commercial-hvac` / `installation`, and passed the character
and claim checks (30 headlines ≤30, 8 descriptions ≤90, zero duplicates, no barred claims).

Both remain unexecuted. After the page is published and passes real-browser QA the sequence is:
revalidate → supersede and re-fingerprint if any destination, copy or before-state changed →
create both PAUSED on exact approval → read back policy status and every asset → only then a
separate enable plan, once the ads are APPROVED and the page and tracking pass.

No CTR, CPC, conversion or lead-volume improvement is claimed. Two RSAs in one ad group is not
an evenly allocated A/B test.

---

## 5. Routing negative status — GATED

`AMB-0910-COMM-XNEG-1` · `A70260017DAD` · 1 operation · **GATED, unchanged.**

BROAD `commercial` as an **ad-group** negative on the residential SKAG 202339087634 only.
**Never at campaign or account level.**

Not to be added until the commercial ad group has a live HTTP-200 destination, approved ads,
eligible keywords, correct tracking, and has been enabled and confirmed capable of serving.
Applied earlier it suppresses commercial demand instead of redirecting it.

Current state confirms the gate is closed: ad group 199748801029 is PAUSED with **0 ads**, and
its two keywords are `UNDER_REVIEW`.

---

## 6. Executed / blocked / awaiting approval

### Executed (earlier sessions, not replayed)

| Plan | Fingerprint | Ops | Result |
|---|---|---|---|
| `AMB-0910-COMM-1` | `A9173FADBA82` | 3 | Ad group 199748801029 PAUSED + 2 keywords · readback 0 FAIL |
| `AMB-0910-CPC-CAP-1` | `7EA6922309EB` | 2 | Gas Boiler $25, HVAC Replacement $30 |
| `AMB-0910-BUD-2` | `93541FBB5D7F` | 2 | Budgets → $421.55/day |
| `AMB-0909C-NEG-COMMERCIAL` | `9F88FEE76803` | 1 | Account-level `commercial` removed, 272→271 |
| `AMB-0909C-COMP-1` · `AMB-0909-ADS-1` · `AMB-0909C-NEG-SAVAGE` | — | 10 | earlier sessions |

### Blocked / gated

| Item | Blocker |
|---|---|
| `AMB-0910-COMM-RSA-2 41C183D15C93` | Landing page 404 |
| `AMB-0910-COMM-XNEG-1 A70260017DAD` | Commercial ad group not yet serving |
| Commercial enable plan | Page + QA + approved ads |
| One-conversion-per-submission test | No approved non-production/test path |
| `WC-0910-OFFLINE-SOURCE-1` | Needs WhatConverts admin action + approval |
| Six-ad policy appeal · August Auction Insights | Claude in Chrome not connected |

### Do not execute

`AMB-0909C-CPC-INST-2 5D57E0EF3B70` REJECTED · `AMB-0910-COMM-NEG-1-FULL A774B9C14896` REJECTED ·
`AMB-0910-COMM-NEG-1 C4142D5D5DE0` SUPERSEDED · `AMB-0910-RSA-ACR-1 19E2F2FFC311` SUPERSEDED ·
`AMB-0910-COMM-RSA-1 30312BC45992` SUPERSEDED · `46C39C6B7091` · `D448BFDE4650` ·
`23BE8FF0F24C` · `CE289F3508A2` · `A435FA09AC97` · `DE376F91F449`

---

## 7. Consolidated approval block

| Plan | Fingerprint | Ops | Status |
|---|---|---|---|
| **`AMB-0910-COMM-NEG-2`** | **`A9C9BCBDDD74`** | **18** | **VALIDATED_OK — ready** |
| `AMB-0910-RSA-ACR-2` | `1F166DE17017` | 1 | ready — AC Repair challenger, create-paused |
| `AMB-0910-COMM-RSA-2` | `41C183D15C93` | 2 | GATED — 404 |
| `AMB-0910-COMM-XNEG-1` | `A70260017DAD` | 1 | GATED — group must serve first |

**Exact next approval line:**

```
APPROVE AMB-0910-COMM-NEG-2 A9C9BCBDDD74 18 operations FOR 2401959466
```

Safe to execute now — the ad group is PAUSED with zero ads, so the negatives cannot suppress
anything today. The ad group stays paused.

**Account state unchanged this session:** budgets $421.55/day = $12,815.12 (headroom $184.88) ·
ceilings $25/$25/$30/$25/$30 · campaign negatives 6,158 · account-level negatives 271 ·
conversion actions 16 · IP blocks 2,796 · ClickCease template intact.

## Evidence

```
receipts/validate-only/AMB-0910-COMM-NEG-2-2026-09-10.json
reports/ambient-cooling-heating/evidence/
  2026-09-10e-wc-offline-source.json        Source = Offline analysis, 371 leads, no PII
  2026-09-10e-neg2-conflict-tests.json      all conflict tests + residual risk
clients/ambient-cooling-heating/plans/
  AMB-0910-COMM-NEG-2.json                  A9C9BCBDDD74
  AMB-0910-COMM-NEG-1.SUPERSEDED.json  ·  AMB-0910-COMM-NEG-1-FULL.REJECTED.json
  WC-0910-OFFLINE-SOURCE-1.md               WhatConverts change plan, NOT executed
handoffs/ambient-commercial-hvac-installation-2026-09-10/DEVELOPER_HANDOFF.md
```

No credential, token, secret, or unredacted lead PII appears in any artifact.
