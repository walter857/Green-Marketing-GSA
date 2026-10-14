# PLAN F — LANDING PAGE / WEBSITE FIXES

**STATUS: NOT APPROVED. DO NOT EXECUTE. NO WEBSITE CHANGE HAS BEEN MADE.**

**Account:** Softwind Power Washing - Live · `1521725229` · **Service:** Power Washing
**Drafted:** 2026-08-25 · **Re-verified in a real browser:** 2026-08-25

---

## Why this plan carries no Google Ads fingerprint

Everything below is a **WordPress / tag-manager change**, not a Google Ads API mutation.
Per the approval model these must never share a fingerprint with an Ads plan, so this
document is deliberately not fingerprinted and cannot be approved with an `APPROVE PLAN-x`
phrase.

**One related item was moved out of this document rather than bundled into it.** Repointing
the sitelinks is a Google Ads asset change, so it lives in
`2026-08-25-plan-h-sitelink-destinations.yaml` with its own fingerprint. Splitting it that
way is a small deviation from the requested file list; the alternative was either to bundle
an Ads mutation into a website plan or to drop the finding. Flagged rather than done quietly.

---

## F-1 · Remove the published authoring instruction (P0)

**Page:** `https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/`
**Re-verified 2026-08-25.** Still present in live body copy:

> "Refresh siding, driveways, patios, walkways, pavers, and concrete **without making the
> page about unrelated services**."

| | |
|---|---|
| **Why** | An internal authoring instruction was never removed. It is visible to every visitor on the page carrying **$108.99 — 64% of all account spend** and 4 of the account's 6 clicks. |
| **Evidence** | `snapshots/landing-pages-2026-08-25.json` rendered body text |
| **Exact change** | Delete the clause `without making the page about unrelated services` from the "Cleaner Exterior Surfaces" block. Suggested replacement: *"Refresh siding, driveways, patios, walkways, pavers and concrete."* |
| **Expected effect** | Removes an obvious credibility defect. No traffic or CTR lift is claimed. |
| **Risk** | None. Text deletion on a single block. |
| **Rollback** | Restore the previous block text. |
| **Approval required** | **YES** — WordPress content change, separate deployment approval. |

---

## F-2 · Resolve the evergreen countdown (P1)

**Pages affected: all nine offer landing pages verified**, including the three paused-SKAG
pages checked today.

Observed text: **"Offer Ends in — 06 DAY 02 HRS 55 MIN"**. Two different pages loaded
seconds apart both read approximately 6 days 2 hours 55 minutes, which indicates a rolling
per-visitor timer rather than a fixed deadline. The block it sits inside is headed **"Get A
Free Quote" / "FREE POWER WASHING QUOTE"** — **there is no offer to expire.**

| | |
|---|---|
| **Why** | A resetting countdown attached to a free quote is manufactured urgency. It is a Google Ads misleading-claims risk and an FTC deceptive-urgency risk, and it sits on the pages receiving 100% of paid traffic. |
| **Evidence** | `landing-pages-2026-08-25.json` and `landing-pages-paused-skags-2026-08-25.json`, `countdown_present: true` on every offer page |
| **Option A (recommended)** | Remove the countdown component from all offer pages. |
| **Option B** | Attach it to a **real, dated, client-approved offer** with a fixed end date, and let it expire genuinely. |
| **Blocking question** | Is the countdown tied to a real offer? Currently **UNKNOWN**. If the answer is no, Option A is the only defensible choice. |
| **Expected effect** | Removes a trust and compliance risk. Conversion-rate effect is genuinely unknown — fake urgency sometimes lifts short-term conversion and damages trust. No lift is claimed. |
| **Risk** | Low. Possible small short-term CVR change in either direction. |
| **Rollback** | Re-enable the component. |
| **Approval required** | **YES** — WordPress change, plus a client answer on whether a real offer exists. |

---

## F-3 · Decide on the second Google Ads tag `AW-17878095007` (P0 — investigate first)

Every offer page fires **two** Google Ads conversion IDs:

| Tag | Belongs to | Verified |
|---|---|---|
| `AW-18369652705` | **This account.** Matches `customer.conversion_tracking_setting.conversion_tracking_id` for `1521725229`. | Confirmed by API read |
| `AW-17878095007` | **UNKNOWN — a different Google Ads account.** | Owner not identified |

Re-verified today: the second tag is present on all six original offer pages **and** on all
three paused-SKAG pages (`/power-washing-soft-washing/`, `/house-washing-company/`,
`/soft-house-washing/`). It is applied site-wide on the offer subdomain, not to one page.

| | |
|---|---|
| **Why** | A second Google Ads account is receiving this client's conversion and audience signals. Depending on its configuration this can duplicate conversion credit, leak first-party data, and make any future cross-account attribution unreliable. |
| **Evidence** | `landing-pages-*.json` `trackers.google_ads_gtag` on nine of nine offer pages |
| **Exact change** | **NONE YET.** Investigation only. Identify the owner of Google Ads customer `17878095007`: check the Green Marketing MCC `3373711342` account list first, then ask the client. Determine which events it receives and whether it holds conversion actions for these pages. |
| **Expected effect** | Establishes whether duplicate or contaminating conversion signals are possible. |
| **Risk of acting too early** | **Removing it blind could break another party's legitimate reporting** — for example a previous agency's account, or the client's own separate Landscape & Masonry account. |
| **Rollback** | Not applicable at investigation stage. |
| **Approval required** | MCC lookup: **NO**. Client question: **YES**. Any tag removal: **YES**, as a separate change once ownership is known. |

