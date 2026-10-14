# Ambient — tracking repair tasks 2026-09-23

Green Marketing has already repaired everything reachable through the Google Ads API.
What remains needs either the WhatConverts UI or a website deployment.

---

## TASK 1 — WhatConverts: register the main-site form (HIGHEST VALUE)

**Owner:** whoever holds the WhatConverts UI login for profile 105803.
**Why it matters:** 13 of the 18 currently enabled heating ad groups send traffic to
`ambientcoolingandheating.com`. None of their form submissions is being captured.

**The evidence.** The profile script at `https://s.ksrndkehqnwntyxlhgto.com/105803.js`
contains a hard allowlist:

```js
var form_list = [["205016","#gform_1",""]];
var form_full = document.querySelectorAll("form" + form_name);   // → form#gform_1
```

Only `#gform_1` is registered.

| Site | Form id | Captured? |
|---|---|---|
| `offer.ambientcoolingandheating.com` | `gform_1` | **yes** |
| `ambientcoolingandheating.com` | `gform_2` | **no — never, not once** |

Confirmed three ways: all 7 web-form leads since 2026-08-01 came from the offer subdomain;
a controlled test on 2026-09-21 produced lead `259273825` from the offer form in 26 seconds
and produced **nothing** from the main-site form; both forms submitted successfully and
both fired `en=form_submit` to Google Ads.

**The fix:** in WhatConverts → Tracking → Form Tracking for profile 105803, add the
main-site form so `form_list` contains `#gform_2` as well as `#gform_1`.

**Acceptance test:** submit the main-site form once with `TEST — DO NOT DISPATCH`; a
`Web Form` lead must appear in profile 105803 within two minutes, with the main-site field
labels (`First Name:*`, `Last Name:*`, `Contact Number:*`, `Service:*`, `Message:*`).

**Note:** this cannot be automated. WhatConverts public API v1 exposes only `accounts`,
`profiles`, `leads` and `users` — there is no endpoint for form tracking configuration.

---

## TASK 2 — WhatConverts: stop it re-promoting its own conversion actions

**Owner:** same.

`AMB-0918-CONV-1` set **WC Lead** (`7643656486`) and **WC Calls** (`7643656075`) to
Secondary on 2026-09-18. By 2026-09-23 both read Primary again. `change_event` holds no
`CONVERSION_ACTION` rows for the window, so the mechanism is not provable from the API.

The leading hypothesis is that saving the WhatConverts → Google Ads integration re-asserts
whichever actions are named as its Lead and Call conversion names. Green Marketing has
re-demoted them today under `AMB-0923-CONV-2`. **Please check whether saving that
integration flips them back.** If it does, the integration needs to point at different
actions, or the demotion has to be re-applied after every save.

---

## TASK 3 — WhatConverts: WC Calls has no supported upload route

**Owner:** same, plus a decision from Green Marketing.

`WC Calls` is type `UPLOAD_CALLS` and has recorded **zero** conversions for its entire
lifetime. `UPLOAD_CALLS` expects Google-forwarded call data (Google's own forwarding
number, call start time, caller id). WhatConverts tracks calls on **its own** numbers,
which are not Google forwarding numbers, so there is nothing it can legitimately upload
into that action.

The workable route for a WhatConverts-tracked call is a **click-based** upload
(`UPLOAD_CLICKS`) using the GCLID captured in the visitor session — which only exists when
the caller browsed the site first. It has been demoted to Secondary, not deleted.

**Also relevant:** the call-duration threshold is set to *longer than 59 seconds*. A real
`google/cpc` call on 2026-09-23 lasted **56 seconds** (lead `259722907`) and was therefore
not eligible. That is the threshold working as configured — flagged so it is a decision,
not a surprise.

---

## TASK 4 — Website: main-site form and page defects (developer)

1. **Duplicate DOM ids.** The main site renders **two** forms both with `id="gform_2"`, and
   101 duplicate element ids per page. `document.getElementById` returns only the first, so
   anything bound by id reads or writes the wrong form. Give each instance unique ids.
