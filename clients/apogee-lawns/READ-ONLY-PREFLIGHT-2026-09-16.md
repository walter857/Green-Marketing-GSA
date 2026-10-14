# Apogee Lawns LLC — read-only preflight, 2026-09-16

**Account:** Apogee Lawns LLC - Live · **8164626278** · similar-local-service ·
**Service:** Permanent Christmas light installation
**Mode:** READ. No Google Ads mutate call was issued, not even `validate_only`. No GTM change.
No form submitted, no telephone link dialled. Both Drive documents opened read-only.

---

## 1. Identity gate — PASS

| Check | Result |
|---|---|
| `customer.descriptive_name` | `Apogee Lawns LLC - Live` — exact match |
| `customer.id` | `8164626278` — exact match to 816-462-6278 |
| `- live` marker | present (identity only; authorizes nothing) |
| manager / test account | false / false |
| status | ENABLED |
| currency | **USD** (expected USD) |
| time zone | **America/Chicago** (expected America/Chicago) |
| auto-tagging | **enabled** |
| manager link | `3373711342` Green Marketing, level 1, ACTIVE |
| discovery | 10 `- live` children under the manager; exactly one row matched the ID |

Evidence: `reports/apogee-lawns/evidence/2026-09-16-identity.json`

## 2. Conversion ownership — owned by this child

