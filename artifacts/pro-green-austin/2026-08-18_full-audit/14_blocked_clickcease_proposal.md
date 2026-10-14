# 14 — BLK-001 Regenerated: ClickCease `ccpturl`

**Pro Green - Austin - Live | `7380491929`**
**Status: STILL BLOCKED. No fingerprint. Not approvable. Nothing was executed.**
**ClickCease remains active and was never queried, disabled or modified.**

---

## 1. Why this document exists

`BLK-001` in `11_exact_change_plan.yaml` recorded a `current_state_verbatim` that is **no longer
correct**. The preflight drift check caught it before execution. The executed plan file is left
frozen as the record of what was approved; this document supersedes `BLK-001` only.

---

## 2. The field is oscillating — this is the new finding

`customer.tracking_url_template` has now been observed in **two different states across three
distinct periods**. Each reading was stable across consecutive reads at the time.

| When | `ccpturl` value | Reads |
|---|---|---|
| 2026-08-18, first read of the engagement | `progreenlandscapesolutions.com` | 1 |
| 2026-08-18 → 2026-08-19 | `offer.sehydroseed.com` | 5, identical SHA-256 each time |
| 2026-08-19, preflight and after | **`progreenlandscapesolutions.com`** | 3, identical SHA-256 each time |

**I owe you a correction.** In `00_identity_and_source_log.md` I recorded that first reading as a
possible misread on my part, because five subsequent reads disagreed with it. That was the wrong
conclusion. The first reading was accurate. The field genuinely moves back and forth, and every
value is stable while it lasts.

Everything else in the template is constant across all readings — same tracker host, same
`id=Y6qzID4E9cPYCj`, same twelve macros, same parameter order. **Only `ccpturl` changes**: 11 of 12
parameters were identical between the last two states.

`change_event` shows no rows for this in the window, which is expected — it does not cover
customer-level fields — so the API cannot tell us who or what is writing it.

---

## 3. What this changes about the recommendation

The earlier proposal assumed a one-time hand correction in Google Ads would hold. **The oscillation
makes that assumption unsafe.** A field that flips between two values without any Google Ads change
event is characteristic of an **external system writing it on a schedule** — and ClickCease's Google
Ads integration does exactly that: it maintains the account tracking template so clicks route
through its tracker.

The most likely reading of the evidence, stated as a hypothesis and not a fact:

> One ClickCease configuration is writing `progreenlandscapesolutions.com` and another is writing
> `offer.sehydroseed.com` to the same Google Ads account, so the two take turns.

If that is right, then **editing `ccpturl` inside Google Ads would be overwritten** — possibly
within hours — and we would have spent an approval on a change that does not hold.

Note also that **neither observed value is the landing-page host**. All 12 live ad destinations are
on `offeraustin.progreenlandscapesolutions.com`, which has never appeared in this field.

### Revised recommendation

**The fix belongs in ClickCease, not in Google Ads.** Specifically:

1. In the ClickCease account, confirm which domain is registered for Pro Green Austin, and confirm
   whether any SE Hydroseed property is pointed at Google Ads customer `7380491929`.
2. Correct the configuration there so ClickCease writes a single, correct `ccpturl`.
3. Then re-read `customer.tracking_url_template` over several days to confirm it has settled.
4. Only if it does **not** settle should a Google Ads-side edit be considered, and it would need
   its own fingerprint at that time.

**Green Marketing should perform steps 1 and 2 inside ClickCease.** I was instructed not to query,
disable or modify the ClickCease manager, and I have not.

---

## 4. The proposal, regenerated against today's value

Retained only for the case where a Google Ads-side edit is eventually judged correct.

**Current value, verified three times on 2026-08-19:**

```
https://monitor.clickcease.com/tracker/tracker.aspx?id=Y6qzID4E9cPYCj&adpos={adposition}
&locphisical={loc_physical_ms}&locinterest={loc_interest_ms}&adgrp={adgroupid}&kw={keyword}
&nw={network}&url={lpurl}&cpn={campaignid}&device={device}&ccpturl=progreenlandscapesolutions.com
&pl={placement}
```

**Proposed value — one parameter changed, everything else byte-identical:**

```
… &device={device}&ccpturl=offeraustin.progreenlandscapesolutions.com&pl={placement}
```

| | |
|---|---|
| Field mask | `tracking_url_template` |
| Only difference | `ccpturl=progreenlandscapesolutions.com` → `ccpturl=offeraustin.progreenlandscapesolutions.com` |
| Preserved unchanged | tracker host, `id=Y6qzID4E9cPYCj`, `{adposition}`, `{loc_physical_ms}`, `{loc_interest_ms}`, `{adgroupid}`, `{keyword}`, `{network}`, `{lpurl}`, `{campaignid}`, `{device}`, `{placement}`, parameter order |
| Proposed value verified? | **No.** Still a proposed value only. |
| Object count | 1 |
| Rollback | restore the current value recorded above |

---

## 5. Why it stays blocked — now two reasons

1. **The correct domain is still unverified.** `ccpturl` must match what is registered inside
   ClickCease. That cannot be read from Google Ads and must not be guessed.
2. **New: a Google Ads-side edit may not hold.** The field is under active external control, so a
   manual correction risks being reverted without notice.

**Unblock conditions, both required:**

- Green Marketing confirms from the ClickCease account the exact domain registered for Pro Green
  Austin, and whether an SE Hydroseed property is also pointed at customer `7380491929`.
- The field is observed to be stable for at least 72 hours after any ClickCease-side correction.

Only then would this be regenerated with a verified value and issued a fingerprint.

---

## 6. Impact while it stays open

Every Austin paid click still routes through `monitor.clickcease.com` with a `ccpturl` that names
either the Pro Green root domain or another company's domain, neither of which is the landing-page
host. ClickCease's protection and reporting for this account cannot be relied on until it is
resolved.

**This does not affect anything executed on 2026-08-19.** No approved action touched this field, the
readback confirms we did not write it, and the three applied subplans are independent of it.

**NO CHANGE WAS MADE TO THE CLICKCEASE CONFIGURATION OR TO
`customer.tracking_url_template`.**
