# Ambient Cooling & Heating: Google Ads handoff briefing

**Account:** Ambient Cooling - Live · Google Ads customer ID 240-195-9466 · managed under the Green Marketing MCC (337-371-1342)
**Prepared by:** Green Marketing, 2026-09-30
**Data freshness:** Account state and September figures come from a fresh read-only Google Ads API pull on 2026-09-30 at 11:20 ET. Sept 29 is the last complete day and Sept 30 is partial. Everything earlier comes from dated audit records (Aug 17 – Sep 27).

---

## 0. How to use this document (instructions for the assistant)

You are helping Green Marketing, a Google Ads agency, manage this client. Treat this document as the source of truth for history and decisions. Some rules:

1. **You have no live access** to Google Ads, WhatConverts, GTM or the website. When a decision depends on current numbers, ask for a fresh export instead of assuming the numbers below still hold.
2. **Do not reopen settled decisions** (Section 12) unless new evidence contradicts them. Several of them were learned the hard way.
3. **Optimize for qualified leads and profit**, not clicks, Ad Strength or Optimization Score. Quote any cost per qualified lead (CPQL) as an upper bound, because call attribution is incomplete (Section 6).
4. **Never invent business facts.** Don't claim prices, discounts, financing, licenses, insurance, reviews, guarantees, response times, same-day, emergency or 24/7 service in ads or landing pages. None of these are verified (Section 1).
5. **Every Google Ads change needs explicit approval** from the Green Marketing approval owner before it is made. Create new things paused, then enable them in a separate step after checking.
6. **Local Services Ads (LSA) are out of scope.** Another department runs them with a separate budget. Don't analyze, recommend or count LSA.

---

## 1. At a glance (2026-09-30)

| Item | Current state |
|---|---|
| Season strategy | **Heating.** Residential cooling was paused on 2026-09-22. Heating runs on 7 Search campaigns. |
| What is serving | 18 "core" heating ad groups with 2 approved ads each (36 ads, all APPROVED). Every ad goes to an `offer.ambientcoolingandheating.com` landing page. |
| Monthly cap | **$10,000/month hard cap**, set by the owner on 2026-09-21. At most **$325/day** in enabled budgets. Monthly math is daily × 30.4. |
| Enabled daily budgets | **$305/day** ($285 heating + $20 holding budget on the Commercial campaign, which serves nothing). The remaining $20 of the $325 is on a paused Performance Max shell. |
| Bidding | Maximize Clicks with a per-campaign max CPC ceiling on every campaign (Section 7.4). |
| Schedule | Mon–Fri 08:00–16:00 ET, matching the published business hours. No weekends. |
| Geography | 75 Central Maryland location targets (28 cities, 5 neighborhoods, 42 ZIP codes). "Presence" targeting only. |
| September spend | **$3,018.41** through Sept 29 (87 clicks, 6 primary conversions), plus $145.18 so far on Sept 30. |
| Heating since the offer-page launch (Sept 24–29) | $1,214.07 · 42 clicks · **2 primary conversions**, both real paid leads carrying a Google click ID on Sept 28 (Section 8) |
| Biggest blockers | (1) Offer-page form rejects submissions where the "(optional)" message field is empty. (2) Cache and attribution defect on the landing pages. (3) Calls from ads can be counted twice. (4) Call button is paused on the two largest heating campaigns until a real call verifies the new number. |
| Next decision point | The heating review planned for "Fri Oct 2 or $1,000 of core spend, whichever first" has already triggered: core spend passed $1,000 on Sept 29 (Section 10). |

---

## 2. Business facts (client truth)

- **Business:** Ambient Cooling & Heating LLC, residential and commercial HVAC in Central Maryland (Severn, Severna Park, Columbia and surrounding areas).
- **Websites:**
  - Main site: `ambientcoolingandheating.com` (WordPress, NitroPack cache/CDN). Used for SEO, Business Profile and LSA.
  - Paid landing pages: `offer.ambientcoolingandheating.com` (WordPress + Divi + Gravity Forms, hosted on SiteGround with a full-page proxy cache, pages set to noindex). **Owner rule since 2026-09-24: paid ads may only point to offer-subdomain pages.**
- **Published hours:** Mon–Fri 8:00 a.m. to 4:00 p.m. Eastern, closed Saturday and Sunday. This comes from the contact page and the site's schema.org opening hours. Unanswered calls go to voicemail and are returned.
- **Published offer:** A free quote request. No price, discount or dollar value is published.
- **Barred claims** (never use): pricing or discounts, same-day, emergency, 24/7, guaranteed response time, years in business, license number, "Licensed & Insured" (withdrawn by the owner on 2026-09-10), ratings or review counts, guarantees or warranties, manufacturer certifications.
  - Note: the main site's template banner says "SAME DAY HVAC SERVICES." That claim is not verified, and no ad repeats it.
- **Commercial HVAC** is confirmed in scope by the owner (2026-09-10), with evidence from five website pages.
- **Services out of scope:** oil furnace and oil heating replacement, and tankless water heaters. Tankless historically cost $12,531.77 for 2 conversions.
- **Service area wording on the landing pages:** "Severn, Severna Park & Columbia, MD." The targeting is wider: 75 locations including Annapolis, Arnold, Bowie, Catonsville, Crofton, Edgewater, Elkridge, Ellicott City, Glen Burnie, Laurel, Odenton, Pasadena, Severn, Severna Park, Timonium and others. Columbia is covered only by ZIP codes 21044/21045/21046, not by a city target.
- **Business economics are unknown:** average job value, close rate, margin and CRM outcomes have never been supplied. WhatConverts `quote_value` and `sales_value` are empty on every lead. ROAS and CAC cannot be computed.
- **September CPQL guardrails (cooling):** $150 for AC Repair, $250 for HVAC Repair and $280 for HVAC Installation. **No CPQL target has been set for heating.**

### Tracking stack

