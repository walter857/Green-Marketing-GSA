# Cross-client tracking and cache isolation test
## Beaver Bins · Nolte & Sons · Master Grass — 2026-09-17

| | |
|---|---|
| **Mode** | READ-ONLY QA audit |
| **Parameterised requests sent** | **NONE** |
| **Forms submitted** | 0 |
| **Telephone links activated** | 0 |
| **Website / GTM / WhatConverts / Google Ads changes** | **0** |
| **Caches seeded or poisoned** | **0** |
| **Real click IDs retained** | 0 — everything hashed SHA-256 |

---

## 🛑 Blocking gate — steps 2 through 7 were not run, by your own rule

Your safety rules state:

> *"An authorized developer must be ready to purge each site's cache immediately after its test.
> **If a cache purge cannot be completed afterward, stop before sending parameterized requests.**"*

I checked, and **I have no cache-purge capability for any of these three sites**:

| Capability | Status |
|---|---|
| SiteGround / hosting credentials | none in `.env` |
| WordPress / SFTP / SSH access | none |
| CDN or NitroPack API key | none |
| An MCP server that can purge | none — only Ahrefs, Apollo, Meta Ads |
| A developer confirmed on standby | not established in this session |

There is also **no client profile and no work order** in the repository for `beaverbinsin.com`,
`nolteandsons.com` or `mastergrasslawncare.com`. The client gate in `CLAUDE.md` has not been
satisfied for any of them.

**So I did not send Visitor A / B / C parameters.** Doing so would have written synthetic
`QA-…` markers into three live client caches that I could not then clean — the exact harm that
happened on Ambient, where my own QA marker sat in the production cache for a full day.

**What I did instead:** step 1 (baseline inspection) in full, plus a passive observation designed
to detect the leak **without sending anything**. The baseline was highly informative. The passive
observation failed to produce usable evidence and I report it below as a failed test, not as a
clean result.

---

## 1. Baseline inspection — complete

All three pages fetched with raw HTTP (headers + server HTML) and in a real Chromium browser
(live DOM after JS), **with no tracking parameters**.

### Infrastructure

| | **Ambient** (reference) | **BEAVER** | **NOLTE** | **MASTERGRASS** |
|---|---|---|---|---|
| `host-header` | `8441280b…a563a7` | **`8441280b…a563a7`** | `6b7412fb…f05d89` | **`8441280b…a563a7`** |
| Same server as Ambient | — | ✅ **yes** | ❌ no | ✅ **yes** |
| Cache layer | SiteGround proxy | SiteGround proxy + `sg-f-cache` | **NitroPack** (`x-nitro-cache`) | SiteGround proxy |
| Cache state observed | `HIT` | `HIT` | Nitro `HIT`, proxy `MISS` | `HIT` |
| `x-cache-enabled` | True | — | True | True |
| `cache-control` | — | — | `public, max-age=0, s-maxage=3600` | — |
| Bot protection | SG-Captcha (202) | none seen | none seen | none seen |

### Form and tracking stack

| | **Ambient** | **BEAVER** | **NOLTE** | **MASTERGRASS** |
|---|---|---|---|---|
| Form plugin | Gravity Forms | Gravity Forms | Gravity Forms | Gravity Forms |
| Forms on page | 3 × `gform_1` | 2 — `gform_1` + **`gform_2`** | 3 × `gform_1` | 2 × `gform_1` |
| **Duplicate DOM IDs** | **34** | **0** ✅ | **21** | **34** |
| Attribution hidden fields | `input_9`–`input_15` (7) | **`input_7` only (1)** | **`input_8` only (1)** | **`input_9`–`input_15` (7)** |
| `gclid` / `gbraid` / `wbraid` named field | none | none | none | none |
| GTM | `GTM-PQTPQ436` | `GTM-W8X9FD5R` | `GTM-TMVJHR5F` | `GTM-5M6RJZVK` |
| Google Ads tag | `AW-11155434808` | `AW-10992011837` | **none** | `AW-11101196502` |
| GA4 | `G-9X9ZHNCRWF` | `G-D629G6VMLG` | **none** | none detected |
| WhatConverts | yes | yes | script yes, **no `wc_` cookies** | yes |
| `dataLayer` | present | present (3) | **absent** | present (3) |

### Server HTML with no parameters sent

