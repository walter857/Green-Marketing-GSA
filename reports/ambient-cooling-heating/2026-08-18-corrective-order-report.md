# Ambient Cooling & Heating — Launch Remediation

**Client:** Ambient Cooling & Heating LLC
**Child account:** `Ambient Cooling - Live` · **ID** `240-195-9466` (`2401959466`)
**Manager:** `Green Marketing` `337-371-1342` · **ClickCease Client Center** `281-508-2755` (authorized, protected, untouched)
**Vertical:** heating-cooling · USD · America/New_York
**Date:** 2026-08-18 · **Phases executed:** `READ` + `DRAFT`

> **No external change was made.** Every Google Ads call was a GAQL `SELECT`. Every web request
> was a `GET`. Nothing was created, enabled, paused, edited, or deleted. **No form was
> submitted, no telephone link was clicked, no call was placed.** No budget changed. The
> ClickCease manager link, its ACTIVE status and its permissions are exactly as found.
> **The superseded negative plan `12E7572A25B9AFF0` was not applied, in whole or in part.**

Facts are labelled **SUPPLIED** (given by Green Marketing), **OBSERVED** (read from the live
account or a live page today), **INFERRED** (reasoned, not proven), **PROPOSED** (drafted, awaiting approval).

---

# Lead summary

## ✅ What is fixed

1. **GTM is live and correct on all five paid pages.** *(OBSERVED)* One head snippet, one
   noscript, one `gtm.js` request returning 200, container initialized, `dataLayer` running, no
   duplicate container, Consent Mode v2 signals present. GA4 and the Google Ads conversion
   linker for `11155434808` both fire through it.
2. **The main-site number is gone from the paid pages.** *(OBSERVED)* Zero occurrences of
   410-761-0932 anywhere in the HTML or visible text of any page, at either viewport.
3. **Campaign scaffolding is built to spec.** *(OBSERVED)* Search-only, Search Partners off,
   Display off, PRESENCE targeting both ways, 75 location targets, English, Phrase+Exact only,
   no Broad, budgets exactly matching the $13,000 allocation, Maximize Clicks as instructed.
4. **The ad schedule has no duplicate rows.** *(OBSERVED)* Six clean, non-overlapping rows per
   campaign — that item in the corrective order was based on stale data. It is, however,
   **restrictive**: see §14, now superseded by the approved 24/7 decision.

## ⛔ What remains broken

1. **Two of five campaigns have never served a single impression.** Gas Boiler Repair and HVAC
   Replacement: **0 impressions since launch**, because both of their RSAs are DISAPPROVED and
   the ad groups have no other eligible ad.
2. **The CONSUMER_FINANCE disapproval is a false positive, and I can now prove it.**
3. **An account-wide negative list is silently blocking core demand** — including `commercial`
   (3.83 historical conversions, $1,043 spend) and four Maryland place names inside the service area.
4. **The mobile "Call Now" button dials an unapproved number**, (410) 914-1456.
5. **The form captures zero attribution.** All seven hidden fields are empty on a click carrying
   gclid + gbraid + wbraid + five UTMs. Offline conversion import is impossible as built.
6. **A tel-tap is still a Primary biddable conversion**, alongside a duplicate form action.
7. **Every sitelink sends paid traffic to the main site**, which has a different phone and no form.
8. **Landing-page experience is BELOW AVERAGE** on every measured keyword; Quality Score is 1–2.

## ⏸ What is blocked on your approval

Six fingerprinted packages, below. **Nothing proceeds without the matching fingerprint.**

## ▶ The next safest action

**Approve the RSA package `0BCC73A397580856`.** It creates 6 replacement RSAs **paused**, costs
nothing, changes no live delivery, and is the only action that unblocks the two dead campaigns.
In parallel, answer the **three questions** in §9 — they are the only things I cannot decide myself.

---

# 1. Identity gate — ✅ PASS

Fresh read-only lookup on 2026-08-18 *(OBSERVED)*:

| Check | Result |
|---|---|
| `customer.id` | `2401959466` ✅ exact |
| `customer.descriptive_name` | `Ambient Cooling - Live` ✅ exact, `- live` marker present |
| Manager / test account | `false` / `false` ✅ |
| Status | `ENABLED` ✅ |
| Hierarchy | level 1 under `3373711342` "Green Marketing" ✅ |
| Currency / timezone | USD / America/New_York ✅ |
| Work-order validator | **PASS** ✅ |

**ClickCease manager link** *(SUPPLIED + OBSERVED)*: `customers/2815082755`, link `345789060`,
status **ACTIVE**. Recorded in `client.yaml` as a **confirmed, authorized, protected** client
fact. No plan in this report touches it.

Pre-change snapshots saved to `clients/ambient-cooling-heating/snapshots/`:
`pre-change-structure-2026-08-18.json` (23 campaigns, 68 ad groups, 6,968 keywords, 107 ads,
17 shared sets, 7,015 shared criteria, 23 conversion actions, 271 campaign assets),
`pre-change-performance-2026-08-18.json` (5 windows + 955 change events),
`landing-page-qa-2026-08-18.json`, `landing-page-attribution-test-2026-08-18.json`.

---

# 2. Delivery reality — the launch is barely running

*(OBSERVED, 2026-08-14 → 2026-08-18)*

| Campaign | Status | Impr | Clicks | Cost | Conv | Avg CPC | Impr. share |
|---|---|---:|---:|---:|---:|---:|---:|
| HVAC Repair | ENABLED | 206 | 2 | $42.06 | 0 | $21.03 | 17.7% |
| AC Repair | ENABLED | 49 | 3 | $50.12 | 0 | $16.71 | 10.0% |
| HVAC Installation | ENABLED | 12 | 0 | $0.00 | 0 | — | 18.2% |
| **Gas Boiler Repair** | ENABLED | **0** | 0 | $0.00 | 0 | — | — |
| **HVAC Replacement** | ENABLED | **0** | 0 | $0.00 | 0 | — | — |
| **Total** | | **267** | **5** | **$92.18** | **0** | **$18.44** | |

Five days, $92.18 spent against roughly $2,138 available: **4.3% of budget**. `search_budget_lost_impression_share`
is effectively zero. **Budget is not the constraint** — disapprovals and Quality Score are. Do not raise budgets.

**Quality Score** *(OBSERVED)* — `hvac repair near me` = **1** (all three components below average);
`ac repair near me` = **2** (expected CTR below average, ad relevance average, **landing-page
experience below average**). No promise is made about Quality Score; these are the three
components Google actually publishes, and they will be re-reported once traffic accumulates.