| Tool | ID / detail |
|---|---|
| Google Tag Manager | `GTM-PQTPQ436`, one container on both domains. **Version 17 is live** (v16 is the rollback). |
| GA4 | `G-9X9ZHNCRWF` (property 364077190), fires through GTM |
| Google Ads tag | `AW-11155434808`, fires through GTM |
| WhatConverts | Account 115814, profile **105803** "Ambient Cooling & Heating". Handles call tracking, dynamic number insertion (DNI), form capture, and lead uploads to Google Ads. |
| ClickCease | Linked as a second manager account (281-508-2755). Owns the account tracking template. **Protected: never remove or modify this link.** |
| Other pixels on the pages | Microsoft UET, Meta pixel and Nextdoor pixel. These are not part of the Google measurement plan. |

---

## 3. Phone number architecture

This is critical. Many earlier errors came from mixing up these numbers.

| Number | Role | Rules |
|---|---|---|
| **(410) 761-0932** | Ambient's real line and the **forwarding destination** of every tracking number | Must never appear on a paid landing page, not even in the HTML source. |
| **(410) 705-6354** | WhatConverts number "GSA Cooling Traffic". It is the approved number printed on the offer landing pages and sits on Google call asset `407995613637`. | Fixed-source ("Offline") number, so every call is labeled google/cpc regardless of the real source. It cannot tie a call to a click. It serves both the call asset and the pages, which blurs the two. |
| **(410) 914-1456** | WhatConverts DNI number "Website Traffic". It is a one-number "All Traffic" pool that swaps in on page load. | Mixed-source: it catches organic, direct and paid visitors. On Sept 28 it carried a real paid call bound to a Google click ID, so session-level DNI does work on the offer pages. |
| **(410) 415-9517** | "GSA's Heat Traffic". Since 2026-09-25 it is the **heating call-asset number** (Google asset `424764337810`, Mon–Fri 8–16). WhatConverts type changed to "Google Ads Extension". | Legacy callers still dial it, so its label alone doesn't prove a paid click. The GTM tag "GA - Phone Call Conversion" still points at it. That tag is inert for now, but it must be retargeted before this number ever appears on a page. |
| **(410) 216-4650** | "GLE Traffic", the Google Ads phone override on the Severn and Annapolis Business Profiles (paid Maps and location assets) | Relabeled google/cpc in WhatConverts on 2026-09-27 (applies to new calls only). |
| 410-449-4021, 410-429-7280, 410-513-9803 | Business Profile tracking numbers | Organic. Not paid. |
| 410-429-7756, 410-498-4240, 410-705-4945 | LSA numbers | Out of scope. |
| 410-324-2742 | Facebook | Not Google. |

**Call-asset status today:**
- The 415-9517 call asset is ENABLED on Boiler, Heat Pump, Thermostat, Maintenance and Geothermal.
- It is **PAUSED on Heating & Furnace Repair and Heat/Furnace Install & Replace, the two biggest campaigns.** They stay paused until one genuine ad call proves the routing and the WhatConverts upload.
- The old 705-6354 call asset is paused on all heating campaigns.

---

## 4. Timeline

**Cooling phase**

- **2026-08-14:** Five Search campaigns launched: AC Repair, HVAC Repair, HVAC Installation, HVAC Replacement and Gas Boiler Repair.
  - $13,000/month maximum (Search only). Only 10 keywords (2 per campaign).
  - Maximize Clicks with **no CPC ceiling**.
- **Aug 17–22:** Agency audit and cleanup.
  - Unlinked two account-level callouts making barred claims ("Licensed & Insured", "Claim Your Discount").
  - Moved sitelinks off the main site onto offer pages.
  - Cut Primary conversions to 3.
  - Replaced weak HVAC Repair ads; the new ads rated EXCELLENT.
  - Raised HVAC Installation's budget to $176.15. At the time it was the only budget-limited campaign.
  - Added car/auto/boat negatives on AC Repair.
- **Aug 19–20:** A 24/7 test coincided with an invalid-click spike: 92% of raw clicks since launch, worst overnight on mobile. Google filters invalid clicks and does not bill them. The schedule was restored to Mon–Fri 8–20 plus Sat 8–13.
- **Aug 28:**
  - The keyword `hvac installers` (Phrase, no location word) was found to have spent $2,430 on 102 clicks with **0 conversions**, about 30% of all spend, mostly on competitor-name searches.
  - It was swapped to `hvac installers near me`.
  - Seven competitor negatives were added.
- **Aug 29:** Bulk rollout of **5,652 campaign-level negatives** mined from all-time search terms.
- **Aug 31 – Sep 1:** 79 competitor-name keywords were added and removed about 19 hours later ($44 cost). No remediation was needed.
- **Sep 4, 16:56 ET:** Max-CPC ceilings of **$25 / $25 / $30** were set in the Google Ads web interface on AC Repair, HVAC Repair and HVAC Installation. Delivery fell about 97% and conversions went to zero (Section 5).
- **Sep 9:** Audit found the ceiling outage, plus bulk negatives blocking Ambient's own services, including the `Savage` PHRASE negative that blocked a targeted city (Section 5).
- **Sep 10:** 13 changes executed:
  - Removed the `savage` negative from all five campaigns.
  - Removed the account-level `commercial` negative.
  - Added exact-match competitor negatives.
  - Paused 2 disapproved ads.
  - Cut Gas Boiler to $5/day and HVAC Replacement to $20/day, for a total of $421.55/day ($12,815/month).
  - Created the Commercial HVAC Installation ad group, paused.
- **Sep 15:**
  - Commercial ads and assets created (paused).
  - **Proved the landing-page cache defect** (Section 6).
  - August unit economics built.
- **Sep 16:** Heating research. Paused and removed heating campaigns hold **$108k of history**, and heating clicks cost about a quarter of cooling clicks.
- **Sep 17–18:**
  - First heating build (2 campaigns, created paused).
  - Enabled budgets cut to $237/day.
  - WhatConverts upload actions demoted (later reversed by the owner).

**Heating phase**

- **Sep 21 – owner decision:** Full heating transition.
  - 31 heating services approved for advertising.
  - 7 campaigns and 30 ad groups.
  - $10,000/month hard cap, $325/day maximum.
  - Residential cooling to $0.
  - Oil and tankless out.