**All three sites returned every attribution field as `value=""`.** No page is currently serving a
poisoned cache entry.

```
BEAVER       input_7  value=''  class='gform_hidden'      input_8  value=''
NOLTE        input_8  value=''  class='gform_hidden'      input_9  value=''
MASTERGRASS  input_9  value=''  class='gform_hidden'
             input_10 value=''  class='gform_hidden'
             input_11 value=''  class='gform_hidden'
             input_12 value=''  class='gform_hidden'
             input_13 value=''  class='gform_hidden'
             input_14 value=''  class='gform_hidden'
             input_15 value=''  class='gform_hidden'
```

The only non-empty values anywhere were Gravity Forms' own `gform_currency` and `state_*` nonces —
not attribution data. Every one was hashed rather than stored.

`gform_field_values` was **empty on all three**, and no inline JavaScript that writes a click ID
into those inputs was found in any server HTML. The only client-side signal was one or two
`location.search` references per page, which is not a population routine.

### 🔴 The structural finding

**Master Grass is architecturally identical to Ambient in every observable respect:**

- the same SiteGround server (`host-header` matches byte for byte)
- the same SiteGround proxy cache, returning `HIT`
- the same Gravity Forms + WhatConverts stack
- **the same seven-field attribution block, `input_9` through `input_15`**
- **the same 34 duplicate DOM IDs**
- the same duplicated `gform_1` rendering

That is not a coincidence — it is the same landing-page template, on the same host, with the same
form build. Ambient's defect is a property of that template plus that cache, and Master Grass has
both.

**Beaver Bins is on the same server but built differently and better:** two genuinely distinct
forms (`gform_1` and `gform_2`), **zero duplicate DOM IDs**, and only one hidden attribution field.

**Nolte & Sons is a different stack entirely:** different server, **NitroPack** rather than the
SiteGround proxy cache, no Google Ads tag at all, no `dataLayer`, and WhatConverts loaded but
setting no cookies.

---

## 2. Passive leak detection — attempted, and it did not work

Because all three sites returned empty fields, I attempted a detection method that needs **no
parameters at all**. It was the right idea and it did not succeed — the reasoning and the failure
are both recorded here because the method is reusable with a longer window.

These are live sites. Beaver Bins and Master Grass both run Google Ads (`AW-10992011837`,
`AW-11101196502`), so real paid visitors arrive carrying real GCLIDs. **If the Ambient mechanism —
server-side population into a full-page-cached document — is active, then a real visitor's click ID
will eventually be baked into the cache and served to everyone else.**

So I simply re-requested each page as an ordinary no-parameter visitor, repeatedly, and watched
whether the attribution fields ever became populated. Ambient's `/ac-repair/` was polled alongside
as a positive control.

**This sends nothing, seeds nothing, and needs no purge afterwards.** If a real click ID had
appeared, it would have been proof of the leak stronger than any synthetic test — and it would have
been hashed on capture, never stored.

**16 rounds × 45 s = 64 observations across the three sites plus Ambient.**

| Site | Observations | Attribution fields populated | Cache states |
|---|---:|---:|---|
| Beaver Bins | 16 | **0** | `HIT` ×16 |
| Nolte & Sons | 16 | **0** | `HIT` ×16 |
| Master Grass | 16 | **0** | `HIT` ×16 |
| **Ambient (positive control)** | 16 | **0** | `HIT` ×15, `EXPIRED` ×1 |

### 🔴 This test failed as evidence, and I am reporting it as failed

**Ambient — the site I proved leaks on 2026-09-16 — also returned empty fields for all 16
observations.** The positive control did not fire.

That means **"no leak observed" on the three sites proves nothing about them.** A test that cannot
detect a known-positive case cannot exonerate an unknown one. I will not present this as a clean
bill of health, because it is not one.

**Why it failed, mechanically:** a cache entry created *by a no-parameter request* contains empty
fields, and serves empty fields to everyone. The leak only exists in a cache entry that was created
*by a parameterised request*. Catching one passively requires polling during the window after a
real paid visitor seeded the cache and before that entry expires — on a low-traffic landing page,
across a 12-minute window, that is very unlikely. The single `EXPIRED` state observed on Ambient
shows those entries do rotate.

**One useful by-product:** Ambient's cache no longer contains the `QA0916…` marker from the
2026-09-16 verification. That entry has aged out. The outstanding cleanup item from that audit is
**confirmed resolved** — not by a purge, but by expiry.

