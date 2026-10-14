#!/usr/bin/env python3
"""Runbook + monitoring script + approval queue + deliverables README/summary + ZIP."""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "clients/softwind-power-washing"
DEL = C / "deliverables/2026-09-02-final-launch-package"
DEL.mkdir(parents=True, exist_ok=True)
(C / "runbooks").mkdir(exist_ok=True)

# ---------------- monitoring script ----------------
(ROOT / "scripts/softwind_monitor.py").write_text('''#!/usr/bin/env python3
"""Softwind post-launch monitor. READ-ONLY. Constructs no operation, calls no mutate service.

Usage:  python scripts/softwind_monitor.py [health|terms|spend|invalid|campaign|adgroup|
        keyword|rsa|location|device|schedule|audience|demo|quality|all]
"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
D = "segments.date BETWEEN '2026-09-02' AND '2026-12-31'"
Q = {
 "health": f"""SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
        metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
        FROM campaign WHERE {D} AND campaign.status!='REMOVED'""",
 "terms": f"""SELECT search_term_view.search_term, ad_group.name,
        segments.search_term_match_type, metrics.impressions, metrics.clicks,
        metrics.cost_micros, metrics.conversions FROM search_term_view WHERE {D}""",
 "spend": f"""SELECT segments.date, campaign.name, metrics.cost_micros, metrics.clicks,
        metrics.average_cpc FROM campaign WHERE {D} AND campaign.status!='REMOVED'""",
 "invalid": f"""SELECT campaign.name, metrics.clicks, metrics.invalid_clicks,
        metrics.invalid_click_rate, metrics.cost_micros FROM campaign
        WHERE {D} AND campaign.status!='REMOVED'""",
 "campaign": f"""SELECT campaign.name, metrics.impressions, metrics.clicks, metrics.ctr,
        metrics.average_cpc, metrics.conversions, metrics.search_impression_share,
        metrics.search_rank_lost_impression_share, metrics.search_budget_lost_impression_share
        FROM campaign WHERE {D} AND campaign.status!='REMOVED'""",
 "adgroup": f"""SELECT ad_group.name, metrics.impressions, metrics.clicks, metrics.ctr,
        metrics.average_cpc, metrics.conversions FROM ad_group
        WHERE {D} AND ad_group.status='ENABLED'""",
 "keyword": f"""SELECT ad_group.name, ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type, metrics.impressions, metrics.clicks,
        metrics.average_cpc, metrics.conversions FROM keyword_view WHERE {D}""",
 "rsa": f"""SELECT ad_group.name, ad_group_ad.ad.id, metrics.impressions, metrics.clicks,
        metrics.ctr, metrics.conversions FROM ad_group_ad
        WHERE {D} AND ad_group_ad.status='ENABLED'""",
 "location": f"""SELECT campaign.name, metrics.impressions, metrics.clicks, metrics.cost_micros
        FROM location_view WHERE {D}""",
 "device": f"""SELECT segments.device, metrics.impressions, metrics.clicks, metrics.cost_micros,
        metrics.conversions FROM campaign WHERE {D} AND campaign.status!='REMOVED'""",
 "schedule": f"""SELECT segments.day_of_week, segments.hour, metrics.clicks, metrics.cost_micros
        FROM campaign WHERE {D} AND campaign.status!='REMOVED'""",
 "audience": f"""SELECT campaign.name, metrics.impressions, metrics.clicks
        FROM campaign_audience_view WHERE {D}""",
 "demo": f"""SELECT ad_group.name, metrics.impressions, metrics.clicks, metrics.cost_micros
        FROM gender_view WHERE {D}""",
 "quality": """SELECT ad_group.name, ad_group_criterion.keyword.text,
        ad_group_criterion.quality_info.quality_score,
        ad_group_criterion.quality_info.search_predicted_ctr,
        ad_group_criterion.quality_info.creative_quality_score,
        ad_group_criterion.quality_info.post_click_quality_score
        FROM keyword_view WHERE ad_group_criterion.quality_info.quality_score > 0""",
 "conversions": """SELECT conversion_action.name, metrics.all_conversions
        FROM conversion_action WHERE segments.date BETWEEN '2026-09-02' AND '2026-12-31'""",
}

def main() -> int:
    what = sys.argv[1] if len(sys.argv) > 1 else "health"
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    keys = list(Q) if what == "all" else [what]
    for k in keys:
        if k not in Q:
            print(f"unknown view: {k}. options: {', '.join(Q)}"); return 2
        print(f"\\n===== {k.upper()} =====")
        try:
            for r in svc.search(customer_id=cid, query=Q[k]):
                print(" ", r)
        except Exception as e:
            print("  ERROR:", str(e)[:200])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")

(C / "runbooks/2026-09-02-post-launch-monitoring.md").write_text("""# POST-LAUNCH MONITORING RUNBOOK — from 2026-09-02 17:39 ET

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
""", encoding="utf-8")

# ---------------- approval queue ----------------
(C / "plans/2026-09-02-future-approval-queue.md").write_text("""# FUTURE APPROVAL QUEUE — 2026-09-02

**One approval at a time, in dependency order.** An approval command appears **only** where the
plan has exact current resource IDs, known current and proposed values, non-zero executable
actions, a passing `validate_only` where applicable, a current fingerprint, and no unresolved
dependency.

## Ready now

### 1. PLAN-GA-LAUNCH-2A — Final ad-group routing negatives

| | |
|---|---|
| Purpose | Enforce one-owner-per-keyword across the six live ad groups |
| Status | **APPROVAL READY** |
| Dependency | **MET** — all six owner ad groups enabled and verified 2026-09-02 17:39 |
| Actions / Objects / Mutations | **103 / 103 / 103** |
| Fingerprint | **`4A82B3B7C1EA`** |
| `validate_only` | PASS — 103 create operations validated, 0 created |
| Risk | LOW — every criterion collision-tested against the live inventory; 0 self-blocking |
| Rollback | Remove the added ad-group negative criteria |
| Earliest safe execution | **Now.** Owner groups are live. |

```
APPROVE PLAN-GA-LAUNCH-2A 4A82B3B7C1EA FOR 1521725229
```

> **A judgement call worth your attention.** These 103 negatives are safe and validated, but the
> six ad groups have not yet served a single impression. Waiting for real routing evidence would
> tell us which negatives are actually needed rather than which are theoretically correct. The
> plan is ready whenever you want it; my recommendation is to let it run a few days first.

## Blocked or deferred — no approval command

| # | Plan | Purpose | Status | Dependency | Actions | Fingerprint | Earliest safe point |
|---|---|---|---|---|---:|---|---|
| 2 | **PLAN-GA-NEG-1** | Universal traffic-quality negatives | DRAFT | 5 candidates all have 0 clicks and $0 spend | 5 | none | 14-day checkpoint |
| 3 | **PLAN-GA-BID-1** | Evidence-based CPC ceiling | BLOCKED | needs post-launch billable clicks + landing-page fix | 2 | none | 3-day checkpoint at the earliest |
| 4 | **PLAN-R7A1-GTM** | GTM form-measurement repair | BLOCKED | no Tag Manager credential | ~5 | none | when GTM read access exists |
| 5 | **PLAN-R7A2-WHATCONVERTS** | DNI and call attribution | BLOCKED | `WHATCONVERTS_API_TOKEN` is empty | ~6 | none | when WhatConverts read access exists |
| 6 | **PLAN-GA-ASSET-1** | Asset completion | BLOCKED | business identity, rights-cleared images, answered hours | 6 | none | when client inputs arrive |
| 7 | **PLAN-GA-AUD-1** | Audience observations | DEFERRED | all lists below the ~1,000 Search minimum (largest is 210) | 3 | none | when a list crosses the threshold |
| 8 | **PLAN-GA-RETIRE-1** | Legacy retirement, campaign `24145053510` last | BLOCKED | replacements must serve and be verified first | ~30 | none | after 7–14 days of clean serving |
| 9 | **PLAN-R7A4-CROSS-ACCOUNT** | Sibling tag scoping | BLOCKED | needs a separate sibling-account work order and approval | ~2 | none | after that work order exists |
| 10 | **Post-repair form test** | Re-verify conversion after website fixes | BLOCKED | website P0 work must ship | ~8 | none | after ClickUp P0 tasks land |

## Not fingerprinted, by rule

Developer tickets · provisional plans · blocked plans · placeholder plans · zero-action plans ·
cross-account actions without their own work order. Superseded: `PLAN-GA-LAUNCH-2`,
`PLAN-GA-LAUNCH-3`, `PLAN-GA-LAUNCH-4` (replaced by 2A / 3A / RETIRE-1). Void: `D04DBC638033`.
""", encoding="utf-8")
print("runbook + queue written")
