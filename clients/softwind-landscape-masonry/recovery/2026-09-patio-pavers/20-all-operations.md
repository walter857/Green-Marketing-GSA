# Every proposed operation, one row each

Total operations across the five packages: **111**.
No operation below has been executed. All five passed `validate_only`
through `scripts/execute_approved_plan.py` on 2026-09-03.

## PLAN-SLM-BID-2  (P0-1) - 2 operation(s), fingerprint `8C71888E09CC`

### BID-01 - campaign `23484806108`

| Field | Value |
|---|---|
| Campaign | Patio |
| Ad group | - |
| Current | target_spend.cpc_bid_ceiling_micros = UNSET (no ceiling) |
| Proposed | **target_spend.cpc_bid_ceiling_micros = 16000000 (about $16.00)** |
| Rollback | clear target_spend.cpc_bid_ceiling_micros (back to UNSET) |
| Evidence | strategy=TARGET_SPEND, ceiling today=NONE, avgCPC by month={'2026-05-01': 5.97, '2026-06-01': 7.7, '2026-07-01': 8.47, '2026-08-01': 11.04, '2026-09-01': 13.98}, most expensive day={'date': '2026-08-06', 'cost': 46.67, 'clicks': 3, 'day_cpc': 15.56}, converting keyword CPCs=[8.27, 10.91] |
| Reason | No CPC ceiling exists, so nothing bounds the price of a click under Maximize Clicks. |
| Expected effect | Caps the price of a click at $16.00. Modelled retention 99.6% of historic clicks and 100% of historic conversion credits. |
| Risk | Lower auction competitiveness. Monitor search_rank_lost_impression_share; if it rises sharply with no gain in click volume, raise the ceiling through a new plan. |
| Dependency | none |

### BID-02 - campaign `23489296528`

| Field | Value |
|---|---|
| Campaign | Pavers |
| Ad group | - |
| Current | target_spend.cpc_bid_ceiling_micros = UNSET (no ceiling) |
| Proposed | **target_spend.cpc_bid_ceiling_micros = 18000000 (about $18.00)** |
| Rollback | clear target_spend.cpc_bid_ceiling_micros (back to UNSET) |
| Evidence | strategy=TARGET_SPEND, ceiling today=NONE, avgCPC by month={'2026-05-01': 7.16, '2026-06-01': 11.16, '2026-07-01': 11.31, '2026-08-01': 21.04, '2026-09-01': 22.76}, most expensive day={'date': '2026-08-20', 'cost': 46.54, 'clicks': 1, 'day_cpc': 46.54}, converting keyword CPCs=[7.75, 11.09, 12.61, 13.25, 14.71, 16.75, 26.54] |
| Reason | No CPC ceiling exists, so nothing bounds the price of a click under Maximize Clicks. |
| Expected effect | Caps the price of a click at $18.00. Modelled retention 87.3% of historic clicks and 88% of historic conversion credits. |
| Risk | Lower auction competitiveness. Monitor search_rank_lost_impression_share; if it rises sharply with no gain in click volume, raise the ceiling through a new plan. |
| Dependency | none |

## PLAN-SLM-BUD-2  (P0-2) - 2 operation(s), fingerprint `BB9869E17E37`

### BUD-01 - campaign_budget `15309303030`

| Field | Value |
|---|---|
| Campaign | Patio |
| Ad group | - |
| Current | amount_micros = 33000000 ($33.00/day) |
| Proposed | **amount_micros = 24000000 ($24.00/day)** |
| Rollback | amount_micros = 33000000 ($33.00/day) |
| Evidence | sole campaign on this budget; reference_count=1, shared=False |
| Reason | Projected September spend exceeds the $2,000 account cap at the current budgets. |
| Expected effect | Reduces this campaign's daily exposure; combined projection falls to $1760.36. |
| Risk | Fewer daily clicks in an account already buying 3-6 a day. |
| Dependency | none |

### BUD-02 - campaign_budget `15314089588`

| Field | Value |
|---|---|
| Campaign | Pavers |
| Ad group | - |
| Current | amount_micros = 33000000 ($33.00/day) |
| Proposed | **amount_micros = 32000000 ($32.00/day)** |
| Rollback | amount_micros = 33000000 ($33.00/day) |
| Evidence | sole campaign on this budget; reference_count=1, shared=False |
| Reason | Projected September spend exceeds the $2,000 account cap at the current budgets. |
| Expected effect | Reduces this campaign's daily exposure; combined projection falls to $1760.36. |
| Risk | Fewer daily clicks in an account already buying 3-6 a day. |
| Dependency | none |

## PLAN-SLM-KW-2  (P0-3) - 7 operation(s), fingerprint `B7A11B246D74`

