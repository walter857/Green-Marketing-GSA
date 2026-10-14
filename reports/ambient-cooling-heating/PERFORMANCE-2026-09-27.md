# Ambient heating Search: performance review (2026-09-27)

Data: `snapshots/performance-2026-09-27.json`. Window 2026-09-17..09-26. Core ad groups moved to offer pages
on 09-24 and the deferred groups were paused on the afternoon of 09-25. Ads serve Mon–Fri 08–16 only.

## Search terms (re-checked 09-27)
- 190 distinct search terms; 0 off-topic terms left unblocked.
- Added PHRASE "how does" and "how often" (informational questions).
- Guards dropped "how many", "how long" and "what is a": each would block a replacement-research test search or an
  on-target heating search.
- Negatives now on the heating campaigns: 78 EXACT (list 12252013691) plus 491 in list 12249470554.
- Off-topic spend found: $109.15 of $621.00. It was concentrated in Heating Repair: $57.43 of that group's $153.61.

## Totals
- All seven campaigns: 1,091 impressions, 28 clicks, $621.00, **0 conversions of any action**.
- Leads: no WhatConverts lead with a click ID. One Google call record: 52 s on 09-25, under the 60 s threshold.
  The only paid-labelled WhatConverts leads were a wrong-number call (09-23) and a legacy text to 415-9517.
- Groups that are now held spent $150.41 before the pause: Maintenance $82.22, Geothermal $50.58,
  Ductless Installation $17.61. Nothing since.
- Core groups on offer pages (09-24..09-26): $448.42, 16 clicks, 0 leads. At a 5–10% landing-page conversion rate that
  is roughly 1–2 expected leads, so 0 is not yet a signal.

