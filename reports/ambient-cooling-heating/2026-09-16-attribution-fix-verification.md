# Ambient Cooling - Live | 2401959466
# Attribution fix verification — independent QA

| | |
|---|---|
| **Date** | 2026-09-16, America/New_York |
| **Scope** | Tracking QA for the six paid HVAC landing pages |
| **Mode** | READ + QA |
| **Website changes** | **0** |
| **Google Ads changes** | **0** |
| **Forms submitted** | **0** |
| **Telephone links activated** | **0** |
| **Cache purges** | **0** |
| **VERDICT** | # 🔴 FAIL — FIX NOT COMPLETE |

---

## 1. Identity gate — PASS

`Ambient Cooling - Live | 2401959466` — 10/10 checks: name exact · id exact (child, not the
Green Marketing MCC) · manager=false · test=false · ENABLED · USD · America/New_York · `- live`
present · GM manager `3373711342` ACTIVE · ClickCease `2815082755` ACTIVE.

---

## 2. Headline finding

**The cache defect is not fixed. It is unchanged.** The only thing that has changed is *which*
visitor's values are stuck in the cache.

The decisive evidence is a single line from the raw **server HTML** — the document as it leaves the
server, before any JavaScript runs:

```
REQUESTED : /ac-repair/?gclid=QA0916ACREPAIRR1T140501&utm_campaign=QA0916ACREPAIRR1T140501CAMP…
            (brand-new incognito context, no cookies, no storage)

RESPONSE  : HTTP 200, x-proxy-cache: HIT, 158,617 bytes

SERVER HTML CONTAINS:
   input_14 = QA0916ACREPAIRR4T140122A        <- a DIFFERENT visitor's GCLID
   input_11 = QA0916ACREPAIRR4T140122ACAMP
   input_12 = QA0916ACREPAIRR4T140122ATERM
   input_13 = QA0916ACREPAIRR4T140122ACONT
```

`QA0916ACREPAIRR4T140122A` was a marker from a **different test, in a different browser, four
minutes earlier**. A new visitor received it, baked into the HTML, before JavaScript ran.

### The single most informative data point

Of 24 tests, exactly **one** was served with `x-proxy-cache: MISS` — `hvac-replacement`, run 2.
It is the **only** test whose own values reached the form:

| Cache state | Tests | Own values in the form? |
|---|---:|---|
| `MISS` | 1 | ✅ **yes** — its own UTMs rendered correctly |
| `HIT` | 19 | ❌ **no** — a previous visitor's values every time |

That isolates the mechanism beyond argument: **the attribution fields are still populated
server-side, and the rendered page is still stored by the full-page proxy cache.** When the cache
misses, the code works. When it hits — which is almost always — it serves someone else's data.
This is the same root cause reported on 2026-09-15.

---

## 3. Cache status for every page (Test 1)

Raw HTTP, no JavaScript:

| Page | HTTP | `SG-Captcha` | `x-proxy-cache` (browser) | `cache-control` | Stale values in server HTML |
|---|---|---|---|---|---|
| `/ac-repair/` | 202 → 200 | challenge | **HIT** | `no-store,no-cache,max-age=0` (on the stub) | **YES** |
| `/hvac-repair/` | 202 → 200 | challenge | **HIT** | ″ | no (cached empty) |
| `/hvac-installation/` | 202 → 200 | challenge | **HIT** | ″ | no (cached empty) |
| `/hvac-replacement/` | 202 → 200 | challenge | **HIT** / one MISS | ″ | **YES** |
| `/gas-boiler-repair/` | 202 → 200 | challenge | **HIT** | ″ | **YES** |
| `/commercial-hvac-installation/` | 202 → 200 | challenge | **HIT** | ″ | **YES** |

Other headers seen: `Server: nginx` · `X-Robots-Tag: noindex` · `Host-Header: 8441280b…` ·
`X-Proxy-Cache-Info: DT:1`. No NitroCDN header on this subdomain.

> **A cache HIT is not automatically a failure** — and I applied that rule. It fails here because
> the cached HTML demonstrably contains a previous visitor's tracking values, and JavaScript does
> **not** overwrite them.

### About the HTTP 202 responses

Every first request returned **HTTP 202** with a 179-byte body and the header `SG-Captcha: challenge`
— SiteGround's bot protection, triggered by my test client's request volume from a single IP.

