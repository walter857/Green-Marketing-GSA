# 25 — Candidate and Count Reconciliation

**Account:** Pro Green - Austin - Live | `7380491929` | outdoor design & build  
**Window:** 2026-08-01..2026-08-22 (completed days 2026-08-01..2026-08-21, partial day 2026-08-22)  
**Snapshot:** `clients/pro-green-austin/snapshots/negatives-fresh-read-2026-08-22.json` read 2026-08-22T13:27:29.342047+00:00  
**Mode:** READ + AUDIT + DRAFT + VALIDATE-ONLY. No external write.

## 1. Why the previous counts did not reconcile

| Previous statement | What it actually was | Resolution |
|---|---|---|
| 349 search-term rows | Correct. The API returns 349 rows for the window. | Confirmed against a fresh read. |
| KEEP 9 + WATCH 215 + NEGATIVE_PHRASE 11 + INSUFFICIENT_DATA 90 = **325** | The old classifier aggregated rows to one row per `(term, ad group)` pair before writing the CSV, and separately dropped any row whose campaign was not ENABLED. 325 was the count of surviving pairs, not of source rows. | **The 24 missing rows are the duplicate `(term, ad group)` collisions.** This run keeps every source row: 36 normalized terms occur on more than one row, contributing 42 extra rows, and the two totals now differ only because the old file also merged rows that differed by matched keyword or search-term match type. The replacement CSV has 349 rows and reconciles exactly on rows, terms, impressions, clicks, cost and conversions. |
| 25 competitor brands | 25 **objects** in the `competitor_brand` family. The written list held 24 names. | **No competitor was omitted from the written list.** `allied outdoor solutions` appeared twice, once in `Hardscaping \| BOFU` and once in `Landscape Design \| BOFU`, so 24 distinct phrases produced 25 ad-group objects. |
| 28 ad-group actions | 27 distinct phrases + 1 duplicated phrase = 28. | Consistent once the duplicate above is accounted for. |
| 54 campaign-level objects | 27 distinct phrases x 2 campaigns = 54. | Arithmetically consistent, but it described a hypothetical campaign-scoped plan that was never built. The plan that carried fingerprint `4EEF81C7F2F5` contained 28 **ad-group** objects. |

## 2. Row-level reconciliation, replacement run

| Measure | Source (API) | Verdict CSV | Match |
|---|---:|---:|:--:|
| Search-term rows | 349 | 349 | YES |
| Distinct raw terms | 307 | 307 | YES |
| Distinct normalized terms | 307 | 307 | YES |
| Impressions | 797 | 797 | YES |
| Clicks | 25 | 25 | YES |
| Cost | $555.45 | $555.45 | YES |
| Conversions | 0.0 | 0.0 | YES |
| Conversion value | $0.00 | $0.00 | YES |

Every one of the 349 returned rows carries a verdict. No zero-impression, zero-click, duplicate or partial-day row was dropped. The raw search term is preserved verbatim in `raw_search_term`; `normalized_search_term` exists only for deduplication and matching.

### Duplicate terms

36 normalized terms appear on more than one row, contributing 42 extra rows. A term repeats when it is served by more than one ad group, by more than one matched keyword, or under more than one search-term match type. Both campaigns can serve the same query because they hold adjacent themes.

