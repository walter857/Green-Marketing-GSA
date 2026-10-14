# Ambient Cooling - Live — Autonomous Master Optimization Run

**Account** Ambient Cooling - Live · 240-195-9466 / 2401959466 · America/New_York · USD
**Run window** 2026-08-21 20:34 EDT → 2026-08-22 01:35 EDT
**Managers** Green Marketing 3373711342 ACTIVE · ClickCease Client Center 2815082755 ACTIVE
**Google Ads mutations executed** 1 · **Website/GTM/WhatConverts changes** 0

---

## 1. Business outcome

One authorized change was made: **HVAC Installation daily budget $138.16 → $176.15.** It passed
all eight gate conditions and its readback passed. Every other resource in the account is
byte-for-byte unchanged.

Two validated packages are held back and need approval. One is blocked by a live landing-page
defect the developer has not yet fixed.

The account is **not** at risk of breaching the $13,000 August maximum. Worst case is now
**$12,068.66**, leaving **$931.34** of headroom.

---

## 2. Identity and integrity

| Check | Result |
|---|---|
| Descriptive name | `Ambient Cooling - Live` exact match |
| Customer ID / timezone / currency | 2401959466 · America/New_York · USD |
| Manager / test account | false / false |
| Manager links | 3373711342 ACTIVE, 2815082755 ACTIVE — untouched |
| Concurrency | 3 stray Python PIDs found; **none** targets 2401959466, zero established TCP connections, jobB writer script no longer exists on disk, ~1.7 s CPU over 2–3 days. Defunct, not active writers. Not terminated. |
| Structural baseline | All 11 buckets matched the expected pre-run values exactly. Zero drift. |

**Completed packages verified without replay.** Campaign settings, six ad-schedule rows per
campaign, call-asset schedule and exclusivity, the RSA swap, the six preserved replacement RSAs,
sitelinks, callouts, the primary conversion set, shared-set non-attachment and the 75 locations
all verified in place. Two assertion failures in my own harness were investigated and were **my
errors, not account defects**:

- I asserted `MANUAL_CPC`. Bidding is actually **`TARGET_SPEND` (Maximize Clicks), uncapped, no
  portfolio strategy** on all five — consistent and unchanged. This materially affects budget
  behaviour and is reflected below.
- I asserted all CONSUMER_FINANCE ads were paused. Two show `ENABLED` — but they sit in **ad
  group 202339087874, which is REMOVED** (a stray HVAC Replacement SKAG inside the AC Repair
  campaign). A removed ad group cannot serve; 0 impressions, 0 clicks, $0.00 confirmed. Inert. No
  mutation warranted.

Three fingerprints on the do-not-execute list were still marked `live` in the local ledger — a
real hazard, since a future session could have picked them up. Marked superseded with reasons:
`80868F985D33B756`, `6A2DE7A6589CA2B7`, `12E7572A25B9AFF0`.

`work-order.yaml` carried a stale `expected_ad_schedule` of 08:00–16:00. Corrected to separate
**published business hours** (M–F 08:00–16:00) from **approved paid delivery** (M–F 08:00–20:00 +
Sat 08:00–13:00), and the phone architecture, barred claims and budget-maximum facts were added.
Validator: `Work order: PASS`.

---

## 3. Execution results

| Package | Fingerprint | Decision | Validate | Result |
|---|---|---|---|---|
| HVAC Installation budget | `BFB9FD367F639CA4` | **EXECUTED** | VALIDATE_OK | Readback PASS, 6/6 asserts |
| Gas Boiler keyword `[boiler repair]` | `3D823A10CB3C0B25` | **BLOCKED** | VALIDATE_OK | LP gate FAIL — not executed |
| Landing-page production deployment | `93A9DF4AA19675E8` | **BLOCKED** | n/a | No source, no staging, no backup, no deploy authority |
| Automotive negatives (AC Repair) | `EACEC7CBAE85FF2B` | **NEW — needs approval** | VALIDATE_OK | Not executed |
| Developer handoff addendum B | `7A28BBF93AF27F8D` | Documentation | n/a | Written |

### Why the budget package executed

The prompt required eight conditions. The one I could not confirm at 20:34 EDT was
*"reporting has settled through the latest eligible hour"* — delivery closed at 20:00 and Google
cost data lags up to ~3 hours, and the headroom was only **$0.08**.

By 01:22 EDT both objections had resolved:

- **Settlement confirmed empirically, not assumed.** 2026-08-21 cost read $808.11 at 20:57 and
  **$808.11 again** 5.39 h after close. It did not restate.
- **Headroom moved $0.08 → $931.34** because one day rolled off (11 → 10 remaining days).

