#!/usr/bin/env python3
"""Ambient CPL control monitor. DRY-RUN / ALERT-ONLY. THIS FILE CONTAINS NO GOOGLE ADS WRITE CODE.

    python scripts/ambient_cpl_monitor.py            # morning gate on complete days + provisional exposure

What it does, every run:
  1. Re-runs scripts/ambient_0930_cpl_reconcile.py (identity gate, spend from every click type, click_view gclid
     join, call_view match, WhatConverts default+duplicate+spam, QA removed, unique genuine paid leads).
  2. Reads current campaign budgets and serving status (ENABLED campaign + ENABLED ad group + >=1 ENABLED ad).
  3. Applies the Ambient CPL rules (target $280, hard ceiling $350) to account, program, campaign and ad-group
     scopes, cumulative from the scope's first spend since 2026-08-14 (history is never reset), and writes
     clients/ambient-cooling-heating/monitoring/cpl-monitor-<date>-<HHMM>.json (+ .md summary).
  4. Proposes, never performs, pause actions on exact resource IDs.

Exit codes: 0 = no alert, 2 = alert/stop/breach present, 1 = data failure (no conclusions are written as valid).
Deployment status: NOT ACTIVE unless a scheduler, an alert recipient and an approval record say otherwise.

LIMITS (no guarantee): the zero-lead stop threshold min($300, $350 - D) is a risk-reduction heuristic, NOT a guarantee
that $350 cannot be crossed. D uses 2 x the HIGHEST budget set on the current day (a same-day cut does not lower that
day's charging limit), but Google can exceed 2x on a single day (Boiler Services spent 2.6x on 2026-09-29), cost data
lags and is restated, clicks accrue before they are reported, an alert-only run depends on a human acting in time,
API or execution failures leave exposure running, and a lead counted today can later be reclassified (spam, wrong
number), which removes headroom from scopes that already have leads. No automatic restart. No pause authority.
"""
from __future__ import annotations
import sys, json, subprocess, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ambient_0909_lib import client, q, identity_gate, E, SNAP, CLIENT_DIR  # noqa: E402

TZ = ZoneInfo("America/New_York")
TARGET, CEILING, ZERO_ALERT, ZERO_CAP = 280.0, 350.0, 280.0, 300.0
MON = CLIENT_DIR / "monitoring"