- **Sep 21–22:** Heating built and enabled.
  - 113 keywords, 334 cross-campaign routing negatives, 38 ads.
  - Residential cooling paused, with budgets kept for rollback.
  - **Ad schedule corrected to the real business hours, Mon–Fri 8–16**, on every campaign and the call asset.
- **Sep 23:**
  - Tracking audit found that WhatConverts only captures form `#gform_1`. Main-site forms (`#gform_2`) had **never** been captured.
  - Owner directive: WC Lead and WC Calls are Primary conversions.
- **Sep 24:**
  - **Offer-page-only migration** executed: new heating offer pages and 24 new ads. All main-site ads were paused.
  - **GTM v16** fixed thank-you-page conversions that fired on any page visit.
  - The on-page form conversion was demoted to Secondary (fallback).
- **Sep 25:**
  - Budget concentrated on 18 core ad groups. Deferred groups had their ads paused, and labels were applied.
  - Performance Max pilot built but **held paused**.
  - Heating call asset moved to 415-9517.
  - GTM v17 went live (phone-number consistency tag).
  - Two housing-policy appeals filed. **Both ads now read APPROVED with no policy flags (checked 2026-09-30).**
  - WhatConverts Google Ads integration settings documented (enhanced conversions ON, Section 6).
  - Six internal QA test leads marked spam.
- **Sep 26–27:**
  - Two heating negative shared lists built (78 exact + 491 phrase/broad).
  - Performance and click-forensics review.
  - 216-4650 relabeled.
- **Sep 28:** First two **heating paid leads with Google click IDs**:
  - a form from `/boiler-replacement/`
  - a 266-second call through the DNI number after landing on `/hvac-replacement/`
  - Both were uploaded and counted as "WC Lead" Primary conversions.
- **Sep 30:** Fresh read.
  - No user or API edits since Sept 25 at about 18:00. The entries in the change log for Sept 28–30 are Google system status updates.
  - All 36 enabled ads are approved.

---

## 5. Cooling: what went wrong and why it was paused

The five cooling campaigns (launched Aug 14) had several stacked problems. In rough order of money lost:

1. **Uncapped Maximize Clicks.**
   - From Aug 14 to Sep 3 the account paid **$46.66 per valid click** ($8,025 on 172 clicks). AC Repair averaged about $109 per click and HVAC Repair about $71.
   - Campaigns routinely spent about 2× their daily budget, which Google allows on any single day.
   - Some exact "near me" clicks cost $130–$153.
2. **A bad keyword theme.** `hvac installers` (Phrase, no location word) matched competitor company names. It spent $2,430 on 102 clicks with 0 conversions, about 30% of spend. It was fixed on Aug 28.
3. **Then CPC ceilings set too low (Sep 4).**
   - The $25/$25/$30 caps sat below the price of nearly every click that had ever converted.
   - Converting clicks averaged $112.65 in August versus $48.25 for non-converting clicks.
   - **12 of 13 converting clicks in the account's history cost more than the caps.**
   - Delivery collapsed from about $382/day to about $21/day and conversions went to zero.
   - Lesson: a cap removed the converting price band and kept the cheap non-converting traffic.
4. **Over-reaching bulk negatives (Aug 29).** A reverse audit found live negatives blocking Ambient's own demand:
   - 12 major HVAC manufacturer names (Carrier, Trane, Lennox and others) at campaign and account level
   - `commercial`
   - thermostat and humidifier terms
   - `licensed` and `free`
   - the targeted city **Savage, MD**
   
   Savage and `commercial` were fixed. Manufacturer unblocking is on hold: whether Ambient services those brands isn't verified, and its site only names York.
5. **Measurement noise.**
   - The same form or call could be counted by two or three conversion actions.
   - The landing pages had the cache defect described in Section 6.
   - Paid calls mostly carried no click ID.
   - In total, only 8 of 101 WhatConverts leads (Aug 14 – Sep 10) carried a click ID.
6. **Quality Score limits.** AC Repair had QS 4 with below-average expected CTR. HVAC Repair had QS 2 with a below-average landing page. Most impression share was lost to **ad rank**, not budget.
7. **Smaller defects, all since fixed:**
   - The Gas Boiler page said "Your HVAC Replacement in 3 Simple Steps."
   - The ad schedule ran past the real business hours.
   - Sitelinks pointed at main-site pages showing the wrong number.

### August unit economics (the cleanest window: the five campaigns were 100% of paid spend)

| Metric | Value |
|---|---|
| Spend | $6,842.80 |
| Paid leads (WhatConverts) | 14 |
| Qualified (WhatConverts "quotable = Yes") | 8 (7 new-business) |
| CPL | $488.77 |
| CPQL | **$855.35** ($977.54 new-business only) against $150–$280 guardrails |
| Qualified mix | AC Repair 3 · HVAC Replacement 2 · HVAC Installation 1 · Duct/Airflow 1 |

These ratios use published Maryland 2026 job-value benchmarks, **not Ambient's own prices**:
- **Replacement and installation carried about 94% of pipeline value.**
- **AC Repair returned about $0.51 of revenue per $1 of ad spend.** It spent $2,551 for about $1,298 of pipeline and was underwater even at a 100% close rate, yet it had the biggest budget.
- Installation and Replacement returned about 9.5:1.

On a 90-day view:
- Paid search was only **7.5% of all Ambient leads**. Business Profile was 70% and LSA 16%.
- Paid search leads qualified at **52.6%**, so they are not junk.
- Paid web forms were the best sub-source: 5 of 7 qualified.

### Cooling state now

- AC Repair (`24132507741`, $45 budget), HVAC Repair (`24132507750`, $70) and HVAC Replacement (`24132507753`, $15) are **PAUSED**. Their budgets are kept for rollback.
- HVAC Installation campaign (`24132507747`) is ENABLED at $20/day only because it holds the **Commercial HVAC Installation** ad group:
  - The residential HVAC Installation ad group is paused.
  - The Commercial ad group is enabled, but both of its ads are **paused**, so it serves nothing.
  - The commercial landing page `/commercial-hvac-installation/` has open problems: developer instruction text published on the page, an empty gallery, an "Offer Ends in" countdown for an offer that doesn't exist, and a tripled form.
  - Commercial demand is only about 10 searches/month in the area.