`google_ads_conversion_customer = 8164626278`, `cross_account_conversion_tracking_id = 0`.
No manager-level cross-account conversion configuration. Actions belong here.
`conversion_tracking_status = NOT_CONVERSION_TRACKED`.
`conversion_tracking_id = 18453077620` → expected GTM destination **AW-18453077620**
(from the child's tracking ID, never derived from the customer ID; still to be
re-read from the first action's tag snippet before any GTM tag uses it).
`accepted_customer_data_terms = false`, `enhanced_conversions_for_leads = false`.

## 3. Account inventory — greenfield

Campaigns 0 · budgets 0 · ad groups 0 · keywords 0 · ads 0 · **conversion actions 0** ·
customer conversion goals 0 · custom goals 0 · assets 0 · product links 0 (no GA4) ·
labels 0 · auto-apply subscriptions 0 · portfolio strategies 0.
Lifetime 2015-01-01→2026-09-16: **0 impressions, 0 clicks, $0.00, 0 conversions.**
Account-level negatives: 1, `CONTENT_LABEL PARKED_DOMAIN` (Google default).

### Billing — LAUNCH BLOCKER
Two billing setups, **both `CANCELLED`** (`8584340188` 2026-09-15 08:14, `8584421311`
2026-09-15 08:54). Zero APPROVED / APPROVED_HELD / PENDING. `account_budget` returns 0 rows.
An account with no active billing setup cannot serve.

### Seven pre-existing negative lists — DO NOT ATTACH ANY

| id | name | status | members | refs | match mix |
|---|---|---|---|---|---|
| 11807294063 | Christmas Lights Install | ENABLED | 424 | 0 | B109 / P294 / E21 |
| 11813144900 | General List | ENABLED | 1111 | 0 | B1109 / E2 |
| 12178646912 | General List - Irrigation Repair | ENABLED | 1107 | 0 | B1105 / E2 |
| 11811255121 | Leaf Removal initial | ENABLED | 386 | 0 | B386 |
| 11840874961 | Paver | ENABLED | 387 | 0 | B387 |
| 11840890006 | Outdoor Kitchen | ENABLED | 386 | 0 | B386 |
| 10667314427 | Names | REMOVED | 436 | 0 | P436 |

4,237 criteria total, **0 attached to any campaign**. A reverse audit (do the existing
negatives block the proposed positives?) found:

* `11807294063` contains **PHRASE `permanent christmas lights`** — blocks this campaign's
  own head keyword and every `permanent christmas lights …` query. It also holds BROAD
  `permanent christmas lights install`, `permanent christmas light install`, and EXACT
  `permanent christmas lights near me`, `diy permanent christmas lights`,
  `led permanent christmas lights`.
* `11813144900` and `12178646912` each hold single-word BROAD `cost`, `price`, `pricing`,
  `best`, `hire`, `emergency`, `reviews` — terms CLAUDE.md protects and the strategy
  document explicitly keeps eligible.

## 4. Live site and tag stack

| Finding | Result |
|---|---|
| `https://apogeelawns.com/` | 200, WordPress + Elementor 4.2.4 |
| `/permanent-christmas-lights-lincoln-ne/` | **404 — not published** |
| `/thank-you/permanent-christmas-lights/` | **404 — not published** |
| GTM containers found | **0** — `GTM-M545Z8T2` is not installed |
| Google Ads tags / GA4 / gtag / dataLayer | **0 occurrences sitewide** |
| Consent platform | none detected |
| WhatConverts / CallRail / other DNI | **none detected** |
| Form platform | Forminator, one shared module `1611` sitewide |
| Form success behaviour | `redirect_url` = the page's own URL on every page. **No dedicated success URL exists anywhere.** |
| Unique lead ID exposed | no |
| Phones sitewide | `+14022027261` only |
| **402-526-5754 occurrences** | **0** |
| Privacy Policy / Billing Policy | present |
| Terms and Conditions | **not in the sitemap** |
| Existing organic page | `/permanent-holiday-lights-lincoln-ne/` |

Pages audited: home, `/permanent-holiday-lights-lincoln-ne/`,
`/lawn-care-lighting-estimates-lincoln-ne/`, `/contact/`, `/privacy-policy/`.

**No competing DNI system exists** — that half of the website-call branch is clear.
The blocker is that the container is absent and the PPC number is not on the site.

### Hardening the "no tags" finding
A non-JS client has produced a false "no tracking" result before, so this was checked three
more ways rather than trusted from one fetch. The pages returned are fully rendered
(370 KB home page with complete Elementor markup, real titles, the full Forminator form
configuration, 88 same-origin asset references) — not a captcha stub. All **17** enqueued
same-origin JS files were fetched and grepped: zero contain `GTM-`, `AW-`, a GA4 ID,
`googletagmanager.com`, `gtag(` or `dataLayer.push` (the only two "hits" were the strings
`g-recaptcha` and `g-selected` inside Forminator). And the installed plugin set is
**astra-sites, elementor, forminator, header-footer-elementor, wp-smushit** — there is no
tag-management, Site Kit, GTM4WP or analytics plugin, so no mechanism exists to inject a
container client-side. The finding is solid.

## 5. Geo resolution — 14 of 14, all ENABLED, all parent Nebraska (21162)

| Requested | ID | Type | Canonical |
|---|---|---|---|
| 68372 | 9024671 | Postal Code | 68372,Nebraska |
| 68430 | 9024703 | Postal Code | 68430,Nebraska |
| 68527 | 9024754 | Postal Code | 68527,Nebraska |
| 68347 | 9024651 | Postal Code | 68347,Nebraska |
| 68526 | 9024753 | Postal Code | 68526,Nebraska |
| 68461 | 9024728 | Postal Code | 68461,Nebraska |
| 68516 | 9024746 | Postal Code | 68516,Nebraska |
| 68520 | 9024748 | Postal Code | 68520,Nebraska |
| Waverly, NE | 1021783 | City | Waverly,Nebraska |
| Eagle, NE | 1021647 | City | Eagle,Nebraska |
| Lincoln, NE | 1021696 | City | Lincoln,Nebraska |
| Ashland Township, NE | 9195288 | Municipality | Ashland Township,Nebraska |
| Crete, NE | 1021635 | City | Crete,Nebraska |
| Nemaha Precinct, NE | 9233865 | Municipality | Nemaha Precinct,Nebraska |

Selection was made by **exact canonical-name match, not by the suggest API's reach
ordering**. Reach ordering silently proposed ZIP 68104 (Omaha) for "Waverly", the
"Northwest Omaha" neighbourhood for "Eagle", and ZIP 68333 for "Crete". Nebraska (21162)
is the parent of all 14 and is never a target.

Open: `Nemaha Precinct` is unique in the table, but the API exposes no county. Nebraska has
a Nemaha Precinct in Lancaster County and a Nemaha County ~70 miles from Lincoln. The
neighbouring requested ZIPs (68372 Sprague, 68430 Hickman) are southern Lancaster County,
which is consistent with the Lancaster precinct. Worth one line of confirmation.

## 6. Keyword Planner — demand, not budget, is the binding constraint

Approved-area figures (top 10 of the 14 targets; the service caps geo targets at 10).
Keyword Planner collapses synonyms into one shared bucket — these are **per-bucket
ceilings and must never be summed**.

| Bucket | avg/mo | Sep | Oct | Nov | Dec | Sep–Dec | comp | TOP low–high |
|---|---|---|---|---|---|---|---|---|
| **permanent christmas lights** | **90** | 50 | 140 | **480** | 170 | **840** | HIGH | **$4.66–$13.76** |
| permanent christmas light installation | 10 | 10 | 20 | 10 | 10 | 50 | — | none |
| permanent christmas lights installer | 10 | 0 | 0 | 10 | 0 | **10/yr** | — | none |
| permanent holiday light installation | 10 | 0 | 0 | 10 | 0 | **10/yr** | — | none |
| permanent holiday lights | 10 | 10 | 10 | 10 | 10 | 40 | HIGH | none |
| everlights installer / installation | **0** | 0 | 0 | 0 | 0 | **0** | — | none |
| christmas light installation | 20 | 20 | 70 | 140 | 10 | 240 | MEDIUM | none |
| jellyfish lighting / trimlight | 30 / 20 | — | — | 70 / 70 | — | — | HIGH / LOW | none |

`permanent christmas lights` is the **only bucket in the entire research set that returned
top-of-page bid data**. The two ad groups in the Drive plan together carry roughly **60
searches across the whole Sep–Dec peak season**; the head bucket carries about **840** —
roughly 14× more.

### Omaha comparison (NOT in the approved geo list)

| Bucket | Lincoln Sep–Dec | Omaha Sep–Dec | Omaha TOP low–high |
|---|---|---|---|
| permanent christmas lights | 780 | **1,440** | **$2.13–$14.69** |
| christmas light installers near me | 120 | 1,240 | $2.56–$10.31 |
| christmas light installation | 240 | 860 | $2.04–$6.00 |

Omaha roughly doubles head-bucket demand **and enters cheaper** ($2.13 vs $4.66 TOP low).
`apogeelawns.com` titles its own page "Permanent Holiday Lights Install Lincoln & Omaha, NE"
and states "Installation Available for Homes & Businesses in Lincoln, Omaha & Surrounding
Areas in Nebraska". Adding Omaha is the single highest-leverage change available — and it
is a scope decision, not a technical one.

## 7. Claims — what the client's own site already publishes

Verified first-party on `/permanent-holiday-lights-lincoln-ne/`: "EverLights Certified
Dealer"; "Apogee Lawns is a certified EverLights dealer and installer serving Lincoln,
Omaha, and surrounding Nebraska areas"; **"5-year warranty"**; **IP67** waterproof rating;
app control with "over 15 million colors", schedules, Alexa and Google Home; "Installation
Available for Homes & Businesses"; "free consultation"; a "GET MY FREE ESTIMATE" button.

The brief bars warranty, certification, IP-rating, dealer and EverLights wording from ads,
so **none of it is used** in the proposed copy. Recorded here because the conflict is worth
knowing: these claims are already public on the client's own site, so written confirmation
would unlock materially stronger copy quickly. Only generic app-control, year-round-use,
professional-installation, homes-and-businesses and free-estimate language is used, each
supported by the site's own text.

## 8. Blockers

| ID | Blocker | Blocks |
|---|---|---|
| **BLK-001** | `similar-local-service` scope approval absent (`approved: false`, approver and reason are placeholders) | **every external write, including Stage A** |
| **BLK-002** | Both billing setups CANCELLED; no active billing | enablement |
| **BLK-003** | No Google Tag Manager access in this session — no browser tool, no Tag Manager API client, no GTM credential | the entire GTM audit, workspace, Preview, Tag Assistant and publication |
| **BLK-004** | `GTM-M545Z8T2` not installed on any page | all conversion measurement |
| **BLK-005** | 402-526-5754 appears 0 times on the site; ownership, routing and answer hours unverified | call asset, calls-from-website tag |
| **BLK-006** | PPC landing page and thank-you page both 404 | campaign final URL, RSAs, sitelinks, form conversion trigger |
| **BLK-007** | `[[LIVE_ANSWER_HOURS_CENTRAL]]` unresolved | ad schedule and call-asset schedule |
| **BLK-008** | No dedicated success URL exists; Forminator 1611 redirects to the same page and exposes no lead ID | form conversion and deduplication |
| **BLK-009** | Terms and Conditions page not found in the sitemap | landing-page legal requirement |

BLK-003 is a capability limit of this session, not a client-side fault. Phases 3 (GTM
draft), 5 (Preview and Tag Assistant) and 6 (publication) cannot be performed here at all
and need either a browser-enabled session or a developer hand-off.

## 9. Plans

* `plans/APG-0916-CONV-A.yaml` — 3 conversion actions, created Secondary. **3 mutations.**
  Fingerprint **`B62E6142E9CD`**.
* `plans/APG-0916-CAMP-B.yaml` — paused Search campaign, 2 SKAGs, 4 keywords, 4 RSAs,
  14 locations, 75 negatives. **116 mutations.** Fingerprint **`849EAED2873F`** —
  not approvable until BLK-006 and BLK-007 clear.

Red team: `scripts/apg_0916_preflight.py`, 5 FAIL / 0 WARN, every failure an owner input
(3× BLK-001, 1× schedule, 1× open placeholders). All technical checks pass: character
limits, pins, banned-claim scan, 75 negatives none protected and none blocking a positive,
policy defaults, budget math, identity consistency, secret scan.

## 10. Evidence index

```
reports/apogee-lawns/evidence/2026-09-16-identity.json
reports/apogee-lawns/evidence/2026-09-16-inventory.json
reports/apogee-lawns/evidence/2026-09-16-inventory2.json
reports/apogee-lawns/evidence/2026-09-16-inventory3.json
reports/apogee-lawns/evidence/2026-09-16-geo-resolution.json
reports/apogee-lawns/evidence/2026-09-16-geo-picked.json
reports/apogee-lawns/evidence/2026-09-16-keyword-planner.json
reports/apogee-lawns/evidence/2026-09-16-omaha-comparison.json
reports/apogee-lawns/evidence/2026-09-16-preflight.json
scripts/apg_lib.py, apg_0916_identity.py, apg_0916_inventory{,2,3}.py,
scripts/apg_0916_geo.py, apg_0916_planner.py, apg_0916_preflight.py
```

No lead PII, credentials, cookies, tokens or browser-session data are stored in any of them.

## 11. Repository note

`python -m gm_gsa.cli` **silently no-ops and exits 0** — `src/gm_gsa/cli.py` has no
`if __name__ == "__main__"` guard, and the `gm-gsa` console script is not installed in
`.venv`. A work order run that way appears to pass whatever its contents. The validator was
therefore invoked by direct import. Worth fixing before anyone trusts the CLI exit code.
