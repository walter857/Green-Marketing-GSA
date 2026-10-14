# Ambient Cooling - Live | corrected decision package | 2026-08-28

**Account:** Ambient Cooling - Live · **Child customer ID:** 2401959466 · USD · America/New_York
**Mode:** READ + DRAFT + VALIDATE-ONLY · **Mutations executed: 0**

Identity gate PASS on every check. Both manager links ACTIVE. Most recent account change
event is still **2026-08-22 09:36:07** — nothing has touched the account.
Unchanged-resource proof: 15 of 15 checks PASS
(`receipts/post-reverify-unchanged-proof-2026-08-28.json`).

> **Three of my earlier conclusions were wrong.** The re-verification you asked for
> disproved them. All three original fingerprints are now VOID. Details in each section.


> **STATUS UPDATE 2026-08-28:** the three packages below were APPROVED and EXECUTED.
> `82ACD4953536C020` (7 ops), `6F2B6ABBCEB992E4` (1 op) and `E50EDFE7644A9B5F` (1 op) —
> nine operations total, all readbacks PASS. See the Execution Addendum in
> `2026-08-27-august-audit.md`. Packages B and C remain VOID; D-2 remains HOLD.

---

## 0. Headline corrections

| # | Earlier claim | Verified reality |
|---|---|---|
| 1 | CPC ceilings of $60 / $40 are conservative cost control | **Every one of the 5 Primary-converting clicks cost $68.16–$153.06.** A $60 ceiling on AC Repair and HVAC Repair would have blocked **100% of converting traffic.** |
| 2 | The Business Profile location asset produced zero leads and is 19.5% waste | **`LOCATION_EXPANSION` carried 2 of the 6 platform Primary conversions**, neither of them the WC Lead artifact. Location click types: $1,050.21 → 2 conversions = **$525 CPL, better than the account's $964.02.** |
| 3 | `WC Lead` counting despite false flags proves a biddable goal overrides the action flags | **Disproved.** `CONTACT/WEBSITE` is `biddable=true` right now, yet all four WC Lead conversions after 2026-08-21 show `conversions=0.0`. It is a **historical artifact**, not an active defect. |

A fourth correction: my ClickUp bullet said every sitelink was moved to the paid offer
pages. **False** — 4 of 9 active sitelinks still point at the main website.

---

## 1. Original plan ACE80A09AC134C85 — complete contents, then split

### The 30 operations as originally bundled

**ADJ-1 — 24 × CREATE `campaign_criterion`, PHRASE, campaign 24132507747 (HVAC Installation)**

`croppmetcalfe`, `furr`, `michaels`, `michael and sons`, `michael & sons`, `woodfin`,
`blauch`, `armbridge`, `bluedot`, `mccrea`, `barstow`, `elmar mechanical`, `hugee`,
`kirkland`, `bahr`, `beltway hvac`, `supreme service today`, `total comfort`,
`maryland mechanical`, `amazing plumbing`, `amazing heating`, `hvac precision services`,
`horizon services`, `len the plumber`

**ADJ-2 — 1 × CREATE `campaign_criterion`, BROAD, campaign 24132507741 (AC Repair):** `automotive`

**ADJ-3 — 5 × UPDATE `campaign.target_spend.cpc_bid_ceiling_micros`**
AC Repair 0 → 60,000,000 · HVAC Repair 0 → 60,000,000 · HVAC Installation 0 → 40,000,000 ·
HVAC Replacement 0 → 40,000,000 · Gas Boiler 0 → 40,000,000

**ADJ-4 — 5 × UPDATE `campaign.excluded_parent_asset_set_types` += `LOCATION_SYNC`** on all five

### Split into one fingerprint per change type