- Cooling-season plans still awaiting approval (an AC Repair pinned-headline test, HVAC Repair CPC changes, and others) are **parked until spring**.

---

## 6. The cache and tracking problems, and what we did about them

There are **two different caches** plus several related tracking defects. They explain why paid attribution was unreliable.

### 6.1 SiteGround full-page cache on the offer landing pages (the main "cache issue")

**The problem, proven 2026-09-15:**
- The Gravity Forms on the offer pages have hidden attribution fields (gclid and UTM source, medium, campaign, term and content; now `input_1_9`–`input_1_26`).
- These fields were filled in **on the server** from the visitor's URL.
- SiteGround then cached the **whole rendered page** (`x-proxy-cache: HIT`) and served that copy to later visitors.
- So one visitor's click ID and UTMs were replayed to everyone who got the cached copy, whatever their own URL said.
- In testing, **0 of 24 fresh page loads captured the visitor's own gclid**, and values from an earlier test load showed up for later visitors.
- Consequence: form leads could be credited to the wrong click, campaign or keyword, or to nothing.

**How it was diagnosed:**
- We compared the raw server HTML (before JavaScript) with the live page.
- Each test used a unique marker value, then checked whether a later clean request returned that marker.
- A "field is non-empty" check can't tell a real capture from a stale cached one.
- **Side effect we disclosed:** QA loads with parameters can themselves seed the cache, so test URLs must use a cache-busting parameter and never prime the shared copy.

**Progress since then:**
- **Sep 17–18:** The replay no longer reproduced. Cached copies came back with empty attribution fields.
- **Sep 24:** Retracted an earlier claim that the `Vary` header proved a leak. Tests showed the cached body is byte-identical with or without a gclid in the URL.
- **Sep 25 recheck on a paused page:**
  - A request with a unique parameter was a cache MISS, and the server filled the field correctly.
  - A request with only UTM parameters was a cache HIT on the shared copy with **empty** fields.
  - So SiteGround drops UTMs from the cache key, and **the visitor's own values are lost** on cached hits.
  - After any purge or expiry, the first visitor with parameters can seed the shared copy for everyone.
- **Sep 27 health check:**
  - All 13 heating offer pages loaded clean, with 0 attribution fields carrying stale values.
  - But the **form's hidden gclid field is empty on every 2026 web-form lead**.
  - The click IDs WhatConverts does record come from its **own cookie session** (`wc_visitor` / `wc_client` / `wc_swap`), not from the form fields.
  - That is why the Sept 28 form lead still had a click ID.

**The remaining fix (developer task D7, still open):**
- Fill the hidden fields in the browser from the current visitor's URL and cookies, instead of on the server.
- Or exclude the offer pages from the SiteGround full-page cache.
- Acceptance test: two requests with different `utm_content` values each show their own value in the live DOM, and a clean request shows neither.

### 6.2 NitroPack on the main site

- NitroPack **delays all JavaScript until the first user interaction.** A visitor who bounces without interacting fires no GTM, GA4, Ads or WhatConverts tags, and automated load-and-check tests falsely report "no tags."
- NitroPack also **copies and freezes third-party scripts for a year.** Its copy of the WhatConverts script dates from 2026-09-18.
  - When we registered the main-site form `#gform_2` in WhatConverts on Sept 23, the live WhatConverts script updated, but the site kept serving the frozen copy.
  - **Main-site form leads are still not captured by WhatConverts.**
  - Fix (developer): exclude the WhatConverts host from NitroPack optimization, then purge. A purge alone just freezes a new copy.
- This matters less for paid search now, because every ad goes to the offer subdomain, which loads WhatConverts directly. It still matters for Business Profile and organic leads.

### 6.3 Other tracking defects found and fixed

| Defect | Status |
|---|---|
| The thank-you page fired the Primary form conversion on **any** visit, even without a submission | **Fixed** in GTM v16 (Sep 24). The conversion needs a confirmed submission plus a session token and transaction ID. The GA4 `form_submission` rule was tightened the same way. |
| Gravity Forms 2.9 never fires a normal `submit` event, so a submit listener missed real submissions | **Fixed** in GTM by detecting the submit-button click and withdrawing it if validation errors appear |
| Offer-page header showed 761-0932 in the HTML (button label) while dialing 705-6354 | **Masked** in the browser by GTM v17. The HTML still needs the developer fix (D1). |
| WhatConverts only captures forms listed in its profile allowlist (`#gform_1` = form 205016) | Offer pages use `#gform_1`, so they are captured. Main site uses `#gform_2`, now registered but frozen by NitroPack. |
| Internal QA test leads were uploaded to Google Ads | 6 QA leads marked spam in WhatConverts. Google credited none. GTM v16 suppresses Ads, UET and GA4 events for the QA identity. QA leads are excluded from reporting. |

### 6.4 Open landing-page defects on the offer site (developer list dated 2026-09-25)

| # | Problem | Why it matters |
|---|---|---|
| **D6** | The message field `input_1_7` is labeled "(optional)" but the server **rejects an empty value** | **Likely losing real form leads right now.** Highest priority. |
| **D7** | Server-side attribution fields plus the full-page cache (6.1) | Form attribution |
| **D5** | `form#gform_1` rendered 3 times per page, about 106 duplicate element IDs | Can break validation, accessibility and tracking. The developer must tell us any new form IDs before publishing, because WhatConverts must register them. |
| **D1** | 761-0932 still in the page HTML (header and some body links) | Only GTM hides it today |
| **D4** | Copy mismatches: heat-pump installation and replacement pages say "Heat Pump **Repair**"; boiler-replacement FAQ says "Heat Pump Repair Questions"; thermostat pages' CTA says "Boiler Installation" | Message match and Quality Score |
| **D2** | `/boiler-installation/` shows boiler **maintenance** content and `/boiler-maintenance/` shows installation content | Blocks the Boiler Installation ad group |
| C1 | No consent/privacy line near the form submit buttons (privacy link is in the footer only) | Needs owner approval of the wording |
| — | Publish `/geothermal-heat-pump/` (content and images are ready in Google Drive) | Unblocks the $20/day geothermal test |

