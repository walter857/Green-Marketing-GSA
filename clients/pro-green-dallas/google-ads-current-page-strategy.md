# Google Ads Strategy on the Current Landing Pages — 2026-08-11

**Account:** Pro Green - Dallas - Live · **8735782888** · manager **3373711342**
**Constraint:** improve Google Ads around the **existing** pages. No final URL changes this run.

Evidence labels: **[FRESH-API]** · **[RUNTIME]** · **[USER]** · **[INFER]** · **[UNVERIFIED]**

---

## 1. Fresh performance — all [FRESH-API], queried 2026-08-11

| Window | Impr | Clicks | Cost | CTR | Avg CPC | Conv | All conv | IS | IS lost budget | IS lost rank | Invalid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **90 d** (05-14→08-11) | 3,560 | 190 | **$2,973.76** | 5.34% | $15.65 | **5.0** | 21.0 | 52.8% | 19.1% | 28.1% | 27 |
| **30 d** (07-13→08-11) | 1,366 | 89 | $1,019.98 | 6.52% | $11.46 | **3.0** | 11.0 | 38.2% | 27.7% | 34.1% | 16 |
| **prev 30 d** (06-13→07-12) | 1,201 | 58 | $1,003.53 | 4.83% | $17.30 | **1.0** | 3.0 | 67.1% | 12.2% | 20.7% | 4 |
| **MTD** (08-01→08-11) | 722 | 46 | $369.97 | 6.37% | **$8.04** | **0.0** | 2.0 | 29.4% | **34.4%** | 36.2% | 7 |

**Trend read.** CTR is improving (4.83% → 6.52%) and CPC is falling ($17.30 → $11.46 → $8.04),
which are genuinely good signals. But **impression share is collapsing** (67.1% → 38.2% → 29.4%)
and **share lost to budget has nearly tripled** (12.2% → 34.4%). The campaign is being squeezed by
budget precisely as it is getting more efficient.

**Zero conversions since 2026-07-31.** [FRESH-API] Last call conversion 2026-07-29, last form
conversion 2026-07-31. Eleven days and $369.97 with nothing recorded.

### Why the historical $484.11 CPL is not a qualified-lead CPL

$484.11 was **cost ÷ Conversions** over an older 90-day window. Both terms are wrong:

- **The denominator counts only what the account can still record.** Website-call action
  `6886103719` has recorded nothing since **2026-02-28** because it swaps for a number that does
  not render on these pages **[RUNTIME]**. `6616343220` "Clicks to call" died the same day.
- **The primary mobile CTA does not dial.** Both pages carry `href="tel:%91phone%93"`, an
  unresolved shortcode, on traffic that is **100% mobile** **[RUNTIME]**.
- **The denominator counts raw events, not qualified leads.** Google native tracking cannot
  express "qualified" or "quotable". Spam and wrong numbers would count identically.
- **The numerator contains measured waste** — $294.56 on competitor queries alone, zero conversions.

**Correct statement:** cost per *countable event* was $484.11. **True cost per qualified lead is
unknown.** The [USER] target is **$120 CPQL** and **$180 max per booked estimate**; neither can be
measured until WhatConverts qualified imports are proven.

---

## 2. Structural analysis

### Ad groups — 30-day [FRESH-API]

| Ad group | ID | Impr | Clicks | Cost | Conv |
| --- | --- | --- | --- | --- | --- |
| Sprinkler Repair Near Me | `151125103616` | 466 | 32 | $356.45 | 1.0 |
| Irrigation Repair Near Me | `190202910461` | 420 | 28 | $346.39 | 2.0 |
| Sprinkler System Repair | `191996690566` | 480 | 29 | $317.14 | **0.0** |

Spend is evenly balanced; the themes are genuinely distinct. **No overlap requiring resolution was
found** — a duplicate check across all 44 active keywords returned zero duplicates.

**`Sprinkler System Repair` was not paused** despite 0 conversions. Its traffic goes to Page A,
where only form leads can currently be counted at all, so its zero is **[INFER] a measurement
artifact rather than proof of failure** — and the run rules forbid pausing a valid in-scope keyword
purely on low conversion volume.

### Landing-page assignment — recorded, not changed

| Ad group | Serving ad | Final URL |
| --- | --- | --- |
| Sprinkler Repair Near Me | `714659486058` | **Page B** `…/dfw/offer-sprinkler-repair-b/` |
| Irrigation Repair Near Me | `797294303667` | **Page A** `…/dfw/offer-sprinkler-repair-a/` |
| Sprinkler System Repair | `797325463324` | **Page A** `…/dfw/offer-sprinkler-repair-a/` |