All eight conditions then passed, and I executed. Pre-write drift checks re-ran the identity gate,
manager links, fingerprint reproduction, all five budget before-states, MTD and the worst-case
calculation, then validate-only on the exact single operation.

### Budget arithmetic

```
worst case = MTD + (total daily budget × 2 overdelivery × remaining days)
           = 2,756.06 + (465.63 × 2 × 10)
           = 12,068.66          headroom 931.34
```

The 2× multiplier is **not** theoretical here. HVAC Installation has run at **199.5 %, 197.4 %,
199.9 %, 199.7 %** of its daily budget on the last four delivery days — it is pinned to Google's
overdelivery ceiling under uncapped Maximize Clicks. Any budget increase converts to real spend
immediately. The conservative model is therefore the correct one.

---

## 4. Campaign-by-campaign assessment (MTD, billable only)

| Campaign | Impr | Clicks | Cost | CTR | CPC | Prim. conv | CPA | Budget lost IS | Rank lost IS | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HVAC Installation | 1,110 | 40 | $1,100.44 | 3.60 % | $27.51 | 0.0 | n/a | **54.14 %** | 3.04 % | **Budget raised** |
| AC Repair | 155 | 12 | $997.60 | 7.74 % | $83.13 | 1.0 | $997.60 | 3.28 % | **61.11 %** | Rank-constrained — HOLD |
| HVAC Repair | 433 | 7 | $605.88 | 1.62 % | $86.55 | 2.0 | $302.94 | 2.82 % | **70.06 %** | Watch new RSAs |
| HVAC Replacement | 61 | 2 | $52.14 | 3.28 % | $26.07 | 0.0 | n/a | 0.00 % | 52.94 % | HOLD |
| Gas Boiler | 2 | 0 | $0.00 | — | — | 0.0 | n/a | 0.00 % | 66.67 % | Blocked on LP |

**HVAC Installation** — the only supported increase candidate, and the evidence holds: budget-lost
IS 54 %, rank loss ~3 %, CPC roughly a third of the repair campaigns. It has **zero Primary
conversions on 40 clicks**, which I am flagging as the run's top risk. I did not treat that as
disqualifying: at a plausible 5 % conversion rate, zero in 40 clicks has ~13 % probability — unlucky,
not decisive — and it did produce one WhatConverts lead (secondary, `all_conversions` 1.0), so it
is not producing literally nothing. The 24 h / 72 h / 7-day checkpoints carry an explicit rollback
trigger at $2,000 spend with zero Primary conversions.

**AC Repair** — 61 % rank-lost IS with only 3 % budget loss. This is a quality and rank problem, not
a budget problem. Quality Score 4, landing-page experience AVERAGE, expected CTR BELOW_AVERAGE.
More budget would buy nothing. Correct action is landing-page and relevance work first.

**HVAC Repair** — 70 % rank-lost IS, QS 2, landing-page experience **BELOW_AVERAGE**. The two new
RSAs (821714108336, 821714108339) are ENABLED / APPROVED / EXCELLENT. Too early to judge; assess at
7 settled days on qualified leads and CPL, **not** on CTR against the old 1.45 % baseline.

**HVAC Replacement** — 2 clicks. Insufficient data. QS 2, landing-page experience BELOW_AVERAGE.
Hold expansion until the landing page improves.

**Gas Boiler** — 2 impressions, zero delivery. Eligibility, policy, ads, negatives, targeting and
budget all verified clean; this is a keyword-volume problem. The fix is the approved Exact keyword,
which stays blocked until the page is corrected.

---

## 5. Conversions and measurement

Primary and counted remains exactly the approved set: **1068114183** Calls from ads ·
**6885463625** LP Submit Lead Forms · **6885576934** LP phone-call leads. WC Lead, WC Calls, Call
BTN Click and Visit Thank you page all remain Secondary and uncounted.

The known form double count is prevented from entering the Primary Conversions column while the
current Primary/Secondary configuration remains unchanged.

One observation worth recording: HVAC Repair's **WC Lead shows `conversions` 1.0** while HVAC
Installation's shows 0.0. That is not a regression — `metrics.conversions` is stamped at conversion
time, so the HVAC Repair row predates Plan B. Historical columns do not reprocess. Under the
current configuration, clean Primary conversions MTD are **2** (one call, one form), plus that one
pre-Plan-B artifact.

Five conversion actions are `primary_for_goal=true` but `include_in_conversions_metric=false`
(Local actions — Directions, Website visits, Menu views, Other engagements, Clicks to call). They
do not enter the Conversions column and do not affect bidding. No change proposed.