### KW-01 - ad_group_criterion `543919818878`

| Field | Value |
|---|---|
| Campaign | Pavers |
| Ad group | Paver Installation Near Me (Pharse) |
| Current | ENABLED |
| Proposed | **PAUSED** |
| Rollback | ENABLED |
| Evidence | authority=USER-2026-09-03 recovery prompt, section 2: asphalt paving, asphalt repair and blacktop are explicitly outside the approved service scope. This is a DECLARED-SCOPE exclusion, not a performance judgem… | all-time spend $132.69, 5 clicks, 1.0 raw credits, qualified leads UNKNOWN - no CRM join exists |
| Reason | Keyword text names asphalt, a service outside both work orders. |
| Expected effect | Keyword stops entering auctions; history and ID are preserved. |
| Risk | Loses the asphalt lead route, which is the intent. Reversible by setting status back to ENABLED. |
| Dependency | none |

### KW-02 - ad_group_criterion `297075223566`

| Field | Value |
|---|---|
| Campaign | Pavers |
| Ad group | Paver Installation Near Me (Pharse) |
| Current | ENABLED |
| Proposed | **PAUSED** |
| Rollback | ENABLED |
| Evidence | authority=USER-2026-09-03 recovery prompt, section 2: asphalt paving, asphalt repair and blacktop are explicitly outside the approved service scope. This is a DECLARED-SCOPE exclusion, not a performance judgem… | all-time spend $102.01, 4 clicks, 0.0 raw credits, qualified leads UNKNOWN - no CRM join exists |
| Reason | Keyword text names asphalt, a service outside both work orders. |
| Expected effect | Keyword stops entering auctions; history and ID are preserved. |
| Risk | Loses the asphalt lead route, which is the intent. Reversible by setting status back to ENABLED. |
| Dependency | none |

### KW-03 - ad_group_criterion `309567954442`

| Field | Value |
|---|---|
| Campaign | Pavers |
| Ad group | Paver Installation Near Me (Pharse) |
| Current | ENABLED |
| Proposed | **PAUSED** |
| Rollback | ENABLED |
| Evidence | authority=USER-2026-09-03 recovery prompt, section 2: asphalt paving, asphalt repair and blacktop are explicitly outside the approved service scope. This is a DECLARED-SCOPE exclusion, not a performance judgem… | all-time spend $13.21, 1 clicks, 0.0 raw credits, qualified leads UNKNOWN - no CRM join exists |
| Reason | Keyword text names asphalt, a service outside both work orders. |
| Expected effect | Keyword stops entering auctions; history and ID are preserved. |
| Risk | Loses the asphalt lead route, which is the intent. Reversible by setting status back to ENABLED. |
| Dependency | none |

### KW-04 - ad_group_criterion `300588535183`

| Field | Value |
|---|---|
| Campaign | Pavers |
| Ad group | Paver Installation Near Me (Pharse) |
| Current | ENABLED |
| Proposed | **PAUSED** |
| Rollback | ENABLED |
| Evidence | authority=USER-2026-09-03 recovery prompt, section 2: asphalt paving, asphalt repair and blacktop are explicitly outside the approved service scope. This is a DECLARED-SCOPE exclusion, not a performance judgem… | all-time spend $0.0, 0 clicks, 0.0 raw credits, qualified leads UNKNOWN - no CRM join exists |
| Reason | Keyword text names asphalt, a service outside both work orders. |
| Expected effect | Keyword stops entering auctions; history and ID are preserved. |
| Risk | Loses the asphalt lead route, which is the intent. Reversible by setting status back to ENABLED. |
| Dependency | none |

### KW-05 - ad_group_criterion `298883953673`

| Field | Value |
|---|---|
| Campaign | Pavers |
| Ad group | Paver Installation Near Me (Pharse) |
| Current | ENABLED |
| Proposed | **PAUSED** |
| Rollback | ENABLED |
| Evidence | authority=USER-2026-09-03 recovery prompt, section 2: asphalt paving, asphalt repair and blacktop are explicitly outside the approved service scope. This is a DECLARED-SCOPE exclusion, not a performance judgem… | all-time spend $0.0, 0 clicks, 0.0 raw credits, qualified leads UNKNOWN - no CRM join exists |
| Reason | Keyword text names asphalt, a service outside both work orders. |
| Expected effect | Keyword stops entering auctions; history and ID are preserved. |
| Risk | Loses the asphalt lead route, which is the intent. Reversible by setting status back to ENABLED. |
| Dependency | none |

### KW-06 - ad_group_criterion `303329780817`