**This is also action P0-A04 in PLAN-A.** Recorded in both because the investigation is
measurement work while any eventual fix is a website change.

---

## F-4 · The phone-number split (P1 — context, not a defect to fix blindly)

| Location | Number | Tracked? |
|---|---|---|
| Google Ads call asset `403335872180` | **(631) 502-7946** | Yes |
| All nine offer landing pages (`tel:` links and body copy) | **(631) 502-7946** | Yes |
| `softwindli.com` — contact-us, our-work, service-areas, reviews, services/landscaping/pressure-washing | **(631) 502-5402** | **No** |

**Do not assume the main-site number is an error.** The main site is branded *Softwind
Landscape & Masonry* — the parent business — and `(631) 502-5402` is most likely its
legitimate main line, while `(631) 502-7946` is a dedicated campaign tracking number. Both
can be correct simultaneously.

**The actual defect is not the number. It is that paid traffic is being sent to pages where
a resulting call is invisible to Google Ads and to WhatConverts.** That has already
happened: the `SITELINKS` click type recorded **1 click at $40.07 — 23% of all account
spend** — landing on `softwindli.com/services/landscaping/pressure-washing/`.

Two independent fixes, either of which closes the hole:

| Fix | System | Where |
|---|---|---|
| **(a) Stop sending paid traffic to untracked pages** | Google Ads | **PLAN-H** — recommended first, lower risk, no site change |
| **(b) Add dynamic number insertion for paid visitors on main-site pages** | Website | Below — larger change, only if the client wants main-site pages to stay as paid destinations |

### F-4b · Dynamic number insertion (only if (a) is rejected)

| | |
|---|---|
| **Why** | If main-site pages are to remain paid destinations, they must show the tracked number to paid visitors. |
| **Exact change** | Configure WhatConverts (already present site-wide) to swap `(631) 502-5402` to the tracked number for visitors arriving with a `gclid`/`gbraid` or `utm_medium=cpc`. |
| **Expected effect** | Calls from sitelink traffic become attributable. |
| **Risk** | MEDIUM. Number-swap misconfiguration can show a tracking number to organic visitors or break click-to-call on mobile. Requires testing. |
| **Rollback** | Disable the swap rule. |
| **Approval required** | **YES** — website/tag change, and WhatConverts access which is not currently held. |
| **Recommendation** | **Do PLAN-H first.** It is cheaper, safer, reversible in one edit, and it also improves message match. Revisit F-4b only if the client wants the main site kept as a paid destination. |

---

## F-5 · Review gating on `/reviews/` (P3 — compliance, client decision)

`https://softwindli.com/reviews/` presents a **HAPPY / NEUTRAL / POOR** emoji selector
before routing the reviewer.

| | |
|---|---|
| **Why** | `config/agency.yaml` sets `review_collection.prohibit_review_gating: true`. Google's own review policy also prohibits gating — routing satisfied customers to a public review form while diverting unhappy ones. |
| **Evidence** | `landing-pages-retry-2026-08-25.json` H2 "CLICK THE EMOJI THAT REPRESENTS YOUR EXPERIENCE" |
| **Secondary finding** | The reviews shown are for **fencing, tree removal and hedge trimming** — not power washing. Weak message match for a power-washing searcher. |
| **Third finding** | This page returned an **SG-Captcha interstitial** that a full browser could not clear on first attempt at either viewport. It cleared on retry. Real users usually pass it, but a paid click landing on a captcha is a genuine risk. |
| **Exact change** | Offer the review link to **all** customers without sentiment routing. |
| **Approval required** | **Client decision.** This is the client's website and their review process, outside the Google Ads account. Raised, not actioned. |
| **Interaction with PLAN-H** | If PLAN-H is approved, the `Customer Reviews` sitelink stops sending paid traffic here, which reduces the paid-traffic exposure regardless of what the client decides about gating. |

---

## Change counts — Plan F

| | |
|---|---|
| Google Ads mutations | **0** |
| Campaigns changed | 0 |
| Budgets changed | 0 |
| Bidding settings changed | 0 |
| Ad schedules changed | 0 |
| Ad groups enabled | 0 |
| Keywords changed | 0 |
| Ads changed | 0 |
| Negatives added | 0 |
| Assets changed | 0 |
| Final URLs changed | 0 |
| Conversion actions changed | 0 |
| **WordPress content edits proposed** | **2** (F-1, F-2) |
| **Tag/investigation items** | **1** (F-3, investigation only — no removal proposed) |
| **Conditional website change** | **1** (F-4b, only if PLAN-H is rejected) |
| **Client-decision items** | **1** (F-5) |

---

## Recommended order

1. **F-1** — free, zero risk, sits on 64% of spend. Do it first.
2. **F-3** — investigate only. Blocks nothing, but nothing else about tagging can be
   decided until ownership is known.
3. **F-2** — needs one client answer (is the offer real?), then remove or legitimise.
4. **F-4** — prefer **PLAN-H** over F-4b.
5. **F-5** — raise with the client; no urgency for the Ads account once PLAN-H lands.

**NOT APPROVED · DO NOT EXECUTE · NO WEBSITE CHANGE HAS BEEN MADE**