| Normalized term | Rows | Campaigns | Ad groups | Matched keyword / match type |
|---|---:|---:|---:|---|
| `best landscaping companies near me` | 3 | 1 | 1 | `landscape designers near me` [EXACT]; `landscape designers near me` [PHRASE] |
| `hardscape companies near me` | 3 | 1 | 1 | `hardscape contractors near me` [EXACT]; `hardscape contractors near me` [PHRASE] |
| `landscaper near me` | 3 | 1 | 2 | `landscape designers near me` [EXACT]; `landscape designers near me` [PHRASE]; `outdoor living contractors near me` [PHRASE] |
| `landscaping companies near me` | 3 | 1 | 2 | `landscape designers near me` [EXACT]; `landscape designers near me` [PHRASE]; `outdoor living contractors near me` [PHRASE] |
| `patio installation near me` | 3 | 1 | 2 | `hardscape contractors near me` [PHRASE]; `patio contractors near me` [EXACT]; `patio contractors near me` [PHRASE] |
| `paver installers near me` | 3 | 2 | 3 | `hardscape contractors near me` [PHRASE]; `outdoor living contractors near me` [PHRASE]; `patio contractors near me` [PHRASE] |
| `allied outdoor solutions austin` | 2 | 2 | 2 | `residential hardscape contractor` [PHRASE]; `residential landscape design company` [PHRASE] |
| `backyard designer` | 2 | 1 | 1 | `landscape designers near me` [EXACT]; `landscape designers near me` [PHRASE] |
| `best landscapers near me` | 2 | 1 | 2 | `landscape designers near me` [PHRASE]; `outdoor living contractors near me` [PHRASE] |
| `el bambis pavers` | 2 | 1 | 2 | `paver installation company` [PHRASE]; `paver patio installation company` [PHRASE] |
| `garden landscaping companies near me` | 2 | 1 | 2 | `landscape designers near me` [PHRASE]; `outdoor living contractors near me` [PHRASE] |
| `hardscaping near me` | 2 | 1 | 1 | `hardscape contractors near me` [EXACT]; `hardscape contractors near me` [PHRASE] |

_(36 duplicate terms in total; the full set is in the verdict CSV and in `25_candidate_reconciliation.json`.)_

## 3. Verdict totals

| Verdict | Intent family | Rows | Impr | Clicks | Cost |
|---|---|---:|---:|---:|---:|
| **KEEP** | _all_ | **20** | **95** | **15** | **$356.06** |
| | VERIFIED_SERVICE_INTENT | 9 | 16 | 10 | $251.23 |
| | GENERIC_LANDSCAPING | 8 | 54 | 5 | $104.83 |
| | CONVERTED_FAMILY | 3 | 25 | 0 | $0.00 |
| **ALREADY_BLOCKED** | _all_ | **7** | **21** | **5** | **$97.33** |
| | PRE_EXISTING_NEGATIVE | 7 | 21 | 5 | $97.33 |
| **NEGATIVE_PHRASE** | _all_ | **47** | **180** | **4** | **$81.80** |
| | COMPETITOR | 34 | 125 | 2 | $36.39 |
| | WRONG_MARKET | 7 | 17 | 1 | $33.01 |
| | WRONG_SERVICE | 1 | 5 | 1 | $12.40 |
| | WRONG_MATERIAL | 5 | 33 | 0 | $0.00 |
| **WATCH** | _all_ | **175** | **378** | **1** | **$20.26** |
| | MANUFACTURER_PRODUCT | 5 | 9 | 1 | $20.26 |
| | COMPETITOR_UNVERIFIED | 84 | 123 | 0 | $0.00 |
| | VERIFIED_SERVICE_INTENT | 49 | 149 | 0 | $0.00 |
| | SERVICE_MATERIAL_VARIANT | 1 | 3 | 0 | $0.00 |
| | GENERIC_LANDSCAPING | 32 | 82 | 0 | $0.00 |
| | COMPETITOR_WITH_CONVERSION_EVIDENCE | 1 | 4 | 0 | $0.00 |
| | AMBIGUOUS_ADJACENT_SERVICE | 2 | 7 | 0 | $0.00 |
| | LOCAL_SERVICE_IN_TARGET_AREA | 1 | 1 | 0 | $0.00 |
| **INSUFFICIENT_DATA** | _all_ | **100** | **123** | **0** | **$0.00** |
| | VERIFIED_SERVICE_INTENT | 95 | 114 | 0 | $0.00 |
| | UNCLASSIFIED | 5 | 9 | 0 | $0.00 |
| **TOTAL** | | **349** | **797** | **25** | **$555.45** |

## 4. Candidate reconciliation