2. **Same-day claim.** Every main-site page carries
   `CONTACT AMBIENT FOR SAME DAY HVAC SERVICES TODAY!` next to `(410) 914-1456`. Ambient
   publishes **Mon–Fri 08:00–16:00, closed weekends** (contact page and schema.org
   `OpeningHoursSpecification`). Remove the claim or replace it with the real hours.
3. **DNI still swaps to `410-914-1456`.** The instruction of record is that the main site
   shows `410-761-0932` with DNI disabled. `wc_swap` still reads
   `4109141456+..+4107610932+..+230773` on every page.
4. **No hidden attribution inputs.** Neither form carries a gclid/gbraid/wbraid/utm hidden
   field. That is not automatically wrong — WhatConverts reads attribution from its own
   cookie server-side — but it means the form itself preserves nothing, so if WhatConverts
   misses the form (Task 1) the click id is lost entirely.

---

## TASK 5 — Google Ads: website call conversion points at the wrong number

**Owner:** Green Marketing (Google Ads side).

Both form pages fire
`googleadservices.com/pagead/conversion/11155434808/wcm?cc=ZZ&dn=4104159517` on load.
`dn=4104159517` is **410-415-9517**, which is a *WhatConverts* tracking number
("GSA's Heat Traffic", 44 of its 49 leads are `google/cpc`) and is **not published on
either site**. So Google's website-call swap is configured against a number no visitor
ever sees, and it cannot swap anything.

Decide whether to repoint it at the number actually shown on the site, or retire it. This
is a separate decision from the number architecture and has not been changed.

---

# CORRECTION 2026-09-23 (later) — supersedes Tasks 2 and 3 above

Two statements in the version above were wrong and are retracted.

## Retracted 1 — "demote WC Lead and WC Calls"

Tasks 2 and 3 above were written around demoting the WhatConverts actions. **The owner has
directed the opposite and it is now applied:**

| Action | ID | State |
|---|---|---|
| WC Lead | `7643656486` | **PRIMARY** |
| WC Calls | `7643656075` | **PRIMARY** |
| GA4 form_submission | `7389995485` | Secondary (unchanged) |
| LP Phone call leads | `6885576934` | Secondary (newly demoted — 0 events ever, so nothing lost) |

Executed as `AMB-0923B-CONV-A / B515A5DFD479`, 6 assertions, 0 FAIL. Both WC actions now
also read `include_in_conversions_metric = true` again — demoting them had silently set
that to false.

## Retracted 2 — "WC Calls is structurally unsupported"

I claimed `UPLOAD_CALLS` had no supported route for WhatConverts-tracked calls. **That was
wrong.** WhatConverts' documented design is exactly this: put the WhatConverts tracking
number on the Google Ads Call Asset, Google swaps it for a Google forwarding number, and
the call conversion is imported by **timestamp matching** (not GCLID). That is a supported
route and it is the configuration Ambient already has — call asset `407995613637` carries
`(410) 705-6354`, which is a WhatConverts tracking number.

**Eligible calls demonstrably existed.** On the call-asset number in 2026: 44 calls, **25
longer than 59 seconds**, all `Completed` / `Answered` with caller ID present, 20 of them
`google/cpc`. WC Calls recorded **zero**. So the route is supported, the raw material
exists, and delivery is failing somewhere between WhatConverts and Google.

### The most likely cause, and the one thing to check first

Google's requirement (developers.google.com/google-ads/api/docs/conversions/upload-calls):

> "A mobile click-to-call click cannot be imported as a conversion if there is no Google
> forwarding number attached to the call."

WhatConverts' requirement: **call reporting must be enabled at the Google Ads account level
AND on the specific call asset.**

Measured in the account today:

| Setting | Value |
|---|---|
| `call_reporting_enabled` | **true** |
| `call_conversion_reporting_enabled` | **false** |
| Account call conversion action | `conversionActions/179` — a Google-owned system action, not visible in this account's own list |
| All 5 call assets | `USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION` → they defer to the account, which has conversion reporting **off** |

**Do NOT set the account call conversion action to WC Calls.** WC Calls is type
`UPLOAD_CALLS`, which is for *imported* calls. The account-level call conversion action is
for Google's own *native* call conversions and expects a native action. Pointing it at WC
Calls would be the mistake the owner explicitly warned against.

**A second, equally plausible cause:** the offer landing pages print
`CALL: (410) 705-6354` directly on the page. Anyone who reads that number off the page and
dials it never touches a Google forwarding number, so Google has no record to match and the
import is correctly ignored. Some or all of those 25 "eligible" calls may be direct dials
rather than call-asset clicks. Google's own `call_view` holds 547 call records
(519 `HIGH_END_MOBILE_SEARCH`, 18 `MANUALLY_DIALED`), so both populations exist.

**Next action (WhatConverts UI + Google Ads UI, jointly):** open the WhatConverts Google Ads
integration, confirm the Call Extension Conversion is set to WC Calls and is actually
sending, and read its upload error log for the 25 eligible calls. That log is the one piece
of evidence not reachable from any API.

## Still correct from the version above

Task 1 (register `#gform_2`) stands, and is now confirmed complete: a census of all 8 live
ad destinations at desktop **and** mobile, rescanned after interaction, found exactly two
selectors account-wide — `#gform_1` (offer, 3 instances/page, registered) and `#gform_2`
(main site, 2 instances/page, **not registered**). No popup, modal or lazy-loaded form
exists. The fix is one selector.

Tasks 4 and 5 stand unchanged.

## New — GBP locations: there are THREE, not one

| Asset | Place ID | Label / store code |
|---|---|---|
| `102853408140` | `ChIJM78Y4J39t4kR1s80FfOVBy0` | `**BIP** Ambient Cooling & Heating - Woodbine, MD` |
| `138665832571` | `ChIJ6QkkL9f3t4kRFF3QSwemdVY` | store `01821972159722428876` |
| `245790011117` | `ChIJz4rGOnj3t4kRhqc0X7y0wjk` | store `14076769768679331336` |

They reach Ads through asset set `8620443109` (`LOCATION_SYNC`, ENABLED), not through
direct campaign links. Location placements are serving: Aug–Sep shows `LOCATION_EXPANSION`
46 clicks, `GET_DIRECTIONS` 6, `CALLS` 10.

**The Google Ads phone number override is a GBP-side setting and is not readable through
the Google Ads API.** To verify whether `410-216-4650` (GLE Traffic) is used exclusively
for paid location placements, open each of the three locations in Business Profile →
Advertising / Google Ads phone number and record what each shows. WhatConverts shows that
number carrying 17 leads in 2026, 15 of them labelled `GLE Traffic` — consistent with paid
location use, but 2 leads came from other sources, so it is **not** provably exclusive.
Organic GBP numbers (`410-429-7280`, `410-449-4021`) must stay separate from it.

---

# UPDATE 2026-09-24 — call evidence, DNI plan, and one more retraction

## RETRACTED — the cache-leakage claim

I previously wrote that `Vary` omitting the query string proved a synthetic `?gclid=` could
be cached and served to real visitors. **That reasoning was wrong.** `Vary` governs which
*request headers* create separate cache entries; it never governs the query string, which
is part of the cache key by default. Tested directly: `?gclid=AAA1`, `?gclid=BBB2` and the
clean URL all return a **byte-identical** body (same SHA-256, same length) on both domains.
The page does not server-render a click ID at all, so there is no visitor-specific data in
the cached HTML to leak.

**What this changes:** a parameterised production test is not the hazard I described.
The cleanup requirement still stands as a matter of hygiene, but it is not blocking.

## WC Calls — resolved with actual call evidence

