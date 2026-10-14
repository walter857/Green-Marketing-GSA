# ClickUp activity update — Ambient Cooling - Live (2401959466) — 2026-09-10 (session C)

Completed work and measured results only. No forecast. No improvement reported as achieved.
Local Services Ads are out of scope for this project and are not covered here.

---

## Changed in the account today (2 operations, readback 0 failures)

**Max CPC ceilings applied to the last two uncapped campaigns.** Gas Boiler Repair and HVAC
Replacement were still running on uncapped Maximize Clicks. They now carry $25.00 and $30.00,
matching the peer campaigns that share the same cost-per-lead limits.

All five campaigns now have a ceiling: AC Repair $25, Gas Boiler Repair $25, HVAC
Installation $30, HVAC Repair $25, HVAC Replacement $30.

Combined daily budget **$421.55**, which is **$12,815.12** over 30.4 days — **$184.88 under**
the $13,000 monthly Search maximum. Budgets, bidding strategy, keywords, negatives, geo
targeting and ads were all verified unchanged.

---

## Disapproved ads — inventory complete, appeal blocked

All six paused legacy ads were pulled fresh from the API. Every one is PAUSED, DISAPPROVED,
REVIEWED, FULLY_LIMITED, topic CONSUMER_FINANCE:

- Gas Boiler Repair: 820900825428, 820900825431
- HVAC Installation: 820900825434, 820900825437
- HVAC Replacement: 820944944368, 820944944371

Their destination URLs are all HVAC service pages — nothing finance-related.

**Delivery is fully covered.** Each affected ad group holds four ads, exactly two of them
enabled and approved. No ad was re-enabled, edited or duplicated, and no ZIP-code targeting
was touched.

**The appeal could not be filed.** The API returns the policy topic but not the evidence —
it does not say which asset or destination Google actually cited. That detail and the
Dispute-decision button exist only in the Google Ads interface, and no connected browser is
available in this session. The appeal is ready to file the moment browser access is restored.

We should not select "Made changes to comply" unless the interface names a specific
finance-related item that was genuinely corrected.

---

## Gas Boiler landing page — original defect fixed, five items still open

The heading now correctly reads **"Your Gas Boiler Repair in 3 Simple Steps."** Checked in a
real browser on desktop and mobile:

**Passing (14 of 20):** page loads, boiler-specific title, H1 and all six H2s, canonical
correct, the old "HVAC Replacement" wording is gone from both the rendered page and the HTML
source, the paid number (410) 705-6354 displays and dials correctly, the organic number never
appears and is not even present in the source, Google Tag Manager is live, WhatConverts is
running, and dynamic number insertion behaves correctly under paid-click parameters.

**Still open (5):**

1. No Privacy link and no Terms link on the page — and the same is true of all five paid
   landing pages.
2. Three copies of the same form share identical element IDs (`gform_1` and 30+ others,
   each appearing three times). This can break form validation, accessibility and conversion
   tracking.
3. The form does not capture the Google click ID.
4. Form submission was not tested — there is no approved test path, and submitting on the
   live site would create a real customer lead and fire a real conversion.
5. Thank-you behaviour and one-conversion-per-submission remain unverified for the same
   reason.

Because of items 4 and 5, no boiler keyword package is being submitted for approval yet.

---

## A measurement problem worth attention

Two findings from the landing-page inspection and the WhatConverts reconciliation:

**An unexplained third phone number appears on all five paid landing pages** —
(410) 914-1456, labelled "Call Now". It is neither the paid tracking number nor the organic
number. Anyone who taps it is not being tracked as a paid lead.

**Paid-search phone calls are losing their click ID.** WhatConverts labels 21 leads as paid
("cpc"), but only 8 carry an actual click identifier. Eight of the unidentified ones are
labelled google/cpc, all are phone calls or texts, none captured a landing URL — and every
single one occurred on a day when the campaigns took paid clicks. Web form leads keep their
click ID; calls do not.

**What this means practically:** the paid-lead counts below are a floor, not the true number,
and the cost-per-lead figures are an upper bound. The real cost per lead cannot be calculated
until call tracking captures the click ID. No bid decision should rest on these numbers until
that is fixed.

---

## Where paid search actually stands

WhatConverts is connected and working — 101 leads pulled, no personal data retained, no
credentials exposed. Every lead was classified on hard evidence rather than on its label:

- 7 confirmed paid-search leads matched to a specific campaign
- 1 with a click ID that could not be matched to a click
- 4 tagged as Google Business Profile
- 89 carrying no click identifier and no tracking tags at all

Note: those 89 leads have an **unproven** channel. Earlier I described them as coming from
Business Profile and organic; that inferred a channel from a label rather than measuring it,
and I have corrected it.

Confirmed unique qualified leads from paid search, before the CPC caps existed:

| Campaign | Spend | Unique qualified leads | Cost per lead (upper bound) | Target |
|---|---|---|---|---|
| AC Repair | $3,051.47 | 3 | $1,017.16 | $150 |
| HVAC Installation | $2,914.33 | 1 | $2,914.33 | $280 |
| HVAC Repair | $1,906.86 | 1 | $1,906.86 | $250 |

Since the caps went on (Sept 5–9) the campaigns have taken only 4 valid clicks and produced
no conversions. **That is far too small a sample to judge anything** — it neither proves the
caps are working nor that they are too tight.

**Market context from Keyword Planner** (all 75 Maryland targets, exact keyword set): "ac
repair near me" shows a top-of-page bid range of $19.94–$117.36 and "hvac repair near me"
$4.72–$143.47. The $25 ceiling sits near the bottom of that range. These are market
reference points, not recommended bids.

---

## Commercial HVAC Installation — fully drafted, nothing created

Three approval packages are built and waiting. Two blockers stand in the way:

1. **The commercial landing page does not exist** —
   `offer.ambientcoolingandheating.com/commercial-hvac-installation/` returns a 404. The
   main-site version loads but shows the organic phone number, so it is not usable for paid
   traffic.
2. **The supplied launch pack was not found** — the Word document, the copy-paste file and
   the four images are not on this machine. The ad copy in the draft was written to the
   stated specification and must be reconciled against the real pack before anything is
   created.

Verified along the way: the word "commercial" is not blocked anywhere that could interfere.
The 41 shared-list entries containing "commercial" are landscaping and tree-service terms
sitting in lists attached to zero campaigns.

A developer handoff for the landing page is included in the full report, covering tracking,
the correct phone number, unique element IDs, Privacy and Terms links, and the claims that
must not be used.

---

## Headline pinning

Recommendation confirmed: **pin three keyword-forward headlines to position 1, not one.**
One pin locks the most visible slot to a single line and stops Google testing openers. Three
pins guarantee the service keyword leads while still letting Google rotate and report on
which opener wins.

The earlier AC Repair challenger has been withdrawn and replaced because it used
"Licensed & Insured," which is no longer being used in this workstream. The replacement keeps
the three-pin structure with the claim removed. No licence number or insurance certificate is
needed any more.

Worth stating plainly: the CTR difference between the two current AC Repair ads (2.77% vs
3.56%) is mostly a device-mix artefact — on desktop the "weaker" ad actually wins. Pinning is
a hypothesis we intend to test, not a proven gain.

---

## Awaiting approval

| Package | Fingerprint | Ops | What it does |
|---|---|---|---|
| AMB-0910-COMM-1 | A9173FADBA82 | 3 | Commercial HVAC ad group + 2 keywords, created paused |
| AMB-0910-RSA-ACR-2 | 1F166DE17017 | 1 | AC Repair challenger ad, 3 headlines pinned, created paused |
| AMB-0910-COMM-RSA-1 | 30312BC45992 | 2 | The two commercial ads — held until the landing page exists |
| AMB-0910-COMM-XNEG-1 | A70260017DAD | 1 | Route commercial searches away from the residential ad group — held until the commercial group is live |

Nothing above has been executed. Creating an ad never turns it on; that needs a second
approval after quality checks.

**Closed out:** the HVAC Installation CPC increase to $65 is formally rejected and should
never be revived — the evidence used to justify it came from clicks bought when no ceiling
existed, which argues against the increase rather than for it.

---

## Needs a decision

1. Restore connected-browser access so the policy appeal and the August Auction Insights
   exports can be completed.
2. Provide a staging site or approved test path so forms can be tested without creating real
   leads.
3. Build the commercial landing page and supply the launch pack.
4. Explain or remove the third phone number (410) 914-1456 on the landing pages.
5. Fix click-ID capture for phone calls — until then, cost per lead cannot be measured
   accurately.