**This is a test-client obstacle, not a site defect, and I have not scored it as one.** A real
browser solves the challenge and is redirected to the real page; 20 of 24 tests did exactly that and
were measured normally. The 4 that did not clear it are reported **INCONCLUSIVE**, never FAIL.

A plain `urllib`/`curl` fetch receives only the 179-byte stub. Testing this site without a real
JavaScript browser produces a false result in either direction.

---

## 4. Results — 24 parameterised tests (Tests 2 + 3)

Each test: brand-new incognito context · no cookies · no localStorage · no sessionStorage · unique
markers containing page, run and timestamp · ≥9 seconds settle **after** the real page rendered ·
raw server HTML *and* live DOM both inspected · hidden-field mapping **discovered**, not assumed.

| Page | Test | Device | Cache | Expected ID | Observed ID | UTMs | Dup IDs | GTM | WC | Result |
|---|---|---|---|---|---|---|---:|---|---|---|
| ac-repair | run1 gclid | desktop | HIT | `…R1T140501` | **`…R4T140122A`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| ac-repair | run2 gbraid | mobile | HIT | `…R2T140501` | **`…R4T140122A`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| ac-repair | run3 wbraid | desktop | HIT | `…R3T140501` | **`…R4T140122A`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| ac-repair | run4 warm-B | desktop | HIT | `…R4T140501B` | **`…R4T140122A`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| hvac-repair | run1 gclid | desktop | HIT | `…R1T140501` | *(empty)* | ✗ | 34 | ✓ | ✓ | **FAIL** |
| hvac-repair | run2 gbraid | mobile | HIT | `…R2T140501` | *(empty)* | ✗ | 34 | ✓ | ✓ | **FAIL** |
| hvac-repair | run3 wbraid | desktop | HIT | `…R3T140501` | *(empty)* | ✗ | 34 | ✓ | ✓ | **FAIL** |
| hvac-repair | run4 warm-B | desktop | HIT | `…R4T140501B` | *(empty)* | ✗ | 34 | ✓ | ✓ | **FAIL** |
| hvac-installation | run1 gclid | desktop | HIT | `…R1T140501` | *(empty)* | ✗ | 34 | ✓ | ✓ | **FAIL** |
| hvac-installation | run2 gbraid | mobile | HIT | `…R2T140501` | *(empty)* | ✗ | 34 | ✓ | ✓ | **FAIL** |
| hvac-installation | run3 wbraid | desktop | HIT | `…R3T140501` | *(empty)* | ✗ | 34 | ✓ | ✓ | **FAIL** |
| hvac-installation | run4 warm-B | desktop | challenge | `…R4T140501B` | — | — | — | — | — | *INCONCLUSIVE* |
| hvac-replacement | run1 gclid | desktop | challenge | `…R1T140501` | — | — | — | — | — | *INCONCLUSIVE* |
| **hvac-replacement** | **run2 gbraid** | **mobile** | **MISS** | `…R2T140501` | **own UTMs ✓** | **✓** | 34 | ✓ | ✓ | **UTMs pass · gbraid NOT captured** |
| hvac-replacement | run3 wbraid | desktop | HIT | `…R3T140501` | **`…R2T140501…`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| hvac-replacement | run4 warm-B | desktop | HIT | `…R4T140501B` | **`…R2T140501…`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| gas-boiler-repair | run1 gclid | desktop | HIT | `…R1T140501` | **`…1T140122`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| gas-boiler-repair | run2 gbraid | mobile | HIT | `…R2T140501` | **`…1T140122`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| gas-boiler-repair | run3 wbraid | desktop | HIT | `…R3T140501` | **`…1T140122`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| gas-boiler-repair | run4 warm-B | desktop | HIT | `…R4T140501B` | **`…1T140122`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| commercial-hvac | run1 gclid | desktop | HIT | `…R1T140501` | **`…R1T140122`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| commercial-hvac | run2 gbraid | mobile | challenge | `…R2T140501` | — | — | — | — | — | *INCONCLUSIVE* |
| commercial-hvac | run3 wbraid | desktop | HIT | `…R3T140501` | **`…R1T140122`** | ✗ | 34 | ✓ | ✓ | **FAIL** |
| commercial-hvac | run4 warm-B | desktop | challenge | `…R4T140501B` | — | — | — | — | — | *INCONCLUSIVE* |

### Counts