Traffic is **mobile-dominant**: 40 of 49 AC Repair and 157 of 206 HVAC Repair impressions. That
makes the mobile phone defect (§5) commercially significant, not cosmetic.

---

# 3. The CONSUMER_FINANCE disapprovals — a provable false positive

## What the API returned *(OBSERVED)*

| Ad | Ad group | Ad status | Policy |
|---|---|---|---|
| 820900825434 | SKAG \| HVAC Installation | **DISAPPROVED** | CONSUMER_FINANCE / FULLY_LIMITED |
| 820900825437 | SKAG \| HVAC Installation | **DISAPPROVED** | CONSUMER_FINANCE / FULLY_LIMITED |
| 820944944368 | SKAG \| HVAC Replacement Near Me | **DISAPPROVED** | CONSUMER_FINANCE / FULLY_LIMITED |
| 820944944371 | SKAG \| HVAC Replacement Near Me | **DISAPPROVED** | CONSUMER_FINANCE / FULLY_LIMITED |
| 820900825428 | SKAG \| Gas Boiler Repair | **DISAPPROVED** | CONSUMER_FINANCE / FULLY_LIMITED |
| 820900825431 | SKAG \| Gas Boiler Repair | **DISAPPROVED** | CONSUMER_FINANCE / FULLY_LIMITED |

**Two more ads carry the same topic** and were not in the original brief: **820900825422** and
**820900825425**, at `AREA_OF_INTEREST_ONLY`, inside ad group **202339087874** — a
**`SKAG | HVAC Replacement Near Me` ad group sitting inside the AC Repair campaign**. That ad
group is already REMOVED so nothing serves from it, but its ads and keywords are still ENABLED.

## Why this is a misclassification, not a copy problem

**Evidence 1 — every asset is flagged, including the brand name.** *(OBSERVED)* On ad
820900825428, **17 of 19 assets** are DISAPPROVED for CONSUMER_FINANCE, including
`"Boiler Not Heating Properly?"`, `"Local Gas Boiler Repair"`, `"Restore Warm Indoor Comfort"`
and `"Ambient Cooling & Heating"`. A phrase-level trigger does not flag a company name.

**Evidence 2 — Google supplied no asset-level evidence at all.** *(OBSERVED)* Every
`policy_topic_entry` returns an **empty** `constraints` list (`{}`) and **zero** `evidences`.
There is no cited snippet to remove.

**Evidence 3 — the decisive one — near-identical copy was APPROVED elsewhere.** *(OBSERVED)*

| Headline | HVAC Repair ad 820900825563 | Gas Boiler ad 820900825431 |
|---|---|---|
| "Take Control of Home Comfort" | ✅ **APPROVED** | ⛔ DISAPPROVED |
| "Get Answers Before You Decide" | ✅ **APPROVED** | ⛔ DISAPPROVED |
| "Make a Confident Repair Choice" | ✅ **APPROVED** | ⛔ DISAPPROVED |
| "Choose Ambient With Confidence" | ✅ **APPROVED** | ⛔ DISAPPROVED |
| "Start With a Free Quote" | ✅ **APPROVED** | ⛔ DISAPPROVED |

The same decision-framing language is approved in one ad group and disapproved in another.

**Evidence 4 — the landing-page hypothesis does not survive testing either.** *(OBSERVED)* I
scanned all five pages for finance vocabulary. `/hvac-installation/` and `/hvac-replacement/`
contain the word **"budget"** in visible copy; **`/gas-boiler-repair/` contains no finance
language whatsoever** and is still disapproved. Destination content does not explain the split.

**Conclusion (INFERRED, clearly labelled):** the split follows the *service category* —
installation, replacement and boiler work are big-ticket home improvement, adjacent to home-improvement
lending — not the wording. This is an automated classifier error. The prior audit's guess that
`honest, upfront pricing`, `Plan your HVAC installation` and `A new HVAC system is a major
decision` caused it is **not supported**: those phrases appear in only 2 of the 6 ads, and the
cleanest ad in the set (820900825428) is disapproved anyway.

## The ZIP-targeting conflict is real *(OBSERVED + verified against Google policy)*