| Step | Count |
|---|---:|
| Prior competitor candidates re-evaluated | 24 |
| Prior candidates retained after verification | 20 |
| Prior candidates rejected after verification | 4 |
| Phrases carrying those retained candidates | 20 |
| Newly verified competitor phrases added this run | 7 |
| Brand-shaped queries found but NOT verified | 76 |
| **Unique candidate phrases** | **34** |
| &nbsp;&nbsp;of which COMPETITOR | 27 |
| &nbsp;&nbsp;of which WRONG_MARKET | 5 |
| &nbsp;&nbsp;of which WRONG_MATERIAL | 1 |
| &nbsp;&nbsp;of which WRONG_SERVICE | 1 |
| Removed because already effectively blocked | 0 |
| Removed because of a conflict | 0 |
| Terms retained as WATCH instead of blocked | 93 |
| Base target count (34 x 2 campaigns) | 68 |
| Campaign targets removed | 0 |
| **Proposed campaign targets** | **68** |
| &nbsp;&nbsp;Progreen Austin \| Search \| Hardscape Construction | 34 |
| &nbsp;&nbsp;Progreen Austin \| Search \| Outdoor Living & Design | 34 |

### Count logic

```
base target count   = 34 safe unique phrases x 2 campaigns = 68
minus already blocked = 0
minus unsafe          = 0
final object count    = 68
```

Candidate phrases **34**, campaign targets **68**, YAML actions **68**, YAML objects **68**, CSV rows **68**, validate-only operations **68**. All six reconcile.

### Every phrase appears in exactly one ad group family or several?

Campaign scope makes this question moot for the plan, but it is recorded for evidence. These phrases were observed in more than one ad group during the window:

| Normalized term | Ad groups |
|---|---|
| `allied outdoor solutions austin` | Hardscaping \| BOFU, Landscape Design \| BOFU |
| `best landscapers near me` | Landscape Design \| Near Me, Outdoor Living \| Near Me |
| `el bambis pavers` | Patios \| BOFU, Pavers \| BOFU |
| `garden landscaping companies near me` | Landscape Design \| Near Me, Outdoor Living \| Near Me |
| `landscape design and construction near me` | Landscape Design \| Near Me, Outdoor Living \| Near Me |
| `landscape retaining wall contractors near me` | Hardscaping \| Near Me, Retaining Walls \| Near Me |
| `landscaper near me` | Landscape Design \| Near Me, Outdoor Living \| Near Me |
| `landscaping companies near me` | Landscape Design \| Near Me, Outdoor Living \| Near Me |
| `patio contractor near me` | Outdoor Living \| Near Me, Patios \| Near Me |
| `patio installation near me` | Hardscaping \| Near Me, Patios \| Near Me |
| `patio installers near me` | Hardscaping \| Near Me, Patios \| Near Me |
| `paver installers near me` | Hardscaping \| Near Me, Outdoor Living \| Near Me, Patios \| Near Me |
| `paving companies near me` | Driveways \| Near Me, Pavers \| Near Me |
| `paving contractors near me` | Driveways \| Near Me, Hardscaping \| Near Me |
| `residential landscape designer` | Landscape Design \| BOFU, Landscape Design \| Near Me |

_17 terms in total appeared in more than one ad group. This is exactly why the replacement plan is campaign-scoped: a categorically unwanted query is unwanted wherever it lands, and ad-group scoping would have left every other ad group open._

## 5. Prior candidates rejected, with the reason

| Prior candidate | New verdict | Why |
|---|---|---|
| `apollo pergola` | WATCH / MANUFACTURER_PRODUCT | Apollo Opening Roof is a louvered-pergola manufacturer in Roseville CA that sells through builders, not an Austin landscaping competitor. Pergolas are a verified Pro Green service, so the query carries real pergola-buying intent. Blocking it would suppress a qualified prospect. |
| `cedarcrest` | WATCH / COMPETITOR_UNVERIFIED | No company of that name could be confirmed, and Cedarcrest is a common subdivision and street name. The query may be a resident asking for landscaping in Cedarcrest, who is exactly the customer this campaign wants. |
| `clean scapes` | WATCH / COMPETITOR_WITH_CONVERSION_EVIDENCE | Clean Scapes, LP is a verified Austin firm, but the conflict check found that the all-time query 'clean scapes austin texas' recorded all_conversions = 1.0 on a $4.91 click. Overriding a documented conflict to gain a negative worth 4 impressions and $0.00 this month is a bad trade. |
| `stones and scapes` | WATCH / COMPETITOR_UNVERIFIED | Not confirmed. The nearest verified firm is 'Scapes and Stones' in North Las Vegas, a different name in a different market. |