| Pkg | Change type | Objects | Fingerprint | Validate-only | Decision |
|---|---|---:|---|---|---|
| **A-1** | Competitor negatives (strict-screened) | 7 | `82ACD4953536C020` | VALIDATE_OK | **SAFE TO APPROVE** |
| **A-2** | Vehicle protection, AC Repair | 1 | `6F2B6ABBCEB992E4` | VALIDATE_OK | **SAFE TO APPROVE** |
| **B** | Maximize Clicks CPC ceilings | 5 | — | not regenerated | **VOID** |
| **C** | Business Profile / location asset | 5 | — | not regenerated | **VOID** |
| **D** | — no other adjustment — | 0 | — | — | n/a |

`ACE80A09AC134C85` is marked **VOID / do-not-execute** on disk.

---

## 2. Competitor negatives — under the stricter rule

Your rule: *do not negative an ambiguous company name, HVAC manufacturer, equipment brand,
location, or generic service phrase.* Applied mechanically to all 25:
**8 ALLOW, 17 REJECT.** Recoverable cost drops from $760.28 to **$238.51**.

### ALLOW — package A-1 (7 on HVAC Installation 24132507747) + A-2 (1 on AC Repair)

| Negative | Match | Scope | Campaign ID | Impr | Clicks | Cost | Prim. conv | Sec. conv | Converting history | Blocks active kw | Blocks 5 services | Brand/equip/service/location? | Already covered? |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| `croppmetcalfe` | PHRASE | campaign | 24132507747 | 31 | 4 | $105.14 | 0.0 | 0.0 | none | 0 | 0 | no — coined company name | no |
| `michael and sons` | PHRASE | campaign | 24132507747 | 9 | 1 | $32.44 | 0.0 | 0.0 | none | 0 | 0 | no | no |
| `armbridge` | PHRASE | campaign | 24132507747 | 2 | 1 | $29.76 | 0.0 | 0.0 | none | 0 | 0 | no — coined | no |
| `bluedot` | PHRASE | campaign | 24132507747 | 3 | 1 | $29.39 | 0.0 | 0.0 | none | 0 | 0 | no — coined | no |
| `blauch` | PHRASE | campaign | 24132507747 | 2 | 1 | $24.50 | 0.0 | 0.0 | none | 0 | 0 | no — coined | no |
| `hugee` | PHRASE | campaign | 24132507747 | 2 | 1 | $17.28 | 0.0 | 0.0 | none | 0 | 0 | no — coined | no |
| `michael & sons` | PHRASE | campaign | 24132507747 | 2 | 0 | $0.00 | 0.0 | 0.0 | none | 0 | 0 | no | no |
| `automotive` | BROAD | campaign | 24132507741 | 3 | 0 | $0.00 | 0.0 | 0.0 | none | 0 | 0 | no | **no** — `auto` BROAD does not cover it |

Supporting terms include `croppmetcalfe columbia / fairfax / linthicum heights / hvac /
service experts`, `michael and sons hvac`, `hvac michael and sons`, `armbridge hvac`,
`bluedot hvac`, `blauch brothers harrisonburg va`, `hugee corp`, `hugee hvac`,
`automotive air conditioning repair near me`, `automotive ac mechanic near me`.

### REJECT — 17, and why

| Negative | Cost forgone | Rejected because |
|---|---:|---|
| `furr` | $112.98 | single ambiguous token (surname / "fur") |
| `amazing plumbing` | $56.72 | contains generic service word `plumbing` |
| `maryland mechanical` | $50.17 | contains place name `maryland` **and** service word `mechanical` |
| `woodfin` | $38.67 | place name (Woodfin, NC) |
| `michaels` | $35.80 | ambiguous (retail brand / surname) |
| `amazing heating` | $30.68 | contains core service word `heating` |
| `bahr` | $29.36 | ambiguous surname |
| `barstow` | $29.21 | place name (Barstow, CA) |
| `supreme service today` | $23.56 | contains `service` |
| `mccrea` | $22.01 | ambiguous surname |
| `elmar mechanical` | $20.98 | contains `mechanical` |
| `beltway hvac` | $20.90 | place-ish `beltway` + service word `hvac` |
| `kirkland` | $17.57 | place name + Costco brand |
| `hvac precision services` | $16.90 | contains `hvac` and `services` |
| `total comfort` | $16.26 | contains `comfort` |
| `horizon services` | $0.00 | contains `services` |
| `len the plumber` | $0.00 | contains `plumber` |

