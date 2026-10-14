# Apogee Lawns LLC - Live: full account briefing and performance research

Prepared 2026-10-05 by Green Marketing's Google Ads agent from fresh read-only data. Paste this whole file into a
new ChatGPT chat as its starting context.

---

## 0. Instructions for the assistant reading this

You are helping Green Marketing (a Google Ads agency) manage one client account. Treat everything below as the
record of what has been done and what is known. Rules:

1. Never invent business facts (prices, reviews, ratings, response times, licences, service areas, offers). The
   only verified claims are listed in section 9. Anything else needs the owner's confirmation first.
2. Settled decisions in section 14 are closed. Do not re-propose them unless the owner reopens them.
3. Optimize for qualified leads and sold jobs, not clicks, Ad Strength or Google's Optimization Score.
4. Agency defaults: Search campaigns only, Phrase and Exact match only (no Broad without approval), Search
   Partners and Display off, two responsive search ads (RSAs) per ad group, no automatically applied Google
   recommendations, every change approved before it is made.
5. Never put a customer's name, phone number, email or address into any document.

---

## 1. Account identity

| Item | Value |
|---|---|
| Google Ads account | **Apogee Lawns LLC - Live** |
| Customer ID | **816-462-6278** |
| Manager (MCC) | Green Marketing, 337-371-1342 |
| Currency / time zone | USD / America/Chicago (Central) |
| Business | Apogee Lawns LLC, Lincoln, Nebraska. Lawn care company that also sells and installs permanent holiday lighting |
| Website | https://apogeelawns.com/ |
| Paid landing page | https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/ |
| Service advertised | **Permanent Christmas light installation** (one service only) |
| Agency vertical | similar-local-service, approved by Walter on 2026-09-16 ("a closely related local home-service installation service") |
| Campaigns in the account | **1** (there are no other campaigns) |
| Billing | Approved payment setup active since 2026-09-16 19:01 (two earlier setups from 2026-09-15 were cancelled) |

Services explicitly **out of scope** for this campaign: seasonal Christmas light hanging, removal and storage;
lawn mowing, fertilization, aeration, overseeding; commercial lawn care; leaf removal; irrigation repair; pavers
and outdoor kitchens.

---

## 2. The short version

- The campaign has run since **2026-09-21**. Through 2026-10-04 it earned **194 impressions, 7 clicks, $46.32
  spend, 3.6% CTR, 0 conversions**.
- **It launched in the off-season.** For "permanent christmas lights" in Lincoln, an average year puts 4% of
  searches in September, 13% in October, **50% in November** and 18% in December (Google Keyword Planner, three
  full years). Impressions are already rising: from about 7 a day in the first week to about 20 a day last
  week, and 37 on 2026-10-04.
- **The market is small even at peak.** The main search term averages about 90 searches a month in the service
  area (480 to 720 in November). Installation-specific searches are about 10 a month each. The ads already show
  for about **81% of the searches they qualify for**, so most of the available demand is already being reached.
- **Low CTR has two clear causes:**
  1. Half of all impressions appeared **below the search results**. Those 97 impressions earned **0 clicks**;
     the 97 top-of-page impressions earned all 7 (7.2% CTR). The installation keyword gets **11.5% CTR at the
     top**, which is healthy.
  2. The exact keyword `[permanent christmas lights]` had **91 impressions and 0 clicks**. Google matches it to
     product-shopping searches like "permanent outdoor lights", "best permanent outdoor lights" and "types of
     permanent outdoor christmas lights", from people comparing products and DIY kits rather than hiring an
     installer.
- **Ad Rank is weak for reasons that cost nothing to fix.** The ads have **no sitelinks, no location assets,
  no images, no business name or logo**: only 6 callouts, 1 structured snippet and a call button. Google
  rates the campaign "Limited by bid strategy" (the $8 maximum CPC).
- **Zero conversions is not yet evidence of failure.** Seven clicks at the planned 5% conversion rate predicts
  0.35 leads. WhatConverts confirms there is no hidden paid lead: 0 leads from Google Ads in this period. Form
  conversion tracking still cannot fire in Google Ads; see section 11.
- **Local Services Ads (LSA) are producing the account owner's leads.** WhatConverts shows 11 LSA leads
  (8 texts, 3 calls, all marked quotable) in the same two weeks.

---

## 3. Timeline of everything done

