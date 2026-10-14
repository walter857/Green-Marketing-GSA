# Pro Green Landscape Solutions — Confirmed Business Decisions

**Authoritative record.** Confirmed by the user on **2026-08-11**. This document **supersedes
conflicting assumptions** in earlier audit, continuation, or plan files. Where an earlier
document disagrees, this one wins and the earlier statement is marked corrected in place.

Evidence labels used throughout the project:
**[FRESH-API]** proven by fresh Google Ads API data ·
**[RUNTIME]** proven by public/runtime inspection ·
**[USER]** confirmed by the user ·
**[INFER]** high-confidence inference ·
**[UNVERIFIED]** not established.

---

## 1. Identity and authorization

| Field | Value | Label |
| --- | --- | --- |
| Customer-facing business name | **Pro Green Landscape Solutions** | [USER] |
| Market | **Dallas–Fort Worth, Texas** | [USER] |
| Google Ads account name | **Pro Green - Dallas - Live** | [FRESH-API] |
| Child customer ID | **8735782888** — definitive identifier | [FRESH-API] |
| Authorized manager / login ID | **3373711342** (Green Marketing), link `342593485`, **ACTIVE** | [FRESH-API] |
| WhatConverts profile | **ProGreen DFW**, Profile ID **107007** | [USER] + [RUNTIME] |

### Second manager account — resolved

**Manager `2815082755`** (link `345783752`, **ACTIVE**) is the **ClickCease invalid-click /
spam-IP protection integration**. Green Marketing authorized it. **[USER]**

**Standing rule:** Claude must **not** query, inspect, or modify that manager account. It is
recorded here only so its presence is never mistaken for an unknown intruder again. This
supersedes open item **U-A / U31**, which is now **CLOSED**.

Corroborating evidence found this run: the **account-level tracking template** points at
`monitor.clickcease.com` **[FRESH-API]** and the campaign carries **6 IP_BLOCK criteria**,
both consistent with a ClickCease deployment.

---

## 2. Market separation — Dallas is not Austin

**[USER]** Dallas and Austin are **separate operations**.

| | Approved wording |
| --- | --- |
| **Dallas landing page** | "Professional Irrigation, Sprinkler Repair & Irrigation System Repair in **Dallas, Fort Worth & Frisco, TX** and Surrounding Areas." |
| **Austin service area** (separate) | "Austin, Round Rock & Cedar Park, TX and surrounding areas." |

**Hard rule:** no Austin language, locations, phone numbers, tags, or assets may appear on the
Dallas landing page.

`AW-11240766632`, `GTM-54Q4TVXF`, and the observed **(512) 890-2716** replacement number
**strongly suggest an Austin configuration** — but **ownership remains [UNVERIFIED]**. Public
runtime evidence may be documented. **No account associated with `AW-11240766632` may be
queried.** The recommendation is to **exclude** these from the new Dallas page specification;
**nothing about them is changed during planning.**

---

## 3. Phone architecture — four distinct roles

**[USER]** confirmed, corroborated by [RUNTIME] and [FRESH-API] where noted.

| Number | Role | Evidence |
| --- | --- | --- |
| **(214) 300-9564** | **Website base / swap number** that appears in the page source | [RUNTIME] WhatConverts `Swap Number = 2143009564` |
| **(214) 301-4622** | **WhatConverts website pool tracking number** that dynamically replaces the base number | [RUNTIME] `Website Traffic` / source `All Traffic` |
| **(214) 301-3385** | **WhatConverts number used specifically as the Google Ads call asset** | [FRESH-API] asset `89872541418`; [RUNTIME] `GSAs traffic` / `Google Call Extension` |
| **(206) 890-3969** | **Forwarding destination** in the WhatConverts call flow. **The business owner answers this destination.** Unanswered calls go to **voicemail** | [RUNTIME] call flow `Incoming CF - ProGreen DFW`; role and answering party [USER] |

**Open item U-C / U24 is CLOSED** — (206) 890-3969 is the owner's answering destination. The
Seattle NPA is explained and is **not a defect**.

### Standing phone rules

1. **Preserve every phone number during planning.** No number is changed anywhere.
2. **Never hard-code (214) 301-4622 as the website's base number.** It is a pool number, not a
   base number.
3. The canonical page **renders (214) 300-9564 in its source** and lets WhatConverts DNI
   replace it with an available website-pool number.
