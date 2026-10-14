# MasterGrass - Live: deep audit, 2026-09-26

**Identity:** MasterGrass - Live | child 9487471092 | vertical landscaping | scope: every service with spend (Landscaping Search - BOFU 23905193676, Hardscaping Search - BOFU 23914692658) | manager 3373711342 ACTIVE | read-only, nothing changed.

Gate: `clients/mastergrass-lawn-care/work-order.yaml` + `client.yaml` created and validated (PASS); fresh API identity check PASS (`reports/mastergrass-lawn-care/evidence/2026-09-26-identity.json`).

## Executive finding

The last 7 days (Sep 19-25) cost **$386.06 for 12 clicks and 0 leads**, and **$374.67 (97%) of it was spent Sep 23-25**, right after three same-week changes: Landscaping was switched from capped Maximize Clicks ($25) to uncapped Maximize Conversions (Sep 21), its budget went from $36.90 to $132/day (Sep 23), and broader phrase keywords were added (Sep 23). CPC went from **$17.97 (Sep 1-20) to $37.47 (Sep 23-25)**. Hardscaping was also moved to Maximize Conversions (Sep 23) and has served 13 impressions in 7 days.

Twelve clicks at the June-July click-to-lead rate (~11%) predicts ~1.3 leads, so one empty week is not proof by itself. The real problem is older and bigger:

1. **Most calls to Master Grass are not reaching anyone.** Since **2026-07-28**, **111 of 160 calls (69%)** across every tracking number (GBP, website, Facebook, LSA and both paid-search numbers) ended on the carrier message *"...has a voicemail box that has not been set up yet. Please try your call again later. Goodbye."* Every number forwards to the same business line (ending 2765). Before Jul 28, unanswered callers reached a working voicemail. Only **5 calls in two months** (all channels) lasted a minute or more without that message. Last 7 days: 12 of 19 calls failed this way; 3 were real conversations. Paid-number calls since Jul 28: 6 of 11 failed.
2. **Paid search stopped producing new leads in August, and Google Ads could not tell.** WhatConverts unique paid leads: June 8 ($200 each), July 10 ($137), **August 0**, Sep 1-18 3, last 7 days 0. Over the same August, Google Ads reported **9 conversions**. Every August "WC Call Lead" came from a repeat caller or a tester (one caller rang 5 different tracking numbers across 2 days), and WhatConverts uploaded about **2 conversions per real forwarding-number call** (11 WC Call Lead conversions Aug 20 - Sep 8 against 6 forwarding-number calls). The Sep 21/23 switch to Maximize Conversions then handed bidding to that polluted signal.
3. **Demand is small and falling with the season.** Landscaping eligible impressions: ~1,600 (June) -> ~1,150 (July) -> ~585 (Aug) -> ~500/month (Sep). At 5% CTR that is ~25 clicks and roughly 2-3 leads a month even when everything works.

## Evidence

| # | Issue | Impact | Exact resource | Confidence |
|---|---|---|---|---|
| 1 | Business line voicemail not set up; 69% of calls since Jul 28 hear "not set up yet ... goodbye" | Lost callers on every channel, including paid | WhatConverts account 64716 / profile 94840, destination ...2765, all 6 tracking numbers; transcripts (k-anonymous phrase count, 70-74 of 78 calls at 45-49 s) | High |
| 2 | Uncapped Maximize Conversions + budget 3.6x on Landscaping | CPC +109%; $374.67 in 3 days, 0 leads | Campaign 23905193676: `target_spend` $25 ceiling removed 2026-09-21 16:15; budget 15630863938 $36.90 -> $132.00 2026-09-23 08:46 (both web UI, agency login) | High |
| 3 | Hardscaping stalled | 13 impressions / 7 days | Campaign 23914692658: top keyword paused 09-21 16:20; switched to Maximize Conversions 09-23 09:32 with 0 conversions in the prior 30 days | High |
| 4 | Bidding goal is polluted | Smart bidding learns from tests/repeats and ~2x double uploads | Custom goal 6458035587 = "WC Call Lead" (7636028109, UPLOAD_CALLS) + SUBMIT_LEAD_FORM/WEBSITE ("WC Form Lead" 7636013230). Aug WC Call Lead 8 conversions vs 0 unique paid calls | High |
| 5 | Paid calls filed as "duplicate" and relabelled GBP Traffic in WhatConverts | Paid calls invisible in the default WC report and API | Aug 20, 26, 27 forwarding-number calls matched to WC by time and duration; WC API returns duplicates/spam only when asked | High |
| 6 | Landing pages: form header says "Hardscaping" on the Landscaping page | Intent mismatch on the highest-spend page | offer.mastergrasslawncare.com/landscaping-contractor/ | High |
| 7 | Landing pages: identical 3 testimonials (Sarah M / Daniel R. / Emily T.) on all 10 offer pages, evergreen "Offer ends in 95 days" (3 days on two pages) countdown for a free quote, "Callback <10 min", "Install start <=7 days", "Project complete on time" | Trust and policy risk (FTC fake-review rule, Google misrepresentation); "Callback <10 min" is contradicted by finding 1 | All 10 offer pages | High (claims) / Unverified (testimonial authenticity) |
| 8 | Ads and every H1 name **Altoona**, but Altoona (50009) is not targeted | Copy speaks to a town the campaign cannot reach | Targets: Ames + 21 ZIPs + 1-mile radius; "Altoona" headlines drew 309+ impressions | High |
| 9 | Quality Score 1-4, expected CTR "below average" on every keyword that has a score | Higher CPC for the same position | e.g. landscaping companies near me QS 1, landscaping services QS 4 | High |
| 10 | One RSA per ad group; ad strength POOR on Pavers, Patios, Outdoor Kitchens | Less testing, weaker CTR | 10 enabled RSAs, 0 pins, 0 image/logo/business-name assets | High |
| 11 | Old shared negative lists are attached only to paused campaigns | Live campaigns rely on ~82 campaign negatives each | 19 shared sets; attaching "Leaf Removal initial", "Outdoor Kitchen" or "Paver" would block 19-23 live keywords each, "General Negative Keyword List" would have blocked $245 of in-scope terms | High |
| 12 | No UTM suffix; every click goes through a ClickCease redirect | WhatConverts can only attribute paid via gclid; iOS gbraid/wbraid clicks become "direct" | Customer tracking template `monitor.clickcease.com/...`; final_url_suffix empty at every level. ClickCease redirect could not be tested (DNS-blocked here) | Medium |
| 13 | French Drain ad group "Not eligible: has disapproved ads" while its only ad is APPROVED and served this week | Status contradiction to check in UI | Ad group 195877148126 / ad 811758936858 | Low |