**Lead quality is UNKNOWN.** No authenticated WhatConverts session was available and credentials
were not requested. WC Lead is not treated as qualified merely because its source is WhatConverts.

---

## 6. Search terms and negatives

Full corpus classified across four windows — since-launch, 30, 90 and 365 days — **1,612 rows**
written to `exports/search-terms-verdicts-2026-08-21d.csv`. Raw terms were classified against a
service-intent whitelist; only aggregates and flagged terms were surfaced.

Since launch: **343 KEEP** ($1,936.03, 3 conversions) · **49 WATCH** ($78.71) ·
**11 NEGATIVE-CANDIDATE** ($65.02, 0 conversions).

This **revises** the earlier "$17.24 of irrelevant spend, no recurring pattern" finding. There is a
clear recurring cluster: **seven distinct vehicle and marine AC terms in AC Repair**, one costing
**$47.78**, all with zero conversions — `car air conditioner repair near me`, `ac car repair near
me`, `bmw car ac repair near me`, `car ac repair near me`, `car ac service near me`, `auto ac
repair near me`, `boat air conditioner repair near me`.

Proposed: **three campaign-level BROAD negatives on AC Repair only** — `car`, `auto`, `boat`
(`EACEC7CBAE85FF2B`). Conflict testing is clean on every axis: blocks 0 of 31 Ambient service
phrases, 0 of 5 active keywords, 0 converting terms, not already in the 59-member account-level
set, no protected or caution-list term touched. **`car` does not block `carrier ac repair`** —
negative keywords match whole words — and that was explicitly tested.

Deliberately **not** negated: `goodman certified technician near me` (Goodman is an HVAC brand; a
homeowner may want service Ambient performs — an earlier automated pass flagged it on the token
"certified", which was too aggressive and is withdrawn); `home depot mini split installation cost`
and `lowes hvac installation` (retailer-framed but the underlying service is one Ambient performs,
one click, not a repeated pattern → WATCH); `midea hvac distributor near me` (one occurrence).

Shared set **11813144900 "General List"** (1,111 members, contains the single words `repair` and
`Repair`) remains unattached to the five. It must never be attached — it would block every repair
keyword in the account.

---

## 7. Landing pages

Deployment plan `93A9DF4AA19675E8` **reproduces byte-for-byte**, but 4 of 6 deployment
preconditions fail: no website source, no staging, no confirmable backup, no deploy authority. An
independent search of the workspace confirms no site source, theme or deployment configuration
exists locally. **Nothing was published.**

Fifteen live renders across five pages (desktop, mobile, and desktop with tracking parameters), all
HTTP 202 at 158–173 KB — well clear of the ~12 KB SG-Captcha stub, all first-attempt successes.

**Working correctly:** all five H1s service-specific and correct; all canonicals self-referencing;
GTM-PQTPQ436 and WhatConverts present on all five; **click-ID capture verified working** (a test
gclid plus all five UTMs were captured into `wc_client`); **zero barred claims** on any page — no
24/7, same-day, emergency, guaranteed or financing language. The HVAC Installation H1 reads "HVAC
**Installers**", which correctly matches the active keyword `hvac installers` — that is alignment,
not a defect.

**Six defects handed off (`7A28BBF93AF27F8D`):**

1. **P0** — `/gas-boiler-repair/` still shows `Your HVAC Replacement in 3 Simple Steps`. Re-verified
   still live at 01:30 EDT. Blocks the keyword.
2. **P1, newly found** — `/hvac-repair/` shows `Recent AC Repair Work`. Same duplication pattern.
3. **P1 — phone race condition root cause identified.** The `wc_swap` cookie on **all five** pages
   reads `4109141456+..+4107610932+..+230773`. That is runtime proof that **+14107610932 is the
   configured WhatConverts swap *source*** for profile 105803. The swap is client-side, so any DOM
   read before the script completes sees the pre-swap number. Not random, not constant. Fix is to
   change the swap source to the approved paid base — but **only after Green Marketing confirms
   4107610932 is stale rather than deliberately retained.**
4. **P2** — malformed `tel:` hrefs on all five (`tel:(410) 705-6354`, `tel:4107056354`). Normalize
   the href only; touching the markup WhatConverts keys on will break DNI.
5. **P1** — **three duplicate `<form id="gform_1">` instances per page**, 34 duplicate DOM ids each.
   Invalid HTML, breaks `label[for]` association, and is a plausible contributor to duplicate form
   conversions.
6. **P1** — **zero Privacy Policy and Terms links** on any page. HVAC Repair and HVAC Replacement
   both report landing-page experience BELOW_AVERAGE. Missing legal links are a recognised trust
   signal and a plausible contributor, but Google does not expose per-signal attribution — this is
   an **inference, not proven causation**.