4. All visible phone links and `tel:` values must be **valid and compatible with WhatConverts
   replacement**.
5. **Eliminate `tel:%91phone%93`** in the proposed page.
6. **(214) 301-3385 stays assigned to the Google Ads call asset.**
7. **Google website-call replacement and WhatConverts DNI must never compete to replace the
   same number.**
8. **Do not remove the `__awcc` tag** while any live ad or asset still points to a compatible
   old landing page.
9. **Do not exclude conversion action `6886103719`** until all live dependencies are removed
   **and** a tested, non-duplicating replacement exists.

> **CORRECTION — supersedes `final-audit-and-revamp-plan.md` §17 Batch 1 items 1.3 and 1.6.**
> That plan proposed excluding `6886103719` from the Conversions column and removing the
> `__awcc` tag in the *first* batch. Rules 8 and 9 **forbid that ordering.** Both actions move
> to the **post-cutover** stage. The revised sequencing is in
> `batch-1-resource-level-preview.md`.

---

## 4. Canonical landing page

**[USER]** One canonical campaign landing page.

| Field | Decision |
| --- | --- |
| **Host** | **`https://offer.progreenlandscapesolutions.com/`** |
| **Recommended slug** | **`/sprinkler-irrigation-repair/`** |
| **Recommended final URL** | **`https://offer.progreenlandscapesolutions.com/sprinkler-irrigation-repair/`** |

### Why this slug

It has to serve **all three live ad groups** — `Sprinkler Repair Near Me`,
`Irrigation Repair Near Me`, and `Sprinkler System Repair` — whose top-spending keywords are
`irrigation repair services`, `sprinkler repair services`, `sprinkler system repair`,
`sprinkler repair`, and `irrigation repair near me` **[FRESH-API]**.

- It contains **both canonical head terms** — "sprinkler … repair" and "irrigation repair" —
  so ad-to-URL relevance holds for every ad group instead of favouring one.
- It is short, human-readable, and free of filler.
- **Geo is deliberately excluded from the slug.** A `-dallas` suffix would weaken message match
  for the Fort Worth and Frisco searchers the approved positioning explicitly names, and the
  ZIP-level targeting already constrains geography far more precisely than a slug could.
- It avoids the words `offer`, `discount`, and `10-off`, which tie the URL to a promotion that
  is **expired** and must not be revived.

### In scope

Sprinkler repair · Irrigation repair · Sprinkler head repair · Valve repair

### Out of scope — must not appear

New irrigation-system installation · irrigation-system design · winterization · general
landscaping · any unrelated service

### Approved positioning

> "Professional Irrigation, Sprinkler Repair & Irrigation System Repair in Dallas, Fort Worth &
> Frisco, TX and Surrounding Areas."

Copy may be improved for readability and conversion but must retain these services and this
market intent.

---

## 5. Verified claims and prohibited language

**[USER] Verified — may be used:**

- Licensed and insured
- Free estimates
- 18-point check
- Customer satisfaction guarantee
- Same-day service is **sometimes** available

**Required wording for same-day service, verbatim:**

> **"Same-Day Service May Be Available."**

**Never promise or guarantee same-day or emergency service.**

**Prohibited on the new page and in new ad copy:**

| Item | Reason |
| --- | --- |
| **10% OFF** | **Expired promotion** [USER] |
| Installation messaging | Out of scope |
| Winterization messaging | Out of scope; also an excluded service in `client.yaml` |
| General landscaping messaging | Out of scope |
| Any unverified claim | GM policy |

> **CORRECTION.** This closes open item **U-I / Q5**. Earlier documents listed "Same Day" and
> "18 Point Check" as **[UNVERIFIED]** and flagged the "10% OFF" callout as pending. Both are
> now resolved: the 18-point check is verified, same-day is **conditional-only**, and 10% OFF
> is **expired and prohibited**.

---

## 6. Nelio A/B decision

**[USER]** Recommendation accepted: **end experiment 3619 and use one canonical page — but
not yet.**

**Confirmed safe sequence. Do not deviate.**

1. Build the new canonical page.
2. Verify phone replacement, forms, attribution fields, tags, page performance, responsive behaviour.
3. Confirm the new page can receive traffic safely.
4. Repoint all live Google Ads URLs and assets.
5. Verify the cutover.
6. **Only then** end Nelio 3619 and retire or redirect obsolete pages.