| Date (CT) | What happened |
|---|---|
| 2026-09-15 | Two billing setups were created and both ended up cancelled. |
| 2026-09-16 | Account identity verified. Read-only preflight: the account was brand new (0 campaigns, 0 conversion actions, $0 lifetime spend). Keyword Planner research showed **demand, not budget, is the limit**. All 14 service-area locations resolved to Google location IDs, matched by exact name (Google's suggestion tool proposed Omaha ZIP 68104 for "Waverly", which was rejected). Seven pre-existing negative keyword lists were audited and **none were attached**: one list blocked the campaign's own main keyword, and two contained bare negatives like cost, price, best and hire that agency policy protects. Walter approved the similar-local-service scope. The form-lead conversion action was created. New billing setup approved at 19:01. |
| 2026-09-17 | The two call conversion actions were created. Walter set all three conversions to Primary; the website-call action was demoted back to Secondary because its tag could not yet fire. **Campaign created PAUSED** (121 objects, 0 readback failures). GTM workspace built: Google tag, form conversion tag, website-call tag, triggers, lead_id variable. **Call asset** added with 402-526-5754 (Mon-Fri 8-5, Sat 8-12). Strategy and landing-page Google Docs corrected. 8 approved image crops produced from 5 client photos (not uploaded to Google Ads). GTM version 2 published. |
| 2026-09-21 09:04 | **Campaign enabled** in the Google Ads web interface. |
| 2026-09-25 08:26 | **Tablets set to -100%** in the web interface. Owner reason: "Landing pages are not tablet optimized so I excluded them." |
| 2026-09-28 | Three audits. Run A was superseded (it wrongly recommended Omaha, a settled exclusion). Run B, an independent audit, concluded the design is sound and volume is limited by niche demand plus the September trough, and that the form conversion cannot fire. Run C, a measurement repair handoff, produced a developer checklist. Run D recorded owner answers: tablets stay excluded; a qualified lead is "someone who asks for the service on the form or on the call"; Apogee installs customer-supplied lights. **GTM version 3** ("Add Conversion Linker tag") published 14:38. |
| 2026-09-25 to 10-05 | **No account changes.** Google's change history has no edits after 09-25. |
| 2026-10-05 | This briefing: fresh snapshot, Keyword Planner seasonality, search-term study, WhatConverts lead check. Nothing was changed. |

---

## 4. Strategy and why

- **Goal:** qualified leads for permanent Christmas light installation in Lincoln and nearby towns, within
  **$500 a month** ($16.44 a day; Google's monthly cap is daily x 30.4 = $499.78).
- **Planning economics** (Green Marketing assumptions, not results): target cost per lead $100 (acceptable
  launch range $90-$125), 5% click-to-lead rate, 20% lead-to-sale rate, which implies an affordable average CPC
  of about $5. The **$8.00 max CPC is a delivery ceiling**, not the expected price. Gross profit per sold job is
  still unknown.
- **Why so narrow:** Keyword Planner showed the installation phrases carry about 60 searches across the whole
  September-December season. The only meaningful search bucket is "permanent christmas lights" (about 840 searches
  September-December in the service area). The build therefore has:
  - Ad group 1: installation intent, Phrase + Exact.
  - Ad group 2: the main term, **Exact only**. Phrase was rejected because a forecast showed it reaches mostly
    product and DIY searches (Govee, Trimlight, Gemstone, Reddit, TikTok) with no hiring intent.
- **Bidding:** Maximize Clicks with an $8 ceiling, because there is no conversion data to train a
  conversion-based strategy, and form tracking does not work yet.
- **Search only:** no Search Partners, no Display, no Broad Match, no AI Max, no automatically created text,
  no Performance Max.
- **Location:** 14 Lincoln-area targets with "Presence" (people physically in the area). **Omaha is excluded**
  by a settled owner decision.
- **Schedule:** ads run 24/7 (form leads are fine any hour); only the call button is limited to answer hours.

---

## 5. Campaign settings (verified 2026-10-05)

| Setting | Value |
|---|---|
| Campaign | `S \| Website Leads \| Permanent Christmas Lights \| Apogee Lawns \| $500 \| 09_2026` (ID 24257151015) |
| Status | **Enabled**, serving. Google status: **Limited - bidding strategy limited** |
| Type / networks | Search. Google Search only; Search Partners OFF; Display OFF |
| Bidding | Maximize Clicks, **maximum CPC $8.00** |
| Budget | **$16.44/day**, standard delivery, not shared (budget ID 15884926233) |
| Locations | 14 targets, Presence for both targeting and exclusion (list in section 8) |
| Language | English |
| Ad schedule | None (24/7) |
| Devices | Desktop and mobile normal; **tablet -100%** (campaign and both ad groups) by owner decision |
| Broad match / AI Max / text automation | Off / not enabled / opted out |
| Tracking | Auto-tagging on. Final URL suffix: `utm_source=google&utm_medium=cpc&utm_campaign=apogee_permanent_lights_2026&utm_term={keyword}&utm_content={creative}&utm_matchtype={matchtype}&utm_device={device}&utm_network={network}&utm_adgroup={adgroupid}` |
| Negative keyword lists attached | None. 75 campaign-level negatives instead (section 8) |

---

## 6. Ad groups, keywords and results (2026-09-21 to 2026-10-04)

| Ad group | Keyword | Match | Impr | Clicks | CTR | Cost | Impr. share | Top / abs. top | Quality Score |
|---|---|---|---|---|---|---|---|---|---|
| AG \| Permanent Light Installation | permanent christmas light installation | Phrase | 101 | 6 | 5.9% | $41.16 | 80.8% | 66.7% / 38.5% | not yet rated |
| AG \| Permanent Light Installation | permanent christmas light installation | Exact | 0 | 0 | - | $0 | - | - | not yet rated |
| AG \| Permanent Light Installation | permanent christmas lights installer | Phrase | 0 | 0 | - | $0 | - | - | not yet rated |
| AG \| Permanent Light Installation | permanent christmas lights installer | Exact | 2 | 1 | 50% | $5.16 | 100% | 100% / 10% | not yet rated |
| AG \| Permanent Christmas Lights Exact | permanent christmas lights | Exact | 91 | **0** | **0%** | $0 | 80.3% | 66.7% / 16.7% | **6** (expected CTR, ad relevance, landing page all "average") |

Notes: all keywords are approved and eligible. "Not yet rated" means Google has not had enough data to give a
Quality Score. Impression share is the share of searches the ad was eligible for where it actually showed.

---

## 7. Ads: every headline, description and landing page

**All four ads send people to the same page:**
`https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/`. All four are approved with Ad Strength
"Average". Headlines marked [H1] are pinned to position 1 (Google rotates among the three pinned options);
the rest are unpinned.

### Ad 1 (ID 825023783007), ad group "Permanent Light Installation"
Display path: `/permanent/install`. Results: 91 impressions, 6 clicks, 6.6% CTR, $39.50.

Headlines: Permanent Light Installation [H1] · Permanent Christmas Lights [H1] · Lincoln Permanent Lights [H1] ·
Professional Installation · One Install, Year-Round Use · App-Controlled Lighting · Custom Colors and Schedules ·
No Annual Light Setup · Homes and Businesses · Request a Free Estimate · Installed Once, Used All Year ·
Plan Your Lighting Project

Descriptions:
1. Professional permanent Christmas light installation in Lincoln. Request a free estimate.
2. One professional install replaces yearly hanging, removal and storage.
3. Choose colors, patterns and schedules from the app after installation.
4. Tell Apogee Lawns about your home or business and get a custom estimate.

### Ad 2 (ID 825023783010), ad group "Permanent Light Installation"
Display path: `/permanent/install`. Results: 12 impressions, 1 click, 8.3% CTR, $6.82.

Headlines: Permanent Christmas Lighting [H1] · Permanent Lights Installed [H1] · Lincoln Lighting Installer [H1] ·
One Install, Year-Round Use · No Annual Light Setup · Lights Ready Every Season · Control Lights From Your Phone ·
Custom Colors and Schedules · Lighting for Every Occasion · Professional Installation · Homes and Businesses ·
Request Your Free Estimate

Descriptions:
1. Install the lighting once and use it for Christmas, events and everyday accents.
2. Professional installation along the roofline, then control it from your phone.
3. Skip the yearly setup, removal and storage with a permanent lighting system.
4. Request a free permanent-lighting estimate for your Lincoln-area property.

### Ad 3 (ID 825023783013), ad group "Permanent Christmas Lights Exact"
Display path: `/christmas/lights`. Results: 74 impressions, **0 clicks**.

Headlines: Permanent Christmas Lights [H1] · Lincoln Permanent Lights [H1] · Permanent Light Installation [H1] ·
Professional Installation · One Install, Year-Round Use · App-Controlled Lighting · Custom Colors and Schedules ·
No Annual Light Setup · Homes and Businesses · Request a Free Estimate · Built for Year-Round Use ·
Apogee Lawns Lighting

Descriptions:
1. Permanent Christmas lights installed in Lincoln. Request a free estimate.
2. A permanent system, not annual hanging and removal. Installed once, used all year.
3. Use app-controlled colors, patterns and schedules for Christmas and every season.
4. Tell us about your home or business and get a custom permanent-lighting estimate.

### Ad 4 (ID 825023783016), ad group "Permanent Christmas Lights Exact"
Display path: `/christmas/lights`. Results: 17 impressions, **0 clicks**.

Headlines: Permanent Christmas Lighting [H1] · Year-Round Christmas Lights [H1] · Permanent Lights in Lincoln [H1] ·
One Install, Year-Round Use · No Annual Light Setup · Control Lights From Your Phone · Custom Colors and Schedules ·
Lighting for Every Occasion · Professional Installation · Homes and Businesses · See Lighting Possibilities ·
Request Your Free Estimate

Descriptions:
1. One permanent lighting system for Christmas, events and everyday accent lighting.
2. Change colors, patterns and schedules from your phone after professional installation.
3. No yearly setup or takedown. The system stays installed and ready every season.
4. Request a free custom estimate from Apogee Lawns for your Lincoln-area property.

### Landing page

| Item | Value |
|---|---|
| URL | https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/ (used by all 4 ads) |
| Host | A separate subdomain (`offer.`), WordPress + Gravity Forms. Not the main site |
| Last verified | 2026-09-17 (page source): returns 200, noindex, paid number 402-526-5754, Google Tag Manager GTM-M545Z8T2 and the WhatConverts script installed, Privacy and Terms links, no Omaha, no rating claims. 2026-09-28 (real browser): renders cleanly on desktop and on a 390 px phone screen, with a sticky call/estimate button |
| Known content defects (09-28) | **Three internal drafting notes are published on the page** (C1 to C3 in section 11) |
| Form | Gravity Forms form 1 (`gform_1`). WhatConverts tracks it. It sends no Google Ads conversion (section 11) |
| Thank-you page | `/thank-you/permanent-christmas-lights/` **did not exist on 09-28** (WordPress redirected it to the landing page) |
| 2026-10-05 check | The host returned a SiteGround captcha challenge to the automated check (HTTP 202, 209-byte page), so the page could not be re-verified from this machine. It needs a real-browser check |

---

## 8. Assets, locations and negatives

### Assets linked to the campaign (all approved)

| Type | Content | Impr / clicks (09-21 to 10-04) |
|---|---|---|
| Call | 402-526-5754, US. Shows Mon-Fri 08:00-17:00 and Sat 08:00-12:00 Central only. Counts calls of 60 s or longer as "Call \| Permanent Lights \| Ads \| 60s" | 19 / 0 calls |
| Callout | Homes and Businesses | 58 / 1 |
| Callout | App-Controlled Lights | 92 / 0 |
| Callout | Custom Colors and Scenes | 100 / 2 |
| Callout | Year-Round Use | 87 / 3 |
| Callout | Professional Installation | 44 / 0 |
| Callout | Local Installation | 69 / 2 |
| Structured snippet | Header "Service catalog": Permanent Light Install, Residential Lighting, Commercial Lighting | 4 / 0 |

**Missing:**
- **Sitelinks (0).** The single biggest gap: no extra links under the ad.
- **Location assets (0).** No Google Business Profile is linked, so there is no address or map pin.
- **Image assets (0).** 8 approved crops exist in Google Drive; written commercial-use rights for the photos are
  still outstanding.
- **Business name and logo (0).** Google requires advertiser verification first.
- **Price assets (0).** There are no verified prices.

### Locations targeted (14, Presence)
Lincoln (city) · Waverly (city) · Eagle (city) · Crete (city) · ZIP 68372 · 68430 · 68527 · 68347 · 68526 · 68461 ·
68516 · 68520 · Ashland Township · Nemaha Precinct. **Omaha is excluded by decision.** Impressions came mostly
from Lincoln (113 through the Lincoln city target, 46 through ZIP 68516).

### Campaign negative keywords (75)
Broad: amazon, career, careers, costco, distributor, distributors, diy, ebay, garland, garlands, indoor,
inflatable, inflatables, instructions, job, jobs, kit, kits, laser, lasers, lowes, menards, projector, projectors,
rent, rental, rentals, salary, supplier, suppliers, temu, tutorial, tutorials, walmart, wholesale, wreath, wreaths.
Phrase: app download, app not working, best christmas displays, celebright, christmas at the zoo, christmas light
hanging service, christmas light removal, christmas light repair, christmas light storage, christmas light tour,
christmas lights for sale, christmas lights map, christmas parade, customer supplied, do it yourself, drive
through, gemstone, govee, holiday event, holiday light tour, holiday lights for sale, holiday lights map, home
depot, how to, jellyfish, labor only, light show, lighting festival, lights show, my own lights, oelo, replacement
christmas bulbs, seasonal light installation, take down christmas lights, target christmas lights, trimlight,
where to buy, zoo lights.

Deliberately **not** negatives (agency policy protects them): cost, price, pricing, best, hire, near me, local,
emergency, quote.

---

## 9. Verified claims that may be used in ads (source: Apogee's own website)

- Professional installation for homes and businesses.
- Free consultation and custom design; free, no-obligation quote; pricing based on the roofline's linear footage.
- App control, over 15 million colors, schedules, works with Alexa and Google Home (product features).
- Year-round use (holidays, game days, everyday accent lighting).
- "The entire job is completed in one day for most homes": usable **only** with "most homes", never as a
  guarantee.
- EverLights 5-year **product** warranty: only as a product warranty, never as an installation warranty.
  Apogee's site says it is a certified EverLights dealer, but the ad brief still bars the EverLights brand
  name in ad text.
- "Veteran Owned & Operated" appears on the home page but has not been confirmed for ads.
- **Not usable:** star ratings or review counts (Google reviews could not be verified), any price, any response
  time, Omaha, installation of customer-supplied lights (owner-confirmed but not advertised).

---

## 10. Conversion tracking and phones

| Conversion action | ID | Type | Goal status |
|---|---|---|---|
| Lead \| Permanent Lights \| Form Submit \| Thank You | 7772803337 | Website (form) | **Primary**, biddable |
| Call \| Permanent Lights \| Ads \| 60s | 7773013199 | Calls from ads (call button), 60 s minimum | **Primary**, biddable |
| Call \| Permanent Lights \| Website \| 60s | 7773043879 | Calls from website, 60 s minimum | Secondary, not biddable (promote only after a real call is verified) |

All count one per click, with a 30-day window and no value. Campaign-level goals are set so only these count.

**Google Tag Manager (GTM-M545Z8T2), published version 3** (unchanged on 2026-10-05): Google tag
AW-18453077620; form conversion tag (label KOL7CImirvocEPS8jt9E) that fires only on the
`/thank-you/permanent-christmas-lights/` page **and** a dataLayer event `apg_permanent_lights_lead` carrying a
lead ID; website-call tag (label lp3jCKf5vPocEPS8jt9E) on the landing page; Conversion Linker.

**Phones (owner ruling 2026-09-17, settled):**
- **402-526-5754** is the advertising, landing-page and WhatConverts number ("GSA Traffic"). Its call flow
  records the call, then dials 402-202-7261.
- **402-202-7261** is Apogee's real line, published on the main site. It is the forwarding destination only and
  never goes in ads.
- On the main site, WhatConverts swaps 402-202-7261 for 402-783-8482 ("Website Traffic").
- LSA leads come in on 402-256-7520 and Google Business Profile leads on 402-383-2673.

**WhatConverts** (call and form tracking) captures Gravity Forms form 1 and calls on the tracked numbers. A lead
counts as qualified when the person asks for permanent Christmas light installation on the form or the call
(owner definition).

---

## 11. Known measurement defects and the developer checklist

1. **The form conversion cannot fire in Google Ads.** The trigger needs a thank-you page that did not exist on
   09-28, plus a dataLayer event that is pushed nowhere. WhatConverts still captures form leads, so leads are
   not lost, only invisible to Google Ads bidding and reporting.
2. **Developer checklist** (ready since 09-28, status not confirmed):
   - Publish the thank-you page (A01).
   - Exclude the landing page and thank-you page from caching (A02).
   - Redirect only accepted, non-spam entries to the thank-you page with a lead ID (A03).
   - Push `apg_permanent_lights_lead` with that lead ID on the thank-you page (A04).
   - Remove the three drafting notes (A05):
     - C1: "Reconfirm the current EverLights relationship and commercial availability before publication."
     - C2: "Exact consultation steps and estimate timing require client confirmation."
     - C3: "Exact installation timing and handoff process require client confirmation."
   - Keep one form instance per page (A06).
   - Capture the click ID and UTMs into hidden fields (A07).
   - Confirm where leads are delivered (A08).
3. **Calls are configured but untested.** Nobody has made a routing test call to 402-526-5754 yet (A12).
4. GTM version 3 is unchanged as of 10-05, which suggests the developer fix has not shipped. That can't be
   confirmed from this machine (see the captcha note in section 7).

---

## 12. Performance detail

### Windows

| Window | Impr | Clicks | CTR | Cost | Avg CPC | Impr. share | Lost to rank | Lost to budget | Conv. |
|---|---|---|---|---|---|---|---|---|---|
| 09-21 to 10-04 (all) | 194 | 7 | 3.6% | $46.32 | $6.62 | 80.7% | 12.4% | 6.9% | 0 |
| 09-21 to 09-27 | 52 | 3 | 5.8% | $18.69 | $6.23 | 72.2% | 9.3% | 18.5% | 0 |
| 09-28 to 10-04 | 142 | 4 | 2.8% | $27.63 | $6.91 | 85.7% | 14.3% | 0% | 0 |

Budget used: $46.32 of $230.16 available (20%). Budget is not the constraint today.

### Daily

| Date | 09-21 | 09-22 | 09-23 | 09-24 | 09-25 | 09-26 | 09-27 | 09-28 | 09-29 | 09-30 | 10-01 | 10-02 | 10-03 | 10-04 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Impr | 2 | 4 | 2 | 6 | 8 | 15 | 15 | 22 | 19 | 20 | 11 | 16 | 17 | 37 |
| Clicks | 0 | 0 | 0 | 0 | 1 | 0 | 2 | 1 | 0 | 2 | 0 | 0 | 1 | 0 |

### Where the clicks came from

| Segment | Impr | Clicks | CTR |
|---|---|---|---|
| **Top of page** | 97 | 7 | **7.2%** |
| **Other (below results)** | 97 | 0 | **0%** |
| Installation keyword, top of page | 52 | 6 | **11.5%** |
| Installation keyword, below results | 49 | 0 | 0% |
| Main keyword `[permanent christmas lights]`, top | 44 | 0 | 0% |
| Main keyword, below results | 47 | 0 | 0% |
| Mobile | 153 | 6 | 3.9% |
| Desktop | 40 | 1 | 2.5% |
| Tablet (excluded) | 1 | 0 | - |

Calls from the call button: 0 (19 call-eligible impressions). Conversions: 0 of every type.

### Leads in WhatConverts, 2026-09-21 to 10-05 (counts only)

| Source | Leads | Notes |
|---|---|---|
| **Google Ads paid search** | **0** | No google/cpc lead, no click ID, no call on 402-526-5754 |
| LSA Traffic | 11 | 8 text messages + 3 calls, all marked quotable. The service asked about is not known |
| Google Business Profile | 3 calls | 1 quotable, 1 pending, 1 not |
| Nextdoor | 1 text | not quotable |
| Direct web form on offer.apogeelawns.com root | 1 | not quotable; not an ad visitor (ads land on the slug with UTMs) |

Also present: 10 duplicates and 1 spam, which WhatConverts hides by default.

---

## 13. Research findings

### A. Is this the season? Yes, and it is just starting.

Share of the year's searches for "permanent christmas lights", averaged over the three full years from
September 2023 to August 2026 (Google Keyword Planner):

| Area | Sep | Oct | **Nov** | Dec | Jan-Aug combined |
|---|---|---|---|---|---|
| Lincoln city | 4% | 13% | **50%** | 18% | 15% |
| Service area (10 largest targets) | 5% | 13% | **49%** | 19% | 14% |
| Nebraska (shape only) | 4% | 11% | **52%** | 20% | 13% |
| United States (shape only) | 6% | 11% | **46%** | 22% | 15% |

Monthly searches in the service area for that term: Oct/Nov/Dec 2023 = 140/480/210; 2024 = 170/720/260;
2025 = 140/480/170. The installation-specific phrases are too small locally to show a reliable curve (10-70 a
month at best), but nationally they follow the same November peak.

**What this means:** the campaign launched at the very bottom of the year (September is about 4% of demand).
October is the ramp and November alone is about half the year. Daily impressions nearly tripled from the
first week (about 7 a day) to the second (about 20 a day). Judge the campaign on November, not September.

### B. Why so few impressions?

1. **Small market (structural).** About 90 searches a month on average for the main term in the whole service
   area, and about 10 a month for each installation phrase. Lincoln is a mid-sized market, and permanent
   lighting is a niche purchase.
2. **Off-season launch (temporary).** See A.
3. **Not the settings.** The ads already show for 80.7% of eligible searches; only 12.4% is lost to Ad Rank and
   6.9% to budget (the budget loss was on the first launch days only and is now 0%). Locations, language and
   schedule match the plan. The 75 negatives block no buyer searches.
4. **Omaha is excluded by decision.** It would roughly double demand, but it is a settled business decision
   (section 14).

### C. Why is CTR low (3.6%)?

1. **Position.** Half of the impressions were below the search results, where nobody clicked. At the top, CTR
   is 7.2%, and 11.5% for the installation keyword. Ad Rank is held back by:
   - the $8 CPC ceiling (Google labels the campaign "Limited by bid strategy");
   - an average Quality Score of 6 on the main term;
   - **missing assets**, which Google counts toward Ad Rank;
   - competition. Trimlight and Blingle both have Lincoln location pages, and LSA ads appear above text ads on
     many local service searches.
2. **Wrong intent on the main term.** `[permanent christmas lights]` Exact is matched by Google to close
   variants. 61 of its 89 visible impressions were close variants, nearly all product or DIY research, such as "permanent
   lights", "permanent outdoor lighting", "best permanent outdoor lights", "led permanent christmas lights" and
   "types of permanent outdoor christmas lights". It earned 0 clicks in 91 impressions, even in its 44
   top-of-page impressions. The ads speak to someone hiring an installer; these searchers are comparing
   products.
3. **Name searches matched the installation keyword.** "brilliant by night (nebraska)" (12 impressions; this
   name could not be identified as a company in a web search) and "inception permanent lighting" (1 impression;
   Inception Lighting is a permanent lighting system brand). They are navigational, so 0 clicks is expected.
4. **Small ads.** With no sitelinks, images, location or business name, the ad takes less space and looks less
   established than competitors' ads.
5. **Copy is generic.** The copy is generic: features plus "free estimate". It doesn't use the verified
   differentiators: free custom design consultation, priced by roofline footage, most homes installed in one
   day, over 15 million colors, works with Alexa and Google Home. It also says nothing to the DIY or product
   shopper.

### D. Why so few clicks (7)?

Few impressions multiplied by a 3.6% CTR. The two levers are getting more impressions to the top of the page
(assets, then possibly bids) and making the main-term ads relevant to product researchers.

### E. Why no conversions?

1. **Sample too small.** At the planned 5% conversion rate, 7 clicks should produce 0.35 leads. Zero is the
   most likely outcome.
2. **Nothing is being lost.** WhatConverts has no paid-search lead, so this is not hidden conversions.
3. **The tracking could not have recorded a form lead anyway** (section 11), so the developer fix is needed
   before November.
4. **No calls.** The call button showed 19 times and got no calls.
5. **Untested landing page.** Seven visits cannot measure it, and it still shows internal drafting notes, which
   can reduce trust.

### F. Search-term study (all 33 terms Google shows, 2026-09-21 to 10-05)

Google shows terms for 125 of the 194 impressions (64%). **All 7 clicks came from searches Google hides for
privacy (too few searches each)**, so the clicked queries themselves cannot be seen.

| Search term | Matched keyword (match) | Impr | Verdict |
|---|---|---|---|
| permanent christmas lights | permanent christmas lights (exact) | 28 | Core term; keep |
| brilliant by night nebraska | permanent christmas light installation (phrase, close variant) | 8 | Name/navigational; negative |
| permanent lighting on house | permanent christmas lights (exact, close variant) | 8 | Product research |
| permanent lights | permanent christmas lights (exact, close variant) | 7 | Product research |
| best permanent outdoor lights | permanent christmas lights (exact, close variant) | 5 | Product comparison |
| permanent christmas lights lincoln ne | installation (phrase, close variant) | 5 | **Local buyer; add as Exact** |
| brilliant by night | installation (phrase, close variant) | 4 | Name/navigational; negative |
| permanent lighting | head term (close variant) | 4 | Product research |
| permanent lights on house | head term (close variant) | 4 | Product research |
| permanent outdoor christmas lights | head term (close variant) | 4 | Product research |
| permanent outdoor lighting | head term (close variant) | 4 | Product research (also landscape lighting) |
| permanent outdoor lights | head term (close variant) | 4 | Product research |
| outdoor permanent lights | head term (close variant) | 3 | Product research |
| permanent house lights | head term (close variant) | 3 | Product research |
| best permanent christmas lights | head term (close variant) | 2 | Mixed; protected word, keep |
| cost of permanent lights on house | installation (phrase) | 2 | **Cost research; keep** |
| cost to install permanent outdoor lights | installation (phrase) | 2 | **Cost research; keep** |
| high end permanent christmas lights | head term (close variant) | 2 | Product research, premium buyer |
| how much do forever christmas lights cost | installation (phrase) | 2 | **Cost research; keep** |
| how much does it cost to have permanent christmas lights installed | installation (phrase) | 2 | **Buyer cost research; keep** |
| how much does it cost to have permanent lights installed | installation (phrase) | 2 | **Buyer cost research; keep** |
| led permanent christmas lights | head term (close variant) | 2 | Product research |
| outdoor permanent holiday lights | head term (close variant) | 2 | Product research |
| permanent christmas lights installation near me | installation (phrase) | 2 | **Local buyer; keep** |
| permanent holiday light installation near me | installation (phrase) | 2 | **Local buyer; keep** |
| permanent light for house | head term (close variant) | 2 | Product research |
| permanent lighting installation | installation (phrase) | 2 | **Buyer; keep** |
| types of permanent outdoor christmas lights | head term (close variant) | 2 | Informational; negative "types of" |
| year round christmas lights | head term (close variant) | 2 | Product research |
| inception permanent lighting | installation (phrase, close variant) | 1 | Competitor brand; negative |
| permanent christmas light installation near me | installation (phrase) | 1 | **Local buyer; keep** |
| permanent lights on house cost | installation (phrase) | 1 | **Cost research; keep** |
| permanent outdoor light | head term (close variant) | 1 | Product research |

**Grouped (visible impressions):**
- Main term itself: 28.
- Product or DIY research via the main term's close variants: 61.
- Buyer, local or cost searches via the installation keyword: 23.
- Name or competitor searches: 13.

### G. Keyword verdict

The keyword set is **right in concept**: the installation keyword is the workhorse and buyer, cost and
"near me" searches already reach it. **New keywords will not change the volume picture**, because the local
market for each additional phrase is about 10 searches a month.

| Keyword idea | Local volume (avg / Nov) | Verdict |
|---|---|---|
| `[permanent christmas lights lincoln ne]` | 10 / 50 | **Add (Exact, ad group 1).** Seen in search terms; strongest local intent |
| `[permanent christmas lights near me]` | 10 / 10 | **Add (Exact, ad group 1).** Local hiring intent |
| `[permanent lighting installation]` | 10 / 10 | Optional (Exact). Seen once; fast-growing nationally |
| `[permanent holiday light installation]` | ~10 a year | Optional (Exact); very low |
| Cost phrases ("permanent christmas lights cost", etc.) | 10 / 10 | Do not add separately: already matched, and ads have no verified price to answer them |
| "permanent outdoor lights" | 30 / 170-210 | **Do not add.** Product shoppers (same family that earns 0 clicks today) |
| "christmas light installation" | 20 / 140 | **Do not add.** Seasonal hanging, an excluded service |
| Phrase match on "permanent christmas lights" | - | **Do not add.** The search terms prove it would bring more product research (settled decision) |
| "everlights" | 10 / 20 | Low; brand use in ads is barred by the brief. Not now |

---

## 14. Settled decisions (do not reopen)

- **Omaha: EXCLUDED** (2026-09-16; "not to be reopened on search volume or website wording").
- **Phone:** 402-526-5754 is the ad, landing-page and WhatConverts number; 402-202-7261 is only the forwarding
  destination (owner ruling 2026-09-17).
- **Main term stays Exact only** until search terms justify Phrase. They currently argue against it.
- **Tablets excluded** (owner, 2026-09-28: landing pages not tablet optimized). Restoring them needs a tablet
  layout QA and a new approval.
- **Budget: $500 per month** ($16.44 a day).
- **None of the 7 old negative keyword lists may be attached** (they block the campaign's own keywords).
- **Qualified lead** = asks for permanent Christmas light installation on the form or the call.

---

## 15. Recommended plan (nothing below has been done; every change needs approval)

**Priority 1: before November (measurement). Owner and developer.**
- Ship the developer checklist in section 11 (thank-you page, lead ID, dataLayer push, remove the three
  drafting notes, cache exclusion, click-ID capture).
- Then run one controlled test form submission in GTM Preview and one routing test call to 402-526-5754.
- Without this, Google Ads cannot count a single form lead during the month that holds half the year's demand.

**Priority 2: raise Ad Rank and CTR without spending more (assets).**
- **Sitelinks (6).** Draft below. Each needs its own destination on the offer subdomain, for example section
  anchors or short pages added by the developer. Main-site pages would break the paid phone and tracking setup.

  | Sitelink | Line 1 | Line 2 |
  |---|---|---|
  | Request a Free Estimate | Priced by your roofline footage | Free, no-obligation quote |
  | How Installation Works | One-time professional install | Most homes done in one day |
  | Free Custom Design | Free consultation and design | Plan colors for your roofline |
  | App-Controlled Colors | Over 15 million colors | Works with Alexa & Google Home |
  | Permanent Lighting FAQ | Cost, warranty and upkeep | Answers before you book |
  | Homes and Businesses | Residential roofline lighting | Commercial lighting options |

- **Location assets:** link the Google Business Profile (the profile owner must accept the link).
- **Images:** upload the 8 approved crops once written commercial-use rights for the photos arrive.
- **Business name and logo:** after advertiser verification.

**Priority 3: fix the main-term ad copy for product researchers.**
Replace the weaker main-term ad (ID 825023783016, 17 impressions) with an ad that speaks to people comparing
products. Keep two ads per ad group. Every claim below is from the verified list in section 9, and every line
fits Google's limits (30 / 90 characters).

- Headlines: Permanent Christmas Lights · Pro-Installed Permanent Lights · Skip the DIY Light Kit · Free Custom
  Lighting Design · Most Homes Installed in 1 Day · Over 15 Million Colors · Works With Alexa & Google Home ·
  Priced by Your Roofline · Free, No-Obligation Quote · Lincoln Permanent Lights · Lights for Every Holiday ·
  Request a Free Estimate
- Descriptions:
  1. Permanent lights professionally installed on your eaves. Get a free, no-obligation quote.
  2. Free consultation and custom design. Most homes are installed in one day.
  3. Control over 15 million colors from the app. Works with Alexa and Google Home.
  4. Pricing is based on your roofline footage. Request a free Lincoln-area estimate.

**Priority 4: keyword and negative hygiene (small, low risk).**
- Add Exact `[permanent christmas lights lincoln ne]` and `[permanent christmas lights near me]` to ad group 1.
- Add phrase negatives "brilliant by night", "inception" and "types of".
- Approve the pending plan **APG-0928-NEG-LO** (fingerprint 58362D536336). It removes the negatives "labor only"
  and "my own lights", because Apogee does install customer-supplied lights.

**Priority 5: bids, decided around 2026-10-15 to 10-20 with real October data.**
- Keep Maximize Clicks with the $8 ceiling until the assets are live. Average CPC is already $6.62, above the
  ~$5 the planning economics can afford, and a September forecast showed a $10 ceiling adds no clicks while $12
  adds about 6.6 at roughly $19.55 each.
- If fewer than about 60% of the installation keyword's impressions are at the top of the page after the
  assets go live (today 52 of 101, 51%), the next step is **Manual CPC split by keyword**: installation keywords bid higher, where top-of-page CTR is
  11.5%; the main term bid lower, where top-of-page CTR is 0%. Maximize Clicks applies one ceiling to every
  keyword and cannot do this.
- Whether paying more per click is worth it depends on **gross profit per sold installation**, which is still
  unknown.

**Expectations for November (rough, stated assumptions):** if installation searches double to triple from
early October and the main term grows about fourfold at today's CTR, expect roughly **1-2 clicks a day in
November** (30-60 for the month), about $200-$400 of spend at today's CPC, and at the planned 5% conversion
rate **about 1.5 to 3 leads**. Better assets and copy raise this; the market size caps it. The $16.44 daily
budget (about 2.5 clicks a day at today's CPC) should cover the projected November traffic; watch for
"Limited by budget".

**Not recommended:** Broad match, Performance Max, Display, Search Partners, AI Max, raising the budget beyond
$500, "christmas light installation" (excluded service), Omaha (settled), applying Google's automatic
recommendations.

---

## 16. Open questions for the owner (only what changes the plan)

1. **Gross profit per sold installation** (or average job value and margin), and what counts as a sold job.
   This sets how much a click can be worth.
2. **Developer status** of checklist items A01-A08, especially the thank-you page, the lead ID and removal of
   the three drafting notes.
3. **Written commercial-use rights** for the four client photographs (needed for image assets).
4. **Advertiser verification** status (needed for business name and logo) and approval to link the **Google
   Business Profile** (location assets).
5. May ads say **"Veteran Owned & Operated"** and use the **EverLights** brand name? Both appear on Apogee's site
   but are not approved for ads.
6. **Local Services Ads:** does the LSA profile include permanent or holiday lighting, or only lawn care? LSA
   produced 11 quotable leads in these two weeks.

---

## 17. Reference IDs

| Object | ID |
|---|---|
| Campaign | 24257151015 |
| Budget | 15884926233 |
| Ad group 1, Permanent Light Installation | 200347713516 |
| Ad group 2, Permanent Christmas Lights Exact | 200347713556 |
| Keywords | 385217173659 (installation, phrase), 546844124143 (installation, exact), 1968954080156 (installer, phrase), 2261056242205 (installer, exact), 306097636075 (permanent christmas lights, exact) |
| RSAs | 825023783007, 825023783010 (ad group 1); 825023783013, 825023783016 (ad group 2) |
| Call asset | 422649064971 |
| Callouts | 422487159850, 422487181204, 422571032091, 422571064683, 422571064692, 422571077787 |
| Structured snippet | 422487159856 |
| Conversion actions | 7772803337 (form), 7773013199 (calls from ads), 7773043879 (website calls) |
| Google Ads tag | AW-18453077620 |
| GTM container | GTM-M545Z8T2, published version 3 |
| WhatConverts | account 119788, profile 174313 |

## 18. Sources and freshness

- Google Ads API, read-only, pulled 2026-10-05. Performance covers 2026-09-21 to 2026-10-04 (complete days);
  2026-10-05 had no data yet.
- Google Keyword Planner, 47 months (October 2022 to August 2026). Values are Google's rounded buckets, and
  related phrases share buckets, so rows are never added together.
- WhatConverts API, 2026-09-21 to 2026-10-05, counts only, no contact details.
- Published GTM container script, 2026-10-05.
- Landing page: last real-browser check 2026-09-28. The 2026-10-05 automated check was blocked by the host's
  captcha.
- Competitor references:
  - [Trimlight Lincoln](https://trimlight.com/locations/lincoln)
  - [Blingle Lincoln permanent lighting](https://www.blingle.com/lincoln-ne/areas-we-serve/meadowlane/permanent-lighting/)
  - [Inception Lighting](https://www.bizbuysell.com/start-up-business/join-the-booming-permanent-lighting-industry-with-inception-lighting/2292547)
  - "Brilliant by Night" could not be identified in a web search.