Search terms: 580 unique live-campaign terms. All-time visible cost $2,704: 51% commercial in-scope, 29% in-scope without clear intent, 11% out-of-scope ($309), 6% other Master Grass services such as lawn and tree work ($158). The last 7 days show only $189.90 of the $386 (49% of spend has no visible query); $73.07 of the visible part was lawn/tree queries. **Negatives would have saved about $73 of last week's spend. They are a hygiene fix, not the cause.** Negative keywords don't match plurals, so the existing "tree service" negative did not stop "tree services".

WhatConverts last 7 days: 0 paid-labelled leads. Two offer-page web forms (Sep 23 08:48, Sep 26 10:56) are the same contact, both direct to the offer root URL (no ad uses it), both marked Repeat. The Sep 23 form came 2 minutes after the Sep 23 budget edit, which looks like an internal test. No lost paid lead was found.

## Economics (live campaigns, June 1 - Sep 25)

Spend $4,939 | WhatConverts unique paid leads 21 | cost per unique paid lead **$235** (upper bound, calls on untracked paths excluded) | quotable "Yes" 4 -> **$1,235 per quotable lead**. Hardscaping: $1,866 since June for about 1 quotable call. No revenue, close-rate or margin data exists, so CAC/ROAS/profit cannot be computed.

## Prioritized actions (ranked by recoverable dollars)

| Rank | Action | Owner | Expected effect |
|---|---|---|---|
| 1 | **Fix the phone line ending 2765**: set up voicemail today, or route unanswered calls to a WhatConverts voicemail/call queue. Then place one test call per tracking number. | Client (+ agency for WC routing) | Stops losing ~69% of callers on every channel. Biggest lever by far |
| 2 | **PLAN-A bid reset**: Landscaping back to Maximize Clicks with a $25 CPC ceiling and budget $36.90/day (last values before Sep 21-23). **Pause Hardscaping** for the off-season. | Agency, needs approval | Roughly halves CPC (Sep 1-20 $17.97 vs $37.47). At the Sep 23-25 run rate (~$2,700/month on weekdays) the same clicks would cost ~$1,300 at the old CPC: ~$1,400/month saved |
| 3 | **Clean the conversion signal** in WhatConverts' Google Ads integration: upload only Unique leads and calls >=60 s, never duplicates or spam, and mark the tester's number internal. Keep "MasterGrass - Lp - Submit Lead Form" secondary. | Agency, needs approval (WhatConverts write) | Makes future smart bidding possible; stops ~2x inflation |
| 4 | **Landing-page fixes** (developer): Landscaping form header; remove the countdown; remove "Callback <10 min" / "Install start <=7 days" / "on time" until verified; replace the 3 template testimonials with real Google reviews (or remove them); fix the duplicate `gform_1` ids; add gbraid/wbraid hidden fields. | Developer after client facts | Conversion rate and policy safety |
| 5 | **PLAN-C second RSA** for Landscaping Contractor, French Drain and Retaining Walls (drafted, validated: 0 failures). Pins the keyword headline in position 1, drops Altoona, uses verified claims only. Existing RSAs stay live as the control. Created paused. | Agency, needs approval | Targets expected CTR (below average everywhere) and QS |
| 6 | **PLAN-B negatives**: 93 campaign-level objects (63 phrase from agency vocabulary, 20 exact out-of-scope, 8 shared-lexicon phrase, 2 exact lawn-service). 0 conflicts with 145 live keywords, 0 converting terms blocked. Do **not** attach the old shared lists. | Agency, needs approval | ~$120-190/month of visible waste |
| 7 | Add a final URL suffix `utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}&utm_term={keyword}` at account level | Agency, needs approval | WhatConverts attributes paid sessions even without gclid |
| 8 | Altoona: add 50009 to targeting or remove it from ads and H1s | Client decision | Relevance |

## Draft files (local, nothing executed)

- Negatives: `clients/mastergrass-lawn-care/plans/NEG-0926-DRAFT.csv` (93 objects, sha256[:12] DF1ED0718D26). Guard detail: `reports/mastergrass-lawn-care/st/negative-proposal-strategist.csv`, `negative-candidates.csv`, `verdicts.csv` (raw terms on disk only).
- RSAs: `clients/mastergrass-lawn-care/plans/RSA-0926-DRAFT.json`.
- Evidence: `clients/mastergrass-lawn-care/snapshots/audit-2026-09-26/` (API snapshot + redacted WhatConverts), `reports/mastergrass-lawn-care/evidence/` (identity, landing-page browser audit, page text).
- Scripts: `scripts/mg_0926_*.py`, `scripts/mg_lib.py`.

To execute any plan: approve it by name, then the work order moves from `mode: read` to a write mode, validate-only/preflight runs, and a fingerprint is issued for final approval. New RSAs are created paused and need a second approval to enable.
