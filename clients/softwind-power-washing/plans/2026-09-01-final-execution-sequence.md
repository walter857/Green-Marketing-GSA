# SOFTWIND POWER WASHING — FINAL EXECUTION SEQUENCE

**Account** `1521725229` · surviving campaign `24103511039` · generated 2026-09-01
**One approval at a time. Never two. Never a bundle.**

---

## The loop

```
present ONE exact action  ->  Walter approves that exact fingerprint  ->  execute only it
        ^                                                                      |
        |                                                                      v
  prepare next plan  <-  update ledger  <-  complete QA  <-  read resources back
```

**Stop after every single step.** If a write partially succeeds, stop, inventory the created
resource IDs, and propose recovery. Never blindly rerun.

**Never in one fingerprint:** measurement tests · website changes · campaign creation · ad creation
· enablement · negative keywords · bidding · pauses · budgets.

---

## Sequence

| Step | Plan | Type | Mutations | Gate before it can be presented |
|---|---|---|---:|---|
| **1** | **PLAN-R1B** | External test | **0** | **NONE — ready now** |
| 2 | PLAN-R7A | Website | 0 | Stage 1 reported |
| 3 | PLAN-R6A | Create-paused | 40 | Stage 2 deployed + QA |
| 4 | PLAN-R10A | **Enable** | 11 | Stage 3 readback QA passed, real IDs |
| 5 | PLAN-R8A | Negatives | 103 | **Stage 4 verified serving** |
| 6 | PLAN-R3C | Bidding | 1 | Stage 5 + one settled serving day |
| 7 | PLAN-R11A | Pause | 22 | Stages 4+5 verified |
| 8 | PLAN-R13 | Assets | 6 | Client inputs IN-4, IN-5 |
| 9 | PLAN-R2A | Negatives | 10 | 14 days routing data |
| 10 | PLAN-R14 | Measurement backlog | 0 | Stage 1 outcome |
| 11 | PLAN-R9A | Audiences | 12 | Volume exists |
| 12 | PLAN-R15 | Reporting | 0 | Client inputs |

> **Note the ordering swap against the ledger's stage numbers.** Enablement (ledger Stage 5) executes
> *before* routing negatives (ledger Stage 4). That is deliberate and non-negotiable: **a routing
> negative added before its owner ad group is verified serving does not route traffic, it deletes
> it.** The ledger numbers stages by topic; this file orders them by execution.

---

## Hard rules that do not bend

1. **Create paused. Always.** Enabling is a separate approval after readback QA. Never enable in the
   create operation.
2. **No routing negative before its owner group is created, approved, enabled, eligible and verified
   serving.**
3. **Campaign `24145053510` retires LAST**, after every replacement is live and verified. Do not
   pause it early — it is currently half the account's delivery.
4. **PAUSE, never delete.** Deletion requires its own destructive-action approval.
5. **No CPC number is pre-committed.** Not $12, $15, $18 or $22. Derived fresh at step 6 from
   then-current CPC distribution, impression share, Quality Score, and post-structure performance.
6. **Maximize Clicks stays** until conversion tracking is verified, qualified conversions record,
   there is enough reliable data, and lead quality can be judged. The switch to conversion-based
   bidding gets its own plan and is never combined with consolidation or RSA changes.
7. **No demographic exclusions, ever**, without qualified-lead and sold-job evidence. Women are not
   excluded. Unknown gender is not excluded.
8. **Audiences Observation only, 0% modifiers.** Never Targeting mode.
9. **No unverified claim** in any ad, asset or page — no rating, licence, guarantee, response time,
   years in business, or promotion until the client confirms it.
10. **A fingerprint identifies a plan. It does not grant permission.**

---

## Retirement order — step 7 only

1. Displaced duplicate keywords (`power washing services near me` in both campaigns)
2. Displaced ad groups — `202870585430`, `202870585590`
3. Weak replacement-tested RSAs — the 12 live in campaign A
4. Zero-volume city groups — `202870585630`, `202870585670`, `202870585830`
5. Legacy mixed-intent containers — `205713509664`, `205713509704`, `205713509744`
6. **Campaign `24145053510` — LAST**

Every pause plan must carry the exact resource ID, current status, replacement resource, evidence
the replacement is live, historical performance, risk and rollback.

---

## Enablement staging — step 4

**Stage A:** Power Washing · Pressure Washing · House Washing — the three carrying ~97% of measured
demand.
**Stage B:** Soft Washing · Driveway Pressure Washing · Patio Pressure Washing — the three micro
groups, 30/mo combined.

**This order is evidence-based, not habitual, and may change** if Stage 3 readback or Stage 2 page
results support a different one.

After each stage confirm: eligibility · impressions · Search Terms · ads serving · correct final URLs
· no policy problem · **no owner group blocked by a negative** · phone and form paths work.

---

## After each approval

Re-read identity → re-read the exact target resources → recompute the fingerprint → **stop on
mismatch** → run `validate_only` when a mutation payload exists → execute only the approved plan →
stop on partial failure → inventory resource IDs → read everything back → complete QA → update the
ledger → mark the plan complete → prepare the next exact plan → return **only** the next approval
command → stop.