---

## 7. Conversion tracking: current setup

### 7.1 Conversion actions (read 2026-09-30)

| Action | Type | Status | Notes |
|---|---|---|---|
| **WC Lead** (7643656486) | WhatConverts upload (click-based) | **Primary** | Owner directive 2026-09-23. Receives form leads and also website-number calls. |
| **WC Calls** (7643656075) | WhatConverts upload (call-based) | **Primary** | Has recorded nothing so far. It only receives calls on a number typed "Google Ads Extension" that Google matches to its own call records. 415-9517 was set up for this on Sep 25 and is waiting for a real call. |
| **Calls from ads** (1068114183) | Native Google call-asset calls, 60-second minimum | **Primary** | Proven working (46 counted in 2026). Keep it Primary until WC Calls is verified. |
| LP Submit Lead Forms (6885463625) | On-page form tag | Secondary (fallback) since Sep 24 | Demoted to avoid double-counting with WC Lead |
| GA4 form_submission (7389995485) | GA4 import | Secondary | |
| Business Profile "Local actions" and Clicks to call | Google-hosted | Flagged Primary but **not counted** in Conversions | They can't be edited through the API and they don't feed bidding. They inflate "All conversions," so ignore them in reporting. |

**Bidding impact today is nil.** Every campaign uses Maximize Clicks, which ignores conversion goals. The setup matters for reporting now and for any future Smart Bidding or Performance Max.

### 7.2 Known double count (open)

The WhatConverts Google Ads integration has **"Send leads as enhanced conversions = Yes"** with trigger "New Lead Received."
- That uploads **every** lead with a phone number or email to WC Lead, even without a click ID. That includes calls from the Google call asset, which Google's native "Calls from ads" also counts. **One ad call can count twice.**
- Turning enhanced conversions off would stop all website-call uploads, which is not allowed.
- **Agreed fix sequence:**
  1. Give the call asset its own WhatConverts number typed "Google Ads Extension" (done for heating: 415-9517).
  2. Wait for real ad calls and confirm they land as WC Calls, matched to Google's call records, with no duplicate WC Lead.
  3. Only then make native "Calls from ads" non-biddable.
- Note on how Google forwards calls: Google swaps in its own forwarding number only once an ad group gets roughly 20–50 clicks/month. Below that, callers dial 415-9517 directly and Google keeps no call record.

### 7.3 How to read lead data (important)

Report four separate layers and don't infer one from another:
1. **Capture:** did WhatConverts record the lead?
2. **Attribution:** does it have a real session click ID, or just the tracking number's configured label?
3. **Upload:** WhatConverts shows "Success." That means Google accepted the upload, not that it counted.
4. **Google Ads credit:** check conversions by *conversion date*.

A lead labeled "google/cpc" on a fixed-source number is **not** proof of a paid click. Per-call proof is either a Google call record from an ad, or a DNI session with a click ID.

Other data notes:
- The WhatConverts API hides duplicate and spam leads by default. Pull all three sets.
- **"Quotable = Yes"** in WhatConverts is our qualification signal. It is often left unset, and it is still unconfirmed whether "Yes" means *quoted* or *sold*.

### 7.4 Heating campaign settings (all 7)

- Search only: no Search Partners, no Display, no AI Max.
- Automatically created assets off. Final URL expansion off.
- Phrase and Exact match only. One keyword theme per ad group (SKAG style).
- 75 Presence targets. Mon–Fri 08:00–16:00.
- Maximize Clicks with CPC ceilings based on evidence. The ceilings came from pre-Sept-4 clearing prices (roughly the 75th percentile of what converting heating clicks cost), not flat caps:

| Campaign | ID | Daily budget | Max CPC | Primary status |
|---|---|---|---|---|
| Heating & Furnace Repair | 24257819463 | $85 | $42 | Limited (by budget/rank) |
| Heating & Furnace Install & Replace | 24257819466 | $60 | $46 | Limited |
| Boiler Services | 24132507744 | $45 | $60 | Limited |
| Heat Pump & Ductless Heating | 24268690038 | $15 | $35 | Eligible |
| Thermostat Services | 24268690041 | $15 | $20 | Learning |
| Heating Maintenance & Inspection | 24279798229 | $45 | $32 | **Not eligible:** all ads paused (budget-deferred) |
| Geothermal Heat Pump | 24274160783 | $20 | $38 | **Not eligible:** ads paused until its page is published |
| *(Commercial holding)* HVAC Installation | 24132507747 | $20 | $30 | Eligible, but its only enabled ad group has no enabled ads |
| *(Held)* PMax Heating Replacement Pilot | 24295088845 | $20 (paused) | — | Paused |

Negatives on all 7 heating campaigns:
- Shared list "Heating | Out-of-scope search terms (EXACT)" (78 terms).
- Shared list "Heating | Low-intent, off-topic & competitor negatives" (491 terms, including `how does` and `how often`).
- 334 cross-campaign routing negatives, so each search lands in the right ad group.
- Plus older campaign-level negatives on Boiler Services, which is one of the original five campaigns.

---

## 8. The heating revamp

### 8.1 Why heating (research, 2026-09-16)

- The account has **33 campaigns but only 5 were enabled.** 15 paused or removed **heating** campaigns hold **$108,464 of spend, 7,251 clicks and 212 conversions at a $14.96 average CPC.** That is about a quarter of cooling click prices.
- **Historical cost per conversion, best to worst.** Conversion tracking double-counted back then, so trust the ranking more than the dollar values:
  - Heating Repair $253, Heating Maintenance $319, Heating & Boiler Repair calls $335
  - Heating Installation $439–$515
  - Furnace Repair Performance Max $616
  - Gas Boiler Repair $709 (at an $89.90 CPC), Mini Split $778, Gas Boiler Installs $858
  - **Tankless $6,266**