| Metric | Result | Required |
|---|---:|---|
| Tests run | 24 | 24 |
| Rendered and measurable | 20 | — |
| Blocked by SG-Captcha (inconclusive) | 4 | — |
| **Click IDs captured exactly** | **0 of 24** | **24 of 24** |
| — GCLID | **0 of 12** | 12 |
| — GBRAID | **0 of 6** | 6 |
| — WBRAID | **0 of 6** | 6 |
| Confirmed carrying another visitor's values | **12 of 24** | 0 |
| Duplicate DOM IDs (every rendered page) | **34** | 0 |
| Gravity Forms per page | **3** | 1 |

### 🔴 Separate, independent failure: GBRAID and WBRAID have no field at all

Every populated field name observed across all 30 page loads:

```
input_9  = utm_source     input_12 = utm_term
input_10 = utm_medium     input_13 = utm_content
input_11 = utm_campaign   input_14 = gclid
```

**There is no `gbraid` field and no `wbraid` field anywhere on any of the six pages.** Even if the
caching were fixed tomorrow, GBRAID (iOS app / web-to-app) and WBRAID (YouTube/Display-assisted)
click IDs would still be lost. `input_14` only ever receives a `gclid`.

### A note on `input_9` and `input_10`

These appeared to "match" in most tests because `utm_source=google` and `utm_medium=cpc` are
**constants in every test**. A cached value trivially equals the expected value. I re-scored so they
never count as a genuine capture — otherwise the harness would have reported a false pass.

---

## 5. Six no-parameter isolation controls (Test 4)

Fresh context, no click IDs, no UTMs. The form must be **empty**.

| Page | Cache | Result | Values found |
|---|---|---|---|
| `/ac-repair/` | challenge | *INCONCLUSIVE* | — |
| `/hvac-repair/` | HIT | ✅ **PASS** | empty |
| `/hvac-installation/` | HIT | ✅ **PASS** | empty |
| `/hvac-replacement/` | HIT | 🔴 **FAIL** | `QA0916HVACREPLR2T140501CAMP/TERM/CONT` |
| `/gas-boiler-repair/` | HIT | 🔴 **FAIL** | `QA0916GASBOILER1T140122` + CAMP/TERM/CONT |
| `/commercial-hvac-installation/` | challenge | *INCONCLUSIVE* | — |

**2 PASS · 2 FAIL · 2 INCONCLUSIVE.** Required: 6 of 6 clean.

A visitor arriving with **no parameters whatsoever** is being handed a previous visitor's GCLID and
UTM set. Evidence file `04-no-parameters.json` records exactly this on `/ac-repair/`:
`input_14 = QA0916ACREPAIRR4T140122A`, present in the **server HTML**.

The two pages that passed did so because their cached copy happens to hold *empty* fields — not
because isolation works.

---

## 6. Same-visitor persistence (Test 5)

| Step | Marker 1 | Marker 2 |
|---|---|---|
| 1. Enter `/ac-repair/` with marker 1 | ✗ | ✗ |
| 2. Navigate to `/hvac-repair/` with no parameters | ✗ | ✗ |
| 3. Re-enter `/hvac-repair/` with marker 2 | ✗ | ✗ |
| 4. **Separate fresh context**, no parameters | ✗ | ✗ |

**Attribution rule observed: NONE — there is no first-party persistence.** Attribution is read from
the URL at render time only. Nothing is stored in a cookie, localStorage or sessionStorage and
re-applied on a later pageview.

Marker 1 never appeared even on the page that requested it, because that request was served from
cache. **Fresh-context isolation could not be demonstrated as working** — it only "passed" because
neither marker propagated anywhere, which is a symptom of the same defect.

I am not guessing the rule: the observed behaviour is *no persistence layer exists*.

---

## 7. Forms and duplicate IDs (Test 6)

Measured DOM-wide, not only `gform_1`:

| Metric | Observed | Required |
|---|---:|---|
| Gravity Forms per page | **3** | 1 (or fully unique IDs) |
| Form IDs | `gform_1`, `gform_1`, `gform_1` | unique |
| Visible forms | 2 | — |
| Zero-height / hidden duplicate | **1** | 0 |
| **Duplicate DOM IDs** | **34** | **0** |
| Total IDs on page | ~500 | — |

Identical on all six pages. **Unchanged from 2026-09-15.** Labels cannot reliably reference their
fields when `input_1_1`, `input_1_4` and the rest exist three times.

---

## 8. GTM and WhatConverts (Test 7) — ✅ all preserved