**Neither existing A/B page is canonical.** Page A (`postId 3332`) and Page B (`postId 3369`)
are both alternatives in a bidirectional ~50/50 experiment **[RUNTIME]**. Neither is promoted.

---

## 7. Geographic targeting

**[USER]** Business service areas:

Dallas · Fort Worth · Frisco · Irving · Arlington · Plano · Allen · University Park ·
Grand Prairie · Richardson · Preston Hollow · Highland Park · Lakewood · Farmers Branch ·
Balch Springs · Duncanville · Coppell · Grapevine · Vickery Meadow

**Verified service-area pages** (the only ones usable as sitelinks):

`/dfw/service-areas/` + `dallas/` · `fort-worth/` · `frisco/` · `irving/` · `arlington/` ·
`plano/` · `allen/` · `university-park/` · `grand-prairie/` · `richardson/` · `preston-hollow/`

**Standing rules:**

- The live ZIP and location criteria were **strategically selected by the owner** and are the
  **authoritative paid-advertising target set**.
- **Do not delete, replace, expand, or simplify them.**
- **Presence-based targeting only.** Never presence-or-interest.
- Searches clearly outside the approved live targeting should be excluded via negatives.
- **Do not fabricate sitelink URLs** for locations without a verified page.

The complete current inventory with criterion IDs is exported in
`batch-1-resource-level-preview.md` §7 and compared against this list. **Discrepancies are
flagged only; nothing is changed.**

---

## 8. Schedule and devices

### Schedule — already correct, no change needed

**[USER]** Intended serving hours: **Monday–Sunday, 7:00 AM – 7:00 PM Central.**

**[FRESH-API]** Account time zone verified this run: **`America/New_York`** (Eastern).

**Explicit conversion.** Central and Eastern both observe daylight saving time, so the offset is
a constant **+1 hour** year-round:

| Intended (Central) | Account time (Eastern) |
| --- | --- |
| 7:00 AM CT | **8:00 AM ET** |
| 7:00 PM CT | **8:00 PM ET** |

**[FRESH-API]** The campaign is already configured **08:00–20:00 Eastern, all seven days**
(criteria `303280`, `313280`, `323280`, `333280`, `343280`, `353280`, `363280`).

> **CORRECTION — supersedes `final-audit-and-revamp-plan.md` §17 Batch 2 item 2.5 and §13.5.**
> Those documents said the schedule was misaligned and proposed shifting it. **That was wrong.**
> It assumed intended hours of 8 AM–8 PM Central, which was never confirmed. Against the
> now-confirmed **7 AM–7 PM Central**, the existing 08:00–20:00 Eastern schedule is **exactly
> correct**. **Proposed change: none.** Open item **Q8 is CLOSED.**

### Devices

**[USER]** Mobile **enabled** · Desktop **enabled** · Tablet **excluded**.

**[FRESH-API]** Current state on campaign `20315156610`:

| Criterion | Device | `bid_modifier` set? | Value | Meaning |
| --- | --- | --- | --- | --- |
| `30000` | DESKTOP | **yes** | **0.0** | **−100% — excluded** |
| `30001` | MOBILE | no | — | no adjustment |
| `30002` | TABLET | **yes** | **0.0** | **−100% — excluded** |

**Exact required adjustment: one field on one criterion.** Set `30000` `bid_modifier` from
**0.0 → 1.0** (0% adjustment). Leave `30002` at 0.0. Leave `30001` untouched. Open item
**Q7 is CLOSED.** **Not implemented.**

---

## 9. Budget and economics

**[USER]** confirmed constraints:

| Constraint | Value |
| --- | --- |
| **Firm monthly Google Ads budget cap** | **$2,000** |
| Planning equivalent daily budget | **≈ $65.79** ($2,000 ÷ 30.4) |
| Target qualified-lead CPL | **$120** |
| Maximum cost per booked estimate | **$180** |
| Typical job revenue | **≈ $240–$300 per visit** |
| Weekly lead capacity | **≈ 20** |
| Objective | As many profitable completed jobs as capacity allows |
| Approach | **Improve the existing campaign, do not replace it** |

**Not available and not to be invented:** gross margin, close rate, booked-job rate, private
revenue detail.

**Value-based and profit-based bidding stay blocked** until reliable aggregate values or
WhatConverts opportunity/revenue updates exist.

### Current pacing **[FRESH-API]**

