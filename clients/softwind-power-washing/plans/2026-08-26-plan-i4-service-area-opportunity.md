# PLAN-I4 — SERVICE-AREA OPPORTUNITY

**STATUS: OPPORTUNITY ANALYSIS ONLY. NOT A PLAN. NO FINGERPRINT. NOTHING EXECUTABLE.**

**Account:** Softwind Power Washing - Live · `1521725229` · **Service:** Power Washing
**Analysed:** 2026-08-26 · **NO GEO CHANGE IS PROPOSED**

> **This is the single largest demand lever available to the account, and it is the one
> lever that cannot be pulled from this desk.** Every candidate below is marked
> **NEEDS WALTER CONFIRMATION** and none enters an executable fingerprint.

---

## 1. What is targeted today — verified

Eight geo targets, identical on both campaigns, all positive, **no exclusions**,
`positive_geo_target_type: PRESENCE`.

| Geo ID | Type | Canonical name | County |
|---|---|---|---|
| `1022729` | City | Bellmore, New York | Nassau |
| `1023035` | City | **Islip, Islip, New York** | Suffolk |
| `1023415` | City | Syosset, New York | Nassau |
| `1023482` | City | West Islip, New York | Suffolk |
| `9051836` | City | Dix Hills, New York | Suffolk |
| `9052792` | City | Salisbury, New York | Nassau |
| `9198508` | **Municipality** | North Hempstead, New York | Nassau |
| `9214462` | **Municipality** | Babylon, New York | Suffolk |

**The core defect, restated with the ID that proves it.** `1023035` is *Islip, **Islip**,
New York* — the **hamlet**, reach ≈186,000 in Google's own suggestion data. The **Town of
Islip** is a different constant, `9198487`, reach **≈785,000**. The campaign targets the
smaller of the two. Dix Hills is likewise an isolated point inside the Town of Huntington;
Syosset inside the Town of Oyster Bay.

Delivery integrity is clean: `user_location_view.targeting_location` is `true` on every
row. **Zero out-of-area leakage today.**

---

## 2. The client's own published service area — research evidence only

Read from `https://softwindli.com/service-areas/` on 2026-08-26.

> **A town appearing on a marketing page is NOT proof the client serves it for Power
> Washing.** This is research evidence to structure a question, not an authorisation.

**21 towns are named on that page:**

Amityville · Babylon · Bay Shore · Bellmore · Commack · Deer Park · Dix Hills · East Islip ·
Farmingdale · Hauppauge · Huntington · Islip · Lindenhurst · Massapequa · Melville ·
Merrick · Northport · Patchogue · Sayville · Syosset · West Islip

**The campaign targets 8. The client's own site claims 21.** That gap is the finding.

---

## 3. Measured incremental demand

Keyword Planner, `GOOGLE_SEARCH` network, English, the **same 10 head BOFU seeds** across
every geo set so the comparison is like-for-like. Volume buckets collapsed before summing,
so power/pressure synonym pairs are not double counted.

| Geo set | Geos | Distinct monthly searches | Multiplier |
|---|---:|---:|---:|
| **Current 8 targets** | 8 | **360** | 1.00× |
| Current 8 + Town of Islip + Town of Oyster Bay | 10 | **750** | **2.08×** |
| Six towns only (Islip, Oyster Bay, Smithtown, Brookhaven, Babylon, N. Hempstead) | 6 | **1,090** | **3.03×** |
| **Eight-town footprint** (above + Hempstead + Huntington) | 8 | **1,650** | **4.58×** |

Individually measured: Brookhaven **300** · Oyster Bay **230** · Town of Islip **170** ·
Smithtown **140** · Brentwood 10 · Bay Shore 10.

*Two individual measurements — Town of Hempstead and Huntington city — returned a Keyword
Planner quota error (`RESOURCE_EXHAUSTED`) and are reported as unavailable rather than
estimated. They are included in the eight-town aggregate, which did return.*

---

## 4. Candidate additions

Every row: **NEEDS WALTER CONFIRMATION.**

| # | Exact geo target name | Geo ID | Type | Google reach | Measured BOFU demand | On client's page? | Landing-page requirement | Currently verified as served? |
|---|---|---|---|---:|---|---|---|---|
| 1 | Islip, New York | `9198487` | **Municipality** | 785,000 | **170/mo standalone** | **Yes** ("Islip", "East Islip") | Pages already name Islip — **best match of any candidate** | **NEEDS WALTER CONFIRMATION** |
| 2 | Oyster Bay, New York | `9198014` | Municipality | 679,000 | **230/mo standalone** | Yes (Syosset is in Oyster Bay) | Pages name no Oyster Bay town — copy update advised | **NEEDS WALTER CONFIRMATION** |
| 3 | Brookhaven, New York | `9198728` | Municipality | 759,000 | **300/mo standalone** | Partly (Patchogue, Sayville) | No city match — copy update needed | **NEEDS WALTER CONFIRMATION** |
| 4 | Smithtown, New York | `9220615` | Municipality | 261,000 | **140/mo standalone** | Partly (Commack, Hauppauge) | No city match — copy update needed | **NEEDS WALTER CONFIRMATION** |
| 5 | Hempstead, New York | `9198814` | Municipality | **1,290,000** | not measured standalone (quota) | Partly (Merrick, Massapequa) | No city match — copy update needed | **NEEDS WALTER CONFIRMATION** |
| 6 | Huntington, New York | `1023022` | City | 137,000 | not measured standalone (quota) | **Yes** ("Huntington", "Melville", "Northport") | Dix Hills already inside Huntington Town | **NEEDS WALTER CONFIRMATION** |
| 7 | Brentwood, New York | `1022748` | City | 184,000 | 10/mo | No | No city match | **NEEDS WALTER CONFIRMATION** |
| 8 | Bay Shore, New York | `1022719` | City | 156,000 | 10/mo | **Yes** | No city match | **NEEDS WALTER CONFIRMATION** |