## 6. Competitors the previous written summary never listed

Verified this run and **added** to the plan (7 phrases):

| Phrase | Aug impr | Aug clicks | Aug cost | Verification |
|---|---:|---:|---:|---|
| `blingle` | 2 | 0 | $0.00 | Blingle! Premier Lighting (blingle.com), national outdoor and holiday lighting franchise. Competitor for landscape-lighting demand. Covers 'blingle lighting' and 'blingle of central texas'. |
| `estudio ome` | 1 | 0 | $0.00 | Estudio Ome (estudioome.com), Mexico City landscape architecture practice. Competitor brand and wrong market. |
| `ground guys` | 1 | 0 | $0.00 | The Grounds Guys (groundsguys.com), national landscaping franchise offering landscape design, installation and outdoor lighting. Observed spelling is the singular 'ground guys'. |
| `outdoor lighting perspectives` | 2 | 0 | $0.00 | Outdoor Lighting Perspectives (outdoorlightingfranchise.com), North America's largest outdoor landscape lighting franchise. PHRASE scope cannot block generic 'outdoor lighting' demand, because the full three-word phrase must appear. |
| `waterloo artificial turf` | 1 | 0 | $0.00 | Same verified company, second observed spelling. A PHRASE negative on 'waterloo turf' does not cover it, because negative keywords do not match close variants. |
| `yardzen` | 2 | 0 | $0.00 | Yardzen (yardzen.com), national online landscape design-and-build service. Competitor for landscape-design demand. |
| `zeterre` | 2 | 0 | $0.00 | Zeterre Landscape Architecture (zeterre.com), San Francisco Bay Area landscape architecture firm. Competitor brand and wrong market. |

Brand-shaped and **not** blocked, because no reliable confirmation was obtained in this pass. All 76 produced 0 clicks and $0.00 this month, so nothing is lost by waiting for verification:

```
  512 paving austin tx                    alpha paving texas                      amy hovis
  applewood landscaping                   artificial grass pros                   artificial grass pros austin
  atx decks and pergolas                  atx luxury turf                         austin creative landscaping
  austin eischeid                         austin landscapes co                    austin native landscaping austin tx
  b and b landscaping near me             b jane gardens                          beauty scapes
  bennett paving leander tx               big bully turf cost                     bolt landscape design
  breaux's landscaping and custom concretebusby landscaping                       camilleri solutions landscaping
  canopy collective landscaping           casey boyter gardens                    ciel design for gardens
  cornerstone hardscape                   daniels landscaping                     dh landscape design
  double t design and development         dragonscapes landscaping                drake landscaping austin
  eden garden design austin               el bambis pavers                        envy landscape design
  fertile ground austin                   forge outdoor design                    furrow studio austin
  golden hour landscaping                 greenscapes landscaping                 h&m landscape and sprinkler
  henrys hardscape                        heroes landscaping                      herrera landscaping near me
  ivan landscaping                        jackson broussard austin                jurado landscaping
  jxc landscaping                         leons landscaping                       lisa lapaso
  luxe landscape design                   madrone landscape austin                mario landscaping
  mario's landscape service               mathis landscape design                 new native gardens austin
  orca landscape                          peachtree landscaping austin            perfect cuts landscaping
  praetorian landscaping                  proscape landscaping austin tx          rdc paving hutto tx
  s o s masonry and landscaping           signature pavers                        silver leaf landscaping and construction
  southern landscape austin               stallion paving                         stevens paving
  sublime patio austin                    sunscape austin                         the greener side landscaping
  the hillbilly hardscapers               tillman austin tx                       tillman walls
  turf hub cedar park                     umana landscaping                       vera lawn
  wetzel landscaping
```

## 7. Phrases proposed