| Field | Value |
|---|---|
| Campaign | Pavers |
| Ad group | Paver Installation Near Me (Pharse) |
| Current | ENABLED |
| Proposed | **PAUSED** |
| Rollback | ENABLED |
| Evidence | authority=USER-2026-09-03 recovery prompt, section 2: asphalt paving, asphalt repair and blacktop are explicitly outside the approved service scope. This is a DECLARED-SCOPE exclusion, not a performance judgem… | all-time spend $0.0, 0 clicks, 0.0 raw credits, qualified leads UNKNOWN - no CRM join exists |
| Reason | Keyword text names asphalt, a service outside both work orders. |
| Expected effect | Keyword stops entering auctions; history and ID are preserved. |
| Risk | Loses the asphalt lead route, which is the intent. Reversible by setting status back to ENABLED. |
| Dependency | none |

### KW-07 - ad_group_criterion `356532888916`

| Field | Value |
|---|---|
| Campaign | Pavers |
| Ad group | Paver Installation Near Me (Pharse) |
| Current | ENABLED |
| Proposed | **PAUSED** |
| Rollback | ENABLED |
| Evidence | authority=USER-2026-09-03 recovery prompt, section 2: asphalt paving, asphalt repair and blacktop are explicitly outside the approved service scope. This is a DECLARED-SCOPE exclusion, not a performance judgem… | all-time spend $0.0, 0 clicks, 0.0 raw credits, qualified leads UNKNOWN - no CRM join exists |
| Reason | Keyword text names asphalt, a service outside both work orders. |
| Expected effect | Keyword stops entering auctions; history and ID are preserved. |
| Risk | Loses the asphalt lead route, which is the intent. Reversible by setting status back to ENABLED. |
| Dependency | none |

## PLAN-SLM-CONV-2  (P0-5) - 1 operation(s), fingerprint `852D47BE6133`

### CONV-01 - conversion_action `7461619140`

| Field | Value |
|---|---|
| Campaign | Softwind Submit lead form |
| Ad group | - |
| Current | primary_for_goal = True |
| Proposed | **primary_for_goal = False** |
| Rollback | primary_for_goal = True |
| Evidence | day-level co-occurrence: fired 6 days, twin fired 10 days, both 6 days, alone 0 days, identical counts 5 |
| Reason | The WEBPAGE action never once fired on a day the GA4 action did not. Its events are a strict subset, and on 5 of 6 overlapping days the counts are identical. Both carry category SUBMIT_LEAD_FORM, origin WEBSITE and a sub-one-day lag. This is duplicate countin… |
| Expected effect | Reported Conversions falls by up to 8 credits across all history. Historic months are NOT restated - a credit already counted stays in the historical column - so before/after comparisons must be drawn at the change date, never across it. |
| Risk | NONE. Both in-scope campaigns run TARGET_SPEND (Maximize Clicks), which does not consume conversion data for bidding. No learning period is disturbed. This is also why the change is safe to make BEFORE the P2 Smart Bidding readiness gate rather than after. |
| Dependency | none |

## PLAN-SLM-NEG-2  (P0-4) - 99 operation(s), fingerprint `2CD5644B5504`