def main():
    now = datetime.datetime.now(TZ)
    today = now.date().isoformat()
    log = {"run_local": now.isoformat(), "mode": "DRY_RUN_ALERT_ONLY", "writes_performed": 0, "status": "FAILED",
           "rules": {"target_cpl": TARGET, "ceiling": CEILING, "zero_lead_alert": ZERO_ALERT, "zero_lead_cap": ZERO_CAP,
                     "zero_lead_stop": "min(cap, ceiling - D), D = 2 x highest budget set today; risk-reduction heuristic, NOT a guarantee",
                     "window": "cumulative from first spend since 2026-08-14, complete days only; today shown as PROVISIONAL"}}
    MON.mkdir(exist_ok=True)
    stamp = now.strftime("%Y-%m-%d-%H%M")
    out_json, out_md = MON / f"cpl-monitor-{stamp}.json", MON / f"cpl-monitor-{stamp}.md"
    try:
        rec_log = MON / f"cpl-monitor-{stamp}-reconcile.log"
        with rec_log.open("w", encoding="utf-8") as fh:
            rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "ambient_0930_cpl_reconcile.py"), today],
                                stdout=fh, stderr=subprocess.STDOUT, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}).returncode
        if rc != 0:
            raise RuntimeError(f"reconciliation exited {rc}; see {rec_log.name}")
        rec = json.loads((SNAP / f"cpl-reconciliation-{today}.json").read_text(encoding="utf-8"))
        c = client(); ident = identity_gate(c, verbose=False)
        camps, groups = {}, {}
        for r in q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign_budget.id, campaign_budget.amount_micros FROM campaign
                WHERE campaign.status != 'REMOVED'"""):
            camps[str(r.campaign.id)] = dict(status=E(r.campaign.status), budget=r.campaign_budget.amount_micros / 1e6,
                                             budget_id=str(r.campaign_budget.id))
        # budget history: a same-day decrease does not lower that day's charging limit, so use the day's highest budget
        try:
            for r in q(c, f"""SELECT change_event.change_resource_name, change_event.old_resource FROM change_event
                    WHERE change_event.change_date_time >= '{today} 00:00:00' AND change_event.change_date_time <= '{today} 23:59:59'
                    AND change_event.change_resource_type = 'CAMPAIGN_BUDGET' LIMIT 200"""):
                old = r.change_event.old_resource.campaign_budget.amount_micros / 1e6
                bid = r.change_event.change_resource_name.split("/")[-1]
                for v in camps.values():
                    if v["budget_id"] == bid:
                        v["budget"] = max(v["budget"], old)
        except Exception as ex:  # noqa: BLE001
            log.setdefault("warnings", []).append(f"budget history unavailable: {str(ex)[:120]}")
        for r in q(c, """SELECT campaign.id, ad_group.id, ad_group.status FROM ad_group WHERE ad_group.status != 'REMOVED'
                AND campaign.status = 'ENABLED'"""):
            groups[str(r.ad_group.id)] = dict(campaign=str(r.campaign.id), status=E(r.ad_group.status), enabled_ads=0)
        for r in q(c, """SELECT campaign.id, ad_group.id, ad_group_ad.status FROM ad_group_ad WHERE ad_group_ad.status = 'ENABLED'
                AND campaign.status = 'ENABLED' AND ad_group.status = 'ENABLED'"""):
            g = groups.get(str(r.ad_group.id))
            if g:
                g["enabled_ads"] += 1
    except Exception as ex:  # noqa: BLE001
        log["error"] = f"{type(ex).__name__}: {str(ex)[:500]}"
        out_json.write_text(json.dumps(log, indent=1), encoding="utf-8")
        print("MONITOR FAILED - no conclusions:", log["error"]); sys.exit(1)

    serving_c = {cid for cid, v in camps.items() if v["status"] == "ENABLED" and
                 any(g["campaign"] == cid and g["status"] == "ENABLED" and g["enabled_ads"] for g in groups.values())}
    findings = []
    for name, ws in rec["scopes"].items():
        cum = ws.get("launch_to_date")
        if not cum:
            continue
        prov = (ws.get("today_provisional") or {}).get("spend", 0.0)
        kind, rid = name.split(" ")[0], name.split(" ")[1] if name[:2] in ("C ", "G ") else None
        host = rid if kind == "C" else (groups.get(rid, {}).get("campaign") if kind == "G" else None)
        serving = (kind == "C" and rid in serving_c) or (kind == "G" and rid in groups and groups[rid]["status"] == "ENABLED"
                                                         and groups[rid]["enabled_ads"] > 0 and host in serving_c)
        if rid is None:  # account / program totals: serving if any campaign inside them serves
            serving = bool(serving_c) and not name.startswith("COOLING")
        D = 2 * camps.get(host, {}).get("budget", 0.0) if (serving and rid) else 0.0
        S, n = cum["spend"], cum["leads"]
        f = dict(scope=name, serving=serving, spend=S, leads=n, provisional_today=prov, max_one_day=D)
        if n:
            cpl = S / n
            f.update(cpl=round(cpl, 2), band="MET" if cpl <= TARGET else "FREEZE" if cpl <= CEILING else "BREACH",
                     headroom_to_breach=round(CEILING * n - S, 2))
            f["action"] = {"MET": "no automatic scaling", "FREEZE": "freeze expansion; investigate",
                           "BREACH": "immediate containment review"}[f["band"]]
            if not serving:
                f["action"] = "not serving; history only" + (" (breached while serving)" if f["band"] == "BREACH" else "")
            if serving and f["band"] != "BREACH" and f["headroom_to_breach"] - D < 0:
                f["alert"] = "one serving day without a lead can cross $350"
        else:
            stop = min(ZERO_CAP, CEILING - D) if serving else None
            f.update(cpl=None, band="ZERO_LEAD", stop_threshold=stop, spend_without_verified_lead=S)
            if serving:
                if S >= stop:
                    f["action"] = "STOP: propose pause"
                elif S + prov >= stop:
                    f["action"] = "STOP (intraday, provisional): propose pause for the rest of the day"
                elif S >= ZERO_ALERT or S + D >= CEILING:
                    f["action"] = "ALERT: review today"
                else:
                    f["action"] = "watch"
            else:
                f["action"] = "not serving; history only" + ("; exceeded $350 while serving" if S > CEILING else "")
        if serving and kind == "G" and str(f.get("action", "")).startswith("STOP"):
            f["proposed_mutation"] = f"PAUSE ad_group {rid} (requires an approved plan)"
        if serving and kind == "C" and (f.get("band") == "BREACH" or str(f.get("action", "")).startswith("STOP")):
            f["proposed_mutation"] = "containment review: " + ", ".join(
                f"{g}" for g, v in groups.items() if v["campaign"] == rid and v["status"] == "ENABLED" and v["enabled_ads"])
        findings.append(f)
    log.update(status="OK", identity={k: ident[k] for k in ("customer_id", "descriptive_name")}, findings=findings,
               reconciliation_file=f"cpl-reconciliation-{today}.json",
               data_freshness={"complete_days_through": rec["windows"]["launch_to_date"][1], "provisional_day": today})
    out_json.write_text(json.dumps(log, indent=1), encoding="utf-8")
    hot = [f for f in findings if f.get("band") == "BREACH" or str(f.get("action", "")).startswith(("STOP", "ALERT")) or f.get("alert")]
    lines = [f"# Ambient CPL monitor {stamp} (DRY RUN, alert-only, 0 writes, NOT ACTIVE)", "",
             "Thresholds are risk-reduction heuristics, not a guarantee against crossing $350 (see LIMITS in the script).", "",
             f"Complete days through {log['data_freshness']['complete_days_through']}; {today} is PROVISIONAL.", "",
             "| Scope | Serving | Spend | Leads | CPL | Band / action | Provisional today | Proposed |", "|---|---|---|---|---|---|---|---|"]
    for f in sorted(findings, key=lambda x: (not x["serving"], x["scope"])):
        lines.append(f"| {f['scope'][:60]} | {'yes' if f['serving'] else 'no'} | ${f['spend']:,.2f} | {f['leads']} | "
                     f"{'$%.0f' % f['cpl'] if f['cpl'] else 'undefined'} | {f.get('band')} / {f.get('action')}{' / ' + f['alert'] if f.get('alert') else ''} | "
                     f"${f['provisional_today']:,.2f} | {f.get('proposed_mutation', '')} |")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n{len(hot)} scope(s) need attention. Log: {out_json.name}")
    sys.exit(2 if hot else 0)


if __name__ == "__main__":
    main()
