# R7 — Daily Pacing Control

**Account:** Softwind Power Washing - Live · `1521725229` · **Service:** Power Washing
**Active:** 2026-08-26 → 2026-08-31 · **Target:** $2,500 by 2026-08-31

**READ-ONLY. This process NEVER writes a budget. Every adjustment needs its own approval.**

---

## 1. The script

```bash
python scripts/softwind_pacing_check.py --label 09:00
python scripts/softwind_pacing_check.py --label 13:00
python scripts/softwind_pacing_check.py --label 17:00
python scripts/softwind_pacing_check.py --label EOD
```

`SELECT` queries only. It re-runs the identity gate on every checkpoint and aborts if the
account name, ID, manager flag or test flag does not match. Each run writes a receipt to
`clients/softwind-power-washing/receipts/pacing-<date>-<label>.json`.

**Dry-run verified 2026-08-26 10:18 — working.**

---

## 2. Mandatory checkpoints

| Time (America/New_York) | Purpose |
|---|---|
| **09:00** | Overnight spend. Set the day's expectation. Catch runaway CPC from the previous evening. |
| **13:00** | Midday. The first point at which the day's pace is meaningful. |
| **17:00** | The account's highest-demand hour. Last point at which a same-day budget request is useful. |
| **End of day** | Close the day. Recompute the required pace for tomorrow. |

On **2026-08-31** add a **21:00** checkpoint — see the final-day stop.

---

## 3. What every checkpoint reports

| Field | Source |
|---|---|
| MTD spend | `metrics.cost_micros`, Aug 1 → today |
| Today's spend | same, today only |
| Remaining budget | `2500 − MTD` |
| Remaining hours | now → 2026-09-01 00:00 America/New_York |
| Required rolling 24h pace | `remaining ÷ (remaining_hours ÷ 24)` |
| Actual rolling 24h pace | today's spend extrapolated over elapsed hours |
| Projected month-end spend | MTD + actual pace × remaining days |
| Qualified search terms | today's terms joined to the 2026-08-25 verdict file |
| Click count | MTD and today |
| Average CPC | rolling, plus every individual click CPC today |
| Lead count | `metrics.conversions` |
| Search Lost IS (budget) | per campaign |
| Search Lost IS (rank) | per campaign |
| Budget adjustment recommendation | derived — **advisory only** |

---

## 4. Emergency high-CPC stop condition

**This replaces a normal CPC cap while PLAN-B is on hold.** It is a **monitoring rule, not
an automatic mutation.** Nothing changes in the account when it fires — it raises a flag
that a human must act on.

### Triggers

| # | Condition | Threshold | Level |
|---|---|---|---|
| 1 | **Single-click CPC** | ≥ **$40.00** | INVESTIGATE |
| 2 | **Single-click CPC** | ≥ **$60.00** | **STOP** |
| 3 | **Rolling average CPC** (all charged clicks MTD) | ≥ **$38.00** | INVESTIGATE |
| 4 | **Rolling average CPC** | ≥ **$45.00** | **STOP** |
| 5 | **Rank / impression-share context** — campaign holds > 85% impression share with < 15% lost IS (rank) | — | INVESTIGATE |
| 6 | **Unqualified expensive click** — any click ≥ $40.00 whose search term is NOT verdict `KEEP` | — | **STOP** |

### Why these numbers

- **$40.00 investigate**: the account's own observed CPCs are $5.71, $22.11, $22.13,
  $26.66, $40.07, $54.49. Everything at or above $40 sits in the indefensible tail.
- **$60.00 stop**: above the worst click ever recorded ($54.49). Crossing it means
  behaviour the account has never previously exhibited.
- **$45.00 rolling stop**: 1.58× the observed $28.53 mean. Reaching it means the tail has
  become the norm.
- **Trigger 5** catches the specific failure this account is prone to: paying premium
  prices for a position it already owns. Campaign B already runs 100% top impression share.
- **Trigger 6** is the most important. A $40 click is defensible on `power washing near me`.
  It is not defensible on a cost-research or out-of-scope query. **Price alone is not the
  test — price against intent is.**