Joining WhatConverts calls against Google's own `call_view` on start time + duration:

| | |
|---|---|
| WC calls on the call-asset number in 2026 | 44 |
| of those, over the 59s filter (**candidates**) | 25 |
| of those, with a matching Google call record (**eligible**) | **4** |
| with NO Google record → import correctly ignored | **21** |

The 4 eligible ones are all `HIGH_END_MOBILE_SEARCH` with display location `AD` — genuine
call-asset clicks through a Google forwarding number:

```
2026-09-01  wc 195s / google 193s
2026-08-31  wc  82s / google  81s
2026-05-19  wc 160s / google 156s
2026-04-02  wc  79s / google  80s
```

**So duration was never the gate.** 21 of 25 candidates are calls placed by people who read
`CALL: (410) 705-6354` off the offer landing page and dialled it directly. Google has no
record of those, so ignoring them is correct behaviour, not a fault.

**The remaining question is narrow:** 4 calls were importable and WC Calls recorded zero.
Two of the four (Apr, May) are now outside a call-conversion lookback window anyway. Only
2026-08-31 and 2026-09-01 are realistically recoverable.

**Also measured:** `Calls from ads` (`1068114183`) holds **46 all_conversions in 2026**, so
the *native* call path is working. That matters for deduplication — if WC Calls starts
importing the same call-asset calls, both actions would count them. That is exactly why the
planned demotion of `Calls from ads` follows WC Calls being verified, not precedes it.

**Still needed, and only reachable in the WhatConverts UI:** the delivery log for those 4
calls, to distinguish *no upload attempted* / *rejected* / *accepted but unmatched*.

## 410-216-4650 — NOT exclusive to paid

17 leads in 2026, all Phone Call, all forwarding to `410-761-0932`:

| Source | Count |
|---|--:|
| `GLE Traffic/(none)` | 15 |
| `GBP Traffic/(not set)` | 1 |
| `GBP Traffic/(none)` | 1 |

So the label is *mostly* right but **2 of 17 leads arrived under a GBP Traffic source**.
The label alone is not sufficient evidence, and this number cannot be treated as a clean
paid-location signal until that is explained. **The Google Ads phone-number override is a
Business Profile setting and is not exposed by the Google Ads API** — it must be read in
the Business Profile UI for each of the three linked locations
(`102853408140` Woodbine MD, `138665832571`, `245790011117`).

## Paid-only DNI — the concrete requirement

Numbers that are NOT reserved for organic GBP, LSA, Facebook, location or the call asset:

| Number | 2026 leads | Current role |
|---|--:|---|
| `410-914-1456` | 99 | the existing site DNI number (google 53, direct 23) |
| `410-415-9517` | 49 | "GSA's Heat Traffic", google 46 |

**Two numbers are available without repurposing anything reserved.**

- For **source-level** paid attribution ("this call came from paid traffic"), one number is
  enough and no purchase is needed.
- For **session-level** attribution, capacity must exceed concurrent paid sessions. Paid
  delivery is currently a handful of clicks a day, so a 2-number pool is adequate **now**.
  It stops being adequate at roughly 2 concurrent paid sessions — as a rule of thumb, once
  paid traffic exceeds ~40–50 clicks/day at a 30-minute session window, collisions start
  and calls get attributed to the wrong session.
- **No purchase is required today.** If heating delivery scales past that point, the ask
  would be additional WhatConverts tracking numbers at WhatConverts' per-number rate — I do
  not have their current price list, so I am not quoting a figure.

**One behaviour change to confirm:** today the swap applies to all traffic, so organic and
direct visitors currently see `410-914-1456`. Under paid-only DNI they would see the base
number `410-761-0932` instead. That is a change to organic/direct display, and it follows
directly from "paid-traffic-only". Flagging it rather than assuming it.

---

# UPDATE 2026-09-23 23:30 ET — #gform_2 registered; main site blocked by NitroPack

## TASK 1 status — WhatConverts side DONE, website side BLOCKED