| # | Campaign | Negative text | Match | Class | Blocks $ | Blocks clicks | Dependency |
|---|---|---|---|---|---|---|---|
| NEG-001 | Patio | `asphalt` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-002 | Patio | `blacktop` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-003 | Patio | `macadam` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-004 | Patio | `tar and chip` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-005 | Patio | `house washing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-006 | Patio | `patio washing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-007 | Patio | `power washing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-008 | Patio | `pressure washing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-009 | Patio | `soft washing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-010 | Patio | `composite deck` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-011 | Patio | `deck builder` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-012 | Patio | `decking` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-013 | Patio | `trex` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-014 | Patio | `wood deck` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-015 | Patio | `apprentice` | PHRASE | employment_intent | 0.0 | 0 | none |
| NEG-016 | Patio | `patio enclosure` | PHRASE | high_confidence_wrong_service | 16.8 | 2 | none |
| NEG-017 | Patio | `patio enclosures` | PHRASE | high_confidence_wrong_service | 14.24 | 1 | none |
| NEG-018 | Patio | `screen room` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-019 | Patio | `screened in patio` | PHRASE | high_confidence_wrong_service | 8.79 | 1 | none |
| NEG-020 | Patio | `screened patio` | PHRASE | high_confidence_wrong_service | 8.78 | 1 | none |
| NEG-021 | Patio | `sunroom` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-022 | Patio | `paver mold` | PHRASE | diy_information_and_materials_intent | 0.0 | 0 | none |
| NEG-023 | Patio | `paver molds` | PHRASE | diy_information_and_materials_intent | 0.0 | 0 | none |
| NEG-024 | Patio | `plate compactor` | PHRASE | diy_information_and_materials_intent | 0.0 | 0 | none |
| NEG-025 | Patio | `awning` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-026 | Patio | `canopy` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-027 | Patio | `covered patio` | PHRASE | high_confidence_wrong_service | 48.22 | 4 | none |
| NEG-028 | Patio | `gazebo` | PHRASE | high_confidence_wrong_service | 24.65 | 3 | none |
| NEG-029 | Patio | `patio awning` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-030 | Patio | `patio cover` | PHRASE | high_confidence_wrong_service | 9.31 | 2 | none |
| NEG-031 | Patio | `patio roof` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-032 | Patio | `pergola` | PHRASE | high_confidence_wrong_service | 63.32 | 7 | none |
| NEG-033 | Patio | `patio restoration` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-034 | Patio | `paver re sanding` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-035 | Patio | `paver releveling` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-036 | Patio | `paver resanding` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-037 | Patio | `paver restoration` | PHRASE | high_confidence_wrong_service | 13.0 | 1 | none |
| NEG-038 | Patio | `polymeric sand` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-039 | Patio | `paver calculator` | PHRASE | diy_information_and_materials_intent | 0.0 | 0 | none |
| NEG-040 | Patio | `seal coat` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-041 | Patio | `seal coating` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-042 | Patio | `sealcoat` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-043 | Patio | `sealcoating` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-044 | Patio | `concrete sealing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-045 | Patio | `patio sealing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-046 | Patio | `paver sealer` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-047 | Patio | `sealant` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-048 | Patio | `sealing service` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-049 | Patio | `stone sealer` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-050 | Pavers | `asphalt` | PHRASE | high_confidence_wrong_service | 117.88 | 5 | PLAN-SLM-KW-2 |
| NEG-051 | Pavers | `blacktop` | PHRASE | high_confidence_wrong_service | 24.51 | 2 | none |
| NEG-052 | Pavers | `macadam` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-053 | Pavers | `tar and chip` | PHRASE | high_confidence_wrong_service | 27.38 | 2 | none |
| NEG-054 | Pavers | `house washing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-055 | Pavers | `patio washing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-056 | Pavers | `power washing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-057 | Pavers | `pressure washing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-058 | Pavers | `soft washing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-059 | Pavers | `composite deck` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-060 | Pavers | `deck builder` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-061 | Pavers | `deck contractor` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-062 | Pavers | `decking` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-063 | Pavers | `trex` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-064 | Pavers | `wood deck` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-065 | Pavers | `apprentice` | PHRASE | employment_intent | 0.0 | 0 | none |
| NEG-066 | Pavers | `patio enclosure` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-067 | Pavers | `patio enclosures` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-068 | Pavers | `screen room` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-069 | Pavers | `screened in patio` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-070 | Pavers | `screened patio` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-071 | Pavers | `sunroom` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-072 | Pavers | `paver mold` | PHRASE | diy_information_and_materials_intent | 0.0 | 0 | none |
| NEG-073 | Pavers | `paver molds` | PHRASE | diy_information_and_materials_intent | 0.0 | 0 | none |
| NEG-074 | Pavers | `plate compactor` | PHRASE | diy_information_and_materials_intent | 0.0 | 0 | none |
| NEG-075 | Pavers | `awning` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-076 | Pavers | `canopy` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-077 | Pavers | `covered patio` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-078 | Pavers | `gazebo` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-079 | Pavers | `patio awning` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-080 | Pavers | `patio roof` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-081 | Pavers | `patio restoration` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-082 | Pavers | `paver leveling` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-083 | Pavers | `paver releveling` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-084 | Pavers | `paver resanding` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-085 | Pavers | `paver restoration` | PHRASE | high_confidence_wrong_service | 8.36 | 2 | none |
| NEG-086 | Pavers | `polymeric sand` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-087 | Pavers | `paver calculator` | PHRASE | diy_information_and_materials_intent | 0.0 | 0 | none |
| NEG-088 | Pavers | `seal coat` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-089 | Pavers | `seal coating` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-090 | Pavers | `sealcoat` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-091 | Pavers | `sealcoating` | PHRASE | high_confidence_wrong_service | 117.29 | 5 | none |
| NEG-092 | Pavers | `concrete sealing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-093 | Pavers | `driveway sealing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-094 | Pavers | `patio sealing` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-095 | Pavers | `paver sealer` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-096 | Pavers | `paver sealing` | PHRASE | high_confidence_wrong_service | 13.73 | 1 | none |
| NEG-097 | Pavers | `sealant` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-098 | Pavers | `sealing service` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |
| NEG-099 | Pavers | `stone sealer` | PHRASE | high_confidence_wrong_service | 0.0 | 0 | none |

Full per-row evidence including source search terms and the collision-test result is in `20-all-operations.csv` and `06-negative-plan-v2.csv`.
