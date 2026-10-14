# WC-0910-OFFLINE-SOURCE-1 — WhatConverts change plan (NOT EXECUTED)

**Status:** DRAFT — analysis complete, change **not** made.
**Scope:** WhatConverts configuration only. This is outside the Google Ads approval-fingerprint
system, because no Google Ads resource changes. It needs WhatConverts admin action.
**Routing:** unchanged. Nothing was modified in this investigation.

---

## Configuration of record

| Field | Value |
|---|---|
| Profile | Ambient Cooling & Heating |
| Profile ID | 105803 |
| Tracking number | 410-705-6354 |
| Tracking-number name | **GSA Cooling Traffic** |
| Google Ads call asset | 407995613637 |
| Forwarding destination | 410-761-0932 — never public |
| Mixed-source number | 410-914-1456 — never static on paid pages |

> **Correction.** My session-D report said no WhatConverts profile named "GSA Cooling Traffic"
> exists. That was the wrong frame: *GSA Cooling Traffic is the name of the tracking number*,
> not a profile. The profile is Ambient Cooling & Heating (105803). The finding was accurate;
> the label I put on it was not.

---

## The finding

The WhatConverts UI shows **Source = Offline** for 410-705-6354. Measured against 371 lead
records (2026-06-01 → 2026-09-10), that setting is mislabeling paid-search leads **in both
directions**.

### Evidence

All 13 leads on 410-705-6354 are calls or texts. **Zero carry a GCLID.**

| Label | n | With GCLID | With landing_url |
|---|---|---|---|
| `google / cpc` | 8 | **0** | **0** |
| `google / organic` | 5 | 0 | **5** |

The split is the whole story:

- The **8 `cpc` leads have no landing URL and no click ID.** There was no web session to read.
  The `cpc` label therefore did not come from the visitor — it came from the number's own fixed
  source configuration.
- The **5 `organic` leads do have a landing URL.** Where a web session *was* matched, the real
  session source won — and it was **organic**, not cpc.

### Channel control across the whole profile

| Channel | Leads | With GCLID |
|---|---|---|
| Phone Call / Text Message | 363 | **2 (0.6%)** |
| Web Form | 8 | **6 (75%)** |

The click ID survives to web forms and dies at the call boundary. That is consistent with the
number sitting outside dynamic number insertion.

### What this causes

1. **False positives — paid over-credited.** Every call to this number is stamped `google/cpc`
   regardless of where the caller actually came from. Eight leads carry that label on zero
   evidence: no click ID, no landing URL, no session at all. A caller who found the number in
   an organic result, a bookmark, or a saved contact is counted as paid search.
2. **False negatives — paid under-credited.** Because the number is not in the DNI pool, a
   genuine paid visitor's session is never bound to the call. No GCLID means the call cannot be
   joined to a campaign, ad group, keyword or click.

**Net effect on measurement:** cost-per-qualified-lead computed from GCLID joins counts only
web-form leads. With 0.6% of calls carrying a click ID, the qualified-lead denominator is
understated, so **every CPQL figure produced for this account is an upper bound.** At the same
time the `cpc` label on those calls cannot be trusted, so they cannot simply be added back.

### Confidence and limits

This is an inference from lead-record behaviour, not a read of the configuration object. The
WhatConverts API exposes `/accounts` and `/leads`, but `/profiles` returns HTTP 400 and
`tracking-numbers`, `phone-numbers` and `numbers` all return 404 — there is no readable
number-configuration endpoint on this plan. The behavioural evidence is strong and consistent,
but it should be confirmed against the number's settings screen before the change is made.

---

## Proposed change — requires approval and WhatConverts admin access

**Change:** move 410-705-6354 (*GSA Cooling Traffic*) from **Source = Offline** to a
**web-session / dynamic number insertion** configuration, so calls inherit the visitor's real
source, medium, GCLID, GBRAID, WBRAID and UTM values.

**Do not change routing.** The forwarding destination stays 410-761-0932. No other tracking
number is touched. 410-914-1456 keeps its current configuration.

### Expected attribution effect

- Calls from paid clicks begin carrying a GCLID and become joinable to campaign, ad group and
  keyword through `click_view`.
- Calls from organic, GBP or direct visits stop being stamped `cpc`.
- Reported paid call volume will very likely **fall** at first, because the current number is
  over-labelling. **That is a correction, not a regression.**
- CPQL becomes measurable rather than an upper bound. It may move in either direction and no
  improvement is claimed.

### Preconditions

1. Confirm the current setting on the number's settings screen.
2. Confirm the commercial and existing paid landing pages capture and persist GCLID, GBRAID,
   WBRAID and UTM — see the developer handoff. DNI on a page that does not persist the click ID
   will not fully fix call attribution.
3. Confirm the number remains the only static number rendered on paid pages.

### Verification after the change

Compare a 14-settled-day window before and after: share of call leads carrying a GCLID (target:
materially above 0.6%), share labelled `cpc` **with** a click ID, and the count of calls
labelled `cpc` with no landing URL (target: falls toward zero). Report both directions honestly.

### Rollback

Restore Source = Offline on 410-705-6354. No routing or destination change is involved either
way.

### Related observation, out of scope here

Six enabled conversion actions touch calls, four of them primary: `1068114183 AD_CALL`,
`6640721230 GOOGLE_HOSTED "Clicks to call"`, `6885576934 WEBSITE_CALL`,
`7643656075 UPLOAD_CALLS "WC Calls"`, plus `6498555484` and `7389995488` as secondary. Four
primary call actions is a duplication risk for the "exactly one conversion per submission"
requirement. **No conversion-goal change is proposed here** — flagged for a separate plan.
