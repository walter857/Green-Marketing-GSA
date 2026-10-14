# POST-LAUNCH MONITORING RUNBOOK — from 2026-09-02 17:39 ET

**Account** `Softwind Power Washing - Live` / `1521725229`
**All monitoring is READ-ONLY.** `scripts/softwind_monitor.py` constructs no operation and calls
no mutate service.

## Hard rule

**Nothing here schedules or automates an external change.** No automatic negatives, budgets,
bidding, pauses or enablement. Every future write requires: fresh identity → fresh state →
exact plan → fingerprint → approval → readback QA.

## Read-only views

```
python scripts/softwind_monitor.py health        # same-day campaign health
python scripts/softwind_monitor.py terms         # daily search-term review
python scripts/softwind_monitor.py spend         # daily spend and CPC
python scripts/softwind_monitor.py invalid       # invalid clicks and rate
python scripts/softwind_monitor.py campaign      # campaign comparison + impression share
python scripts/softwind_monitor.py adgroup       # ad-group comparison
python scripts/softwind_monitor.py keyword       # keyword comparison
python scripts/softwind_monitor.py rsa           # RSA comparison
python scripts/softwind_monitor.py location      # location performance
python scripts/softwind_monitor.py device        # device performance
python scripts/softwind_monitor.py schedule      # day/hour performance
python scripts/softwind_monitor.py audience      # after observations are added
python scripts/softwind_monitor.py demo          # demographic reporting
python scripts/softwind_monitor.py quality       # Quality Score components
python scripts/softwind_monitor.py conversions   # conversion actions
python scripts/softwind_monitor.py all
```

WhatConverts reconciliation is manual until the API token is populated.

## Checkpoints

| # | When | What to report |
|---|---|---|
| 1 | **First two serving hours** | serving status, impressions, first search terms, policy status, any owner group blocked |
| 2 | **End of first serving day** | spend, valid clicks, invalid clicks, CTR, valid CPC, search terms, routing accuracy |
| 3 | **Three completed serving days** | all of the above + Search IS, Lost IS rank, Lost IS budget, first Quality Score movement |
| 4 | **Seven completed serving days** | add conversions, WhatConverts leads, qualified leads, ad-group and keyword comparison |
| 5 | **Fourteen completed serving days** | full review + revisit deferred routing negatives, universal negatives and the CPC ceiling |

At each checkpoint report: spend · valid clicks · invalid clicks · qualified search terms · CTR ·
valid CPC · conversions · WhatConverts leads · qualified leads · Search IS · Lost IS rank · Lost
IS budget · Quality Score · expected CTR · ad relevance · landing-page experience · policy status
· routing accuracy.

## Judgement rules

- **Do not declare success or failure from one click.** The account took 21 clicks in its entire
  prior life.
- Do not wait for statistical certainty when a structural or tracking defect is *proven* — those
  get fixed on evidence of the defect, not on performance data.
- A reported conversion is **not** a qualified lead while the owner-accepted thank-you exception
  stands. Reconcile every one against WhatConverts and the real lead record.

## Watch list specific to this launch

1. **Routing accuracy** — with zero ad-group negatives live, watch which ad group catches each
   query. That evidence decides PLAN-GA-LAUNCH-2A.
2. **Invalid clicks** — historically ~100% mobile and fully credited. Watch the rate, not the
   count.
3. **Quality Score** — landing-page experience read BELOW_AVERAGE pre-launch. New ads and new
   pages should move expected CTR and ad relevance first.
4. **Campaign overlap** — both campaigns are live. Watch for the same term serving in both; that
   evidence decides consolidation.