| Phrase | Family | Campaigns | Aug impr | Aug clicks | Aug cost | Supporting terms |
|---|---|---:|---:|---:|---:|---|
| `allied outdoor solutions` | COMPETITOR | 2 | 6 | 0 | $0.00 | `allied outdoor solutions austin`, `allied outdoor solutions austin tx`, `allied outdoor solutions san antonio` |
| `biggadike` | COMPETITOR | 2 | 1 | 1 | $14.79 | `biggadike landscape lighting` |
| `blingle` | COMPETITOR | 2 | 2 | 0 | $0.00 | `blingle lighting`, `blingle of central texas` |
| `casas landscaping` | COMPETITOR | 2 | 4 | 0 | $0.00 | `casas landscaping` |
| `cooper and company` | COMPETITOR | 2 | 10 | 0 | $0.00 | `cooper and company austin` |
| `cutters landscaping` | COMPETITOR | 2 | 15 | 0 | $0.00 | `cutters landscaping austin`, `cutters landscaping austin tx` |
| `design ecology` | COMPETITOR | 2 | 3 | 0 | $0.00 | `design ecology austin` |
| `dl landscaping` | COMPETITOR | 2 | 4 | 0 | $0.00 | `dl landscaping` |
| `ecotopes` | COMPETITOR | 2 | 3 | 0 | $0.00 | `ecotopes` |
| `estudio ome` | COMPETITOR | 2 | 1 | 0 | $0.00 | `estudio ome` |
| `four roots landscaping` | COMPETITOR | 2 | 4 | 0 | $0.00 | `four roots landscaping` |
| `ground and garden` | COMPETITOR | 2 | 6 | 0 | $0.00 | `ground and garden austin` |
| `ground guys` | COMPETITOR | 2 | 1 | 0 | $0.00 | `ground guys` |
| `hellas` | COMPETITOR | 2 | 4 | 0 | $0.00 | `hellas matrix turf`, `hellas turf` |
| `magnolia turf` | COMPETITOR | 2 | 6 | 0 | $0.00 | `magnolia turf austin` |
| `outdoor lighting perspectives` | COMPETITOR | 2 | 2 | 0 | $0.00 | `outdoor lighting perspectives` |
| `ps landscapes` | COMPETITOR | 2 | 5 | 0 | $0.00 | `ps landscapes austin` |
| `ranchers landscaping` | COMPETITOR | 2 | 5 | 0 | $0.00 | `ranchers landscaping` |
| `southern turf` | COMPETITOR | 2 | 5 | 0 | $0.00 | `southern turf co`, `southern turf co austin` |
| `terra landscaping` | COMPETITOR | 2 | 2 | 1 | $21.60 | `terra landscaping` |
| `the mark landscapes` | COMPETITOR | 2 | 4 | 0 | $0.00 | `the mark landscapes` |
| `twelve point landscaping` | COMPETITOR | 2 | 4 | 0 | $0.00 | `twelve point landscaping` |
| `waldemar landscaping` | COMPETITOR | 2 | 3 | 0 | $0.00 | `waldemar landscaping` |
| `waterloo artificial turf` | COMPETITOR | 2 | 1 | 0 | $0.00 | `waterloo artificial turf` |
| `waterloo turf` | COMPETITOR | 2 | 20 | 0 | $0.00 | `waterloo turf austin` |
| `yardzen` | COMPETITOR | 2 | 2 | 0 | $0.00 | `yardzen packages` |
| `zeterre` | COMPETITOR | 2 | 2 | 0 | $0.00 | `zeterre` |
| `dallas` | WRONG_MARKET | 2 | 4 | 0 | $0.00 | `outdoor lighting dallas` |
| `dfw` | WRONG_MARKET | 2 | 8 | 0 | $0.00 | `alpha paving dfw`, `outdoor lighting dfw` |
| `lubbock` | WRONG_MARKET | 2 | 1 | 0 | $0.00 | `west texas paving lubbock` |
| `san antonio` | WRONG_MARKET | 2 | 3 | 1 | $33.01 | `pavers san antonio texas`, `retaining wall contractors san antonio` |
| `waco` | WRONG_MARKET | 2 | 1 | 0 | $0.00 | `waco paving` |
| `asphalt` | WRONG_MATERIAL | 2 | 33 | 0 | $0.00 | `asphalt and concrete paving`, `asphalt paving austin`, `asphalt paving austin tx`, `asphalt paving contractors`, `texas asphalt paving` |
| `handrail` | WRONG_SERVICE | 2 | 5 | 1 | $12.40 | `outdoor handrail installation near me` |
