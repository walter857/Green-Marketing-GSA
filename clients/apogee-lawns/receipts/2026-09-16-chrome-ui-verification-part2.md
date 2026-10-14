# Chrome UI verification, part 2 — 2026-09-16

Continues `2026-09-16-chrome-ui-verification.md`. **Read-only. No mutation, no form
submitted, no setting changed.**

---

## 1. GTM container inventory — COMPLETE (Phase 1 items 3 and 4)

Account **6377231045** · Container **264326944** · Workspace **2**

| Item | Observed |
|---|---|
| Account name | **Apogee Lawns** |
| Container | **apogeelawns.com** |
| Container ID | **GTM-M545Z8T2** — exact match |
| Type | Web |
| **Tags** | **0** — "You don't have any tags yet." |
| **Triggers** | **0** — "You don't have any triggers yet." |
| **Built-in variables** | **0 enabled** — "You don't have any built-in variables enabled yet." |
| **User-defined variables** | **0** — "You don't have any user-defined variables yet." |
| **Workspace Changes** | **0** |
| **Pending Changes** | **0 Modified, 0 Added, 0 Deleted** — "You haven't made any changes yet" |
| Folders / Templates | not populated (container is at onboarding state) |
| **Container quality** | **"No Recent Data — No data has been received from your tag. Complete your tag installation."** |
| Overview state | "Welcome to Google Tag Manager … Install Tag Manager" |

**This independently confirms BLK-004 from inside GTM itself**: the container has never
received a single hit, so `GTM-M545Z8T2` is not installed on apogeelawns.com. The earlier
finding was reached by HTTP inspection; this is the server-side counterpart.

**Consequence for the GTM workspace plan:** even the built-in variables are off. The
workspace plan must explicitly enable **Page URL, Page Hostname, Page Path and Referrer**
before any trigger can reference them.

**Versions: not directly opened.** Two URL patterns for the versions view both redirected
to the GTM home list. Not treated as proven. Container state (0 tags, 0 triggers,
0 variables, 0 workspace changes, no data ever received) is consistent with no published
version, but that is inference, not observation, and is flagged as such.

## 2. Google Ads account settings — full read

`Admin → Account settings`

| Setting | Observed | Note |
|---|---|---|
| Account name | **Apogee Lawns LLC - Live** | matches |
| Account status | **Active** | |
| Time zone | **(GMT-05:00) Central Time** | matches America/Chicago |
| **Auto-tagging** | **Yes** | required for GCLID |
| Tracking | **No options set** | no account tracking template |
| **Call ads** | **Call reporting on** | confirms the API reading |
| Negative keywords | **None** | no account-level negatives |
| IP exclusions | **No exclusions set** | |
| **Auto-apply** | **Turned off** | no auto-applied recommendations |
| Lead form ads terms | **Not accepted yet** | correct — not in scope |
| Data protection contacts | **None** (warning icon) | minor hygiene item |
| Third-party measurement | None | |
| Customer Match | Smart bidding and optimized targeting on, conversion-based lists off | |
| High-engagement ads | Turned off | |

**Call recording: STILL NOT OBSERVED.** The "Call ads" row summarises only as "Call
reporting on". Expanding it did not surface a recording control in the extracted text.
Most likely the recording toggle does not render until a call asset or call conversion
action exists — both are currently zero. **Not claimed as verified.** It stays on the
enablement checklist and must be confirmed visually before launch.

## 3. Advertiser verification — INCOMPLETE, and it is a launch-timing risk

`Admin → Policy → Account`

Outstanding tasks shown:

- **"Confirm if you plan to run EU political ads"** — presented under "Complete the tasks"
  (EU regulation requires Google to ask), ~1 min
- "Answer a few questions about your organization" — ~5 mins
- "Provide your Dun & Bradstreet info" — ~5 mins
- "Confirm your affiliation with the organization" — ~5 mins
- "Answer a question about who pays for your ads" — ~1 min, marked Optional

Google's own guidance on the page: **"Review time: 1 day to 10 days"** and
**"Recommendation: Start early to avoid delays."**

**Timing consequence.** The planned start date of 2026-09-21 is five days away. If
verification is triggered and lands at the slow end of Google's stated range, it alone can
push delivery past the planned start. This is independent of the landing page, GTM and
billing blockers.

Every one of these tasks is an identity or organization attestation. **Claude will not
complete any of them.** They require the authorized owner.

### Useful corroboration on the billing question

The page states: **"Your ad disclosure now shows: Ads funded by Apogee Lawns LLC."**

Google already associates this account with **Apogee Lawns LLC** as the funding entity.
That strengthens the concern raised in part 1: the billing signup screen pre-selected the
**Stockdale Outdoors (4984-3370-4007)** payments profile, and Stockdale Outdoors is a
separate Green Marketing client with its own GTM container (`GTM-TKJW3NNL`,
stockdaleoutdoors.com). The owner has since said the payment profile was "updated to
apogee's", but the formal billing instruction in the assignment was returned as an
unfilled `[CHOOSE ONE]` placeholder, so the authorized profile is **not** recorded as
confirmed.

## 4. Still outstanding after part 2

| Item | Status |
|---|---|
| GTM published versions | Not observed — versions URL redirects to home |
| Call recording on/off | Not observed — control likely hidden until a call asset exists |
| Billing restoration | Owner-only; no active billing |
| Advertiser verification | Owner-only; 1–10 day review once started |
| Scope approver name | **Still `[FULL NAME]`** — blocks every write |
| Live-answer hours, phone ownership, ring destination, answerer | Still placeholders |
| Average gross profit per sold project | TBD pending client confirmation |