**Honest limitation:** A-1 recovers $238.51 of $760.28 — about $18/day. The other $521.77
sits behind names that are not safe to block. **Adding names is not the fix.** The keyword
`hvac installers` is the wrong canonical theme; Google's phrase same-meaning expansion maps
"installers" onto "any local HVAC company". Replacing it with tighter BOFU themes
(`hvac installation near me`, `hvac installation cost`, `air conditioning installation near me`)
is the durable answer and belongs in a September keyword plan.

---

## 3. Maximize Clicks CPC ceilings — **VOID**

### Per-campaign CPC distribution (click-weighted, 2026-08-01 → 2026-08-27)

| Campaign | Strategy | Current ceiling | Clicks | Mean | Median | p75 | p90 | Max | CPC on converting terms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| AC Repair | TARGET_SPEND | **0 (uncapped)** | 19 | $90.49 | $80.92 | $123.13 | $145.35 | **$256.48** | **$140.13, $109.87, $68.16** |
| HVAC Repair | TARGET_SPEND | **0** | 13 | $81.31 | $54.25 | $148.67 | $153.03 | $153.06 | **$153.06, $153.03** |
| HVAC Installation | TARGET_SPEND | **0** | 90 | $24.45 | $22.53 | $24.07 | $38.96 | $45.93 | none — 0 conversions |
| HVAC Replacement | TARGET_SPEND | **0** | 4 | $32.51 | $27.14 | $33.59 | $43.25 | $49.69 | none — 0 conversions |
| Gas Boiler Repair | TARGET_SPEND | **0** | 0 | — | — | — | — | — | no data at all |

### Why the proposed ceilings are void

Converting-term CPCs: n=5, **min $68.16, max $153.06, mean $124.85.**

- Proposed AC Repair ceiling **$60** — below all three of its converting CPCs
  ($140.13, $109.87, $68.16). Would have blocked **3 of 3**.
- Proposed HVAC Repair ceiling **$60** — below both of its converting CPCs
  ($153.06, $153.03). Would have blocked **2 of 2**.
- Proposed HVAC Installation ceiling **$40** — sits between p90 ($38.96) and max ($45.93)
  and would suppress current relevant traffic in the one campaign that is genuinely
  budget-limited (56.86% budget-lost impression share). You asked me not to do that.
- Proposed HVAC Replacement ceiling **$40** — below its max ($49.69) on a 4-click sample.
- Proposed Gas Boiler ceiling **$40** — zero clicks ever. No basis whatsoever.

**In this account the expensive clicks are the converting clicks.** A ceiling set anywhere
near the average would remove the leads. **Package B is VOID. No ceiling is recommended.**

### The only defensible variant, and it is still HOLD

An **outlier-only** ceiling on AC Repair at **$175.00** — above the highest observed
converting CPC anywhere in the account ($153.06), below the single $256.48 outlier.
Calculation: `max(converting CPC across account) × 1.14 ≈ $175`, chosen to clear the
converting band with headroom.

It would have trimmed exactly **1 click of 19**, saving at most ~$81. Evidence base: **n=1**.
That is too thin to act on, and I do not recommend it. **HOLD.**

**Every ceiling here is a cost-control idea, not a proven profit-maximizing bid.** Qualified
lead outcomes and a target CPL are unavailable (WhatConverts token empty), so no bid ceiling
in this account can currently be justified on profit grounds.

**The real lever is Quality Score, not a bid cap.** HVAC Repair and HVAC Replacement both
carry **below-average landing-page experience**, and AC Repair below-average expected CTR.
Those are what force $130+ CPCs. Fixing them lowers CPC structurally without suppressing
converting traffic.

---

## 4. Business Profile location asset — **VOID**

