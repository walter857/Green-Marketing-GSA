# 02 — Executive Audit

**Pro Green - Austin - Live | 7380491929 | outdoor design & build | 2026-08-18**
**Mode: READ. No external change was made.**

---

## The number you reported is correct, and here is exactly what it is

You reported 3 conversions and a high cost per lead. The account confirms it precisely.

**Window 2026-07-19 → 2026-08-17 (the entire life of the two live campaigns, which started 2026-07-22):**

| Metric | Value |
|---|---|
| Spend | **$1,754.48** |
| Impressions | 1,899 |
| Clicks | **63** |
| Average CPC | **$27.85** |
| Conversions (Conversions column) | **3** |
| All conversions | 39 |
| Cost per conversion | **$584.83** |
| Conversion rate on clicks | 4.8% |

The 3 conversions reconcile exactly to two actions:

| Conversion action | ID | Type | Count | Campaign |
|---|---|---|---|---|
| `WC leads` | 7644242327 | UPLOAD_CLICKS (WhatConverts) | 2 | 1 Hardscape, 1 Outdoor Living |
| `Calls from ads` | 6566620547 | AD_CALL, 60s minimum | 1 | Outdoor Living |

The other 36 "all conversions" are Google-hosted local actions — 29 "Other engagements" and 6
"Website visits" from location extensions, plus 1 "Clicks to call". They are already excluded from
the Conversions column, which is correct. They are not leads.

**The single call that counted is verifiable:** the retained call log holds exactly three calls on
live campaigns — 85 seconds from a 512 area code on 2026-07-30, and two calls of 4 and 11 seconds
on 2026-08-14 that fell below the 60-second threshold and correctly did not count.

---

## Root causes, in the order they cost you money

### P0-1 — Your landing pages capture no Google click identifier, and the form-lead tag is not firing

This is the one that best explains "3 conversions" against $1,754 of spend.

All 12 live ad destinations are `offeraustin.progreenlandscapesolutions.com` pages using Gravity
Form `gform_3`. Loading `/landscape-design/` in a real browser with a synthetic
`?gclid=…&wbraid=…` shows both identifiers present in the rendered HTML — and the form's only
content hidden input is `input_6`, whose value is the literal unresolved merge tag `{Referer}`.
There is no gclid field, no gbraid, no wbraid, no UTM field, no landing-page field.

The **main site** form (`gform_1`) does it properly: the same test put the gclid into `input_15`,
`utm_medium` into `input_11` and `utm_campaign` into `input_18`. The money pages are the ones
missing it.

Then the account data closes the loop. Over the live window:

- `Progreen - Lp - Submit Lead Form` recorded **0** conversions.
- `Progreen - Lp - Phone Call Leads` recorded **0** conversions.
- `WC leads` recorded **2**.

Real leads happened. Google's own on-page measurement did not see them; only WhatConverts' upload
did. Historically `Progreen - Lp - Submit Lead Form` has 196 conversions, all from the era when the
destination was the `offeraustin.*` root — so the tag worked once and does not appear to fire on the
current sub-pages.

**Why this dominates everything else:** you cannot judge a keyword, an ad, a bid or a budget against
a conversion count that is missing most of its leads. It also blocks the entire offline path —
without a click ID on the lead, qualified-lead and sold-job upload is impossible.

I have not proven the negative. Doing so needs one controlled test submission, which is out of scope
in READ mode and is scoped as `SIT-002`.

### P0-2 — Austin budget is buying clicks to your Dallas and Houston pages

Three **account-level, automatically created, ENABLED** sitelinks serve on both live campaigns:

| Sitelink | Destination |
|---|---|
| Services In Dallas | `https://progreenlandscapesolutions.com/dfw/` |
| Services In Houston | `https://progreenlandscapesolutions.com/houston/` |
| Services In Austin | `https://progreenlandscapesolutions.com/austin/` |

All three served on live Austin ads and all three produced **zero conversions**:

| Account-level sitelink | Impressions attributed | Conversions |
|---|---|---|
| Services In Dallas | 63 | 0 |
| Services In Houston | 57 | 0 |
| Services In Austin | 142 | 0 |

Separately, `click_type = SITELINKS` shows **4 clicks costing $153.72 at a $38.43 CPC** — the
highest CPC of any click type on the account — with zero conversions. That figure covers every
sitelink, hand-built and automatic together.