## Campaigns
| Campaign | Budget / CPC cap | Impr | Clicks | CTR | Avg CPC | Cost | IS | Lost to rank | Lost to budget | Read |
|---|---|---|---|---|---|---|---|---|---|---|
| Heating & Furnace Repair | $85 / $42 | 421 | 8 | 1.9% | $22.71 | $181.71 | 35% | 65% | 0% | Most volume; 37% off-topic (now blocked); $159 on Fri (Google's 2× day); 6 of 8 clicks mobile; call button paused |
| Install / Replace | $60 / $46 | 252 | 5 | 2.0% | $13.87 | $69.33 | 47% | 53% | 0% | Cheapest clicks; Heating Installation 80 impr, 0 clicks; "new furnace cost" QS 1 |
| Boiler Services | $45 / $60 | 45 | 6 | 13.3% | $34.60 | $207.58 | 71% | 18% | 10.5% | Best CTR, dearest clicks ($38.95 since 09-24); hit budget on 2 days; all mobile |
| Heat Pump | $15 / $35 | 5 | 1 | — | $29.58 | $29.58 | 50% | 50% | 0% | Almost no demand yet; Repair and Replacement 0 impr |
| Thermostat | $15 / $20 | 0 | 0 | — | — | $0 | 10% | 90% | 0% | No delivery; very low demand |
| Maintenance (deferred) | $45 / $32 | 324 | 5 | 1.5% | $16.44 | $82.22 | 28% | 72% | 0% | Spent before the pause; now 0 |
| Geothermal (waiting page) | $20 / $38 | 44 | 3 | 6.8% | $16.86 | $50.58 | 44% | 56% | 0% | Main-site ads before the pause; QS 3 (landing page below average) |

## Core ad groups
| Ad group | Impr | Clicks | Cost | Notes |
|---|---|---|---|---|
| Heating Repair | 363 | 7 | $153.61 | $57.43 off-topic (now blocked); phrase "heating repair" / "heater repair" carry the volume |
| Furnace Repair | 46 | 1 | $28.10 | QS 5 (expected CTR below avg, ad relevance above, landing page average) |
| Gas Furnace Repair | 10 | 0 | $0 | One ad housing-limited (appeal pending) |
| No Heat Repair / Electric Furnace Repair | 2 / 0 | 0 | $0 | Low volume |
| Furnace Replacement | 75 | 3 | $51.72 | $9.33 off-topic; EXACT "new furnace cost" QS 1 (1 click, $26.55) |
| Heating Installation | 80 | 0 | $0 | Impressions but no clicks |
| Heating Replacement / Furnace Installation | 23 / 11 | 0 | $0 | Low volume |
| Boiler Repair | 21 | 3 | $125.17 | $41.72 per click |
| Gas Boiler Repair | 20 | 3 | $82.41 | Ads rated EXCELLENT |
| Boiler Replacement | 4 | 0 | $0 | |
| Heat Pump Installation | 5 | 1 | $29.58 | |
| Heat Pump Repair / Replacement, Thermostat x3 | 0 | 0 | $0 | Keywords eligible; no demand yet |

## Findings
1. It is too early to judge lead performance. Two and a half business days on offer pages, 16 core clicks. Furnace search
   demand still ramps about 6.5× from September to January.
2. Reach is limited by ad rank, not budget. 47–65% of eligible impressions are lost to rank in Repair, Install and Heat Pump,
   and average CPCs sit far below the caps there. The caps are not what is holding position.
3. CTR is low on Repair and Install (1.9–2.1%, absolute-top share 15–25%) but high on Boiler (13%).
4. Mobile brings 24 of 28 clicks, yet the Repair and Install/Replace campaigns have no active call button.
5. Boiler clicks are the most expensive ($35–42) with no lead after $208. Boiler leads qualified well last season
   (5 of 5 decided), but CPA ran near $791.

## Recommended next steps (none applied)
- Leave the core groups unchanged until Friday 2026-10-02, or until core spend reaches $1,000, whichever comes first. Then
  judge cost per lead by campaign, using WhatConverts leads and Google call records.
- Once the first genuine 415-9517 ad call verifies routing, enable the call asset on Repair and Install/Replace.
- Boiler: keep the $60 cap for now; lowering caps cut conversions before. If $400 more is spent with no lead,
  revisit Boiler's budget and cap together.
- Run `ambient_0927_heating_neg_increment.py` weekly.

## Click forensics (added 2026-09-27; `snapshots/click-forensics-2026-09-27.json`)

**Where the $621 went**
- $366.41 bought 12 clicks to the offer pages, **11 of them on Friday 09-25**. That is $30.53 a click, for 0 forms and 0 calls.
- $233.10 bought 15 clicks to main-site pages before the migration. Main-site forms are invisible to WhatConverts
  (NitroPack), so any leads there are untracked.
- $21.49 was call and map clicks.
- 100% of impressions and clicks came from inside the targeted area (user_location_view).
- Google filtered **74 invalid clicks** (not charged) against 28 billed clicks.

**Ad position (share of OUR impressions)**
| Campaign | #1 ad | Top block | Impression share | Lost to rank |
|---|---|---|---|---|
| Repair | 45.7% | 70.1% | 35.4% | 64.6% |
| Install/Replace | 57.4% | 81.6% | 46.8% | 53.2% |
| Boiler | 69.6% | 87.0% | 71.1% | 18.4% |
| Heat Pump | 33.3% | 66.7% | 50.0% | 50.0% |

When shown, the ads are mostly at the top. The weakness is reach (auctions missed), not position.

**Click mix:** 81 of 93 raw clicks were mobile. 36 were location-extension clicks, most of them filtered as invalid.
59 raw clicks came from the top slot and 34 from lower on the page.

**Landing page, measured in Chrome on a desktop connection:** server response 1.5 s, full load 11.0 s, 3.4 MB
(2.7 MB of images), 95 requests, 44 scripts. PageSpeed Insights: the API quota was used up and the web report came back empty.

**Why no leads, ranked by evidence**
1. Only 12 tracked clicks. At 5–10% conversion that is 0.6–1.2 expected leads, and 0 is a 30–55% outcome.
2. The form's "(optional)" message field is actually required (D6), so it rejects submissions.
3. Search terms mismatch the page. "Heating repair" traffic lands on an "HVAC Repair" page, and headlines name only
   Severn, Severna Park and Columbia while clicks came from Glen Burnie, Pasadena, Catonsville, Bowie and Timonium.
4. The mobile page is heavy.
5. The Repair and Install/Replace ads have no call button.
6. 18% off-topic spend (now blocked).
7. Ambient's own LSA and Business Profile listings capture heating searchers: 36 non-paid leads in the same window.

GA4 engagement was not read: the connected Chrome profile has no Analytics access.