| Asset | Status |
|---|---|
| GTM container `GTM-PQTPQ436` | ✅ present, 24/24 rendered tests |
| Google Ads tag `AW-11155434808` | ✅ **present** — loads via GTM |
| GA4 `G-9X9ZHNCRWF` | ✅ present, 24/24 |
| WhatConverts script | ✅ present, 24/24 |
| `wc_visitor` cookie | ✅ set, 24/24 |
| `dataLayer` | ✅ present, 24/24 |
| Console errors | 0 blocking |

> **Correction to my own first pass.** An early check recorded the Google Ads tag as absent on
> 24/24 because it read only the rendered DOM. Verified separately against network traffic — the tag
> fires normally:
> `googleadservices.com/pagead/conversion/11155434808/wcm?…` ·
> `googleads.g.doubleclick.net/pagead/viewthroughconversion/11155434808/` ·
> `google.com/rmkt/collect/11155434808/`.
> **The developer did not remove or replace any tracking script.** I would have reported a removed
> conversion tag on a measurement artifact.
>
> Incidental confirmation: that WCM request carries `dn=4104159517` — independently confirming that
> **410-415-9517 is Google's call-forwarding number**, as identified on 2026-09-15.

---

## 9. Mobile and desktop usability (Test 8)

| Check | Result |
|---|---|
| Form loads | ✅ 24/24 |
| Horizontal overflow | ✅ none, desktop or mobile |
| Approved number `(410) 705-6354` displayed | ✅ 24/24 |
| Forwarding number `410-761-0932` public | ✅ never |
| Hidden tracking fields populate | 🔴 with the **wrong** visitor's data |
| Form obstructed by an overlay | ⚠️ 5 of 24 — a fixed header sits over the form's top edge at initial scroll |

### 🔴 REGRESSION — the mixed-source number is now clickable

| Page | `tel:` links |
|---|---|
| `/ac-repair/` | `tel:4107056354` ✓ · `tel:(410) 705-6354` ⚠ malformed · **`tel:+14109141456`** 🔴 **visible + clickable** |
| `/hvac-repair/` | same |
| `/hvac-installation/` | same |
| `/hvac-replacement/` | same |
| `/gas-boiler-repair/` | same |

On **2026-09-15** the `tel:+14109141456` anchor was present but `visible: false`. It is now
**visible and clickable on all five original pages**. A visitor tapping "Call Now" dials
**410-914-1456** — the mixed-source number that must never be on a paid page.

This is **worse** than the state before the developer's work.

Also still unfixed: `tel:4107056354` lacks the `+1` country code, and `tel:(410) 705-6354` contains
unencoded parentheses and a space.

---

## 10. Exact failed fields

| Field | Status |
|---|---|
| `gclid` → `input_14` | 🔴 serves a previous visitor's value, or empty. **0 of 12 captured.** |
| `gbraid` | 🔴 **no field exists.** 0 of 6. |
| `wbraid` | 🔴 **no field exists.** 0 of 6. |
| `utm_campaign` → `input_11` | 🔴 stale on every cache HIT |
| `utm_term` → `input_12` | 🔴 stale on every cache HIT |
| `utm_content` → `input_13` | 🔴 stale on every cache HIT |
| `utm_source` → `input_9` | ⚠️ stale, but masked because the value is always `google` |
| `utm_medium` → `input_10` | ⚠️ stale, but masked because the value is always `cpc` |
| `landing_url`, `first_landing_url`, `campaign`, `ad_group`, `keyword`, `device`, `lead_id`, `consent_state` | 🔴 **no fields exist** |

---

## 11. Acceptance criteria

| # | Criterion | Required | Observed | |
|---|---|---|---|---|
| 1 | All six pages HTTP 200 | 6/6 | 6/6 (after SG-Captcha) | ✅ |
| 2 | 24 of 24 capture their own values | 24 | **0** | 🔴 |
| 3 | 0 of 24 contain stale values | 0 | **12 confirmed** | 🔴 |
| 4 | 6 of 6 no-parameter controls clean | 6 | **2** (2 fail, 2 inconclusive) | 🔴 |
| 5 | Same-session attribution persists | yes | **no persistence layer exists** | 🔴 |
| 6 | New contexts isolated | yes | **not demonstrable** | 🔴 |
| 7 | Zero duplicate DOM IDs | 0 | **34** | 🔴 |
| 8 | GTM installed | yes | yes | ✅ |
| 9 | WhatConverts installed | yes | yes | ✅ |
| 10 | No barred phone number clickable | yes | **`tel:+14109141456` clickable on 5 pages** | 🔴 |
| 11 | No test required a website change | yes | yes — 0 changes | ✅ |

