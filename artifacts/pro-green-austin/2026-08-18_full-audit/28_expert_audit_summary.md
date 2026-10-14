# 28 — Expert Audit Summary: Campaign-Level Negative Package

**Account:** Pro Green - Austin - Live | `7380491929` | outdoor design & build | hardscaping | Austin, Texas
**Mode:** READ + AUDIT + DRAFT + VALIDATE-ONLY. **No external write was performed.**
**Window:** 2026-08-01 through 2026-08-22 inclusive, account timezone `America/New_York`.
**Supersedes:** the voided round-1 ad-group plan (MASTER `2D87A5249784`, EXISTING_RESOURCES `4EEF81C7F2F5`).

---

## Recommendation

Add **34 PHRASE negative keywords at campaign level to each of the two enabled Search
campaigns — 68 objects.** They cover 27 verified competing businesses, 5 metros outside the
approved service area, and 2 trades the client does not sell. Every one passed a duplication
check against the campaign's full effective negative inventory, a conflict check against all
48 live positive keywords, all 50 all-time converting queries and all 133 queries with any
all-conversions value, and the Green Marketing protected-term list.

The measured leak these phrases would have stopped this month is **$81.80 across 4 clicks and
180 impressions**, against $1,281.10 of in-scope spend. The forward-looking value is larger
than the backward-looking one: competitor clicks on this account run $15–$25 each under the
$22 CPC ceiling, so a single blocked competitor click is worth roughly a third of a day's
combined $65.78 budget.

## What changed versus the previous plan

| | Round 1 (VOID) | Round 2 (this plan) |
|---|---|---|
| Level | Ad group, wherever the term happened to land | Campaign, both campaigns |
| Objects | 28 | 68 |
| Unique phrases | 27 | 34 |
| Competitor phrases | 24 | 27 |
| Wrong market | none | 5 |
| Wrong service or material | 3 | 2 |
| Verdict rows | 325 of 349 | 349 of 349 |
| Competitor verification | asserted | third-party confirmed, phrase by phrase |

Campaign scope is the correction that matters. **17 of the window's terms were served by more
than one ad group**, and `allied outdoor solutions` alone appeared in two. A competitor brand
is unwanted wherever it lands, so scoping it to the one ad group that happened to catch it
leaves the other 23 open.

## The four prior candidates this run rejects

1. **`apollo pergola`** — Apollo Opening Roof is a louvered-pergola *manufacturer* in
   Roseville, California that sells through builders. It is not an Austin landscaping
   competitor. Pergolas are a verified Pro Green service, so this query carries genuine
   pergola-buying intent. It is the single most expensive term now left eligible ($20.26,
   1 click) and that is the correct call: one $20 click is cheaper than suppressing a
   qualified design-and-build prospect.
2. **`cedarcrest`** — no company confirmed. Cedarcrest is a common subdivision and street
   name, so `cedarcrest landscaping` may well be a resident asking for landscaping *in*
   Cedarcrest. That is the customer this campaign exists to reach.
3. **`clean scapes`** — Clean Scapes, LP is genuinely an Austin firm, but the conflict check
   found `clean scapes austin texas` recorded `all_conversions = 1.0` on a $4.91 click. The
   term produced 4 impressions and $0.00 this month. Overriding a documented conflict for
   that is a bad trade.
4. **`stones and scapes`** — not confirmed. The nearest verified firm is *Scapes and Stones*
   in North Las Vegas: different name, different market.

## Terms deliberately left eligible

**Generic landscaping stays live.** 29 distinct terms, 40 rows, 136 impressions, 5 clicks,
$104.83 — the largest single family in the window. `landscaper near me` has converted on this
account (1 conversion, $47.22 all-time) and the family describes services the client sells.
Negative keywords do not match close variants, so blocking the plural would not have blocked
the singular in any case, and neither is proposed.

Also untouched: client brand; `paving contractors near me` and `deck builder near me` (deck
construction and concrete are verified first-party Austin services, so these are landing-page
gaps and expansion candidates, not waste); every quote, price, pricing, cost, hire,
contractor, company, local, near-me and emergency intent; and 76 brand-shaped queries that
could not be verified in this pass, all of which produced 0 clicks and $0.00.

**`curbing` is not blocked.** Concrete and masonry are both verified first-party Austin
services and decorative landscape curbing is a plausible component of design-and-build
hardscape work. The word does not appear on the site, so the evidence is ambiguous, and
ambiguous resolves to WATCH. 5 impressions, 0 clicks, $0.00.

## Phase 1 negatives: confirmed effective, no leakage

All five became effective **2026-08-19 08:50:50 account time** via the Google Ads API, at
campaign level on both campaigns. They were part of a set of eight; `mcdugald steele`,
`mirror lake landscaping` and `spring texas` drew no matching query this month.

| Phrase | Level | Match | Campaigns | Matching query dates | Impr / clicks / cost **before** effective | **After** effective |
|---|---|---|---|---|---|---|
| `agc turf` | campaign | PHRASE | both | 08-08 | 3 / 1 / $24.51 | 0 / 0 / $0.00 |
| `ulm austin` | campaign | PHRASE | both | 08-07, 08-11, 08-14 | 4 / 1 / $24.24 | 0 / 0 / $0.00 |
| `garden goat` | campaign | PHRASE | both | 08-09 | 2 / 1 / $19.42 | 0 / 0 / $0.00 |
| `agave landscaping` | campaign | PHRASE | both | 08-04, 08-07 | 2 / 1 / $18.87 | 0 / 0 / $0.00 |
| `astoria lighting` | campaign | PHRASE | both | 08-01 … 08-16 | 10 / 1 / $10.29 | 0 / 0 / $0.00 |

**The $97.33 these terms cost in August is historical, not current leakage.** Every
impression, click and dollar predates the negative. Not one matching query appeared on or
after 2026-08-19. None is duplicated by this plan.

## Data completeness

- **Visible search-term spend covers 43.36% of in-scope spend** ($555.45 of $1,281.10).
  Google withholds low-volume queries, so **56.64% of this month's spend has no visible
  search term at all.** No negative list can protect against queries Google does not
  disclose, and nothing here assumes the export is complete.
- **Current-day data:** Google Ads had released no search-term and no campaign rows for
  2026-08-22 at read time (13:27 UTC / 09:27 account time). The latest available date in both
  series is **2026-08-21**. The partial-day segment is therefore empty, not estimated, and no
  verdict in this package rests on current-day evidence.
- The search-term report records **0 primary conversions** in the window, while the campaign
  report records 1 on 2026-08-04. That conversion is not attributable to any visible search
  term — a direct consequence of the withheld-query gap above.

## Findings outside this package, reported not acted on

- `cost` sits as a **BROAD** negative in the account-level list, blocking a protected
  buyer-intent term account-wide and invisibly. Account-level changes are out of scope here;
  this needs its own approval.
- The account-level negative list (`11260450591`) reports `member_count = 0` while holding
  287 distinct criteria. That is a Google Ads API reporting quirk, not a defect.
- Three shared lists reach both campaigns with 1,243 members; combined with the account-level
  list, 1,530 distinct pairs already apply campaign-wide before any campaign negative.

## Recommendation held for later, deliberately not proposed

Generic landscaping deserves its **own ad group** with its own bid and its own destination so
it can be judged on its own merits, rather than being pulled in through close variants of
`landscape designers near me` on EXACT. That is a structural change and the 48-RSA creative
test only began 2026-08-20. Introducing an unrelated structural variable now would corrupt
that test. Revisit once the RSA test has a readable result.
