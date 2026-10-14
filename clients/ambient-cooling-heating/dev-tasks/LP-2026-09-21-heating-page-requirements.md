# Ambient Cooling & Heating — landing pages required for the heating transition

**Raised:** 2026-09-21 · Green Marketing
**Scope:** the 31-service heating transition (`work-orders/work-order-heating-transition-2026-09.yaml`)
**Authorisation:** none. No WordPress, SiteGround, GTM or WhatConverts change is authorised.

---

## Why this is a specification and not a set of finished content packages

`LANDING_PAGE_CONTENT_WORKFLOW.md` (repo root, mandatory) requires that the work order
identify local paths for three canonical template sources before any page is drafted:

1. blank template screenshot
2. completed service example screenshot
3. **template HTML**

**None of the three exists in this repository.** `templates/landing-page/` contains only
`brief.template.yaml`. The workflow also requires every editable element to be measured
against the template's own character counts, and states plainly: *"Use the actual template
HTML as the baseline. Do not estimate counts from screenshots."*

Per `CLAUDE.md`: *"If the file is missing or unreadable, stop the landing-page workflow and
identify the exact missing path."* So the content packages stop here, and the missing paths
are named:

```
templates/landing-page/<template>.html            MISSING
templates/landing-page/<blank>.png                MISSING
templates/landing-page/<completed-example>.png    MISSING
```

The 2026-09-10 Commercial HVAC Installation page was built from a supplied `.docx` launch
pack (`handoffs/ambient-commercial-hvac-installation-2026-09-10/source/`), not from a
template in this repo. If an equivalent pack or the template HTML is supplied, the full
12-section packages can be produced in one pass.

What follows is everything that does **not** depend on the template: the page inventory,
the gap, the recommended slugs, and the content each page must carry to be a valid
destination for its ad group.

---

## Page inventory, measured 2026-09-21

Evidence: `snapshots/lp-discovery-2026-09-21b.json`. Intent counts are body-text matches
with the site-wide nav/footer baseline subtracted (nav contributes furnace 6, heat pump 5,
boiler 4, ductless 4, geothermal 4 to **every** page — judging a page by its raw counts
overstates every theme).

### Usable today — 12 ad groups

| Page | H1 | Supports | Ad groups served |
|---|---|---|---|
| `/services/heating-services/furnace-repair/` | Furnace Repair in Severn… | repair 21, furnace 18, replace 10, maintenance 3 | Furnace Repair, Gas Furnace Repair, Electric Furnace Repair, Furnace Replacement, Furnace Maintenance |
| `/services/heating-services/` | Heating Services in Severn… | repair 12, maintenance 7, install 7, replace 6 | Heating Repair, Heating Maintenance |
| `/services/heating-services/boiler-repair/` | Boiler Repair in Severn… | repair 29, boiler 19 | Boiler Repair |
| `offer.…/gas-boiler-repair/` | Gas Boiler Repair in Severn… | repair 37, boiler 50, gas 37 | Gas Boiler Repair |
| `/services/cooling-services/mini-splits/` | Mini Splits in Severn… | ductless 16, install 12, repair 11 | Ductless Heating Repair, Ductless Heating Installation |
| `/services/hvac/geothermal-hvac/` | Geothermal HVAC in Severn… | geothermal 16, install 11, repair 12 | Geothermal Heat Pump |

Two caveats recorded rather than hidden:

- The furnace-repair page never says **gas** or **electric**. It supports furnace repair,
  and fuel type is a qualifier rather than a different service, so the two fuel-specific ad
  groups can point at it — but a fuel-specific page would match better.
- The mini-splits page sits on the `/cooling-services/` path. Its content is ductless mini
  splits, which heat and cool, so it is a valid heating destination. The **URL** reads as
  cooling, which is a minor message-match cost.

### Blocked by a technical defect — 4 ad groups

`/services/heating-services/heat-pumps/` renders correctly (HTTP 200, correct H1, working
form) but **Google rejects it as a destination**: `DESTINATION_NOT_WORKING`, 0/3 trials on
2026-09-21, while eight other Ambient URLs passed 3/3 with the identical ad body. Until it
clears, Heat Pump Repair, Replacement, Installation and Maintenance carry keywords but no
ads. See the blocker list in `DEV-2026-09-21-heating-launch-blockers.md`.