**A precision note, so this is not overstated:** the exact dollars flowing to the Dallas and Houston
destinations *cannot* be isolated. Google's asset-level report attributes the whole ad's cost to
every asset that served alongside it, which is why campaign-level sitelinks in the same report sum
to $2,933.64 against total campaign spend of $1,754.48. What is certain is that the Dallas and
Houston sitelinks are serving on Austin ads, are taking clicks, and have produced nothing. Both
campaigns already carry six hand-built advertiser sitelinks, so the automatic ones add nothing but
out-of-market leakage.

The same account-level automatic asset set also serves a structured snippet reading
**"Over 20 Years Of Experience"**. I read the first-party Austin site and searched its full text
for any experience, licence, warranty, rating or project-count claim. **There is none.** That claim
is currently running on live ads and is not supported by any first-party source I can see.

### P0-3 — Every paid click is routed through a third party configured for another company

The account-level tracking template is a ClickCease redirect whose `ccpturl` parameter reads
**`offer.sehydroseed.com`** — a domain belonging to a different business, not any Pro Green host.
Neither live campaign sets its own template, so this governs **100% of paid clicks**. No ClickCease
script was found on any of the 13 destinations, so the redirect half is installed without the
on-page half.

Read the discrepancy note in `00_identity_and_source_log.md`: the first read in this session showed
a Pro Green domain here and every subsequent read showed the SE Hydroseed domain. Treat this field
as volatile and re-read it at preflight.

### P1-1 — The account runs on Eastern time while the market is Central, and the ad schedule makes it bite

The account timezone is `America/New_York`. Austin is `America/Chicago`. Both campaigns carry a
seven-day 08:00–17:00 ad schedule, which in the market means **07:00–16:00 local**.

Hour-of-day data confirms it exactly: delivery exists only in account hours 8 through 16 and is
**zero** outside them. Your ads are dark from **4pm Central onward, every day** — the whole
homeowner evening, for a service homeowners research after work.

### P1-2 — Bidding is set to Maximize Clicks with no CPC ceiling

Both campaigns use `TARGET_SPEND`. That strategy is not optimising for leads; it is buying clicks.
With no `cpc_bid_ceiling` set, it has paid $42.61, $48.15 and $55.31 for single clicks. At $27.85
average CPC, $65.78 a day buys **2.3 clicks a day across 24 ad groups**.

Google's own recommendation feed is flagging this: `MAXIMIZE_CONVERSIONS_OPT_IN` is pending on both
campaigns. **Do not apply it yet** — see the recommendation below.

### P1-3 — A protected buyer term is blocked account-wide, invisibly

The shared set `account-level negative keywords list` (11260450591) holds 295 members, 291 of them
BROAD. Because it is an `ACCOUNT_LEVEL_NEGATIVE_KEYWORDS` set it applies to every campaign, never
appears in any campaign's negative list in the UI, and reports `member_count 0`.

Inside it:

| Negative | Match | What it blocks |
|---|---|---|
| **`cost`** | BROAD | Every cost query on every campaign — "paver patio cost", "outdoor kitchen cost austin". Green Marketing policy explicitly protects `cost`. |
| `oasis` | BROAD | "backyard oasis", "backyard oasis design" |
| `keystone` | BROAD | "keystone retaining wall installation" — a mainstream wall-block brand, while Retaining Walls ad groups are live |
| `black` | BROAD | "black star gravel", "black limestone patio" — common Austin hardscape materials |
| `replacement` | BROAD | "paver replacement", "patio replacement", "driveway replacement" |

And in the `General` list, which is linked to both live campaigns:

| Negative | Match | What it blocks |
|---|---|---|
| **`hire`** | PHRASE | "hire a hardscape contractor" — protected term |
| **`emergency`** | PHRASE | protected term |
| **`shade`** | PHRASE | "shade structure", "shade sail", "patio shade cover" — direct pergola demand, while Pergolas ad groups are live |

For a design-and-build business with large tickets, cost and price queries are buyers, not
researchers. `references/verticals/hardscaping.md` says so in as many words: *"Price and cost terms
can have strong buying intent. Never negative them automatically."*

### P1-4 — Competitor brand names are absorbing live budget

Over the campaigns' life, phrase keywords pulled in local competitor searches with zero conversions:
`mcdugald steele` ($35.10), `mirror lake landscaping spring texas` ($29.17), `agc turf` ($24.51),
`ulm austin` ($24.24), `garden goat landscaping` ($19.42), `agave landscaping austin` ($18.87),
`astoria lighting austin` ($10.29), plus impression-only exposure on `waterloo turf austin`,
`cutters landscaping austin`, `ps landscapes austin`, `cedarcrest landscaping`, `casas landscaping`,
`stallion paving`, `stevens paving`, `allied outdoor solutions austin`, `clean scapes near me`,
`ground and garden austin` and `cooper and company austin`.

