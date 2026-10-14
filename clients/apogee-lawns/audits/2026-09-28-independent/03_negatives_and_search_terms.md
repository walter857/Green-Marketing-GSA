# 03 — Effective negatives and search-term coverage

Files: `03_negative_review.csv` (all 75 live negatives, one row each) and
`03_search_term_verdicts_RAW.csv` (every retrievable search-term row with a verdict; **contains raw
search terms — local only, not for printing or sharing**). Produced by
`scripts/apg_0928b_negative_review.py` from the fresh snapshot. No negative change is authorized.

## Effective negative inventory (fresh, 2026-09-28 19:45 UTC)

| Layer | Count | Live association |
|---|---:|---|
| Campaign negatives on 24257151015 | **75** (37 BROAD, 38 PHRASE, 0 EXACT) | ENABLED |
| Ad-group negatives | 0 | — |
| Shared negative lists | 7 exist (6 ENABLED, 1 REMOVED; 4,237 members) | **0 attached** (`campaign_shared_set` empty, every `reference_count` 0) |
| Account-level negative keyword list | none | only `customer_negative_criterion` 300090179 = CONTENT_LABEL PARKED_DOMAIN (Google default) |
| Cross-negatives between ad groups | none | — |

## Method

- Matching follows Google's documented negative rules (DOC: Google Ads Help 2453972): BROAD blocks a search containing all
  the words in any order; PHRASE the words in order with extra words allowed; EXACT only the exact words; **negatives do
  not match close variants** (plurals and synonyms must be added separately), although Google says they do account for
  casing and misspellings.
- `scripts/apg_negmatch.py`, 9 unit tests passing (`tests/test_apg_negmatch.py`). **Limitations:** the local model does
  not reproduce Google's misspelling handling (so it can under-state blocking), and the positive-reach proxy models only
  literal containment plus plural/installation variants, not meaning-based matching.
- Three evidence sources: (1) every **observed** search term (none can be blocked by definition, since they served);
  (2) **406 Google Keyword Planner ideas** for this service family (real suggestions with volume buckets, not this
  account's queries); (3) one **HYPOTHETICAL** probe query per negative, written to test the purchase-intent risk. Probes
  carry no volume. All 75 probes are blocked by their own negative (probe design check).

## Results

- **Buyer modifiers:** probes combining the service phrase with near me, quote, estimate, price, pricing, cost, best,
  local, hire, installer, installation, contractor, reviews, free estimate, company and lincoln ne → **0 blocked**.
- **Planner ideas reachable by the live positives:** 7 (literal proxy), **0 blocked** by any negative.
- Negatives that block any Planner idea at all: 12. `govee` alone blocks **105 ideas (740 summed bucket volume)**, which
  makes it the highest-value negative on the list: the DIY product dominates this query space.
- Verdicts: **69 KEEP · 3 REMOVE-CANDIDATE · 3 NEEDS-EVIDENCE · 0 NARROW.**

| Verdict | Negatives | Why |
|---|---|---|
| REMOVE-CANDIDATE (low priority, no observed volume) | `christmas light hanging service`, `seasonal light installation`, `take down christmas lights` (PHRASE) | Every positive requires "permanent", so seasonal-only searches cannot reach the campaign anyway (negative reachability). The only queries these can still block also contain "permanent", e.g. hypothetical *permanent christmas light hanging service*, which reads as a buyer. Bundle into the next negative plan only if search terms show such queries |
| NEEDS-EVIDENCE | `labor only`, `customer supplied`, `my own lights` (PHRASE) | They encode an unverified business assumption that Apogee will not install customer-supplied lights. Owner fact required |
| KEEP (examples) | employment, DIY/instructions, retail/marketplaces, events/displays, décor products, rental, trade, competitor systems (Trimlight, Jellyfish, Gemstone, Oelo, Celebright — Apogee's own site says EverLights dealer), `govee` | Intent is not a permanent-installation buyer, or conquest is a business preference |

`best christmas displays` contains the protected word "best" only inside an event phrase; *best permanent christmas light
installer* is **not** blocked (verified).

**Answer: the negatives are not measurably suppressing buyer demand.** Residual risk: queries blocked by a negative never
appear in a search-term report, so absence there proves nothing, and meaning-based positive matching is not modelled.
The three REMOVE-CANDIDATEs are the only plausible leaks, and they have no observed volume.

## Search-term coverage (2026-09-17..09-28)

| | Search-term report | Campaign total | Coverage |
|---|---:|---:|---:|
| Impressions | 42 | 65 | 64.6% |
| Clicks | **0** | **3** | **0%** |
| Cost | $0.00 | $18.69 | 0% |

**Every paid click came from a query Google did not report.** No query-level judgment of the paid traffic is possible.

Whitelist classification of the visible rows (aggregates only; 22 daily rows, 14 distinct terms):

| Bucket | Via keyword | Distinct terms | Impr | Clicks |
|---|---|---:|---:|---:|
| Buyer marker (install, cost, company, near me, quote…) | PHRASE installation | 2 | 3 | 0 |
| Local marker only | PHRASE installation | 2 | 4 | 0 |
| No whitelist marker | PHRASE installation | 1 | 4 | 0 |
| Bare head-term variant | EXACT head | 1 | 12 | 0 |
| No whitelist marker (close variants) | EXACT head | 8 | 19 | 0 |

Verdicts in the RAW file: KEEP ELIGIBLE for buyer, local and bare-head rows; MONITOR for no-marker rows (0 clicks, $0, no
negative proposed). Zero conversions are **not** used as a reason to exclude anything: tracking is broken and the sample
is 3 clicks.