### Missing or insufficient — 14 ad groups

---

## Pages to build

Each entry gives the ad group, its keywords, the recommended slug, and the content the page
must carry. A page is only a valid destination when its own copy supports the intent — the
adjacent parent page mentioning the word a handful of times is not support.

### 1. Emergency Heating Repair — `/services/heating-services/emergency-heating-repair/`

- **Keywords:** PHRASE `emergency heating repair`, `emergency heater repair` · EXACT `emergency heating repair`, `emergency heat repair`, `emergency furnace repair`
- **Current state:** no page. The heating hub says "emergency" once.
- **Must carry:** what qualifies as an emergency; what happens after a request is submitted;
  the actual hours a request is answered and a technician can be dispatched.
- **DOUBLE GATE — this page alone does not unblock the ad group.** `client.yaml` records
  `call_answering_hours_confirmed: false` and `can_answer_after_hours: null`, and every
  campaign runs Mon–Fri 08:00–20:00 plus Sat 08:00–13:00. **Do not write 24/7, same-day, or
  any response-time promise onto this page.** Confirm real answering and dispatch hours
  first, then state exactly those hours.

### 2. No Heat Repair — share page 1, or `/services/heating-services/no-heat-repair/`

- **Keywords:** PHRASE `no heat repair`, `no heat service` · EXACT `no heat repair`, `house has no heat`
- **Recommendation:** fold into the emergency page if that page gives no-heat its own
  section with its own H2. A "no heat" searcher and an "emergency" searcher want the same
  thing. Two thin pages are worse than one page with two real sections.
- **Note:** EXACT `no heat in house` was dropped from the build — Google rejected it under
  `GENERAL_DATING_AND_COMPANIONSHIP`, a false positive on an HVAC term. It is flagged
  exemptible; `house has no heat` carries the same intent and passes cleanly.

### 3. Furnace Installation — `/services/heating-services/furnace-installation/`

- **Keywords:** PHRASE `furnace installation` · EXACT `furnace installation`, `furnace installers near me`
- **Current state:** the furnace-repair page mentions installation 5 times with no
  installation section. Sending installation traffic there is the exact mismatch the
  transition instruction forbids.
- **Must carry:** sizing and assessment, what the installation visit involves, fuel types
  actually installed, what the homeowner has to decide.

### 4. Heating Installation — `/services/heating-services/heating-installation/`

- **Covers two requested labels:** Heating Installation and Heating System Installation
- **Keywords:** PHRASE `heating installation`, `heating system installation` · EXACT `heating installation`, `heating system installation`
- **Current state:** heating hub mentions installation 7 times, no section.
- **Must carry:** whole-system installation as distinct from replacing one appliance; which
  system types are installed; how the system is specified for the house.

### 5. Heating Replacement — `/services/heating-services/heating-replacement/`

- **Covers two requested labels:** Heating Replacement and Heating System Replacement
- **Keywords:** PHRASE `heating replacement`, `heating system replacement` · EXACT `heating replacement`, `heating system replacement`, `replace heating system`
- **Current state:** heating hub mentions replacement 6 times, no section.
- **Must carry:** repair-or-replace decision, signs a system is near end of life, what a
  replacement assessment covers.

### 6. Boiler Installation — `/services/heating-services/boiler-installation/`

- **Keywords:** PHRASE `boiler installation` · EXACT `boiler installation`, `boiler installers near me`
- **Current state:** the boiler-repair page is repair-weighted (repair 29) with 5
  installation mentions. The instruction names this case explicitly: *"Do not send Boiler
  Installation traffic to a repair-only page."*
- **Must carry:** boiler types installed, sizing, what the installation involves.

### 7. Boiler Replacement — `/services/heating-services/boiler-replacement/`

- **Keywords:** PHRASE `boiler replacement` · EXACT `boiler replacement`, `replace boiler`, `new boiler cost`
- **Must carry:** when a boiler is worth replacing rather than repairing, what the
  replacement involves, how the new boiler is specified.