### Estimated incremental spend capacity

At the observed 5.71% CTR and $28.53 CPC, over the remaining days:

| Footprint | Impressions/day¹ | Clicks/day | Spend/day | Over 4 days |
|---|---:|---:|---:|---:|
| Current 8 targets | 57 | 3.3 | $93 | $372 |
| + Islip Town + Oyster Bay (2.08×) | 119 | 6.8 | $194 | $776 |
| Six-town footprint (3.03×) | 174 | 9.9 | $283 | $1,132 |
| **Eight-town footprint (4.58×)** | **263** | **15.0** | **$428** | **$1,712** |

¹ Assumes PLAN-I1 budget, PLAN-I2 enablement and PLAN-I3 schedule are all in force.
Geo expansion alone, on the current 60-hour schedule and $82/day budget, delivers far less.

---

## 5. Distance and dispatch

**Dispatch location: UNKNOWN.** No verified business address is recorded in `client.yaml`.
The offer landing pages name Islip, West Islip and Dix Hills, and the account's own
delivery concentrated in Dix Hills, Babylon and West Babylon — which suggests a Suffolk
County centre of gravity, but that is inference, not a verified address.

Rough corridor logic, offered as context and not as a recommendation:

| Candidate | Position relative to the current footprint |
|---|---|
| Town of Islip | **Contains** the currently targeted Islip hamlet and West Islip. Contiguous. |
| Town of Huntington | **Contains** Dix Hills. Contiguous. |
| Town of Oyster Bay | **Contains** Syosset. Contiguous. |
| Town of Babylon | Already targeted. |
| Town of Smithtown | Adjacent to Huntington and Islip. One town removed. |
| Town of Brookhaven | East of Islip. **Largest geographic area — a job in eastern Brookhaven could be a 45+ minute drive.** |
| Town of Hempstead | Far west Nassau. **Largest population but furthest from the Suffolk centre of gravity.** |

**Candidates 1, 2 and 6 are the safest** — each merely *completes* a town the campaign
already targets a fragment of. Candidates 3, 5 and 7 extend into genuinely new territory
and carry real drive-time risk.

---

## 6. Landing-page consequence — do not skip this

The nine offer landing pages name **Islip, West Islip and Dix Hills** and nothing else.
Their H1s read *"…In Islip, West Islip & Dix Hills, NY"*.

Expanding geo without touching the pages means a searcher in Massapequa or Patchogue clicks
an ad and lands on a page that names three towns, none of them theirs. Consequences:

- **Message match degrades**, which is a Quality Score landing-page-experience input — and
  that component is already **Below Average** on all four keywords that carry a score.
- Conversion rate on the expanded geography will run below the current footprint's.
- The `power-washing-services-islip-west-islip-dix-hills` **URL slug itself names three
  towns**, which is visible in the ad.

**If geo expands beyond Islip/West Islip/Dix Hills, a landing-page copy update belongs in
the same decision** — a PLAN-F item, not an Ads change. At minimum the H1 and hero should
generalise to "Long Island" or name the added towns.

---

## 7. The one confirmation needed

**A single question, one list, one answer:**

> **Which of these does Softwind actually serve for Power Washing?** Tick each town, and
> flag any where the drive time makes a job unprofitable.
>
> | | Town / City | Geo ID |
> |---|---|---|
> | ☐ | **Town of Islip** (completes the hamlet already targeted) | `9198487` |
> | ☐ | **Town of Huntington** (contains Dix Hills) | `1023022` |
> | ☐ | **Town of Oyster Bay** (contains Syosset) | `9198014` |
> | ☐ | Town of Smithtown | `9220615` |
> | ☐ | Town of Brookhaven | `9198728` |
> | ☐ | Town of Hempstead | `9198814` |
> | ☐ | Brentwood | `1022748` |
> | ☐ | Bay Shore | `1022719` |
>
> And one follow-up: **what is the dispatch address**, and what is the furthest drive time
> that still makes a power-washing job worth taking?

**On receipt of that list**, an executable geo plan can be fingerprinted the same day. The
work is a single `campaign_criterion` CREATE per location per campaign — small, fast and
fully reversible. **The blocker is the answer, not the work.**

---

## 8. Why this is not in any fingerprint

`CLAUDE.md` prohibits inventing locations, and `client.yaml` records
`verified_service_area: UNKNOWN`. Targeting a town Softwind cannot service would generate
leads it must decline — worse than not bidding at all, because it spends the budget *and*
damages the brand. **No unverified location enters an executable plan.**

---

**NOT A PLAN · NO FINGERPRINT · NEEDS WALTER CONFIRMATION · ZERO EXTERNAL CHANGES MADE**
