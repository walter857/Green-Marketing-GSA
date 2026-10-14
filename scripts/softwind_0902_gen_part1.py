#!/usr/bin/env python3
"""Generate: 3A receipt, ledger update, platform rules, live-vs-planned, demographics."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "clients/softwind-power-washing"
(C / "runbooks").mkdir(exist_ok=True)

(C / "receipts/2026-09-02-plan-ga-launch-3a-execution-receipt.md").write_text("""# PLAN-GA-LAUNCH-3A — EXECUTION RECEIPT

**Plan** PLAN-GA-LAUNCH-3A · **Fingerprint** `F91589D9EA2A` · **Approved by** Walter Correa
**Executed** 2026-09-02 17:39:49 America/New_York · **Readback** 17:41
**Account** `Softwind Power Washing - Live` / `1521725229` / Power Washing

# THE REBUILT INVENTORY IS LIVE. 45 resources enabled. 29/29 readback assertions pass.

Evidence: `snapshots/launch3a-execution-2026-09-02T173949.json` ·
`snapshots/launch3a-readback-*.json` · `snapshots/launch3a-resource-ids.json`

---

## 1. Pre-execution gate — 20 checks, all pass

Identity · both campaigns ENABLED · both TARGET_SPEND · both ceilings $30.00 · 3B and 3C guards
still paused · **all 12 new RSAs APPROVED** · the 2 House Washing guard keywords PAUSED · the 4
legacy RSAs from 3B/3C PAUSED · the 28 target keywords PAUSED · the 12 target RSAs PAUSED · five
target ad groups PAUSED · `202870585390` already ENABLED · no target resource ID changed ·
**fingerprint `F91589D9EA2A` exact match, payload byte-identical** · no guard keyword, legacy ad
or foreign resource in the payload · `validate_only` **PASS** on all three batches.

## 2. Execution — atomic per batch, `partial_failure = false`

| Batch | Result |
|---|---|
| Ad groups | **5 enabled** |
| Keyword criteria | **28 enabled** |
| Responsive search ads | **12 enabled** |

**No partial failure. No recovery needed.**

## 3. Live serving structure — campaign 24103511039

| # | Final ad group | Ad group ID | Status | Enabled RSAs |
|---|---|---|---|---:|
| 1 | Power Washing | `202870585390` | **ENABLED** | 2 |
| 2 | Pressure Washing | `202870585870` | **ENABLED** | 2 |
| 3 | House Washing | `202870585910` | **ENABLED** | 2 |
| 4 | Soft Washing | `202870586310` | **ENABLED** | 2 |
| 5 | Driveway Pressure Washing | `202870586110` | **ENABLED** | 2 |
| 6 | Patio Pressure Washing | `202870586150` | **ENABLED** | 2 |

## 4. Readback QA — 29 assertions, 0 failed

All six ad groups ENABLED · all 28 new keywords ENABLED with correct Phrase/Exact match · **no
Broad Match enabled anywhere** · both guard keywords still PAUSED in `202870585910` · all 12 new
RSAs ENABLED and still APPROVED · 15 headlines and 4 descriptions each · **no pinning** · every
Final URL and display path matches the approved plan · **every headline and description matches
the approved copy exactly** · exactly two enabled RSAs per final ad group, none above three · all
six legacy RSAs from 3B/3C still PAUSED · campaign `24145053510` ENABLED and unchanged · budgets
unchanged $41.50 / $41.11 · both ceilings $30.00 · both Maximize Clicks · Search Partners OFF ·
Display OFF · AI Max OFF · Presence targeting active · Connecticut still excluded on both ·
conversion goals unchanged · assets unchanged at 20 links · **no routing negative added** · no
audience added · no demographic criteria.

**Account totals:** ad groups 30 (17 enabled) · keyword rows 242 (240 enabled, 2 paused guards) ·
ads 66 (52 enabled).

## 5. A readback bug I caught and corrected

My first readback reported two failures: "only 18 of 28 keywords" and "guard keywords ENABLED".
**Both were artifacts of my own query, not account defects.**

`ad_group_criterion.criterion_id` is **not unique for keywords** — the same ID is reused by every
ad group carrying the same text and match type. Keying the readback dictionary on `criterion_id`
alone collapsed 242 real rows into 125 and let a different ad group's row overwrite the one being
checked.

Re-verified with the correct `(ad_group_id, criterion_id)` key:

- **242** keyword rows, not 125
- **28 of 28** created keywords present and ENABLED
- Both guards in `202870585910` **PAUSED**. The identical criterion IDs also exist in ad group
  `198082079463`, a legacy campaign-B group that was never in scope and is untouched.

