# 04 — Keyword coverage, structure and reproducible forecasts

Matrix: `04_keyword_coverage_matrix.csv` (16 candidates). Scripts: `scripts/apg_0928b_planner.py`,
`scripts/apg_0928b_forecasts.py`. Raw results: `reports/apogee-lawns/evidence/2026-09-28b-{planner,forecasts}.json`.

## Demand and seasonality (Keyword Planner historical metrics, read 2026-09-28 19:50:31 UTC)

Scope: Google Search, English, the 10 largest of the 14 approved targets (the service caps geography at 10; Eagle,
68461, 68347 and Nemaha Precinct are omitted). Values are Planner buckets, not counts. Rows that share a bucket are
never summed.

| Keyword family row | Avg / month | Sep 2025 | Oct 2025 | Nov 2025 | Dec 2025 |
|---|---:|---:|---:|---:|---:|
| permanent christmas lights (head) | 90 | 50 | 140 | **480** | 170 |
| permanent christmas light installation | 10 | 10 | 20 | 10 | 10 |
| permanent christmas lights installer | 10 | 0 | 0 | 10 | 0 |
| permanent holiday light installation | 10 | 0 | 0 | 10 | 0 |
| permanent holiday lights | 10 | 10 | 10 | 10 | 10 |
| permanent christmas lights lincoln ne | 10 | 20 | 20 | 50 | 10 |
| permanent outdoor lights (product-dominated) | 30 | 20 | 70 | 210 | 50 |

**Seasonal versus structural.** Seasonal: the head family ran 50 → 140 → 480 in Sep → Oct → Nov 2025 in this same
geography. September is the trough, so the current 7-day volume understates October and November. That rests on one
season of Planner data. Structural: even at the November peak, the approved area's installer-language rows carry roughly
10 searches a month. The paid pool is small because the service is niche and the market is Lincoln-sized, not because a
setting is broken.

## Forecast scenarios — 2026-09-29 to 2026-12-20 (83 days)

Same horizon as run A, so results are like-for-like, and the whole window is still in the future. **The forecast end date
is not a campaign end date.** Common settings: Maximize Clicks, English, 14 approved geo targets, USD, one campaign, one
budget. One variable changes per row unless marked combined. Read 19:54:00–19:57:05 UTC.

**Tool limits (introspected from the installed google-ads v25 client, not assumed):** `CampaignToForecast` accepts only
language, geo targets, bidding strategy and ad groups; `ForecastAdGroup` accepts only keywords; the response is
campaign-level only. So **no negatives, no tablet −100%, no network setting, no ad schedule, no per-ad-group results, and
no shared-budget or multi-campaign simulation**. Keywords are de-duplicated by text + match type. Official note (Google
Ads Help 7337243): forecasts use about 7–10 days of recent data, adjusted for seasonality, and are refreshed daily.
**Noise band:** adding keywords sometimes *lowers* the forecast (K3 −1.0, K4 −1.7, K6 −1.5), which cannot happen in a
real auction, so differences within about ±2 clicks are noise.

| Scenario | Clicks | Cost | Avg CPC | Δ clicks | Δ cost |
|---|---:|---:|---:|---:|---:|
| **S0 current build** | **55.5** | **$266.57** | $4.80 | — | — |
| C1 CPC cap $6 | 48.3 | $187.43 | $3.88 | −7.2 | −$79.14 |
| C2 CPC cap $10 | 55.5 | $305.48 | $5.50 | +0.0 | +$38.91 |
| C3 CPC cap $12 | 62.1 | $395.58 | $6.37 | +6.6 | +$129.01 (≈$19.55 per extra click) |
| B1 daily $10.00 | 55.5 | $266.57 | $4.80 | 0 | 0 |
| B2 daily $25.00 (sensitivity only; exceeds the approved total) | 55.5 | $266.57 | $4.80 | 0 | 0 |
| K1 + head term PHRASE (isolated test) | 63.5 | $321.78 | $5.07 | +8.0 | +$55.21 (≈$6.90 per extra click) |
| K2 + lincoln + near me ad group (P+E) | 56.7 | $275.16 | $4.85 | +1.2 | +$8.59 |
| K2b + lincoln only (P+E) | 55.5 | $266.57 | $4.80 | 0 | 0 |
| D1 + buyer-modifier head-term group (cost/install/company/near me/lincoln) | 56.6 | $274.80 | $4.86 | +1.1 | +$8.23 |
| D3 that buyer-modifier set **alone** | 1.2 | $8.09 | $6.98 | — | — |
| K3 + holiday *installation* synonyms (P+E) | 54.5 | $263.16 | $4.83 | −1.0 (noise) | — |
| K4 + generic permanent holiday lights (E) | 53.8 | $261.04 | $4.86 | −1.7 (noise) | — |
| K5 + generic permanent holiday lights (E+P) | 76.2 | $351.05 | $4.61 | +20.7 | +$84.48 |
| K6 + permanent outdoor lights (E) | 54.0 | $262.97 | $4.87 | −1.5 (noise) | — |
| E1 + everlights (P+E) / E2 alone | 55.7 / 0.0 | $266.93 / $0 | — | +0.2 | — |
| X2 combined: S0 + K2 at $10 cap | 60.4 | $353.90 | $5.86 | +4.9 | +$87.33 |
| O1 **conditional research only**: Omaha alone, current keywords, own $16.44 | 82.6 | $393.56 | $4.76 | not additive | — |

Standalone deltas overlap and must not be summed. The budget rows show the model sees no budget constraint. That differs
from the live 18.5% budget-lost IS; see `00_README.md` §Diagnosis.

## Keyword and structure verdicts

- **Structure (SKAG discipline) is sound and is kept:** one installation-intent ad group (Phrase + Exact) and one
  head-term ad group (Exact only), tight to one landing page. Grouping does not change reach; keyword coverage does, and
  it is assessed separately below.
- **Verified buyer-intent coverage is not materially narrow.** Explicit buyer and local variants of the head term forecast
  1.2 clicks *on their own* across 83 days and +1.1 on top of the build. They are either already reached through the
  exact keyword's close variants or have no modelled demand. Holiday-installation synonyms: no measurable demand.
  EverLights: 0.
- **The only material incremental volume is ambiguous phrase reach.** K5 (+20.7) and K1 (+8.0). After the live negatives,
  head-term Phrase would newly reach 30 Planner ideas: 10 with buyer markers (90 summed bucket volume) and 20 without
  (120), such as reddit, tiktok, "track", "semi permanent", minleon, "dude dad", "best", "for house". That is the same
  ambiguity that kept the head term Exact-only (settled 09-17, "until search terms earn it"). Live search terms have not
  earned it: the exact keyword's 31 impressions include 19 from 8 no-marker close variants, with 0 clicks.
- **Decision: no Lincoln keyword or ad-group addition is justified by the evidence today.** The head-term Phrase test is
  drafted as a gated, non-fingerprinted plan in `06_lincoln_improvement_draft.md`. No new ad group is proposed, so no new
  RSAs are drafted.
- Avoid: permanent outdoor lights, permanent house lights (product/research; low top-of-page bids), seasonal
  "christmas light installation" (excluded service), and Broad match.