| Measure | Value |
| --- | --- |
| Current daily budget | **$32.50** (budget `12723712793`, STANDARD, not shared) |
| Month-to-date spend, 2026-08-01 → 08-11 (11 days) | **$369.98** |
| Observed daily average | **$33.63** |
| Projected month at this rate | **≈ $1,043** |
| Google-convention monthly equivalent | $32.50 × 30.4 = **$988** |
| **Unused headroom under the $2,000 cap** | **≈ $960–$1,010 / month** |
| Impression share MTD | **29.39%** |
| **IS lost to budget MTD** | **34.44%** |
| IS lost to rank MTD | 36.17% |

**The account is spending about half its authorized cap while losing over a third of available
impressions to budget.** Raising the daily budget toward **$65.79** stays **inside** the
confirmed $2,000 cap and is **not** a cap increase.

**Sequencing constraint:** the increase must **follow** tracking containment. Scaling spend
while conversions are unrecordable buys more untracked clicks. Recommendation and gating are in
Batch 2.

---

## 10. WhatConverts operating policy

**[USER]** WhatConverts is the **lead-detail and qualification source of truth**.

1. WhatConverts records **every** new lead.
2. Only **qualified or quotable** leads should eventually be sent to Google Ads as **primary**
   imported conversions.
3. **Spam, wrong numbers, job seekers, vendors, and out-of-area leads must never be imported**
   as qualified conversions.
4. The **business owner** reviews and qualifies leads.
5. Qualification **may take several days** — so any import must tolerate multi-day latency.
6. Current lead types: **form submissions and phone calls**.
7. Provisional duration rule: a legitimate service inquiry lasting **at least 60 seconds**.
8. **Manual WhatConverts qualification / quotable status is more reliable than duration alone.**
9. WhatConverts may eventually send revenue or sales-value updates **after testing**.
10. **Conversion Updates may only be enabled after successful testing.**
11. **Private customer-level data must never appear in reports or project files.**

### Preservation rules

- **Preserve the existing Google form-submit conversion `6886101052`. Do not delete it.**
- **Preserve the native Google call-asset conversion `6617381255`** until a tested replacement
  exists.

### The duplication rule

A call through the Google Ads call asset already reaches WhatConverts number
**(214) 301-3385**. Importing the same WhatConverts **Google Call Extension** lead would
**duplicate** the native `Calls from Ads` conversion.

> **Exclude Google Call Extension-source calls from WhatConverts conversion imports unless a
> reliable deduplication key and one-to-one reconciliation are proven.**

---

## 11. Open items closed by this decision record

| Item | Was | Now |
| --- | --- | --- |
| U-A / U31 | Unknown manager `2815082755` | **CLOSED** — ClickCease, authorized |
| U-C / U24 | Who answers (206) 890-3969 | **CLOSED** — the business owner; voicemail if unanswered |
| U-G / U33 | Is `offerdfw` staying in service | **CLOSED** — superseded by the new canonical host |
| U-I / Q5 | Claim verification | **CLOSED** — see §5 |
| Q3 | Which landing page is canonical | **CLOSED** — a **new** page; neither A nor B |
| Q7 | Were device exclusions deliberate | **CLOSED** — tablet yes, desktop no |
| Q8 | Intended Dallas hours | **CLOSED** — 7 AM–7 PM CT; already correctly configured |
| Q10 (partial) | Economics | **PARTIAL** — CPL, cost-per-estimate, job revenue, capacity confirmed; margin and close rate still unavailable |
| Q11 | Keep PMax paused | **CLOSED** — improve existing campaign; PMax stays paused |

## 12. Items still open

| Item | Status |
| --- | --- |
| **U-B / Q2** — ownership of `AW-11240766632` / `GTM-54Q4TVXF` | **[UNVERIFIED]** — Austin configuration suspected, unproven. Do not query. Do not change |
| **U-D** — WhatConverts website pool detail (pool name, assigned numbers, URL triggers, attribution rules) | **BLOCKED** — login barrier |
| **U-E / U32** — why `7717433751` and `7717433754` have never received data | **BLOCKED** — needs the WhatConverts send log |
| **U-F** — what changed on 2026-02-28 | **[UNVERIFIED]** — needs site/GTM version history |
| **U-H** — NitroPack deferral behaviour on real mobile devices | **[UNVERIFIED]** |
| Gross margin, close rate, booked-job rate | **Not available. Do not invent.** |