No form was submitted and no telephone link was clicked.

---

## 8. Schedule, geography, ClickCease

Six clean non-overlapping schedule rows per campaign (M–F 08:00–20:00, Sat 08:00–13:00), zero
Sunday rows, all minutes ZERO, on all five campaigns and on call asset 407995613637, which is
linked to exactly the five. 75 positive locations per campaign, zero exclusions, PRESENCE targeting
on both positive and negative geo. No change proposed; overnight delivery stays closed.

To state it precisely: the landing pages and forms remain reachable at all times, but **paid ads
serve only inside the campaign schedule**, so paid form acquisition is not 24/7.

ClickCease untouched — manager link ACTIVE, 2,796 IP exclusions unchanged, account tracking
template intact. The ClickCease tag is absent from the five paid landing pages; recorded as an
observation only, not as a cause of charged traffic.

---

## 9. Resources changed and unchanged

**Changed — exactly one:** campaign budget `15787409441` (HVAC Installation),
`amount_micros` 138160000 → 176150000, mask `["amount_micros"]`, `partial_failure=false`.

**Unchanged and proven:** campaigns 23 · ad groups 68 · ads 115 · keywords 6968 · campaign criteria
13810 · ad schedules 139 · campaign assets 283 · customer assets 1 · conversion actions 16 · IP
exclusions 2796 · shared sets 16. The other four budgets, all five campaign statuses, bidding
strategies, the primary conversion set, the RSA swap states, the call asset, locations, shared-set
associations (0 on the five), campaign-level negatives (0 on the five), the Gas Boiler ad group's
two keywords, both manager links, GTM and WhatConverts.

**Rollbacks used:** none. No write failed.

---

## 10. Monitoring

`scripts/ambient_checkpoint.py` — deterministic, read-only, identity-gated, no background process.

```bash
python scripts/ambient_checkpoint.py --what budget    # 2026-08-23, 08-25, 08-29
python scripts/ambient_checkpoint.py --what keyword   # after the keyword is created
python scripts/ambient_checkpoint.py --what rsa       # 2026-08-28 (7 settled days)
```

Budget rollback triggers, all currently **clear**: projected August cost above $13,000 · HVAC
Installation past $2,000 spend with zero Primary conversions · budget-lost IS below 5 %. Rollback is
one mutation back to 138160000 micros. Do not roll back on a single zero-conversion window, and do
not roll back the RSA swap on CTR alone.

---

## 11. Risks

**P0** — Gas Boiler landing page still shows the HVAC Replacement heading. Blocks `3D823A10CB3C0B25`
and sends broad boiler traffic to mismatched copy.

**P1** — HVAC Installation has zero Primary conversions on 40 clicks and $1,100.44, and just
received more budget. Watch closely at 24 h.
**P1** — Three duplicate form instances per page; plausible contributor to duplicate form events.
**P1** — No legal links on any page; two campaigns report BELOW_AVERAGE landing-page experience.
**P1** — +14107610932 confirmed as the WhatConverts swap source on all five paid pages.
**P1** — Lead quality unknown; no WhatConverts access, so no qualified-lead or sold-job evidence
exists to validate any CPA in this report.

**P2** — Malformed `tel:` hrefs.
**P2** — Automotive AC waste continues until `EACEC7CBAE85FF2B` is approved (~$48 per 8 days).
**P2** — Two inert ENABLED ads inside REMOVED ad group 202339087874. Harmless; cleanup would need a
destructive-action approval and is not worth it.

---

## 12. Artifacts

**Report** `reports/ambient-cooling-heating/2026-08-22-autonomous-final-optimization.md`

**Receipts** `receipts/budget-mutation/readback-2026-08-22.json`

**Snapshots** `master-baseline-2026-08-21d.json` · `phaseA-verification-2026-08-21d.json` ·
`phaseA2-verification-2026-08-21d.json` · `pacing-2026-08-21d.json` · `lp-audit-2026-08-21d.json` ·
`gas-boiler-lp-gate-2026-08-22.json` · `final-inventory-2026-08-22.json`

**Exports** `search-terms-verdicts-2026-08-21d.csv` (1,612 rows)

**Plans** `NEGATIVES-AUTOMOTIVE-AC-REPAIR-2026-08-22.json` (`EACEC7CBAE85FF2B`) ·
`DEVELOPER-HANDOFF-ADDENDUM-B-2026-08-22.json` (`7A28BBF93AF27F8D`)

**Script** `scripts/ambient_checkpoint.py`

No secrets, tokens, cookies, authenticated storage or lead PII stored in any artifact.