The 75 location targets resolve to **42 Postal Codes, 28 Cities, 5 Neighborhoods**. Google's
[Consumer finance in personalized advertising](https://support.google.com/adspolicy/answer/16700846?hl=en)
policy prohibits **ZIP-code targeting** for credit/banking/financial-planning ads in the US and
Canada (effective 2024-02-28); city and radius targeting remain allowed. **If Google keeps
classifying these as Consumer Finance, 42 ZIP targets per campaign are a standing policy
conflict that can escalate to account warnings.**

**Recommendation — one strategy, not a menu:** clean HVAC-only rewrite **plus** appeal. **Do not
remove the approved local targeting to accommodate a false positive.** Ambient advertises HVAC
service; nothing in the account advertises credit or lending. A contingency is drafted (convert
the 42 ZIPs to city + radius equivalents) but is **not** proposed now.

## Appeal route *(verified)*

The Google Ads API exposes **policy *exemption* requests at creation time only**, for ignorable
topics — CONSUMER_FINANCE is not one. **Appeals of existing disapprovals must be filed in the
Google Ads UI** (Policy issues → Appeal). Since [July 21, 2026 Google will not accept in-account
appeals for decisions older than 6 months](https://www.seroundtable.com/google-ads-appeals-limit-41730.html);
these decisions are days old, so that limit does not bite.

- **Six existing disapproved ads → "Dispute decision"** (true false-positive; evidence above).
- **Six new replacement RSAs → no appeal.** They enter review fresh.
- No duplicate appeals. No silent cloning of disapproved content.

---

# 4. Six replacement RSAs — DRAFTED, awaiting approval

**Package:** `clients/ambient-cooling-heating/plans/rsa-replacement-package-2026-08-18.json`
**Fingerprint:** `0BCC73A397580856`
**Creates 6 RSAs, all PAUSED. Modifies 0. Removes 0.**

| Ad group | Campaign | Canonical keyword | Final URL | Paths |
|---|---|---|---|---|
| 202339087634 SKAG \| HVAC Installation | 24132507747 | `hvac installers` | `/hvac-installation/` | `hvac-installers` / `severn-md` |
| 200159223798 SKAG \| HVAC Replacement Near Me | 24132507753 | `hvac replacement near me` | `/hvac-replacement/` | `hvac-replace` / `central-md` |
| 202339087594 SKAG \| Gas Boiler Repair | 24132507744 | `gas boiler repair` | `/gas-boiler-repair/` | `boiler-repair` / `severn-md` |

Two per ad group: one direct-response/service ad, one evaluation-and-comfort-outcome ad. The
second is deliberately **not** framed as a "decision" ad — that framing is what the classifier
appears to dislike, so it is reframed around the physical work and the comfort outcome.

**Validation — 0 errors:** 15 headlines ≤30 chars and 4 descriptions ≤90 chars on all six;
no duplicates within an ad; canonical keyword in ≥3 headlines each (10, 6, 8, 6, 9, 7);
service + location + benefit + trust + CTA coverage; approved locations only (Severn,
Severna Park, Columbia, Central Maryland); display paths ≤15 chars; **no phone number in any
creative** — the approved call asset carries it.

**Banned-language sweep — 0 hits** across: financing, finance, credit, loan, APR, payment,
monthly payment, payment plan, approval, invest, **budget**, afford, upfront pricing, price
guarantee, purchase decision, major decision, installment, interest rate, lease.
**Also 0 hits** on unverified claims: licensed, insured, certified, guarantee, warranty, same
day, emergency, 24/7, years, rated, reviews, award, discount, $, fast, instant, cheap, best
price, #1. **"Free Quote" is used** — it is the published offer on all five pages.

**Pinning:** none. Ad Strength on the current set is `EXCELLENT` on two of the six disapproved
ads with zero pins, so a pin buys no relevance here and would only reduce combinations. The
canonical service term appears in 6–10 of 15 headlines, so Google will surface it without
being forced. This is a judgment call, made and defended rather than escalated.

**Non-blocking warnings (6, all intentional):** `Request a Free Quote`, `Start With a Free
Quote`, `Ambient Cooling & Heating`, `Serving Central Maryland`, `Central Maryland HVAC Team`
and `See Your System Options` repeat across ad groups. These are generic CTA/brand/location
lines, not service claims; repeating them is correct.

### Sequence after approval — enabling is a **separate** approval

1. Approve `0BCC73A397580856` → create 6 RSAs **PAUSED**.
2. Read every field back from the API, diff against the approved package, report.
3. Let policy review complete; report ad-level **and** asset-level status.
4. File "Dispute decision" on the six original disapprovals.
5. **Second explicit approval** to ENABLE the replacements.
6. Confirm replacements are serving.
7. **Destructive approval** to pause the six originals — end state exactly two eligible RSAs per
   active ad group, with no gap in service.

---

# 5. Phone and tracking QA — full evidence in `research/landing-page-qa-2026-08-18.md`

**The 2026-08-17 finding that the pages carried no tags was wrong** and is superseded. It was
produced without a JavaScript engine; SiteGround's SG-Captcha returns a 179-byte stub to any
non-JS client. Re-tested in headless Chrome at 1440×900 and 390×844.

**GTM: ✅ PASS** on all five pages, both viewports — one snippet, one noscript, one `gtm.js`
200, container + `dataLayer` live, no duplicate container, Consent Mode v2 present.

**Phones: ⛔ FAIL.** Three `tel:` links per page:

| href | Desktop | Mobile | Verdict |
|---|---|---|---|
| `tel:4107056354` | visible | visible | ⚠️ right number, missing `+1` |
| `tel:(410) 705-6354` | visible | visible | ⚠️ right number, malformed href |
| **`tel:+14109141456`** | 0×0 hidden | **visible 175×37** | ⛔ **unapproved number** |

**Correction to the fresh-check note in the order:** the hidden link is **not**
`tel:+14107610932` — that number is entirely absent. The live defect is
**(410) 914-1456**, and it is **hidden on desktop but visible and tappable on mobile**, the
opposite of what was reported. It is a hardcoded Divi button (`et_pb_button_5`), not number
swapping — the other two links on the same page carry the approved number, and a swap script
would rewrite all three consistently. **What (410) 914-1456 is, is Question 2 in §9.**

**Attribution: ⛔ FAIL — this is the measurement blocker.** On a click carrying gclid, gbraid,
wbraid and all five UTMs, the parameters survive in the URL and `_gcl_aw` is written, but **all
seven Gravity Forms hidden fields `input_9`…`input_15` are empty** and `gform_field_values` is
empty. **Dynamic population is not configured.** A submitted lead carries no click ID — so
**offline conversion import cannot work as built**, independent of ClickCease.

**Also found:** three `#gform_1` instances per page (duplicate element IDs ×3, breaking label
association and any GTM selector); a field labelled "(optional)" but enforced as required; no
privacy or terms link anywhere; cross-service H2s on `/hvac-repair/` ("Recent AC Repair Work")
and `/gas-boiler-repair/` ("Your HVAC Replacement in 3 Simple Steps"); undocumented Microsoft
UET, Meta and Nextdoor-style pixels. **TLS is ✅ fine** (TLS 1.3, Let's Encrypt, 84 and 82 days
remaining). No countdown timers or placeholder content. The Gravity Forms honeypot is correctly
hidden and is **not** a defect.

**ClickCease redirect test: ⚠️ BLOCKED, not failed.** `monitor.clickcease.com` resolves to
**127.0.0.1** from this machine and `www.clickcease.com` refuses connection, while control
lookups resolve normally and the local `hosts` file is empty — a **network-level DNS sinkhole on
the test machine**, not a site defect. I am explicitly *not* reporting a ClickCease failure.
Re-run `clickcease.py` from an unfiltered network, or click a live ad. **The outcome does not
change the remediation**: the form discards attribution regardless.

---

# 6. Conversion and attribution cleanup — DRAFTED

**Package:** `plans/conversion-goal-package-2026-08-18.json` · **Fingerprint:** `FDE2966C4695C96C`
**Modifies 3. Creates 0. Removes 0. 2 objects blocked pending your answer.**

*(OBSERVED)* The prior finding is confirmed: **`Call BTN Click` (6498555484)** is Primary and
biddable while measuring a telephone-link tap. Two further problems were not previously reported:

- **`Visit Thank you page - Submit Form` (6498555481) is a second Primary SUBMIT_LEAD_FORM/WEBSITE
  action** alongside `Ambient Cooling - LP -Submit Lead Forms` (6885463625) — one lead counted twice.
- **`WC Calls` (7643656075) and `WC Lead` (7643656486)** are Primary WhatConverts upload actions
  in category **CONTACT**, and **WhatConverts is genuinely live on the paid pages** (`wc_visitor`,
  `wc_client`, `wc_swap` cookies) — contradicting `client.yaml`'s `whatconverts_expected: false`.

| Action | Now | Proposed |
|---|---|---|
| 6885463625 LP Submit Lead Forms | Primary | **Primary** — the single form action |
| 6498555481 Visit Thank you page | Primary | → **Secondary** (duplicate) |
| 1068114183 Calls from ads (60s) | Primary | **Primary** — the qualified-call action |
| 6885576934 LP Phone call leads (30s) | Primary | **Primary, duration 30s → 60s** |
| 6498555484 **Call BTN Click** | **Primary** | → **Secondary, observation only** |
| 7643656075 WC Calls / 7643656486 WC Lead | Primary | **BLOCKED** — see Question 1 |

**Campaign goals:** all five campaigns inherit the account defaults, which make
`CONTACT/WEBSITE` and `CONTACT/CALL_FROM_ADS` biddable — that is precisely what makes a tel tap
biddable. Proposed: remove both, leaving `SUBMIT_LEAD_FORM/WEBSITE`, `PHONE_CALL_LEAD/WEBSITE`
and `PHONE_CALL_LEAD/CALL_FROM_ADS`.

**Honest scoping note:** all five campaigns run **TARGET_SPEND (Maximize Clicks)**, which does
**not** use conversion goals to bid. Today the damage is reporting and attribution
contamination, not bid distortion. It must still be fixed **before** any move to Maximize Conversions.

**Call asset:** 407995613637 carries **(410) 705-6354**, US, APPROVED, on all five campaigns
*(OBSERVED)*. Proposed: bind it explicitly to `1068114183` rather than relying on the
account-level default. **The phone number does not change.**

The plan preserves gclid, gbraid, wbraid, all UTMs, lead ID, campaign, ad group, keyword,
device, landing page, consent state and sold outcome, with a dedup rule and an 8-case test
matrix. **It cannot deliver sold-job attribution until the Gravity Forms defect in §5 is fixed** —
that prerequisite is recorded in the package.

---

# 7. Rebuilt search-term and negative-keyword package — DRAFTED

**Package:** `plans/negative-keyword-package-2026-08-18.json` · **Fingerprint:** `E0D26EF2943B941D`
**Supersedes `12E7572A25B9AFF0`, which was not applied and must not be.**
**Creates 1 shared list + 110 negatives. Modifies 0. Removes 0.**

**Corpus read** *(OBSERVED)*: 43,415 search-term rows across five windows (since launch, 30, 90,
365 days, and all time back to 2019), **21,687 unique terms**, $84,404 of historical term spend.
Full per-term workbook: `exports/search-term-verdicts-2026-08-18.csv`.

## Why the old package was wrong, and how this one differs

The superseded package ran a literal conflict check that returned zero conflicts — and still
proposed `heater repair`, `residential boilers`, `ac refrigerant leak`, `furnaces`,
`heat pumps installation` and broad Phrase negatives like `capacitor` and `air filter`. It had
no notion of **whether a term could even reach these campaigns**, and no semantic review.

This rebuild adds two things:

1. **An evidence-calibrated reachability model.** The five live keywords are Phrase and Exact
   only, so most historical terms can never match them. My first model required core noun +
   action verb; the live data **disproved** it — Google matched `hvac companies near me` and
   `hvac mold remediation near me` to Phrase `hvac repair near me`, and `hvac washington dc` and
   `ductless installation` to Phrase `hvac installers`. I widened the model to the core noun
   alone, which surfaces **more** terms for review, never fewer.
2. **A human semantic pass** on every surviving candidate.

**Result:** of 21,687 unique terms, only **424** are both reachable and out of scope. Together
they account for **$432.33 of spend over seven years, 19 clicks, and 0.00 conversions.**

| Bucket | Terms | Clicks | Cost | Conv | Verdict |
|---|---:|---:|---:|---:|---|
| Vehicle & marine A/C | 26 | 4 | $82.77 | 0 | **NEGATIVE — priority 1** |
| Adjacent trades (mold, insulation…) | 103 | 8 | $176.78 | 0 | **NEGATIVE, partly re-routed** |
| Parts / retail / wholesale | 57 | 2 | $77.42 | 0 | **NEGATIVE** |
| Out of area (VA, DC, other metros) | 197 | 4 | $77.95 | 0 | **NEGATIVE, narrow** |
| Employment | 19 | 1 | $17.41 | 0 | **NEGATIVE** |
| DIY / research | 10 | 0 | $0.00 | 0 | NEGATIVE |
| Unrelated boiler / appliance / recall | 7 | 0 | $0.00 | 0 | NEGATIVE |
| Training | 5 | 0 | $0.00 | 0 | **REJECTED — false positives** |

## The single most valuable finding

**`car air conditioner repair near me` cost $47.78 on 2 clicks on 2026-08-17** — that is
**more than half of the AC Repair campaign's entire lifetime spend**, on a car-A/C query, matched
via Phrase `ac repair near me`. Vehicle A/C is the one bucket with proven waste against the live
campaigns and it is priority 1.

## Where I overruled the classifier

- **`program`, `degree`, `class`, `certification` — REJECTED.** `program` would have blocked
  *"heating & air conditioning preventative maintenance program"* (a maintenance-plan lead) and
  *"advantage program hvac"*; `degree` would have blocked the competitor *"a degree above heating
  and cooling"*. Exactly the class of error the old package made.
- **`plumbing` / `plumber` (61 terms) — re-routed, not negatived.** These are almost entirely
  **competitor company names** (F.H. Furr *Plumbing* Heating Air Conditioning, Len the *Plumber*,
  Shepherd *Plumbing* Heating A/C), not plumbing-service demand. Sent to competitor review.
- **`chimney` — dropped by the conflict checker**, which caught it blocking
  *"oil furnace chimney sweep near me"*. Removed rather than overridden.
- **`manual` — rejected**, collides with *"manual j load calculation"*.
- **bare `va` and `dc` — rejected.** `va` collides with VA Medical Center commercial work.
  Only explicit VA city names and non-MD metros are proposed. **`Columbia` and `Chesapeake` are
  excluded** because both name Maryland places.
- **`duct cleaning`, `union`, `water heater`, `thermostat`, `commercial` — WATCH, not negative.**

## Conflict testing — 0 conflicts

All 110 proposals were tested **literally and semantically** against a **287-query protected
set**: the five active keywords, every term that ever converted, every KEEP term costing ≥$25,
and every term the old package would have wrongly blocked.

- **Conflicts with the 287 protected queries: 0**
- **Conflicts with the five active keywords: 0**
- Verified still eligible: `ac capacitor repair`, `ac refrigerant leak`, `heater repair`,
  `residential boiler repair near me`, `commercial boiler repair`, `furnaces`, `hvacs`,
  `heat pumps installation`, `emergency ac repair near me`, `cheap ac repair near me`,
  `ac repair price`, `hire hvac contractor`, and every `near me` / `quote` / `cost` / `best` /
  `local` variant. **None of the protected modifiers is negatived.**

**Cross-service negatives: none proposed.** The five ad groups have distinct core nouns and the
since-launch data shows no internal overlap. Proposing them now would be speculative.

**Competitor terms: 11 surfaced for your manual review**, not negatived. Note that
`f h furr plumbing heating air conditioning & electrical` took **$21.72 of the $92.18 spent
since launch** — competitor conquest at $21.72 a click with broken conversion tracking is
expensive, but it is your commercial call, not mine.

## Shared-list reuse verdicts *(OBSERVED)*

**None of the 17 shared lists is currently attached to any of the five new campaigns, and the
campaigns have zero campaign-level and zero ad-group-level negatives.**

| List | Members | Verdict |
|---|---:|---|
| `10664309518` States List | 48 | ✅ **SAFE TO REUSE** — 0 conflicts |
| `12025671131` GM \| Competitor Brands | 17 | ✅ **SAFE TO REUSE** |
| `12021721179` GM \| Broad Poison | 5 | ⚠️ **REUSE AFTER CLEANUP** — drop BROAD `technicians` |
| `12021722439` GM \| Phrase Blockers | 6 | ⚠️ **REUSE AFTER CLEANUP** — drop PHRASE `hvac work` |
| `10664304544` Names List | 486 | ⚠️ **REUSE AFTER CLEANUP** — 3 conflicts |
| `12022987128` GM \| Competitor Name Tokens | 17 | ⚠️ **REUSE AFTER CLEANUP** — BROAD surnames incl. `plumbing`, `capital` |
| `10720232972` General | 1,148 | ⚠️ **REUSE AFTER CLEANUP** — 20 conflicts, incl. **PHRASE `of`**, `price`, `hire`, `cheap` |
| `12091293463` Ambient - Neg Kwd List | 968 | ⚠️ **REUSE AFTER CLEANUP** — 56 conflicts; 929 BROAD; blocks `aircon`, **`arundel`**, `cheap`, `cleaning` |
| `11813144900` General List | 1,111 | ⛔ **DO NOT REUSE** — contains **BROAD `Repair`** and **BROAD `Fix`**; 170 conflicts |
| `12178646912` General List - Irrigation Repair | 1,107 | ⛔ **DO NOT REUSE** — landscaping vertical; 40 conflicts |
| Christmas Lights / Leaf Removal / Outdoor Kitchen / Paver | 386–424 | ⛔ **DO NOT REUSE** — landscaping in an HVAC account; 0 references, inert |

**No list is attached simply because it exists.**

---

# 8. The finding that was not in the brief — an account-wide negative list

**Package:** `plans/account-level-negative-cleanup-2026-08-18.json` · **Fingerprint:** `BC24DF875FCA1CDD`
**Approval class: DESTRUCTIVE — removes 22 existing negative criteria.**

*(OBSERVED)* Shared set **`11252984411`**, type **`ACCOUNT_LEVEL_NEGATIVE_KEYWORDS`**, status
**ENABLED**, holds **59 BROAD members**. This type applies **account-wide with no campaign
association**, which is why it does not appear in `campaign_shared_set` — and why it was missed.

Members that block Ambient's own demand:

| Negative | Why it is wrong | Historical cost |
|---|---|---|
| **`commercial`** | Blocks all commercial HVAC demand. The live HVAC Replacement RSA literally says **"Commercial HVAC Replacement"** | 344 terms, 49 clicks, **$1,043.02, 3.83 conversions** |
| **`hanover`** | Hanover, **MD** — Anne Arundel County, adjacent to Severn, inside the 75 targets | 52 terms, $50.46 |
| **`aac`** | Standard abbreviation for **Anne Arundel County**, the core service area | — |
| **`dayton`** | Dayton, **MD** — Howard County | 3 clicks, **1 conversion** |
| **`chestertown`** | Chestertown, **MD** | 3 clicks, **2 conversions** |
| **`montgomery county`** | Maryland county | 1 click, **1 conversion** |
| **`upper marlboro`** | Maryland town | 2 clicks |
| **`thermostat`, `thermostats`** | Thermostat faults are ordinary HVAC repair demand | 102 terms |
| **`attic`** | Attic air handlers are in scope | 35 terms, $112.41 |
| **`contract`** | Blocks "hvac service contract" | — |
| **`ruud`, `rudd`, `ducane`, `frigidaire`, `ecobee`** | Manufacturer brands — "ruud furnace repair near me" is service demand | 91 terms |
| **`white`** | Collides with White Marsh, MD | 54 terms |

Also present: a junk non-Latin single-character entry, and `financing` — which is worth **keeping**.

**Honest limitation:** the API reports `member_count = 0` for this set while `shared_criterion`
returns 59 rows, and I cannot prove from the API alone that Google is currently enforcing it.
**Confirm in the UI** (Tools → Shared library → Account-level negative keywords) **before
applying.** The supporting signal is suggestive but not conclusive: `commercial` queries earned
$367 in the last 365 days and **$0 in the last 90**, though the campaigns were mostly paused then.

**This is plausibly a partial cause of the 10–18% impression share.**

---

# 9. Three questions — everything else is decided

These are the only items that need a business decision rather than technical judgment.

### Question 1 — Is WhatConverts the intended call-tracking platform?
`client.yaml` records `whatconverts_expected: false`, but WhatConverts is **live on all five paid
pages** and two WhatConverts upload actions are **Primary** in Google Ads. Two authoritative
sources conflict, so I have not touched either.
**If unanswered:** `WC Calls` and `WC Lead` stay Primary in category CONTACT and keep
contaminating the Conversions column. **My recommendation:** keep WhatConverts, recategorize
`WC Calls` to `PHONE_CALL_LEAD` and set `WC Lead` to Secondary.

### Question 2 — What is (410) 914-1456?
It is the mobile "Call Now" button on all five paid pages. It is neither the approved paid
number nor the main-site number, and I will not guess.
**If unanswered:** the primary mobile call CTA keeps dialling an unattributable number on a
mobile-dominant traffic mix. **My recommendation:** replace it with `tel:+14107056354` unless you
confirm it is a deliberate tracking number.

### Question 3 — ✅ ANSWERED 2026-08-18: 24/7 approved
Green Marketing confirmed all five campaigns may run 24 hours a day, 7 days a week; business
hours stay 08:00–16:00; unanswered calls go to voicemail with prompt follow-up; and no
availability claim may appear anywhere. **See §14 for the exact plan.** One prerequisite
remains: the voicemail path itself is unverified, because confirming it requires placing a real
call — see §14.

---

# 10. Campaign configuration — DRAFTED (v2)

**Package:** `plans/campaign-configuration-package-2026-08-18-v2.json` · **Fingerprint:** `50701AE742FCDEEB`
**Supersedes `3094F3F31663517F`, which is now INVALID** — v1 recommended keeping the Mon–Fri
08:00–20:00 + Sat schedule. See §14 for the 24/7 schedule plan.

- **Sitelinks ⛔** — all 9 assets point at the main site, which has a different phone and no
  matching form. Proposed: create 5 new sitelinks pointing at the existing `offer.` service
  pages (cross-sell), then unlink the 9 main-site sitelinks (28 campaign-asset links,
  **destructive approval**). **Reviews, Our Work, Service Areas and Contact have no compliant
  offer-subdomain equivalent — I am not inventing destinations.** Building them is a separate
  landing-page workflow under `LANDING_PAGE_CONTENT_WORKFLOW.md`.
- **Networks and automation ✅** — verified correct on all five: Search only, Partners off,
  Display off, PRESENCE both ways, no DSA, no campaign tracking template. Nothing to change.
- **Rogue ad group ⚠️** — 202339087874 is already REMOVED and cannot serve; its 2 ads and 2
  keywords are cosmetic debris. **Recommendation: leave until the replacements are live.** Every
  mutation carries risk during remediation, and this one buys nothing.
- **Budgets ⛔ no change** — $427.64/day = $13,000/month, exactly the approved allocation. Only
  4.3% is being spent and budget-lost impression share is ~0. Budget is not the constraint.
- **Landscaping shared lists — no action.** All have `reference_count = 0` and are inert.
  Deleting them destroys data for no delivery benefit.
- **Account-level callouts ⚠️** — `"Licensed & Insured"` and `"Claim Your Discount"` exist at
  account level (assets 89063098373, 89063098376). Both are on the barred-claims list and **no
  discount is published**. Campaign-level callouts take precedence so they should not serve with
  these five campaigns, but they are a standing risk worth removing separately.

# 11. Bidding — no change now

All five campaigns are on **TARGET_SPEND (Maximize Clicks)** *(OBSERVED)*, which is correct
while measurement is being repaired. **Do not move to Maximize Conversions** until there are
**≥14 days of reliable, deduplicated Primary conversion data**. Today there are **0 conversions
on 5 clicks**, and the form captures no attribution — the precondition is not close to met. A
separate bidding plan with volume, CPL/CPQL, target, risk and its own fingerprint comes later.

---

# 12. Approval register

| # | Package | Fingerprint | Creates | Modifies | Removes | Class |
|---|---|---|---:|---:|---:|---|
| 1 | Six replacement RSAs (**paused**) | **`0BCC73A397580856`** | 6 | 0 | 0 | create-paused |
| 2 | Negative keywords + shared list | **`E0D26EF2943B941D`** | 111 | 0 | 0 | create |
| 3 | Conversion goals | **`FDE2966C4695C96C`** | 0 | 3 | 0 | modify |
| 4 | Campaign configuration + **24/7 schedule** (v2) | **`50701AE742FCDEEB`** | 5 | 0 | 58 | **destructive** |
| 5 | Account-level negative cleanup | **`BC24DF875FCA1CDD`** | 0 | 0 | 22 | **destructive** |
| 6 | Landing-page remediation | *drafted, not fingerprinted* | — | — | — | needs site-scope authorization |
| — | Enable replacement RSAs | *issued after readback QA* | — | 6 | 0 | **separate approval** |
| — | Pause the 6 disapproved originals | *issued after replacements serve* | — | 6 | 0 | **destructive** |

**Recommended order:** 1 → (readback) → 5 → 2 → 3 → enable 1 → 4 → pause originals.
Package 5 comes early because it may be suppressing demand account-wide, and it is independent
of everything else.

Approve by naming the fingerprint. **Any edit to a package produces a new fingerprint and voids
the old approval.**

---

# 13. Deliverables written

```
clients/ambient-cooling-heating/
  client.yaml                                    UPDATED — ClickCease manager confirmed+protected;
                                                 GTM status corrected; third phone number; WhatConverts conflict
  work-order.yaml                                UPDATED — campaign-revamp/draft; validator PASS
  snapshots/pre-change-structure-2026-08-18.json         full pre-change resource inventory
  snapshots/pre-change-performance-2026-08-18.json       5 windows + 955 change events
  snapshots/landing-page-qa-2026-08-18.json              5 pages x 2 viewports
  snapshots/landing-page-attribution-test-2026-08-18.json
  exports/search-term-verdicts-2026-08-18.csv            21,687 terms, per-term verdicts
  exports/negative-candidates-2026-08-18.json            424 reviewed candidates
  plans/rsa-replacement-package-2026-08-18.json          0BCC73A397580856
  plans/negative-keyword-package-2026-08-18.json         E0D26EF2943B941D
  plans/conversion-goal-package-2026-08-18.json          FDE2966C4695C96C
  plans/campaign-configuration-package-2026-08-18-v2.json 50701AE742FCDEEB  (supersedes 3094F3F31663517F)
  snapshots/pre-change-schedule-2026-08-18.json           rollback source, 30 criteria verbatim
  plans/account-level-negative-cleanup-2026-08-18.json   BC24DF875FCA1CDD
  research/landing-page-qa-2026-08-18.md                 full landing-page evidence
reports/ambient-cooling-heating/
  2026-08-18-corrective-order-report.md                  this report
```

**Change log:** no resource was touched. Post-change readback reports will be written per phase
as each approval is executed, each proving unrelated resources were unchanged against the
pre-change snapshot above.

---

## Sources

- [Consumer finance in personalized advertising — Google Advertising Policies](https://support.google.com/adspolicy/answer/16700846?hl=en)
- [Restricted targeting in Personalized advertising — Google Advertising Policies](https://support.google.com/adspolicy/answer/143465?hl=en)
- [Fix a disapproved ad or appeal a policy decision — Google Ads Help](https://support.google.com/adspolicy/answer/9338593?hl=en)
- [Policy Exemption Requests — Google Ads API](https://developers.google.com/google-ads/api/docs/policy-exemption/overview)
- [Google Ads sets 6-month timeline for appeals — Search Engine Roundtable](https://www.seroundtable.com/google-ads-appeals-limit-41730.html)

---

# 14. 24/7 ad schedule — exact plan (supersedes the §9 Question 3 options)

**Package:** `plans/campaign-configuration-package-2026-08-18-v2.json`
**New fingerprint:** `50701AE742FCDEEB` · **Invalidates `3094F3F31663517F`**

## Confirmed facts driving this plan *(SUPPLIED 2026-08-18)*

- Published website/business hours remain **8:00 AM – 4:00 PM**.
- All five campaigns are **approved to run 24/7**.
- Unanswered calls go to **voicemail**, with prompt follow-up.
- The call asset stays eligible 24/7 once the voicemail path is verified.
- **No availability claim** may appear in ads or on landing pages.

## Current state *(OBSERVED, fresh read 2026-08-18)*

30 `AD_SCHEDULE` criteria — 6 per campaign × 5 campaigns. All `ENABLED`, all
`negative = false`, all `bid_modifier = 1.0`, so **no bid modifier is lost by removing them**.

**Only 65 of 168 hours per week are eligible — 38.7%. 103 hours per week are blocked.**
**No campaign has a Sunday row at all**, so Sunday is 100% ineligible on all five — a full
seventh of the week that a Mon–Sat view hides.

## Approach — remove, do not recreate

**Remove all 30 restrictive criteria and let Google Ads apply its default all-day, every-day
delivery.** A campaign with zero ad-schedule criteria already runs 24/7.

I am deliberately **not** creating seven all-day rows per campaign. That would be 35 objects
behaving identically to zero objects, while adding 35 more things to audit, 35 more chances of a
partial write, and re-introducing the exact pattern that caused this problem.

## Every criterion that would be removed

| Campaign | Campaign ID | Criterion ID | Day | Current window | Bid mod | End state |
|---|---|---|---|---|---|---|
| AC Repair | `24132507741` | `24132507741~303280` | Monday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| AC Repair | `24132507741` | `24132507741~313280` | Tuesday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| AC Repair | `24132507741` | `24132507741~323280` | Wednesday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| AC Repair | `24132507741` | `24132507741~333280` | Thursday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| AC Repair | `24132507741` | `24132507741~343280` | Friday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| AC Repair | `24132507741` | `24132507741~353252` | Saturday | 08:00-13:00 | 1.0 | **removed -> 24/7** |
| Gas Boiler Repair | `24132507744` | `24132507744~303280` | Monday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| Gas Boiler Repair | `24132507744` | `24132507744~313280` | Tuesday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| Gas Boiler Repair | `24132507744` | `24132507744~323280` | Wednesday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| Gas Boiler Repair | `24132507744` | `24132507744~333280` | Thursday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| Gas Boiler Repair | `24132507744` | `24132507744~343280` | Friday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| Gas Boiler Repair | `24132507744` | `24132507744~353252` | Saturday | 08:00-13:00 | 1.0 | **removed -> 24/7** |
| HVAC Installation | `24132507747` | `24132507747~303280` | Monday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Installation | `24132507747` | `24132507747~313280` | Tuesday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Installation | `24132507747` | `24132507747~323280` | Wednesday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Installation | `24132507747` | `24132507747~333280` | Thursday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Installation | `24132507747` | `24132507747~343280` | Friday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Installation | `24132507747` | `24132507747~353252` | Saturday | 08:00-13:00 | 1.0 | **removed -> 24/7** |
| HVAC Repair | `24132507750` | `24132507750~303280` | Monday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Repair | `24132507750` | `24132507750~313280` | Tuesday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Repair | `24132507750` | `24132507750~323280` | Wednesday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Repair | `24132507750` | `24132507750~333280` | Thursday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Repair | `24132507750` | `24132507750~343280` | Friday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Repair | `24132507750` | `24132507750~353252` | Saturday | 08:00-13:00 | 1.0 | **removed -> 24/7** |
| HVAC Replacement | `24132507753` | `24132507753~303280` | Monday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Replacement | `24132507753` | `24132507753~313280` | Tuesday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Replacement | `24132507753` | `24132507753~323280` | Wednesday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Replacement | `24132507753` | `24132507753~333280` | Thursday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Replacement | `24132507753` | `24132507753~343280` | Friday | 08:00-20:00 | 1.0 | **removed -> 24/7** |
| HVAC Replacement | `24132507753` | `24132507753~353252` | Saturday | 08:00-13:00 | 1.0 | **removed -> 24/7** |

Resource-name form: `customers/2401959466/campaignCriteria/{campaign_id}~{criterion_id}`.
All 30 are listed verbatim in the package and in
`snapshots/pre-change-schedule-2026-08-18.json`.

## Proposed 24/7 end state

| Campaign | Criteria before | Criteria after | Hours/week before | Hours/week after |
|---|---:|---:|---:|---:|
| AC Repair `24132507741` | 6 | **0** | 65 (38.7%) | **168 (100%)** |
| Gas Boiler Repair `24132507744` | 6 | **0** | 65 (38.7%) | **168 (100%)** |
| HVAC Installation `24132507747` | 6 | **0** | 65 (38.7%) | **168 (100%)** |
| HVAC Repair `24132507750` | 6 | **0** | 65 (38.7%) | **168 (100%)** |
| HVAC Replacement `24132507753` | 6 | **0** | 65 (38.7%) | **168 (100%)** |

## Total mutation count

| Operation | Count |
|---|---:|
| `CampaignCriterion` **remove** (AD_SCHEDULE) | **30** |
| `CampaignCriterion` create | 0 |
| `CampaignCriterion` modify | 0 |
| Campaign / budget / bidding changes | 0 |
| Asset changes | 0 |
| **Total mutations for the schedule change** | **30** |

Sent as **one atomic `MutateCampaignCriteria` request with `partial_failure = false`**. If it
fails, I stop, re-query to inventory exactly what was removed, and produce a recovery plan
before any retry.

**109 AD_SCHEDULE criteria on 19 other (paused/removed) campaigns are NOT touched.**

## Call asset — 24/7 with zero mutations *(OBSERVED)*

Call asset **`407995613637`**, phone **(410) 705-6354**, has **`ad_schedule_targets = 0`** — it
carries **no schedule of its own** — and reports `primary_status = ELIGIBLE` on all five
campaigns. Its eligibility is governed entirely by the campaign schedule, so **removing the 30
criteria makes it eligible 24/7 with no asset mutation.**

I also verified **no sitelink or other asset** carries `ad_schedule_targets`, `start_date` or
`end_date`, and that the only criterion types on these campaigns are LANGUAGE (5), DEVICE (15),
AD_SCHEDULE (30) and LOCATION (375). **The 30 campaign criteria are the only time gate.**

> ⚠️ **Prerequisite I cannot clear myself.** Verifying that (410) 705-6354 actually reaches
> the approved voicemail outside 08:00–16:00 requires **placing a real telephone call**, which is
> barred without separate test approval. Either confirm the out-of-hours path yourself, or grant
> explicit test-call approval. **I recommend clearing this before applying**, since the whole
> point of 24/7 delivery is that overnight callers land somewhere recoverable.

## Readback verification procedure

1. `SELECT campaign.id, campaign_criterion.resource_name FROM campaign_criterion WHERE campaign_criterion.type = 'AD_SCHEDULE' AND campaign.id IN (the five)` → **assert 0 rows**.
2. Same query **without** the campaign filter → **assert exactly 109 rows**, all on legacy campaigns — proves no unrelated campaign was touched.
3. Assert all five campaigns still return `ENABLED` / `SERVING` / `TARGET_SPEND` and their original budgets ($141.45 / $42.76 / $138.16 / $78.95 / $26.32).
4. Assert criterion-type counts per campaign are now LANGUAGE 1, DEVICE 3, LOCATION 75, **AD_SCHEDULE 0**.
5. Assert call asset `407995613637` is still attached to all five with phone `(410)705-6354` and `primary_status = ELIGIBLE`.
6. Assert both manager links remain ACTIVE, **including ClickCease `2815082755`**.
7. Compare the mutate response resource-name count to **exactly 30**.
8. After 48 hours, segment by `segments.hour` and `segments.day_of_week` and confirm impressions now appear outside 08:00–20:00 **and on Sunday**.

## Rollback plan

- **Trigger:** any readback assertion fails, or Green Marketing reverses the 24/7 decision.
- **Method:** re-create the same 30 criteria via `MutateCampaignCriteria` create operations using
  the exact day / start / end / `bid_modifier = 1.0` recorded above.
- **Restore mutations:** 30.
- **Source of truth:** `snapshots/pre-change-schedule-2026-08-18.json`, captured read-only before
  any change.
- **Expected IDs:** Google derives ad-schedule criterion IDs deterministically from day and time
  span, so the same IDs (303280, 313280, 323280, 333280, 343280, 353252) should return. **Verify
  by resource name after rollback rather than assuming.**
- **Data loss: none.** Ad-schedule criteria hold no performance history; hour-of-day and
  day-of-week reporting stays available through `segments.hour` / `segments.day_of_week`.

## Budget interaction — watch, do not pre-empt

Unblocking 103 hours per week roughly **2.6×** the eligible time. Under Maximize Clicks the daily
budget still caps daily spend, so **total spend will not rise**, but it will spread across more
hours and the daily budget may now be exhausted earlier in the day. Watch
`search_budget_lost_impression_share` (currently ~0). **Do not raise budgets pre-emptively.**

---

# 15. Availability-claim scan — the RSA package is CLEAN

Scanned all 15 headlines and 4 descriptions of each of the 6 drafted RSAs, all 12 live RSAs, all
271 campaign assets, all 3 account-level assets, and the visible text of all five landing pages.

## ✅ `0BCC73A397580856` is UNCHANGED and remains valid

**Zero** availability, hours, or after-hours claims in the drafted replacement RSAs — no
mention of 24/7, emergency, same-day, after-hours, night, weekend, or response time.
**No new RSA fingerprint is required.** The 12 live RSAs are equally clean.

## ⚠️ Flagged outside the RSA package

| Surface | Item | Issue |
|---|---|---|
| Callout `407418595411` (all 5 campaigns) | "Prompt, Reliable Service" | "Prompt" is a responsiveness claim that can now serve at 02:00; `client.yaml` bars `response_time_promise` |
| `/hvac-repair/` body | "Prompt, Customer-Focused Service" | Same claim on the page |
| All 5 pages | "Call Now: (410) 705-6354" | Implies live answering; soften to "Call Ambient" |
| Sitelinks `407418567061`, `407494691220` | "See available HVAC/heating services" | **False positive** — "available" describes the catalogue, not hours. Already slated for unlinking |
| `/gas-boiler-repair/` | "Smell gas? Leave immediately and call your gas utility or 911..." | **False positive — a correct safety notice. Keep it.** |

Replacing the callout needs its own approval and is **not** in this package's mutation count.

## ⛔ Correction to my own landing-page QA

While scanning for availability language I found two things I previously reported wrongly:

1. **I reported "no countdown timer, no artificial scarcity." That was wrong.** All five pages
   carry a manufactured daily deadline — `/ac-repair/` and `/hvac-repair/` say "**before
   today's timer reaches zero**"; the other three say "**before today ends**"; `/ac-repair/` adds
   "**We are accepting new clients**". **This gets worse under 24/7 delivery**, since overnight
   traffic meets a timer that just expired or silently reset.
2. **I did not report the published review quotes.** Three testimonials per page, labelled
   "Google Review" (`/ac-repair/`, `/hvac-repair/`) or "Customer Review"
   (`/gas-boiler-repair/`), and **each renders three times** alongside the duplicate sections.
   `client.yaml` bars `rating_or_review_count` until verified in writing, so provenance needs
   checking against the Google Business Profile.

Also newly found: `/hvac-installation/` carries **"honest, upfront pricing"** in visible body
text — the exact phrase the prior audit suspected in the *ads*. It does **not** explain the
full CONSUMER_FINANCE pattern (`/gas-boiler-repair/` has no finance language and is disapproved
anyway), but it is removable finance-adjacent copy on a disapproved destination and should go as
appeal hygiene.

Full detail in `research/landing-page-qa-2026-08-18.md` §10, §10b, §10c, §10d.