Green Marketing registered the main-site form in WhatConverts (profile 105803, via the
authenticated UI):

| WC form ID | Name | Attribute | Value | Alt submit | Track |
|---|---|---|---|---|---|
| 205016 | gform_1 (42851) | ID | `gform_1` | No | Yes — **unchanged** |
| **208722** | gform_2 (main site) | ID | `gform_2` | No | Yes — **new** |

The live profile script `https://s.ksrndkehqnwntyxlhgto.com/105803.js` now publishes
`var form_list = [["205016","#gform_1",""],["208722","#gform_2",""]];`
(Last-Modified 2026-09-24 03:18:22 GMT). The script binds with
`querySelectorAll("form#gform_2")`, so **both** `#gform_2` instances on a page are covered.

**The acceptance test was NOT run, deliberately.** The main site does not load that
script. NitroPack serves its own optimized copy:

    https://cdn-ileonjo.nitrocdn.com/.../optimized/rev-59a7f2a/s.ksrndkehqnwntyxlhgto.com/nitro-min-03dbbd4ed2d106d4b3f596089762c82d.105803.js
    last-modified: Fri, 18 Sep 2026 17:48:05 GMT     cache-control: max-age=31536000
    form_list = [["205016","#gform_1",""]]           <- #gform_2 missing

A submission now would email the business a test enquiry and prove nothing. The offer
subdomain is **not** affected: it loads `s.ksrndkehqnwntyxlhgto.com/105803.js` directly
(no NitroPack), so its config is always current.

### Developer action (website — main site only)

1. NitroPack → exclude the WhatConverts script from optimization/combination, so it loads
   from `s.ksrndkehqnwntyxlhgto.com` directly. Match on `ksrndkehqnwntyxlhgto.com`.
   **This is the durable fix.** A purge alone re-freezes the next copy, and every later
   WhatConverts change (form list, DNI pool, swap rules) would go stale again.
2. Purge the NitroPack cache for `ambientcoolingandheating.com`.
3. Confirm: on a main-site page, after the first scroll/click (NitroPack defers JS until
   interaction), the network log shows `s.ksrndkehqnwntyxlhgto.com/105803.js` and no
   `nitro-min-*.105803.js`.

Green Marketing then runs the single labelled test (`scripts/ambient_0923c_gform2_test.py`
has the field map; it must run in a real browser because SiteGround answers headless
clients with HTTP 202 challenge pages).

### Why the 2026-09-22 main-site test proved nothing

Its WhatConverts detector matched URLs containing "whatconverts", but the tracker host is
`ksrndkehqnwntyxlhgto.com`. Its "confirmed" flag matched boilerplate page text. It also
left the required Street Address and City fields empty, so Gravity Forms most likely
rejected it. The live form requires First/Last Name, Email, Contact Number, Service,
Street, City, State, ZIP and Message. Consent boxes are optional.

## WC Calls — per-lead delivery evidence from the WhatConverts UI

The Google Ads integration is connected to **Ambient Cooling (2401959466)**. Lead
conversions go to `WC Lead`, call-extension conversions to `WC Calls`. Trigger: New Lead
Received. Value: Quote Value. Updates to existing conversions: off. Enhanced Conversions:
on. Every lead type: "Sending Data".

| WC lead | Call | WC → Google Ads | Google Ads (by conversion date) |
|---|---|---|---|
| 255745448 | 2026-09-01 9:24 AM, 195 s, 410-705-6354 | **Success**, sent as **WC Lead** | counted — 2.0 WC Lead on 09-01 (HVAC Installation) = this call + the 6:28 PM offer form (also Success / WC Lead) |
| 255575983 | 2026-08-31 12:45 PM, 82 s, 410-705-6354 | **Success**, sent as **WC Lead** | **not counted** — 0 on 08-31 (accepted but unmatched) |