- **Heat pumps were the best heating theme:** $8,527, 26 conversions, $328 per conversion, $15.34 CPC.
- **Geothermal *search terms*** (wherever they were served) cost $1,310 for 59 clicks and 4 conversions, $327.51 per conversion. That is better than the heating average, even though campaigns *named* geothermal had no conversions.
- **Seasonality is steep:**
  - "furnace repair" searches run about 110/month in September, 320 in October, 590 in December and **720 in January** (6.5×).
  - WhatConverts heating leads went from 10 in September to 28 in October and **57 in December** last season.
- **Boiler is the trap:** most heating leads by count, but expensive clicks ($90–$106) and middling qualification.
- Keyword Planner has almost no bid data for heating terms (4 of 64), so bid ceilings came from the account's own auction history.

### 8.2 What was built (Sept 21–22) and then refined (Sept 24–25)

- **7 campaigns, 30 ad groups, 113 keywords,** covering the 31 approved heating services plus the existing Gas Boiler Repair group.
- **Owner prioritization on Sept 25:**
  - Concentrate on core repair and install/replace.
  - Keep a $20/day geothermal test.
  - Defer maintenance, tune-up, inspection, ductless, heat-pump maintenance and boiler maintenance. Their ad groups stay enabled for visibility, but every ad is paused.

**Serving now (label CORE_ACTIVE, 18 ad groups × 2 approved ads):**

| Campaign | Ad group | Landing page (offer.ambientcoolingandheating.com) |
|---|---|---|
| Repair | Heating Repair | `/hvac-repair/` |
| Repair | Furnace Repair · Gas Furnace Repair · Electric Furnace Repair | `/furnace-repair/` |
| Repair | No Heat Repair | `/no-heat-repair/`. Ad copy states Mon–Fri 8 a.m.–4 p.m.; no emergency claim. |
| Install/Replace | Furnace Installation · Heating Installation | `/hvac-installation/` |
| Install/Replace | Furnace Replacement · Heating Replacement | `/hvac-replacement/` |
| Boiler | Boiler Repair · Gas Boiler Repair | `/gas-boiler-repair/` |
| Boiler | Boiler Replacement | `/boiler-replacement/` |
| Heat Pump | Heat Pump Repair / Installation / Replacement | `/heat-pump-repair/`, `/heat-pump-installation/`, `/heat-pump-replacement/` |
| Thermostat | Thermostat Repair / Replacement / Smart Thermostat Installation | `/thermostat-repair/`, `/thermostat-replacement/`, `/smart-thermostat/` |

The `/hvac-installation/` and `/hvac-replacement/` pages talk about "heating and cooling systems," so they are valid heating destinations.

**Held (ad groups enabled but no enabled ads):**
- Emergency Heating Repair: WAITING_AVAILABILITY. Business-hours-only answering can't support emergency intent.
- Boiler Installation: WAITING_LP. Its page has the wrong content (D2).
- Geothermal Heat Pump: GEOTHERMAL_TEST / WAITING_LP. Its page isn't published yet.
- Deferred for budget: Furnace Maintenance, Furnace Tune-Up, Heating Maintenance, Heating Tune-Up, Heating System Inspection, Heat Pump Maintenance, Boiler Maintenance.
- Ductless Heating Repair and Ductless Heating Installation: deferred, and Installation is flagged EVALUATE_DUCTLESS.

**Performance Max pilot:** built and **held paused** (`24295088845`, own $20 budget).
- Two asset groups: "Heating & Furnace Replacement" and "Heat Pump Replacement." Images were taken from the landing pages with owner approval.
- It fails its launch gates:
  - **Economics:** at a $484–$616 raw cost per lead, $45–$60/day for 6 weeks buys only 1–3 qualified leads. That can't produce a readable result.
  - Fixed-source website calls.
  - The call double count.
- Planned launch sequence once the gates pass:
  1. Pause the Maintenance campaign (the $45 donor budget).
  2. Raise PMax to $45/day.
- Stop rules: pause at $900 spend with no click-ID lead, or if cost per raw lead is above $600 after $1,500.

---

## 9. Current performance (fresh read, 2026-09-30)

### 9.1 September to date (Sept 1–29, all campaigns)

| Period | Spend | Clicks | Primary conv. | Notes |
|---|---|---|---|---|
| Sep 1–3 (cooling, uncapped) | $1,182.38 | 17 | 4 | Last days before the caps |
| Sep 4–16 (cooling; caps from Sep 4 16:56) | $365.72 | 14 | 0 | Delivery collapse |
| Sep 17–23 (cooling wind-down, then heating on main-site pages) | $256.24 | 14 | 0 | Main-site forms weren't captured |
| Sep 24–29 (heating on offer pages) | $1,214.07 | 42 | **2** | 4 serving days, about $300 per serving day |
| **Total Sep 1–29** | **$3,018.41** | 87 | 6 | Plus $145.18 on Sep 30 (partial) |

### 9.2 Heating by campaign, Sept 24–29

| Campaign | Impr. | Clicks | Cost | Primary conv. | Impression share (last 7 days) | Lost to rank | Lost to budget |
|---|---|---|---|---|---|---|---|
| Heating & Furnace Repair | 1,067 | 17 | $469.90 | 0 | 39.1% | 43.6% | **17.3%** |
| Heat/Furnace Install & Replace | 569 | 6 | $206.65 | **1** | 48.9% | 51.1% | 0% |
| Boiler Services | 47 | 9 | $333.65 | **1** | 72.2% | 27.8% | 0% |
| Heat Pump | 44 | 3 | $78.42 | 0 | 65.7% | 34.3% | 0% |
| Thermostat | 28 | 2 | $23.65 | 0 | 20.0% | 80.0% | 0% |
| Maintenance (spent Sep 24–25, before its ads were paused) | 194 | 3 | $63.55 | 0 | — | — | — |
| Geothermal (spent Sep 24–25, before its ads were paused) | 22 | 2 | $38.25 | 0 | — | — | — |
| **Total** | **1,971** | **42** | **$1,214.07** | **2** | | | |