### Exact identifiers

| Item | Value |
|---|---|
| Asset set | `8620443109` "Business Profile", type `LOCATION_SYNC`, status **ENABLED** |
| Association level | **Customer level** — `customers/2401959466/customerAssetSets/8620443109`, status ENABLED |
| Campaign-level associations | **none** on any campaign — it is inherited, not attached |
| Location assets inside the set | `102853408140` ENABLED, `245790011117` ENABLED, `138665832571` REMOVED |
| Retired sets | `7135012864` and `7744462455`, both REMOVED |
| Campaigns affected | all five, plus every other Search campaign in the account (all 18 legacy are paused) |

### Performance, 2026-08-01 → 2026-08-27

| Campaign | Click type | Impr | Clicks | Spend | **Primary conv** | All conv |
|---|---|---:|---:|---:|---:|---:|
| HVAC Repair | LOCATION_EXPANSION | 552 | 8 | $558.79 | **1.0** | 2.0 |
| HVAC Installation | LOCATION_EXPANSION | 1,123 | 7 | $175.21 | 0.0 | 1.0 |
| AC Repair | LOCATION_EXPANSION | 212 | 3 | $116.33 | **1.0** | 3.0 |
| AC Repair | GET_DIRECTIONS | 16 | 1 | $98.48 | 0.0 | 1.0 |
| HVAC Installation | GET_DIRECTIONS | 150 | 4 | $79.68 | 0.0 | 4.0 |
| HVAC Repair | GET_DIRECTIONS | 51 | 1 | $21.72 | 0.0 | 2.0 |
| **Total** | | | **24** | **$1,050.21** | **2.0** | 13.0 |

### The two Primary conversions, by conversion action

| Campaign | Click type | Conversion action | Primary conv |
|---|---|---|---:|
| HVAC Repair | LOCATION_EXPANSION | **Calls from ads** | 1.0 |
| AC Repair | LOCATION_EXPANSION | **Ambient Cooling - LP -Submit Lead Forms** | 1.0 |

Neither is the WC Lead artifact (that one splits 0.5 URL_CLICKS / 0.5 SITELINKS on HVAC
Repair). These are a real phone-call lead and a real landing-page form lead.

**Location-asset CPL = $1,050.21 / 2 = $525.11 — better than the adjusted account CPL of
$964.02.**

Google-hosted Local actions it also generated: Directions 7.0, Other engagements 14.0,
Website visits 1.0 — all excluded from the Conversions column by design.

### Attribution gaps, stated plainly

- **WhatConverts is unavailable** (token empty). I **cannot** claim this traffic produced
  zero real leads, and I withdraw that claim.
- Business Profile-side actions (calls placed from the profile, direction requests
  completed, profile website clicks) are **not available through the Google Ads API** and
  were not measured.
- The correct wording throughout is **"zero recorded Google Ads Primary conversions"**,
  never "zero leads". For this asset even that is false — it recorded **two**.

### Exact effect of detaching, and why not to

Setting `excluded_parent_asset_set_types += LOCATION_SYNC` on the five campaigns would stop
location assets serving on paid Search only. It would **not** touch the account-level
Business Profile link, Maps, or organic local visibility, and the 18 legacy campaigns are
unaffected. But it would remove the click type that carried **2 of the 5 real Primary
conversions** at the account's best CPL.

**Decision: VOID.** Not merely on hold — the evidence points the opposite way.

---

## 5. Conversion plan EE6CFAD6667A95A1 — **VOID**