`asphalt paving austin tx`, `asphalt paving contractors` and `asphalt and concrete paving` are also
matching `paver installation company`. Asphalt paving is not paver installation.

### P2-1 — The budget is split evenly when the evidence says it should not be

You reported roughly $1,000 per campaign. The account shows **$32.89/day each = $65.78/day**, which
projects to **$1,999.71 per 30.4 days**. That is accurate and inside the $2,000 cap. The split is
the problem, not the total:

| Campaign | Spend | Clicks | CPC | Conv | Impr. share | Lost to **budget** | Lost to **rank** |
|---|---|---|---|---|---|---|---|
| Outdoor Living & Design | $918.94 | 41 | **$22.41** | **2** | 45.6% | **31.8%** | 22.6% |
| Hardscape Construction | $835.54 | 22 | $37.98 | 1 | 54.7% | 17.7% | **27.7%** |

Outdoor Living & Design is limited by **budget**; Hardscape Construction is limited by **rank**.
Money buys impressions in the first and cannot buy them in the second.

### P2-2 — 24 ad groups on 2.3 clicks a day

The build itself is good: one canonical theme per ad group, phrase + exact, BOFU intent, all 12
themes verified as real first-party Austin services. But 24 ad groups on this budget means
**11 of 24 ad groups took zero clicks** in 27 days, and four keywords are `RARELY_SERVED`
(`outdoor living design and build contractor`, `outdoor fire pit installation company`, each in
phrase and exact). Nothing can be learned from a theme that never serves.

### P2-3 — One RSA per ad group against a policy of two

All 24 live ad groups have exactly one enabled RSA. Expected CTR is `BELOW_AVERAGE` on every keyword
with a Quality Score, while ad relevance is `AVERAGE` or `ABOVE_AVERAGE` — the ads are on-topic but
not compelling. CTR is 3.2–3.4% despite holding 34–48% top-of-page share.

### P3-1 — Invalid click rate of 45% and 65%

Google filtered **94 invalid clicks** — 45% of Hardscape Construction's and 65% of Outdoor Living &
Design's. You were not charged for them, so this is not lost money, but a 60% combined invalid rate
is far above normal and worth watching. It may relate to the ClickCease redirect layer (P0-3). I am
flagging it as a signal, not asserting a cause.

### P3-2 — Duplicate GA4 and GTM measurement

Three GA4 properties are in play (`G-HL5EFB8XKJ`, `G-MHX199EBNJ`, and `_ga_JDFF195TRG` observed on
the main site) and two GTM containers (`GTM-54Q4TVXF` on both hosts, `GTM-PS42RNC` on the main site).
That is how two duplicate GA4 conversion actions reached the Google Ads account.

---

## What is genuinely working — do not "fix" these

| Area | Finding |
|---|---|
| **Location targeting** | All 24 approved locations resolve to exactly the 24 geo target constants both campaigns target. Presence targeting on both. No exclusions, no duplicates, no out-of-scope location. Every one of the 45 geographic rows resolves to metro 200635 (Austin). **PASS.** |
| **Landing-page market integrity** | Zero Dallas or Houston mentions or links on any of the 12 offer pages. H1s match their ad group theme exactly and name Austin. GCLID and UTMs survive to the final URL with no redirect chain. |
| **Network settings** | Search Partners off, Display off, AI Max off, DSA off, automatically created assets opted out at campaign level, Final URL expansion opted out. Matches Green Marketing defaults. |
| **Negative architecture for live keywords** | 1,876 negatives can reach the live campaigns. **Zero of them block any of the 48 live positive keywords.** The `near me` negatives in the twelve `| BOFU` ad groups are correct cross-negation steering traffic to the matching `| Near Me` ad group — not a defect. |
| **The `States` list** | 48 US state names as phrase negatives, correctly **excluding Texas**. Well built. |
| **Auto-apply** | No recommendation auto-apply subscriptions. Nothing is being applied behind your back. |
| **Phone numbers** | The differing numbers are legitimate WhatConverts dynamic insertion: `(512) 890-2716` on the landing pages (matching the Google Ads call asset), `(512) 277-9435` and `(512) 559-1315` on two loads of the same main-site page. **Not a market error. Do not standardise them.** |

---

## What "high CPL" actually is, and what it is not

It is **not** wasted spend on junk queries. Of the $851.62 of live-campaign spend visible in search
terms, only **$33.01 across 11 rows** classifies as a clear negative candidate. The existing 1,876
negatives are doing their job.

The CPL is high because of a chain:

```
$27.85 CPC  ×  $65.78/day  =  2.3 clicks/day
        ↓
   63 clicks in 30 days, spread across 24 ad groups
        ↓
   measurement that misses most leads (P0-1)
        ↓
   3 recorded conversions  →  $584.83 reported CPL
```

The reported CPL is therefore partly a **measurement artefact** and partly a **volume problem**.
Both have to be fixed, and in that order.

---

## Recommended remediation, in order

**Phase 1 — make the account safe and measurable (this approval round)**

1. Stop the Dallas and Houston sitelinks and the unverified "20 years" snippet from serving
   (`EXISTING_RESOURCES`, 2 objects).
2. Clear the mis-configured ClickCease account tracking template (`EXISTING_RESOURCES`, 1 object).
3. Fix the landing-page form so it captures gclid, gbraid, wbraid and UTMs; verify and repair the
   form-submit conversion tag (`SITE_OR_TRACKING`, web team).
4. Demote the four duplicate conversion actions (`CONVERSIONS`, 4 objects).
5. Remove the seven-day Eastern-time ad schedule (`EXISTING_RESOURCES`, 14 objects).
6. Cap CPC at $22.00 on the existing Maximize Clicks strategy (`EXISTING_RESOURCES`, 2 objects).
7. Reallocate to $39.47 / $26.31, total unchanged at $65.78/day (`BUDGET`, 2 objects).
8. Remove the eight blocking negatives; add 21 competitor, asphalt and wrong-market negatives
   scoped to the two live campaigns only (`EXISTING_RESOURCES`, 50 objects).

**Phase 2 — after 30 days of clean data (separate approval)**

9. Move to Maximize Conversions once one form-lead and one call-lead definition are producing
   **15+ conversions per 30 days**. Not before. With 3 conversions in 30 days and a duplicated
   conversion set, target CPA would optimise toward noise — `CLAUDE.md` forbids it and it is the
   wrong call on the evidence.
10. Consolidate to the themes that then show real demand, and add the second RSA per surviving ad
    group.
11. Once the form carries a click ID, stand up the offline path: qualified lead → estimate
    scheduled → sold job → revenue, uploaded through the Google Data Manager API.

**Deliberately not proposed now:** any campaign, ad-group or keyword pause. Low delivery is caused
by budget and CPC, not by ad-group quality, and pausing frees no budget because budget is held at
campaign level. Also not proposed: any change to the 24 locations, or to the one ad group pointing
at the main site — see below.

---

## Two things I deliberately did not touch

**The one live ad group pointing at the main site.** `Hardscaping | Near Me` sends traffic to
`progreenlandscapesolutions.com/austin/services/hardscaping/` while its eleven siblings use the
`offeraustin.*` offer pages. It looks like an inconsistency. But the main-site page produced
**1 conversion from 3 clicks** while the matching offer page produced **0 from 4**. The sample is
far too small to call, and Green Marketing policy says not to change a final URL merely because
another page looks more relevant. It is already an unintended A/B test. Leave it running and read it
once measurement is fixed.

**`West University, Texas, United States`.** Google returns two Texas candidates for that label:
the Neighborhood `9060226` (currently targeted) and the City `9053129` "West University Place",
which is a Houston-area city at ZIP 77005. `geo_target_constant.parent_geo_target` resolves both
only as far as Texas, so the Austin-versus-Houston question **cannot be settled from the Google Ads
API**. Delivery evidence is reassuring — all 45 geographic rows are Austin metro 200635, no Houston
— so the current target is not producing out-of-market traffic. **No geo mutation is proposed and
no guess has been made.** Reported for your confirmation, exactly as the handoff requires.

---

## Profitability: what is missing

Cost per qualified lead, cost per estimate, CAC, ROAS, gross-profit ROAS and profit after ad spend
**cannot be calculated**. The formulas are stated in `07_conversion_and_tracking_audit.md`. The
exact missing inputs are:

| Missing input | Where it must come from |
|---|---|
| Lead → qualified classification | WhatConverts or CRM; not read (PII, no authorisation in the work order) |
| Estimates scheduled and completed | CRM; none named in `client.yaml` |
| Sold jobs and revenue | CRM |
| Average job revenue, gross margin %, close rate | Client-supplied business facts; all null in `client.yaml` |
| Target CPL / CPQL / CAC | Client-supplied; all null |

Until those exist, optimise provisionally for **qualified leads**, not raw conversions. Nothing in
this audit invents a revenue, margin or close-rate figure.

## Local Services Ads

Considered and kept separate, as policy requires. LSA would need its own eligibility check,
Google Guaranteed screening, budget and measurement plan, and no Search budget should move into it
silently. It is not part of this plan.
