# P2 — monitoring, decision gates and future dates

Anchor: **2026-09-03**, America/New_York. Live changes applied this date:
BID-2, BUD-2, KW-2. All dates below are future and **not yet performed**.

## Checkpoint schedule

| Checkpoint | Date (America/New_York) | Command | What decides |
|---|---|---|---|
| Same-day config + readback QA | **2026-09-03** — DONE | `slm_0903_baseline2.py` | Completed: readbacks 2/2, 2/2, 7/7; unchanged proof PASS |
| 24–72h serving / policy / pacing | **2026-09-04 → 2026-09-06** | `slm_0903_baseline2.py` then `slm_0903_bid_bud_evidence.py` | Campaigns still SERVING, no `LIMITED` state, no disapprovals, spend tracking under the new $56/day |
| 7-day query + spend review | **2026-09-10** | `slm_0903_performance.py` then `slm_0903_classify.py` | Wrong-service share, CPC after ceilings, click volume vs the pre-change baseline |
| 14-day CPQL / ceiling step-down | **2026-09-17** | `slm_0903_bid_bud_evidence.py` | Whether to step Patio $16→$14 and Pavers $18→$16 via a NEW plan |
| 30-day keep / modify / rollback | **2026-10-03** | full re-read + `slm_0903_preflight_exec.py` | Formal verdict on all three applied packages |
| 60-day device / schedule / audience | **2026-11-02** | `slm_0903_performance.py` | Only if the sample supports it |
| 90-day profit stability | **2026-12-02** | quality loop + CRM join | Requires SLM-Q11 answered |

## Bidding readiness gate (P2-2) — currently NOT READY

Keep Maximize Clicks with the applied ceilings. Do **not** move to Maximize
Conversions or tCPA until **all** are true:

| Condition | Status 2026-09-03 |
|---|---|
| Primary conversion architecture clean | **NO** — CONV-2 deferred; up to 3 credits per form lead remain possible |
| Attribution complete enough to optimize | **NO** — campaign/ad group/keyword blank in WhatConverts (TRACK-B) |
| Qualified leads identified consistently | **NO** — no qualified-lead definition exists (SLM-Q11) |
| ≥30 qualified conversions in the decision window | **NO** — last lead-type credit of any kind was 2026-08-22 |
| Spend and lead quality stable | **NO** — three settings changed today |
| Separate bidding plan approved | **NO** |

**Verdict: DEFERRED.** Re-evaluate no earlier than 2026-10-03.

## Escalation thresholds

Escalate immediately on: identity mismatch · tracking outage · proven duplicate
primary conversions · landing-page failure or a confirmed common-browser WAF
block on a **real** (non-headless) browser · projected spend above $2,000 ·
wrong-service visible spend above 10% after NEG-3 · any new Broad Match keyword ·
Search Partners, Display, AI Max, DSA or Final URL expansion turning on · new
disapprovals · out-of-area qualified leads from targeting drift · partial write
failure.

## Watch items carried forward

1. **`Calls from ads` vs `Calls from ads (1)`** — both primary AD_CALL actions,
   19 and 13 firing days, zero overlap ever. Not duplicates today. If the dormant
   one resumes while the other is firing, real duplication begins. Check monthly.
2. **2 ENABLED RSAs inside the PAUSED `Paver Patio Installation Near Me` group**
   (ad ids 793879597166, 795049355495). PLAN-SLM-P1A-GUARD covers the 7 keywords
   but not the ads — the executor has no ad-status branch.
3. **Duplicate Pavers ad groups** `191263597345` and `196134824089`.
4. **The 403 to desktop Chrome/Edge UAs from a headless client.** Desktop paid
   traffic converts at 3.53% all-time, so real users are evidently not blocked.
   Confirm on a real desktop browser before any WAF change.
5. **Asphalt queries can still enter via `paving company near me`** until NEG-3
   is approved. KW-2 closed the seven direct doors; the negative layer is not yet
   in place.