- **Note:** EXACT `new boiler cost` is a cost query. The page must handle cost honestly
  without publishing a price — `client.yaml` bars price and dollar claims.

### 8. Boiler Maintenance — `/services/heating-services/boiler-maintenance/`

- **Keywords:** PHRASE `boiler maintenance`, `boiler service` · EXACT `boiler maintenance`, `boiler service`
- **Must carry:** what a boiler service covers, how often, what the technician checks.
- **Commercial note:** these are the most expensive heating clicks in the account
  (CPC $75.08). The boiler-repair page already addresses businesses; this page should too.

### 9. Furnace Tune-Up — `/services/heating-services/furnace-tune-up/`

- **Keywords:** PHRASE `furnace tune up` · EXACT `furnace tune up`
- **Current state:** no page mentions tune-ups at all.
- **Must carry:** what a tune-up includes and how it differs from maintenance. The
  transition instruction keeps Maintenance and Tune-Up as separate ad groups for ad
  relevance, which makes a genuinely distinct page necessary — if the page cannot
  distinguish them, the ad groups should merge instead.

### 10. Heating Tune-Up — share page 9, or `/services/heating-services/heating-tune-up/`

- **Keywords:** PHRASE `heating tune up` · EXACT `heating tune up`
- **Recommendation:** one tune-up page with a furnace section and a whole-system section,
  provided both are real sections.

### 11. Heating System Inspection — `/services/heating-services/heating-system-inspection/`

- **Keywords:** PHRASE `heating system inspection`, `heating inspection` · EXACT `heating system inspection`, `heating inspection`
- **Must carry:** what is inspected, what the report contains, when an inspection is
  appropriate (pre-purchase, pre-winter, after a fault).

### 12–14. Thermostat Repair · Thermostat Replacement · Smart Thermostat Installation

- **Recommended slug:** `/services/heating-services/thermostat-services/` — one page with
  three real sections, because the three services share an audience and each alone is thin.
- **Keywords:** PHRASE `thermostat repair` / `thermostat replacement` / `smart thermostat installation`; EXACT the same plus `replace thermostat`, `nest thermostat installation`
- **Current state:** no page on either domain mentions thermostat work beyond one passing
  reference on the heating hub.
- **CAPABILITY GATE:** `client.yaml` lists all three under
  `services_capability_not_verified`. The transition instruction authorises **advertising**
  them; it does not verify Ambient performs them. **Confirm the capability before this page
  is written**, including whether specific smart-thermostat brands are installed — naming a
  brand is a claim and needs its own verification.

---

## What every new page must satisfy before its ad group is enabled

Same bar as the existing destinations, from the transition instruction:

- HTTP 200 for a normal browser **and** for AdsBot / AdsBot-Mobile, with no SiteGround
  CAPTCHA and no HTTP 202
- correct canonical URL, service-specific title and H1
- Privacy and Terms links
- clean desktop and mobile render
- **no duplicate form or field DOM ids**, one independently addressable form per placement
  (the current main-site template ships **101 duplicate ids** and two forms both called
  `gform_2` — do not reproduce that)
- working submission
- static website number **(410) 761-0932**; `410-914-1456` must not appear or be clickable
- GTM `GTM-PQTPQ436`, GA4 `G-9X9ZHNCRWF`, Google Ads `AW-11155434808`, WhatConverts,
  `wc_visitor`
- GCLID / GBRAID / WBRAID and all UTM fields captured, persisted first-party, and written
  into the submitted lead
- exactly one primary conversion for one approved test submission

## Claims barred on every one of these pages

Unless separately verified and recorded in `client.yaml`: 24/7 availability, emergency
dispatch, same-day service, response times, brands serviced, pricing, financing, free
estimates, licensing, guarantees, review counts or star ratings, and "best" / "top" /
"most trusted" / "most knowledgeable".

The owner's instruction is explicit that it does **not** verify any of these. Three existing
pages already breach this and are listed as DEFECT 5 in
`DEV-2026-09-21-heating-launch-blockers.md`.