**The two paid leads (Sept 28), both carrying a Google click ID:**
1. **Web form** from `/boiler-replacement/`, ad group Boiler Replacement. It came from a single click costing $21.21.
2. **Phone call, 266 seconds,** on the DNI number 914-1456, after landing on `/hvac-replacement/`, ad group Furnace Replacement. That group took 3 clicks and $119.53 that day.

Both show "Quotable: Not Set." **Ask the client to mark them.** That is currently the only qualification evidence for heating.

Other paid-labeled WhatConverts leads since Sept 17:
- A 56-second wrong-number call on 705-6354 (Sept 23, marked not quotable).
- A repeat main-site contact form with an old campaign label and no click ID (Sept 27). Unverified, and not counted as paid.

Overall, 38 non-test leads arrived Sept 17–30, and most came through Business Profile numbers. Only 2 carried a click ID.

### 9.3 What the numbers say

- **It is still too early to judge heating cost per lead.** There are 2 raw paid leads for about $1,110 of core spend, which is about $555 per raw lead, and qualification is unknown. Demand ramps about 3× into October.
- **Reach is limited by ad rank more than budget.** 28–80% of impressions are lost to rank. When the ads do show, they are mostly at the top.
  - The 09-27 click forensics measured 33–70% of shown impressions at position #1 (Heat Pump lowest, Boiler highest), and 67–87% in the top block.
  - The gap is auctions missed. Repair and Install have low CTR (about 2%) and message-match gaps:
    - "heating repair" searches land on an "HVAC Repair" page
    - headlines name only Severn, Severna Park and Columbia, while clicks come from Glen Burnie, Pasadena, Catonsville, Bowie and Timonium
- **New signal:** Heating & Furnace Repair has begun losing **17% of impressions to budget.** It spent 2× its $85 budget on some days: $169 on Sept 28. Watch it, but don't raise it before lead quality is known.
- **Mobile is about 85–90% of clicks,** yet Repair and Install/Replace have no active call button (Section 3).
- **Boiler has the best CTR (13%) and the most expensive clicks (about $37 average since Sept 24).**
- **About $85/day of enabled budget can't spend at all:** Maintenance $45, Geothermal $20, Commercial $20. So the budget that can actually serve is about $220/day.
- Heating clicks average about $26–$37 on the main campaigns (Thermostat about $12), versus $47–$109 in the uncapped cooling period.
- Off-topic search spend (about 18% in the first week) is now blocked by the two shared lists.

---

## 10. Budget and pacing

- **Cap:** $10,000/month hard cap. Enabled daily budgets must stay at or under $325. The absolute ceiling is $328.94/day (= $10,000 ÷ 30.4).
- **Math rule:** monthly = daily × **30.4**, never × 30. Google may spend up to **2× the daily budget on any single day,** but monthly charges can't exceed daily × 30.4.
- **Current:**
  - $305/day enabled, which is $9,272/month at most.
  - With the paused PMax $20, the total is $325, or $9,880/month.
  - Ads serve Mon–Fri only, about 21.7 days a month. At the current ~$300 per serving day, October would land around **$6,500** unless demand grows. It should, seasonally.
- **Budget history:**

| Date | Enabled daily total |
|---|---|
| August | $13,000/month Search max; about $466/day after Aug 22 |
| Sep 10 | $421.55 |
| Sep 18 | $237 |
| Sep 22 | $290 (heating launch) |
| Sep 24 onward | $305 |

- **Rules:**
  - Never raise a budget or CPC just to hit a spend number.
  - Spend utilization comes after lead economics.
  - Recompute month-to-date and remaining days immediately before any budget change.
  - Days with no delivery return no data row, so average daily spend over **calendar** days, not over rows.

---

## 11. Recommended plan from here

This is Green Marketing's current recommendation, in priority order.

1. **Fix lead capture first.** Push the developer on:
   - **D6** (the "optional" field that blocks form submissions): highest.
   - **D7** (cache and attribution).
   - D5 (triplicated form).
   - D1 (phone number in the HTML).
   
   After each fix, purge the SiteGround cache for that URL and run one clean QA submission per page, with no URL parameters and using the QA identity.
2. **Run the heating checkpoint now,** because the $1,000 core-spend trigger was hit on Sept 29.
   - Get the client to mark the two Sept 28 leads quotable Yes or No.
   - Keep the core structure unchanged while volume builds.
   - Judge cost per lead by campaign once each core campaign has roughly $500–$1,000 of offer-page spend, using WhatConverts leads with click IDs plus Google call records.
3. **Turn on the call button for Repair and Install/Replace** as soon as one genuine ad call on 415-9517 is verified:
   - It routes to 761-0932.
   - It shows as WC Calls in WhatConverts.
   - It does not also upload as WC Lead.
   
   Mobile is about 85% of clicks.
4. **Improve ad rank on Repair and Install/Replace** with better relevance, not higher caps:
   - Headlines and landing-page copy that say "heating" and "furnace" instead of "HVAC."
   - City coverage beyond Severn, Severna Park and Columbia, using only verified service areas.
   - A lighter mobile page (full load 11 seconds, 3.4 MB).
   - Only raise a CPC ceiling after checking what *converting* clicks cost.
5. **Budget moves within the $325 cap only.**
   - If the Sept 28 leads qualify and Repair keeps losing more than 15% to budget, move part of the idle Maintenance budget ($45/day, which serves nothing) to Repair and/or Install & Replace.
   - Note this touches the Sept 25 decision that kept Maintenance as the future PMax donor, so it needs owner sign-off.