| Field | Live value |
|---|---|
| Conversion action ID | `7643656486` |
| Name | WC Lead |
| Status | ENABLED |
| Type / category / origin | `UPLOAD_CLICKS` / `CONTACT` / `WEBSITE` |
| `primary_for_goal` | **false** |
| `include_in_conversions_metric` | **false** |
| Counting / lookback / attribution | ONE_PER_CLICK / 60 days / data-driven |
| Customer default goals (CONTACT) | `CONTACT/WEBSITE` biddable=**true**, `CONTACT/CALL_FROM_ADS` biddable=**true**, `CONTACT/GOOGLE_HOSTED` biddable=false |
| Campaign-specific goals | identical on all five campaigns |
| Custom conversion goals | **none exist** |
| Campaigns bidding toward it | **none** — all five are `TARGET_SPEND` (Maximize Clicks), which does not bid to conversions; `selective_optimization` is empty on all five |

### The decisive evidence — WC Lead by date

| Date | Campaign | `metrics.conversions` | `metrics.all_conversions` |
|---|---|---:|---:|
| **2026-08-20** | HVAC Repair | **1.0** | 1.0 |
| 2026-08-21 | AC Repair | **0.0** | 1.0 |
| 2026-08-21 | HVAC Installation | **0.0** | 1.0 |
| 2026-08-22 | AC Repair | **0.0** | 1.0 |
| 2026-08-25 | AC Repair | **0.0** | 1.0 |

**PLAN-B `03F125C189679E35` executed 2026-08-21 00:09 ET.** Every WC Lead conversion after
that timestamp is correctly excluded. The one that counted is from **2026-08-20**, before
the fix.

**Verdict: historical reporting artifact, not an active bidding defect.** Google Ads does
not reprocess or restate the historical Conversions column after an
`include_in_conversions_metric` change — conversions already recorded keep counting in
their original dates permanently.

This also **disproves my earlier inference** that a biddable `CONTACT/WEBSITE` goal
overrides the action flags. `CONTACT/WEBSITE` is biddable=true on all five campaigns right
now, and the four post-fix conversions still did not count. The action flags govern.

`change_event` returned **0** `CONVERSION_ACTION` rows in the last 30 days (1,000 rows
scanned), so it cannot date the flag change; the metric-by-date evidence is the proof.

**Decision: VOID `EE6CFAD6667A95A1`. Make no conversion mutation.** The configuration is
already correct.

---

## 6. Destructive plan C3038EDD9E621944 — split

The original bundled 8 removals, so it is **VOID** and split.

### Package D-1 — `hanover` only · fingerprint `E50EDFE7644A9B5F` · **1 operation** · VALIDATE_OK

| Field | Value |
|---|---|
| Negative text | `hanover` |
| Match type | BROAD |
| Account-level list ID | `11252984411` "account-level negative keywords list" |
| Criterion ID | **`11143481`** |
| Resource name | `customers/2401959466/sharedCriteria/11252984411~11143481` |
| Affected active keywords | **none** (0 of 10) |
| Affected targeted locations | geo `1018614` **Hanover, Maryland, United States**, City, ENABLED — **targeted on all five campaigns** |
| Historical search terms | **0 observed** containing "hanover" |
| Conversions on those terms | 0.0 |
| Measured cost impact to date | **$0.00** |
| Reason | The account explicitly targets Hanover, MD on all five campaigns while blocking every query containing "hanover" account-wide |
| Any other negative blocking Hanover? | **NO** — confirmed against all 59 list members |
| Rollback | re-create a BROAD `hanover` in list 11252984411; criterion ID will differ |

**Confirmed: D-1 removes only the BROAD `hanover` member, nothing else.** Validate-only
passed on exactly **1** removal.

Blast radius: the list is account-wide, so the 18 legacy campaigns are also affected — all
are PAUSED, so live impact is limited to the five.

### Package D-2 — equipment-brand negatives · fingerprint `4D7AF1C9CFCA27F9` · 7 operations · VALIDATE_OK