WhatConverts has never tried to send either call as `WC Calls`. It classifies calls to
410-705-6354 as website calls and uploads them through the click-conversion route. **Do
not re-send 255745448 as WC Calls; that would double-count a call Google already holds.**
255575983 can't be recovered: the click route already failed to match it, and there is no
Google forwarding record for a call-extension upload.

## Phone numbers in WhatConverts (UI, 2026-09-23)

11 active numbers. None is pending, disabled or unverified; those UI badges are hidden
template elements. **Only one number swaps on the site:**

| Number | Name | Source rule | Pool size | Swaps |
|---|---|---|--:|---|
| 410-914-1456 | Website Traffic | Dynamic Number Pool: **All Traffic** | **1** | 410-761-0932 |

The other 10 are fixed-source (Offline / Google My Business / Google Local Service Ads):
2nd GBP Traffic 449-4021, FB Traffic 324-2742, GBP - Ellicott 513-9803, GBP Traffic
429-7280, GLE Traffic 216-4650, GSA Cooling Traffic 705-6354, GSA's Heat Traffic
415-9517, LSA - Ellicott 498-4240, LSA Annapolis 443-238-0061, LSA's - Severn 429-7756.

`410-216-4650` (GLE Traffic): 17 leads in 2026 (Feb 2, Apr 9, May 3, Jun 2, Aug 1),
15 of them "GLE Traffic/(none)". It is low-use and not tied to Google Ads.

## Paid-only DNI — CORRECTED sizing and actual price

**Retracted:** "a 2-number pool is adequate now". Measured paid delivery has 55 of 131
active hours with more than one click and a peak of 5 clicks an hour. Session-level
attribution needs a pool of **5–8 numbers**.

WhatConverts rate card (Billing → Rates, read 2026-09-23): **US local $1.50/number/month +
$0.035/minute**. Toll-free is $2.50/number and $0.055/minute.

| Option | Numbers to buy | Added rental |
|---|--:|--:|
| Reuse 914-1456 + 415-9517, add 3–6 | 3–6 | $4.50–$9.00 / month |
| All-new paid pool of 5–8 | 5–8 | $7.50–$12.00 / month |

Minutes mostly move from the existing numbers rather than add. **Nothing was purchased.**
Any paid-only pool on the main site also needs the NitroPack exclusion above, or the pool
config will never reach main-site visitors.

---

# CORRECTIONS 2026-09-24 (evidence-led)

1. **"Main-site form never captured, not once" is WRONG for January-May 2026.** WhatConverts
   holds main-site Web Form leads under form names GF1/GF2/GF4 on 2026-01-07, 2026-04-22 and
   2026-05-26 (all agency tests, now QA-excluded). The statement holds only from August 2026.
   The NitroPack-frozen script (form_list `#gform_1` only) is still the current blocker.
2. **The two "recoverable" calls were call-ASSET calls through Google forwarding numbers.**
   call_view AD 2026-08-31 12:45:13 (81 s) and 2026-09-01 09:24:10 (193 s), both AC Repair.
   Google's native "Calls from ads" (1068114183) counted each once. WhatConverts ALSO uploaded
   both as WC Lead (UI status Success). WC Lead credited the 09-01 call, so that single call
   counted **twice** as Primary. Nothing needs recovering. The WC Lead / Calls from ads overlap
   for call-asset calls is a live double count to resolve before any demotion.
3. **Paid Maps routing (Business Profile Advanced settings, read 2026-09-24).** Google Ads phone
   number = (410) 216-4650 on Severn (12535525085404134070, label "BIP ... Woodbine") and
   Annapolis (18269000296183001967, store 14076769768679331336). Ellicott City
   (11148970617317834534) has no override and is unverified. Location asset set 8620443109 has
   2 ENABLED members (102853408140 Severn, 245790011117 Annapolis); 138665832571 is REMOVED.
   Google has never recorded a location call in call_view, so paid Maps calls exist only in
   WhatConverts, as "GLE Traffic" on 216-4650, and receive no Google Ads credit.