### Response

| Level | Action |
|---|---|
| **INVESTIGATE** | Record it. Check the matched search term and its verdict. Continue. If it recurs at two consecutive checkpoints, escalate. |
| **STOP** | Notify Walter immediately with the click, the search term, its verdict and the campaign. **Recommend an emergency approval to apply a CPC ceiling** — this is the circumstance in which PLAN-B (`F80E8D398811`) comes off hold early. Do not execute without that approval. |

---

## 5. Budget adjustment protocol

**No budget write is ever automatic.**

1. A checkpoint recommends a change.
2. Draft an exact budget plan: campaign ID, budget ID, current `amount_micros`, proposed
   `amount_micros`, remaining capacity, rollback value.
3. Fingerprint it with `scripts/softwind_plan_fingerprint.py`.
4. Obtain `APPROVE <PLAN-ID> <FINGERPRINT> FOR 1521725229` from Walter Correa.
5. Execute, read back, write a receipt.

Expected cadence: **at most one budget change per day**, taken at the 17:00 checkpoint.
Changing a Maximize Clicks budget more often than daily prevents the strategy from settling
and makes every subsequent reading harder to interpret.

---

## 6. Final-day stop plan — 2026-08-31

**Purpose: do not exceed the approved $2,500.**

Google can deliver up to **2× the daily budget** on any single day. Under PLAN-I1's proposed
$388.14/day combined, a single day can legitimately bill **$776.28**. On the last day of the
month that is enough to overshoot.

### Rules for 2026-08-31

| Trigger | Action |
|---|---|
| MTD ≥ **$2,300** at any checkpoint | Request approval to reduce combined budget to ≈ the exact remaining amount. |
| MTD ≥ **$2,450** at any checkpoint | **Request immediate approval to set both budgets to $1.00/day** for the remainder of the day. |
| MTD ≥ **$2,500** | Same, urgently. The month's objective is met; every further dollar is an overspend. |

Add a **21:00** checkpoint on 2026-08-31 specifically to catch late-evening delivery.

**Rollback after month end:** on 2026-09-01, restore both budgets to whatever September's
plan specifies. Do **not** leave $1.00/day budgets running into September.

**Honest caveat:** a budget reduction is not instantaneous. Google may have already served
impressions that bill shortly afterward. The final-day stop **reduces** overshoot risk; it
cannot eliminate it. If exact adherence to $2,500 matters more than maximising spend, begin
tapering at **$2,300** rather than $2,450.

---

## 7. What the checkpoints cannot tell you

- **Whether a lead actually arrived.** Conversion tracking is **UNVERIFIED** — see PLAN-A1.
  A `leads_mtd` of 0 may mean no leads, or may mean leads that were never recorded. Until
  PLAN-A2 runs, treat the lead count as unproven in both directions.
- **Whether spend was worthwhile.** The script reports cost and qualification, not revenue.
  Client economics (`average_job_revenue`, `close_rate_pct`) are `null`.
- **Whether a click was fraudulent.** Campaign A showed an **87.88% invalid click rate**
  (29 filtered vs 4 charged). Google filters these silently; the pacing script sees only
  charged clicks.

---

## 8. Daily report template

```
SOFTWIND PACING — <date> <checkpoint>

MTD spend              $____        Remaining budget    $____
Today's spend          $____        Remaining hours      ____
Required 24h pace      $____        Actual 24h pace     $____
Projected month-end    $____        Combined budget     $____/day

Clicks MTD / today     __ / __      Rolling avg CPC     $____
Leads MTD              __           Lost IS budget / rank  __% / __%

Qualified terms today:
  $____  __ impr  __ clk   "________"   [KEEP]

Emergency CPC condition:  NO TRIGGER | INVESTIGATE | STOP
  <detail>

Budget recommendation:  <no change | request $____/day | reduce to $____/day>
Approval required:      YES / NO
```

---

**READ-ONLY · NO BUDGET WRITE IS EVER AUTOMATIC · EVERY ADJUSTMENT NEEDS ITS OWN APPROVAL**