6. **Publish `/geothermal-heat-pump/` and fix D2 (boiler installation page),** then enable those ad groups' ads. Each needs approval.
7. **Keep PMax held** until the call double count is fixed and there is a readable Search baseline.
8. **Spring cooling relaunch (plan around February–March 2027):**
   - Prioritize installation and replacement over AC Repair.
   - Keep ceilings above the converting price band.
   - Use no location-less two-word Phrase keywords.
   - Fix the Commercial landing page first.
   - Revisit manufacturer negatives with the client.

### Questions for the client or owner (they change the plan)

1. What does "quotable = Yes" mean at Ambient: quoted, or sold? Can the office mark every lead?
2. Average job value and close rate for furnace or heating replacement, repair and boiler work. These are needed to set a real CPQL target for heating.
3. Does the $10,000/month cap and $325/day maximum carry into October?
4. Can Ambient actually take emergency or after-hours heating calls? Without that, Emergency Heating Repair stays held.
5. Approve the consent/privacy line under the form buttons (C1). Also confirm Ambient is comfortable with WhatConverts enhanced conversions: its setup text says enabling it confirms visitor consent.

---

## 12. Settled decisions: don't reopen without new evidence

| Decision | Why |
|---|---|
| LSA is out of scope | Other department, other budget. The $10k cap is Search only. |
| ClickCease link and template are protected. No IP exclusions added, no ClickCease tag installed. | Owner decision (Aug 20). Google-filtered invalid clicks are not billed. |
| Paid ads go to offer-subdomain pages only | Owner rule (Sep 24) |
| Ads run Mon–Fri 8–16 only. No emergency, same-day or 24/7 claims. | Matches the published hours |
| Oil and tankless services are out | Owner scope (Sep 21). Tankless history cost $6,266 per conversion. |
| WC Lead, WC Calls and Calls from ads are Primary. The LP form tag and GA4 are Secondary. | Owner directive (Sep 23–24). Don't demote Calls from ads until WC Calls is verified. |
| Phrase and Exact only, one theme per ad group. Search Partners, Display, AI Max, auto-assets and URL expansion stay off. | Agency policy |
| 75 Presence targets. Don't exclude states because of search-term text. | Location reports show 100% of recent clicks came from inside the targeted area. Out-of-state words in search terms are just query text. |
| Never attach the old shared lists "General List" (contains `repair`) or "Ambient - Neg Kwd List" (blocks the client's own cities Severn and Arundel, plus words that converted) | They would block the account's own demand |
| Don't negative manufacturers, place names, ambiguous company names or generic service phrases. Never auto-negative "near me," "cost," "price," "quote," "best," "local," "hire" or "emergency." | The bulk-negative lesson from Aug 29 |
| Don't exclude Business Profile location-asset clicks | Once invalid clicks are filtered out, they are among the best-converting click types |
| Don't cap CPCs below the price converting clicks actually cost | The Sept 4 outage |
| AC Repair gets the lowest priority when cooling returns | 0.51:1 revenue-to-spend in August on benchmark job values |
| Performance Max stays held | Economics and tracking gates fail |

---

## 13. Lessons and analysis traps specific to this account

- **Split every metric at 2026-09-04 16:56 ET.** That is when CPC ceilings were first created. Before it the account was uncapped Maximize Clicks, after it capped. A $106 average CPC next to a $25 cap is not a billing error.
- **Converting clicks are the expensive ones here.** Before judging a cap, compare the CPC of converting versus non-converting search terms.
- **A conversion record is not a unique lead.** One form or call can create 2–3 conversion records. Bound the unique-lead count before quoting CPL.
- **Google restates data.** Don't draw conclusions from same-day or unsettled numbers. Also, a conversion counted before a settings change stays in the historical column.
- **Check whether a negative can actually be reached** before calling it harmful. It only costs money if the query could match a live keyword in that same campaign.
- **After any bulk negative change, run the audit in reverse:** test real buyer phrases against every negative.
- **A WhatConverts label is not attribution.** Group by tracking number, and pull duplicates and spam too. Paid calls have hidden in the "duplicate" set before.
- **Test landing pages in a real browser, after interacting with the page.** SiteGround's captcha gives non-browser tools an empty page, and NitroPack delays scripts. Both cause false "no tracking" findings.
- **Housing-policy limits ("Eligible (limited)") on HVAC ads** mean the ad can't use ZIP-code targeting, and 42 of 75 targets are ZIPs. Appeal in the UI with "Dispute decision" instead of rewriting copy. Both Sept 25 appeals appear resolved.
- **Changes made in the Google Ads UI** appear as "Google Ads web client" under the shared agency login. That doesn't identify who made them.

---

## 14. Key IDs reference

| Thing | ID |
|---|---|
| Google Ads account | 240-195-9466 (API: 2401959466) · Green Marketing MCC 3373711342 · ClickCease manager 2815082755 |
| Heating campaigns | Repair 24257819463 · Install/Replace 24257819466 · Boiler 24132507744 · Heat Pump 24268690038 · Thermostat 24268690041 · Maintenance 24279798229 · Geothermal 24274160783 |
| Cooling campaigns (paused) | AC Repair 24132507741 · HVAC Repair 24132507750 · HVAC Replacement 24132507753 · HVAC Installation/Commercial 24132507747 (enabled, $20) |
| Commercial ad group | 199748801029 (ads 824781897834 / 824781897837, both paused) |
| PMax pilot (held) | 24295088845 · asset groups 6751612859, 6751752096 |
| Call assets | Heating 424764337810 (410-415-9517) · Cooling 407995613637 (410-705-6354) |
| Business Profile location asset set | 8620443109 (3 locations) |
| Heating negative lists | 12252013691 (78 exact) · 12249470554 (491) |
| Account-level negative list | 11252984411 |
| Conversion actions | WC Lead 7643656486 · WC Calls 7643656075 · Calls from ads 1068114183 · LP form 6885463625 · GA4 form 7389995485 |
| WhatConverts | Account 115814 · profile 105803 · offer form 205016 (`#gform_1`) · main-site form 208722 (`#gform_2`) · DNI swap rule 230773 |
| GTM / GA4 / Ads tag | GTM-PQTPQ436 (v17 live, v16 rollback) · G-9X9ZHNCRWF · AW-11155434808 |