| Negative | Match | Criterion ID | Blocks active kw | Service probes blocked | Observed terms | Measured cost |
|---|---|---|---:|---:|---:|---:|
| `thermostat` | BROAD | `10624201` | 0 | 2 | 0 | $0.00 |
| `thermostats` | BROAD | `10624211` | 0 | 0 | 0 | $0.00 |
| `ruud` | BROAD | `12341163` | 0 | 1 | 0 | $0.00 |
| `rudd` | BROAD | `13670783` | 0 | 0 | 0 | $0.00 |
| `ecobee` | BROAD | `4367690940` | 0 | 1 | 0 | $0.00 |
| `frigidaire` | BROAD | `10242046` | 0 | 0 | 0 | $0.00 |
| `ducane` | BROAD | `12719736` | 0 | 0 | 0 | $0.00 |

**Decision: HOLD.** Zero observed terms and zero measured cost — the case is theoretical.
Bundle with the September keyword restructure.

`commercial` remains **not proposed** — removing it requires confirmation that Ambient
serves commercial customers, which is an unverified business fact.

---

## 7. Corrected performance

### Account, settled 2026-08-01 → 2026-08-26

| Metric | Platform (as Google reports) | Adjusted (WC Lead artifact removed) |
|---|---:|---:|
| Spend | $4,820.12 | $4,820.12 |
| Primary conversions | 6.00 | **5.00** |
| **CPL** | $803.35 | **$964.02** |

`$4,820.12 / 5 = $964.02`

### Per campaign

| Campaign | Spend | Clicks | Platform conv | Artifact | Adjusted conv | Platform CPL | **Adjusted CPL** |
|---|---:|---:|---:|---:|---:|---:|---:|
| AC Repair | $1,719.33 | 19 | 3.0 | 0.0 | 3.0 | $573.11 | **$573.11** |
| HVAC Repair | $1,010.98 | 12 | 3.0 | **1.0** | **2.0** | $336.99 | **$505.49** |
| HVAC Installation | $1,987.98 | 79 | 0.0 | 0.0 | 0.0 | n/a | n/a |
| HVAC Replacement | $101.83 | 3 | 0.0 | 0.0 | 0.0 | n/a | n/a |
| Gas Boiler Repair | $0.00 | 0 | 0.0 | 0.0 | 0.0 | n/a | n/a |

**Neither number counts qualified leads.** These are Google Ads conversions. WhatConverts
access is unavailable, so lead quality is unverified and CPQL, CAC, ROAS and profit after
ad spend remain uncalculable.

### HVAC Installation zero conversions — corrected statement

79 clicks with 0 conversions. **Assuming a true conversion rate of 5%** — the account's own
observed rate — the probability of zero conversions is `0.95^79 ≈ 1.7%`. The 1.7% figure is
meaningless without that assumption. At a 2% true rate the probability is `0.98^79 ≈ 20%`,
which would be unremarkable. **The observed zero does not by itself prove the theme is bad.**

### Budget-change wording — corrected

HVAC Installation average CPC was $27.51 in 2026-08-18 → 08-21 and $21.93 in
2026-08-23 → 08-26. **CPC decreased during the equal post-change comparison window.**
I make no causal claim that the budget increase produced the decrease.

---

## 8. Sitelink verification — fresh read

40 active `campaign_asset` SITELINK associations across the five campaigns; **9 distinct
active sitelinks**.

| Asset ID | Link text | Final URL | Destination |
|---|---|---|---|
| `410638280061` | AC Repair | `https://offer.ambientcoolingandheating.com/ac-repair/` | offer subdomain |
| `410638280067` | HVAC Repair | `https://offer.ambientcoolingandheating.com/hvac-repair/` | offer subdomain |
| `410638276380` | HVAC Installation | `https://offer.ambientcoolingandheating.com/hvac-installation/` | offer subdomain |
| `410638278156` | HVAC Replacement | `https://offer.ambientcoolingandheating.com/hvac-replacement/` | offer subdomain |
| `410465469923` | Gas Boiler Repair | `https://offer.ambientcoolingandheating.com/gas-boiler-repair/` | offer subdomain |
| `407418567058` | Contact Ambient | `https://ambientcoolingandheating.com/contact-us/` | **MAIN WEBSITE** |
| `407319490559` | Customer Reviews | `https://ambientcoolingandheating.com/reviews/` | **MAIN WEBSITE** |
| `407494691217` | Service Areas | `https://ambientcoolingandheating.com/service-areas/` | **MAIN WEBSITE** |
| `407319490562` | View Our Work | `https://ambientcoolingandheating.com/our-work/` | **MAIN WEBSITE** |