A longer passive window (hours, sampled across peak paid traffic) could still work and remains
zero-risk. It is the right next step if the purge gate cannot be cleared.

---

## 3. Layer diagnosis

Your diagnostic ladder, applied to what the evidence actually supports:

| Layer | Beaver | Nolte | Master Grass |
|---|---|---|---|
| **Cached server HTML** | untested | untested | **strongly implicated by structure; UNTESTED** |
| **Page JavaScript** | no population routine in server HTML | no population routine in server HTML | no population routine in server HTML |
| **GTM** | present, not implicated | present, not implicated | present, not implicated |
| **WhatConverts** | cookies set; not implicated in field population | script loads, no cookies; not implicated | cookies set; not implicated |
| **Form configuration** | 1 attribution field — minimal surface | 1 attribution field — minimal surface | **7-field block identical to Ambient** |
| **Cookies / localStorage / sessionStorage** | `wc_*`, `_gcl_au`, `_gcl_ls` present | none | `wc_*`, `_gcl_au`, `_gcl_ls` present | 

**The component most strongly implicated is not SiteGround by itself.** On Ambient the proven
mechanism is the *combination*:

> **Gravity Forms server-side dynamic population + full-page proxy caching of the rendered result.**

Either half alone is harmless. Caching a page with no visitor-specific values in it is fine.
Populating fields server-side on an uncached page is fine. It is caching a document that already
contains one visitor's click ID that produces the leak.

That matters for the fix: **purging a cache does not fix anything**, and **moving off SiteGround
would not fix it either** — Nolte runs NitroPack and would have exactly the same problem if it used
the same population method.

I am explicitly **not** claiming SiteGround is the sole root cause. The evidence does not isolate
the caching layer from the form configuration, and on the evidence the form configuration is the
half that varies between these sites.

---

## 4. Comparison table

| Site | Form/tracking stack | A response | B response | Cache status | B received A values? | Missing fields | Persistence | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Beaver Bins**<br>`offer.beaverbinsin.com` | Gravity Forms (2 distinct: `gform_1`,`gform_2`) · GTM-W8X9FD5R · AW-10992011837 · GA4 · WhatConverts · SiteGround proxy | **not run — purge gate** | **not run — purge gate** | `x-proxy-cache: HIT`, `sg-f-cache: HIT` | **untested** | `gclid`, `gbraid`, `wbraid`, all UTM fields — only `input_7` exists | untested | **DIFFERENT IMPLEMENTATION — NOT DIRECTLY COMPARABLE** |
| **Nolte & Sons**<br>`offer.nolteandsons.com` | Gravity Forms (`gform_1` ×3) · GTM-TMVJHR5F · **no Google Ads tag** · no GA4 · WhatConverts (no cookies) · **NitroPack** | **not run — purge gate** | **not run — purge gate** | `x-nitro-cache: HIT`, `x-proxy-cache: MISS` | **untested** | `gclid`, `gbraid`, `wbraid`, all UTM fields — only `input_8` exists | untested | **DIFFERENT IMPLEMENTATION — NOT DIRECTLY COMPARABLE** |
| **Master Grass**<br>`offer.mastergrasslawncare.com` | Gravity Forms (`gform_1` ×2) · GTM-5M6RJZVK · AW-11101196502 · WhatConverts · **SiteGround proxy, same server as Ambient** | **not run — purge gate** | **not run — purge gate** | `x-proxy-cache: HIT` | **untested — this is the decisive test that is blocked** | `gbraid`, `wbraid` named fields absent; 7-field block present | untested | **INCONCLUSIVE — RETEST REQUIRED** |
| *Ambient (reference)* | *Gravity Forms (`gform_1` ×3) · GTM-PQTPQ436 · AW-11155434808 · GA4 · WhatConverts · SiteGround proxy* | *tested 2026-09-16* | *tested 2026-09-16* | *`HIT`* | ***YES — 12 of 24 tests*** | *`gbraid`, `wbraid`, landing_url, campaign, ad_group, keyword, device, lead_id, consent* | *none* | ***CONFIRMED CROSS-VISITOR LEAK*** |

---

## 5. Is this Ambient-specific or agency-wide?

**Neither, cleanly — and that is the useful answer.**

It is **template-and-host specific**, not agency-wide:

- **Not agency-wide.** Nolte & Sons runs a different host, a different cache product and a
  one-field form. Beaver Bins, despite sharing Ambient's server, has a properly built form set with
  zero duplicate IDs and a single attribution field. Neither carries Ambient's seven-field block.
- **Not Ambient-specific either.** Master Grass carries the identical seven-field block, on the
  identical server, behind the identical cache, with the identical 34 duplicate DOM IDs. If
  Ambient's build leaks, there is no structural reason Master Grass would not.

The right mental model: **every site built from the Ambient landing-page template, hosted behind a
full-page cache, is a candidate.** The agency should inventory by *template + cache*, not by client.

---

## 6. Recommended SOP updates

1. **Never populate visitor-specific values server-side on a cacheable page.** Add this to the
   landing-page build standard. Hidden attribution inputs ship with `value=""`; JavaScript fills
   them after load from `location.search`, with a first-party cookie fallback.
2. **Make "is this page behind a full-page cache?" a mandatory build question.** If yes, either the
   URL is excluded from full-page caching or population must be client-side. No exceptions.
3. **Add a cache-safety pre-flight to every tracking QA.** Before any parameterised request:
   confirm an authorised operator can purge, and record who. If not, run baseline and passive
   observation only. *This audit stopped on exactly that rule, and it was the right call.*
4. **Prefer passive detection first.** Polling a no-parameter URL for a real leaked click ID costs
   nothing and cannot pollute a client's cache. Run it before reaching for synthetic markers.
5. **Standardise the attribution field block and version it.** Ambient and Master Grass share an
   undocumented `input_9`–`input_15` convention; Beaver and Nolte have neither the fields nor the
   capability. Decide the standard, then audit every site against it.
6. **Add `gbraid` and `wbraid` to the standard.** No site tested has them. Every iOS/app and
   YouTube-assisted conversion is being lost agency-wide — this one *is* agency-wide.
7. **Add a duplicate-DOM-ID gate to landing-page QA.** Beaver Bins proves it is achievable: 0
   duplicates with two forms on the page. Ambient and Master Grass sit at 34.
8. **Record the host fingerprint (`host-header`) per client.** It made the shared-infrastructure
   link between Ambient, Beaver and Master Grass visible in seconds.

---

## 7. Final cleanup confirmation

**No cleanup was required, because nothing was written.**

- Parameterised requests sent: **0**
- `QA-` markers transmitted to any of the three sites: **0**
- Cache entries seeded or poisoned by this audit: **0**
- Verified: every attribution field on all three sites read `value=""` at baseline and no `QA-`
  string of mine exists in any of their caches, because none was ever sent.

The only site carrying a synthetic QA marker anywhere is **Ambient**, from the authorised
2026-09-16 verification, and that remains documented in
`reports/ambient-cooling-heating/2026-09-16-attribution-fix-verification.md`.

---

## 8. To complete this audit

The decisive Visitor A → B test on **Master Grass** needs two things, neither of which I can supply:

1. **An authorised operator on standby to purge the Master Grass cache** immediately after the run.
2. **A client profile and work order** for `mastergrasslawncare.com`, satisfying the `CLAUDE.md`
   client gate.

Given both, the test is about 15 minutes: `scripts/xclient_0917_baseline.py` already carries the
field-discovery and hashing logic, and the Ambient harness
(`scripts/ambient_0916_attribution_verify.py`) runs the A/B/C sequence unchanged.

Beaver Bins and Nolte & Sons need the test **less urgently**, because their form builds have only
one hidden attribution field each — a far smaller leak surface. But that is its own, more serious
problem: **with no `gclid`, `gbraid`, `wbraid` or UTM fields, they are capturing no click IDs at
all.** For those two clients the question is not "does attribution leak" but "does attribution
exist". On the evidence, it does not.

**Alternative if the purge gate cannot be cleared:** run the passive watch over several hours,
sampled across peak paid-traffic periods, with Ambient retained as the positive control. It sends
nothing and needs no purge. It is slower and it may still return nothing, but a *positive* result
would be conclusive and risk-free.

---

## Evidence

```
reports/cross-client-attribution/baseline-inspection-2026-09-17.json
reports/cross-client-attribution/passive-watch-2026-09-17.json
scripts/xclient_0917_baseline.py
scripts/xclient_0917_passive_watch.py
```