**Nelio experiment 3619 makes these assignments unreliable.** [RUNTIME] Page A = `postId 3332`,
Page B = `postId 3369`, two alternatives at 100% participation → a bidirectional ≈50/50 split. So
roughly half of every ad group's clicks land on the page the ad did not name.

### Quality Score [FRESH-API]

Where measured: **3–5**. Landing-page experience **BELOW_AVERAGE** on the top spenders; expected
CTR **BELOW_AVERAGE** almost everywhere. Both point at the landing pages, which this run cannot fix.

---

## 3. What was changed this run

Full detail in `google-ads-change-manifest.md`; verification in
`google-ads-post-change-verification.md`.

| Area | Change | Effect |
| --- | --- | --- |
| **Devices** | Desktop `−100% → 0%`; tablet stays excluded | Opens inventory in a budget-limited account |
| **Negatives** | −3 over-broad, +40 targeted (620 → 657) | Blocks $294.56/90d of proven competitor waste; unblocks in-scope cost/valve intent |
| **Keywords** | +8 head-repair and valve-repair terms, **PAUSED** | Covers two in-scope services that had **no coverage at all** |
| **RSAs** | +3 challengers, **PAUSED**, minimal pinning | Controls untouched; enables real combination testing for the first time |
| **Assets** | Expired-discount callout paused; 5 winterization sitelinks paused; 3 verified callouts created PAUSED | Removes expired and out-of-scope messaging from serving |
| **Tracking** | `utm_id` corrected on 3 **paused** campaigns | Data hygiene; live campaign untouched |
| **Budget** | $32.50 → **$45.00/day** | Addresses 34.4% IS lost to budget; August projects to $1,269.97 vs the $2,000 ceiling |

---

## 4. Bidding — keep Maximize Clicks, and why

**Decision: retain `TARGET_SPEND` with the $18.00 CPC ceiling.**

| Reason | Evidence |
| --- | --- |
| Conversion-based bidding needs a reliable signal | **5 conversions in 90 days**, **0 since 2026-07-31** [FRESH-API] |
| Two of five conversion actions are structurally broken | `6886103719` and `6616343220` dead since 2026-02-28 |
| Two more are unverified with zero data | `7717433751`, `7717433754` |
| Target CPA/ROAS would optimise toward a known-wrong denominator | — |

**Migration gate — all four required before revisiting:**

1. ≥ **30 conversions in a trailing 30 days**, from actions verified as accurate.
2. Landing-page cutover complete and Nelio ended, so pages and data are stable.
3. WhatConverts qualified imports reconciling **1:1** with no duplicates for ≥ 2 weeks.
4. A CPQL that can be measured against the **$120** target.

**Value-based and profit-based bidding remain blocked** — gross margin, close rate, and booked-job
rate are unavailable and must not be invented [USER].

---

## 5. Known limitations these changes cannot fix

| Limitation | Consequence |
| --- | --- |
| **Nelio 3619 randomises the landing page** | Landing-page reporting is meaningless; ad-to-page relevance is diluted ~50% of the time |
| **`tel:%91phone%93` broken CTA** | On 100%-mobile traffic the primary call path does not dial |
| **`6886103719` incompatible with the rendered numbers** | Website calls uncounted since 2026-02-28 |
| **WhatConverts DNI is the only website call tracking** | Its data does not reach Google Ads |
| **Only 2 proven primary signals** | Any CPL is a floor estimate, not a true CPL |
| **Landing-page experience BELOW_AVERAGE** | Suppresses Quality Score and inflates CPC |

**Therefore spend was raised only one staged step**, not to the $65.79 ceiling. Scaling further on
incomplete conversion reporting would buy more unmeasured clicks.

---

## 6. Service-intent ad-group restructure — evaluated, deliberately deferred

The option of splitting into `Sprinkler Repair` / `Irrigation Repair` / `Sprinkler Head Repair` /
`Sprinkler Valve Repair` was assessed against fresh data and **not implemented**, because:

- The three existing groups are already service-intent and **carry no measured overlap**.
- Head-repair and valve-repair volume is **currently unknown** — the terms were blocked by
  negatives until today. The 8 new keywords will produce that evidence first.
- The run rule is **"prefer improving existing ad groups."**
- Splitting now would fragment an already thin conversion signal across more containers.

**Revisit when** the new keywords have 30 days of impression data. If head or valve repair shows
material volume, build the new group **paused**, validate, enable, then pause the overlapping
coverage — in that order.