**5 offer-subdomain, 4 main-website — all active.** The five service sitelinks are each
attached to the other four campaigns (not their own); the four main-website sitelinks are
on all five.

**The ClickUp claim "pointed every campaign sitelink to the paid offer pages" is FALSE and
has been removed.** No sitelink was changed in this pass.

---

## 9. Consolidated approval block — only what is currently safe

```
APPROVE COMPETITOR NEGATIVES PLAN 82ACD4953536C020 FOR 2401959466
APPROVE VEHICLE PROTECTION PLAN 6F2B6ABBCEB992E4 FOR 2401959466
APPROVE HANOVER REMOVAL PLAN E50EDFE7644A9B5F FOR 2401959466
```

Total: **9 operations** — 8 creates, 1 destructive removal. All three VALIDATE_OK.
The removal is a destructive action and carries its own approval line by design.

### Full decision register

| Package | Fingerprint | Objects | Decision |
|---|---|---:|---|
| A-1 competitor negatives (strict) | `82ACD4953536C020` | 7 | **SAFE TO APPROVE** |
| A-2 vehicle protection | `6F2B6ABBCEB992E4` | 1 | **SAFE TO APPROVE** |
| D-1 remove `hanover` | `E50EDFE7644A9B5F` | 1 | **SAFE TO APPROVE** (destructive) |
| B CPC ceilings | — | 5 | **VOID** — would block 100% of converting traffic |
| C location asset | — | 5 | **VOID** — carried 2 of 6 Primary conversions |
| D-2 equipment-brand removals | `4D7AF1C9CFCA27F9` | 7 | **HOLD** — zero observed evidence |
| Original consolidated | `ACE80A09AC134C85` | 30 | **VOID** |
| Original conversion plan | `EE6CFAD6667A95A1` | 10 | **VOID** — artifact, not a defect |
| Original destructive plan | `C3038EDD9E621944` | 8 | **VOID** — split |
| Gas Boiler keywords | `3D823A10CB3C0B25` | — | **BLOCKED** — landing-page heading still wrong |
| Landing-page deployment | `93A9DF4AA19675E8` | — | **BLOCKED** — no deploy authority |

---

## 10. Artifacts

| Artifact | Path |
|---|---|
| Re-verification part 1 (CPC, WC Lead, location, hanover, sitelinks) | `clients/ambient-cooling-heating/snapshots/reverification-2026-08-28-reverify.json` |
| Re-verification part 2 (click-type × action, strict screen) | `clients/ambient-cooling-heating/snapshots/reverification-2026-08-28-reverify2.json` |
| Plan A-1 | `clients/ambient-cooling-heating/plans/AMBIENT-A-1-2026-08-28.json` |
| Plan A-2 | `clients/ambient-cooling-heating/plans/AMBIENT-A-2-2026-08-28.json` |
| Plan D-1 | `clients/ambient-cooling-heating/plans/AMBIENT-D-1-2026-08-28.json` |
| Plan D-2 (held) | `clients/ambient-cooling-heating/plans/AMBIENT-D-2-2026-08-28.json` |
| Validate-only receipt, all four | `clients/ambient-cooling-heating/receipts/validate-only-split-2026-08-28.json` |
| Corrected metrics | `clients/ambient-cooling-heating/receipts/corrected-metrics-2026-08-28.json` |
| Unchanged-resource proof | `clients/ambient-cooling-heating/receipts/post-reverify-unchanged-proof-2026-08-28.json` |
| This report | `reports/ambient-cooling-heating/2026-08-28-corrected-decision-package.md` |

The three original plan files now carry `void: true`, `do_not_execute: true`, and the exact
evidence that voided them.