**7 of 11 criteria fail.**

---

## 12. Controlled form-submission gate

**No form was submitted.**

The gate requires that *the work order already authorizes a production QA submission*. I searched
every Ambient work order and `client.yaml` for such an authorization and **found none**. A previous
session's prompt mentioned a reserved QA identity, but that is not a standing work-order
authorization and I have not treated it as one.

Submitting now would also prove nothing useful: the browser layer fails, so a submission would only
demonstrate that the wrong attribution reaches the CRM.

---

## 13. What the developer still has to do

1. **Stop emitting visitor-specific values into cacheable server HTML.** The hidden inputs must ship
   with `value=""` in the cached document. This is the root cause and nothing else matters until it
   is done. A cache purge alone is not a fix — the next visitor re-poisons it.
2. **Populate client-side after load** from `location.search`, with a first-party cookie fallback
   scoped to the registrable domain, last-touch wins, and an empty result for a direct visit.
3. **Add `gbraid` and `wbraid` fields.** They do not exist.
4. **Add** `landing_url`, `first_landing_url`, `campaign`, `ad_group`, `keyword`, `device`,
   unique `lead_id`, `consent_state`.
5. **Render one Gravity Form per page** and eliminate all 34 duplicate DOM IDs.
6. **Remove `tel:+14109141456` from the DOM** — it is now clickable, a regression.
7. **Normalise every `tel:` href to `tel:+14107056354`.**
8. **Temporary fallback if 2 cannot ship immediately:** exclude the six paid URLs from full-page
   dynamic caching.

Retest command: `scripts/ambient_0916_attribution_verify.py` — require **24/24** and **6/6**.

---

## 14. Evidence

`reports/ambient-cooling-heating/evidence/attribution-2026-09-16/`

| File | Shows |
|---|---|
| `01-gclid-desktop.png` / `.json` | Requested `EVGCLID…`; server HTML returned `QA0916ACREPAIRR4T140122A` |
| `02-gbraid-mobile.png` / `.json` | GBRAID test on the commercial page; **no gbraid field**, stale `QA0916COMMERCIR1T140122` served |
| `03-wbraid-desktop.png` / `.json` | WBRAID test; **no wbraid field**; attribution fields empty |
| `04-no-parameters.png` / `.json` | **No parameters sent** — server HTML still returned `QA0916ACREPAIRR4T140122A` |
| `05-forms-and-duplicate-ids.png` / `.json` | 3 forms, 34 duplicate DOM IDs |
| `06-gtm-whatconverts.png` / `.json` | SG-Captcha challenge page (that capture blocked; GTM/WC confirmed on 24/24 elsewhere) |

Raw data: `clients/ambient-cooling-heating/snapshots/attribution-fix-verification-2026-09-16.json`

### Corrections I made to my own harness

Recorded because each would have produced a wrong verdict:

1. **Cross-run contamination scored as clean.** The leak check compared only against the *current*
   run's markers, so a marker left by an earlier run passed. Re-scored — `gas-boiler-repair`'s
   control moved from PASS to FAIL.
2. **Click-id prefix false positive.** The click-id marker is a prefix of the UTM markers
   (`…T140501` vs `…T140501CAMP`), so substring matching falsely scored GBRAID as captured.
   Re-scored on exact field-value equality: **0 of 24**.
3. **Constant UTM false match.** `utm_source=google` / `utm_medium=cpc` are identical in every test,
   so cached values trivially matched. Excluded from capture scoring.
4. **Google Ads tag falsely reported absent.** Reading only the DOM missed a tag that loads via GTM.
   Verified against network traffic — present.
5. **SG-Captcha 202 treated as a page failure.** Corrected: it is a test-client obstacle. The 4
   affected tests are INCONCLUSIVE, not FAIL.

---

# FINAL VERDICT

# 🔴 FAIL — FIX NOT COMPLETE

**0 of 24** parameterised tests captured their own click ID. **12 of 24** demonstrably carried a
previous visitor's values. **34** duplicate DOM IDs and **3** forms per page, both unchanged. GBRAID
and WBRAID have **no field at all**. The mixed-source telephone number is now **clickable**, which is
a regression.

The one cache `MISS` in the entire run rendered its own values correctly — which proves the code
path works and the **caching architecture was never changed**.

GTM, GA4, the Google Ads tag and WhatConverts are all intact; the developer broke nothing. But the
defect this verification was commissioned to check is present, unchanged, on every page.