The readback script is fixed and now returns 29/29.

## 6. What was deliberately not done

Nothing created. Nothing paused. No campaign paused or renamed. No budget, CPC, bidding, negative
keyword, audience, asset, schedule, location, conversion, website, GTM or WhatConverts change.
**Campaign `24145053510` remains ENABLED and untouched** as the transition campaign.
""", encoding="utf-8")

# ---------------- platform rules ----------------
(C / "audits/2026-09-02-current-google-ads-platform-rules.md").write_text("""# CURRENT GOOGLE ADS PLATFORM RULES — VERIFIED 2026-09-02

Controlling sources are official Google Ads Help and Google Ads API documentation, plus
**empirical evidence from this account**, which outranks documentation where the two could differ.

| Topic | Current rule | Source | Implication for `1521725229` |
|---|---|---|---|
| **Maximize Clicks** | Automated strategy that sets bids to get the most clicks within budget. A **maximum CPC bid limit** can be set to cap what you pay per click. | [About Maximize clicks bidding](https://support.google.com/google-ads/answer/6268626?hl=en) · accessed 2026-09-02 | Both campaigns run TARGET_SPEND with a $30.00 ceiling. The ceiling is the only CPC brake. |
| **CPC bid limit behaviour** | Without a limit, Google adjusts bids freely to spend the budget. Setting one controls cost when CPCs run higher than desired. | same | Removing the ceiling is not an option here — uncapped clicks reached $82.22 in this account. |
| **Bid adjustments under Maximize Clicks** | Bid adjustments **are supported** and apply **on top of** the maximum CPC bid limit. | [Edit your bids](https://support.google.com/google-ads/answer/2470113?hl=en) · accessed 2026-09-02 | Device/location/schedule/audience adjustments would be honoured — but see the evidence bar in `2026-09-02-advanced-bid-adjustment-decision.md`. |
| **RSA headlines / descriptions** | Up to **15 headlines** and **4 descriptions** per responsive search ad. | [About responsive search ads](https://support.google.com/google-ads/answer/7684791?hl=en) · accessed 2026-09-02 | All 12 live RSAs use the full 15/4. |
| **Enabled RSAs per ad group** | **Three.** Not stated in the Help article we could retrieve, but **proven empirically in this account**: a batch enabling a 4th returned `resource_count_limit_exceeded_error: RESOURCE_LIMIT`. | Live API response 2026-09-02, request captured in `snapshots/launch3-build-*.json` | This is why PLAN-GA-LAUNCH-3C was required. Each final ad group now runs exactly 2. |
| **Phrase / Exact match** | Both match close variants, including implied meaning. Exact is tighter but still matches close variants. | [About keyword matching options](https://support.google.com/google-ads/answer/7478529?hl=en) · accessed 2026-09-02 | Phrase + Exact only. No Broad. Close-variant leakage is managed by Search Terms review, not by pre-loading negatives. |
| **Negative keywords** | Negatives do **not** match close variants. A negative EXACT blocks only the literal string. | [About negative keywords](https://support.google.com/google-ads/answer/2453972?hl=en) · accessed 2026-09-02 | Confirms the standing rule: routing negatives cannot fully control positive close variants. |
| **Audience Observation** | Observation reports performance without restricting reach. Targeting restricts. | [About audience targeting](https://support.google.com/google-ads/answer/2497941?hl=en) · accessed 2026-09-02 | PLAN-GA-AUD-1 uses Observation only, 0% modifiers. |
| **Demographics** | Age, gender, parental status and household income can be excluded or bid-adjusted. `UNDETERMINED`/Unknown is a separate bucket. | [About demographic targeting](https://support.google.com/google-ads/answer/2580383?hl=en) · accessed 2026-09-02 | **No exclusions.** Excluding Unknown discards a large share of real buyers. |
| **Conversion-based bidding** | tCPA/tROAS/Maximize Conversions need sufficient recent conversion volume to learn. | [About Smart Bidding](https://support.google.com/google-ads/answer/7065882?hl=en) · accessed 2026-09-02 | Account has **zero** verified conversions. Conversion-based bidding is inappropriate and is prohibited while the thank-you exception stands. |
| **Primary conversion actions** | `primary_for_goal` determines inclusion in bidding and the Conversions column. `include_in_conversions_metric` is deprecated and immutable. | [Conversion goals](https://developers.google.com/google-ads/api/docs/conversions/goals/overview) · accessed 2026-09-01 | Already verified correct in this account — verdict D, no goal-configuration defect. |
| **Offline conversion imports** | New integrations should use **Google Data Manager API**; the legacy Google Ads upload path requires an eligible developer token. | [Conversion imports](https://developers.google.com/google-ads/api/docs/conversions/upload-clicks) · accessed 2026-09-02 | Future qualified-lead and sold-job feedback routes through Data Manager API. Blocked until a CRM exists. |
| **Location Presence targeting** | `PRESENCE` targets people **in** the location, not people merely interested in it. | [About location targeting](https://support.google.com/google-ads/answer/1722043?hl=en) · accessed 2026-09-02 | Both campaigns use PRESENCE/PRESENCE across 80 NY locations with Connecticut excluded. This is also why a real GCLID cannot be generated remotely. |
| **Campaign experiments** | Search campaigns support experiments that split traffic against a control. | [About campaign experiments](https://support.google.com/google-ads/answer/11469760?hl=en) · accessed 2026-09-02 | Noted as a future option for testing a CPC ceiling without risking the whole campaign. Not proposed now — the account lacks the volume to read an experiment. |

**Blogs were not used as a controlling source anywhere in this file.**
""", encoding="utf-8")

# ---------------- live vs planned ----------------
LP = "https://offer.softwindli.com"
rows = [
 ("GOOGLE ADS","Campaign count","2 live (24103511039 + 24145053510)","1 long-term","LIVE BUT NEEDS DATA","consolidation needs its own approval"),
 ("GOOGLE ADS","Campaign names","Power Washing / Pressure Washing","unchanged","LIVE AND VERIFIED",""),
 ("GOOGLE ADS","Campaign status","both ENABLED","both ENABLED during transition","LIVE AND VERIFIED",""),
 ("GOOGLE ADS","Final ad groups","6 ENABLED in 24103511039","6","LIVE AND VERIFIED","readback 29/29"),
 ("GOOGLE ADS","Final positive keywords","28 new ENABLED + 10 reused = 38 objects","38","LIVE AND VERIFIED",""),
 ("GOOGLE ADS","Match types","Phrase + Exact only","Phrase + Exact","LIVE AND VERIFIED","no Broad anywhere"),
 ("GOOGLE ADS","Final RSAs","12 ENABLED, 2 per group","12","LIVE AND VERIFIED","all APPROVED"),
 ("GOOGLE ADS","Headlines","15 per RSA","15","LIVE AND VERIFIED",""),
 ("GOOGLE ADS","Descriptions","4 per RSA","4","LIVE AND VERIFIED",""),
 ("GOOGLE ADS","Final URLs","6 mapped, all HTTP 200","6","LIVE AND VERIFIED",""),
 ("GOOGLE ADS","CPC ceilings","$30.00 both","evidence-based lower ceiling","LIVE BUT NEEDS DATA","PLAN-GA-BID-1"),
 ("GOOGLE ADS","Bidding strategy","Maximize Clicks both","Maximize Clicks until conversions verified","LIVE AND VERIFIED",""),
 ("GOOGLE ADS","Campaign negatives","132 per campaign","unchanged","LIVE AND VERIFIED",""),
 ("GOOGLE ADS","Ad-group routing negatives","0","103 at launch","DRAFTED ONLY","PLAN-GA-LAUNCH-2A"),
 ("GOOGLE ADS","Assets","4 sitelinks + 4 callouts + 1 snippet + 1 call per campaign","complete","LIVE AND VERIFIED",""),
 ("GOOGLE ADS","Image assets","0","client-supplied rights-cleared","BLOCKED","no approved images exist"),
 ("GOOGLE ADS","Business-name asset","0","1 verified","BLOCKED","business identity unresolved"),
 ("GOOGLE ADS","Logo asset","1 at customer level (BUSINESS_LOGO)","campaign-level review","LIVE BUT NEEDS DATA",""),
 ("GOOGLE ADS","Audience observations","0","12 Observation @0%","DRAFTED ONLY","PLAN-GA-AUD-1"),
 ("GOOGLE ADS","Demographic criteria","0","0 - reporting only","LIVE AND VERIFIED","no exclusions, by design"),
 ("GOOGLE ADS","Call schedule","asset stops 17:00, campaigns run to 18:00","match answered hours","BLOCKED","answered hours unverified"),
 ("GOOGLE ADS","Old ad groups","24 legacy remain","retire later","DEFERRED","PLAN-GA-RETIRE-1"),
 ("GOOGLE ADS","Old keywords","30 displaced duplicates + 2 paused guards","retire later","DEFERRED",""),
 ("GOOGLE ADS","Old RSAs","6 paused by 3B/3C, others live in campaign B","retire later","DEFERRED",""),
 ("GOOGLE ADS","Second campaign","24145053510 ENABLED","retire last","DEFERRED","separate approval"),
 ("LANDING PAGES","Browser titles","'Softwind Landscape & Masonry' on all 6","service + correct brand","DRAFTED ONLY","final copy written"),
 ("LANDING PAGES","H1s","city-locked to 3 hamlets","Long Island wording","DRAFTED ONLY",""),
 ("LANDING PAGES","Hero copy","generic","service-specific","DRAFTED ONLY",""),
 ("LANDING PAGES","Service-area copy","3 hamlets","Long Island / Nassau and Suffolk","DRAFTED ONLY",""),
 ("LANDING PAGES","CTA copy","present","Request A Free Quote","DRAFTED ONLY",""),
 ("LANDING PAGES","Phone numbers","(631) 502-7946 rendered","unchanged","LIVE AND VERIFIED",""),
 ("LANDING PAGES","Phone links","malformed tel:(631) on all 7","valid tel:+16315027946","NOT IMPLEMENTED","ClickUp P0"),
 ("LANDING PAGES","Forms","2 copies of form#gform_1, 22 duplicate IDs","exactly one","NOT IMPLEMENTED","ClickUp P0"),
 ("LANDING PAGES","Reviews","none verified","3 relevant per page","BLOCKED","CLIENT REVIEW NEEDED"),
 ("LANDING PAGES","Images","no approved files found locally","rights-cleared client images","BLOCKED","IMAGE-GAPS.md"),
 ("LANDING PAGES","Countdown","resetting, unsupported","REMOVE","DRAFTED ONLY",""),
 ("LANDING PAGES","FAQs","present","service-specific","DRAFTED ONLY",""),
 ("LANDING PAGES","Mobile layout","parity MATCH","unchanged","LIVE AND VERIFIED",""),
 ("LANDING PAGES","Page speed","~165KB HTML, not measured","measure","NOT IMPLEMENTED",""),
 ("LANDING PAGES","Tracking","GA4 + GTM + WhatConverts + ClickCease loading","unchanged","LIVE AND VERIFIED",""),
 ("LANDING PAGES","Thank-you behavior","fires conversion on any visit","gate on real submission","OWNER-ACCEPTED TEMPORARY EXCEPTION","EXC-1"),
 ("MEASUREMENT","Google Ads form conversion","fires after submission - PROVEN","gated on success event","OWNER-ACCEPTED TEMPORARY EXCEPTION",""),
 ("MEASUREMENT","Website-call conversion","0 wcm for 18369652705","Softwind owns the call path","NOT IMPLEMENTED","architecture deferred"),
 ("MEASUREMENT","Call-asset conversion","0 call_view rows ever","working","NOT IMPLEMENTED","no call has occurred"),
 ("MEASUREMENT","WhatConverts","attribution cookies working, DNI broken","DNI repaired","BLOCKED","empty API token"),
 ("MEASUREMENT","GCLID","reaches form POST","preserved","LIVE AND VERIFIED",""),
 ("MEASUREMENT","GBRAID","reaches form POST","preserved","LIVE AND VERIFIED",""),
 ("MEASUREMENT","WBRAID","reaches form POST","preserved","LIVE AND VERIFIED",""),
 ("MEASUREMENT","UTMs","all five reach form POST","preserved","LIVE AND VERIFIED",""),
 ("MEASUREMENT","Sibling-account tag","AW-17878095007 active on all 7 pages","scoped off Power Washing URLs","BLOCKED","needs sibling work order"),
 ("MEASUREMENT","GTM duplicate load","2 bootstraps per page","1","NOT IMPLEMENTED","ClickUp P0"),
 ("MEASUREMENT","Duplicate form","2 per offer page","1","NOT IMPLEMENTED","ClickUp P0"),
 ("MEASUREMENT","Duplicate HTML IDs","22 per offer page","0","NOT IMPLEMENTED","ClickUp P0"),
 ("MEASUREMENT","iconnode","POST on every page, owner unknown","identified","BLOCKED","ClickUp P2"),
 ("MEASUREMENT","Test-lead cleanup","GM TEST DO NOT CONTACT still present","removed","NOT IMPLEMENTED","ClickUp P0"),
]
with (C / "audits/2026-09-02-final-live-versus-planned-status.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["area", "item", "live_state_2026_09_02", "planned_state", "status", "note"])
    w.writerows(rows)

# ---------------- demographics ----------------
D = json.loads((C / "snapshots/postlaunch-data-2026-09-02.json").read_text(encoding="utf-8"))
dev = D["by_device"]
with (C / "audits/2026-09-02-demographic-and-household-income-decision.csv").open(
        "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["dimension", "segment", "impressions", "valid_clicks", "invalid_clicks", "ctr",
                "cpc_usd", "spend_usd", "conversions", "qualified_leads", "sold_jobs",
                "decision", "reason"])
    for k, v in dev.items():
        ctr = round(v["clicks"] / v["impr"], 4) if v["impr"] else 0
        cpc = round(v["cost"] / v["clicks"], 2) if v["clicks"] else 0
        w.writerow(["device", k, v["impr"], v["clicks"], v["invalid"], ctr, cpc, v["cost"],
                    0, 0, 0, "REPORTING ONLY - NO ADJUSTMENT",
                    "Zero conversions account-wide. Mobile carries 17 of 21 valid clicks and "
                    "all 106 invalid clicks; Google filters and credits the invalid ones."])
    for dim, note in (("gender", "Do NOT exclude women. Do NOT exclude Unknown."),
                      ("age", "Do NOT exclude any age range."),
                      ("household_income", "Do NOT exclude any income range."),
                      ("parental_status", "Do NOT exclude any parental status.")):
        w.writerow([dim, "ALL SEGMENTS", "see Google Ads UI", "", "", "", "", "", 0, 0, 0,
                    "REPORTING ONLY - NO ADJUSTMENT, NO EXCLUSION",
                    note + " The account has ZERO verified qualified leads and ZERO sold jobs, "
                    "so no demographic evidence of any kind exists. Impressions and clicks are "
                    "not qualified-lead evidence. Revisit only when sold-job data exists."])

(C / "audits/2026-09-02-advanced-bid-adjustment-decision.md").write_text("""# ADVANCED BID-ADJUSTMENT DECISION — 2026-09-02

**Decision: NO bid adjustment of any kind is applied or proposed. Reporting only.**

## Are adjustments even honoured?

Yes. Official documentation confirms bid adjustments **are supported under Maximize Clicks** and
apply **on top of** the maximum CPC bid limit
([Edit your bids](https://support.google.com/google-ads/answer/2470113?hl=en), accessed
2026-09-02). So the constraint is not technical — it is evidential.

## The evidence bar, and why nothing clears it

The account has **zero verified qualified leads and zero sold jobs**. Every adjustment below would
therefore be set from impressions, clicks or CPC alone, which is exactly the reasoning this
engagement has already rejected once.

| Adjustment | Available data | Decision |
|---|---|---|
| **Device** | MOBILE 207 impr / 17 valid clicks / $504.71 / **106 invalid**; DESKTOP 92 / 4 / $173.76 / 1 invalid | **NO ADJUSTMENT.** Mobile is 81% of valid clicks and 74% of spend. Cutting it to escape invalid clicks would remove most of the account's traffic to solve a problem Google already filters and credits. |
| **Location** | 80 targets, no per-location conversion data | **NO ADJUSTMENT.** |
| **Ad schedule** | Clicks cluster 14:00–16:00, but on 21 lifetime clicks | **NO ADJUSTMENT.** 21 clicks cannot support an hourly curve. |
| **Audience** | No audiences attached yet | **NO ADJUSTMENT.** Observations first, at 0%. |
| **Remarketing list** | None | **NO ADJUSTMENT.** |
| **Call interaction** | 88 call impressions, **0 call clicks, 0 call_view rows ever** | **NO ADJUSTMENT.** The path has never been exercised. |
| **Age** | No conversion data | **NO ADJUSTMENT. NO EXCLUSION.** |
| **Gender** | No conversion data | **NO ADJUSTMENT. NO EXCLUSION. Women are not excluded. Unknown is not excluded.** |
| **Household income** | No conversion data | **NO ADJUSTMENT. NO EXCLUSION.** |
| **Parental status** | No conversion data | **NO ADJUSTMENT. NO EXCLUSION.** |

## Standing rules

- Do not exclude women. Do not exclude Unknown gender. Do not exclude an age or income range.
- Do not treat gender or age stereotypes as performance evidence.
- Record demographic performance for future use; create no approval plan from impression or click
  data alone.
- Revisit only when qualified-lead or sold-job evidence exists, which requires the measurement
  work to land first.
""", encoding="utf-8")
print("part1 written")
