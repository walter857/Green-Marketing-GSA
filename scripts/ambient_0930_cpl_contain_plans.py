#!/usr/bin/env python3
"""Ambient | 2026-09-30 | CPL containment plans under the client CPL requirement (target $280, ceiling $350).

    python ambient_0930_cpl_contain_plans.py plan
    python ambient_0930_cpl_contain_plans.py execute --plan AMB-0930-CPL-CONTAIN-1 --fp <FP>
    python ambient_0930_cpl_contain_plans.py execute --plan AMB-0930-CPL-CONTAIN-2 --fp <FP>

CONTAIN-1 (recommended now): pause ad group 204129717007 'SKAG | Heating Repair' and lower campaign
24257819463's daily budget $85 -> $30. Nothing else in the campaign is paused.
CONTAIN-2 (standby): pause ad groups 204129718047 'SKAG | Boiler Repair' and 202339087594 'SKAG | Gas Boiler Repair'.
Executable ONLY when a fresh reconciliation shows its trigger (Boiler Services campaign CPL > $350 on complete
days, or Boiler Repair zero-lead spend >= $260). Boiler Replacement is not touched.
Hashed content is rebuilt from fresh state at execution; drift changes the fingerprint and the run refuses.
Each plan = one atomic mutate, partial_failure=False, followed by readback. Nothing is enabled by these plans.
"""
from __future__ import annotations
import sys, json, argparse, datetime, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS, SNAP, CLIENT_DIR, ROOT  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets, assert_target_matches  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402
import yaml  # noqa: E402

TARGET = {"child_customer_id": CID, "exact_child_account_name": EXACT_NAME}
REPAIR_CAMP, HR_AG = "24257819463", "204129717007"
KEEP_REPAIR = ["199797580706", "204129717247", "204129717287", "204129717087"]  # Furnace, Gas Furnace, Electric Furnace, No Heat
BOILER_CAMP, BR_AG, GBR_AG, BREPL_AG = "24132507744", "204129718047", "202339087594", "204129718207"
WO_HR = CLIENT_DIR / "work-orders" / "work-order-heating-repair-cpl-containment-2026-09-30.yaml"
WO_PROG = CLIENT_DIR / "work-orders" / "work-order-gas-boiler-repair-cpl-standby-2026-09-30.yaml"
P1, P2 = "AMB-0930-CPL-CONTAIN-1R", "AMB-0930-CPL-CONTAIN-2"


def fresh(c):
    s = {"campaigns": {}, "groups": {}}
    for r in q(c, f"""SELECT campaign.id, campaign.name, campaign.status, campaign_budget.id, campaign_budget.amount_micros,
            campaign_budget.explicitly_shared FROM campaign WHERE campaign.status != 'REMOVED'"""):
        s["campaigns"][str(r.campaign.id)] = dict(status=E(r.campaign.status), budget_id=str(r.campaign_budget.id),
                                                  micros=r.campaign_budget.amount_micros, shared=r.campaign_budget.explicitly_shared)
    for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status FROM ad_group
            WHERE campaign.id IN ({REPAIR_CAMP},{BOILER_CAMP}) AND ad_group.status != 'REMOVED'"""):
        s["groups"][str(r.ad_group.id)] = dict(campaign=str(r.campaign.id), name=r.ad_group.name, status=E(r.ad_group.status), enabled_ads=0)
    for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_ad.status FROM ad_group_ad
            WHERE campaign.id IN ({REPAIR_CAMP},{BOILER_CAMP}) AND ad_group_ad.status = 'ENABLED'"""):
        g = s["groups"].get(str(r.ad_group.id))
        if g: g["enabled_ads"] += 1
    s["enabled_total"] = round(sum(v["micros"] for v in s["campaigns"].values() if v["status"] == "ENABLED") / 1e6, 2)
    return s


def baseline(c):
    """User-controlled state that must be identical before and after CONTAIN-1R, except the two intended changes."""
    b = {"campaigns": {}, "repair_campaign": {}, "repair_groups": {}}
    for r in q(c, """SELECT campaign.id, campaign.status, campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros,
            campaign_budget.amount_micros FROM campaign WHERE campaign.status != 'REMOVED'"""):
        b["campaigns"][str(r.campaign.id)] = [E(r.campaign.status), E(r.campaign.bidding_strategy_type),
                                              r.campaign.target_spend.cpc_bid_ceiling_micros, r.campaign_budget.amount_micros]
    r = q(c, f"""SELECT campaign.id, campaign.network_settings.target_search_network, campaign.network_settings.target_content_network,
            campaign.geo_target_type_setting.positive_geo_target_type FROM campaign WHERE campaign.id = {REPAIR_CAMP}""")[0]
    b["repair_campaign"]["networks"] = [r.campaign.network_settings.target_search_network, r.campaign.network_settings.target_content_network,
                                        E(r.campaign.geo_target_type_setting.positive_geo_target_type)]
    b["repair_campaign"]["criteria"] = sorted(f"{E(x.campaign_criterion.type)}|{x.campaign_criterion.criterion_id}|{x.campaign_criterion.negative}"
        for x in q(c, f"SELECT campaign.id, campaign_criterion.type, campaign_criterion.criterion_id, campaign_criterion.negative FROM campaign_criterion WHERE campaign.id = {REPAIR_CAMP} AND campaign_criterion.status != 'REMOVED'"))
    b["repair_campaign"]["assets"] = sorted(f"{E(x.campaign_asset.field_type)}|{x.asset.id}|{E(x.campaign_asset.status)}"
        for x in q(c, f"SELECT campaign.id, asset.id, campaign_asset.field_type, campaign_asset.status FROM campaign_asset WHERE campaign.id = {REPAIR_CAMP} AND campaign_asset.status != 'REMOVED'"))
    b["repair_campaign"]["shared_sets"] = sorted(str(x.shared_set.id) for x in q(c, f"SELECT campaign.id, shared_set.id, campaign_shared_set.status FROM campaign_shared_set WHERE campaign.id = {REPAIR_CAMP} AND campaign_shared_set.status = 'ENABLED'"))
    for x in q(c, f"SELECT campaign.id, ad_group.id, ad_group.status FROM ad_group WHERE campaign.id = {REPAIR_CAMP} AND ad_group.status != 'REMOVED'"):
        b["repair_groups"][str(x.ad_group.id)] = {"status": E(x.ad_group.status), "ads": [], "kws": []}
    for x in q(c, f"SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.status FROM ad_group_ad WHERE campaign.id = {REPAIR_CAMP} AND ad_group_ad.status != 'REMOVED'"):
        b["repair_groups"][str(x.ad_group.id)]["ads"].append(f"{x.ad_group_ad.ad.id}|{E(x.ad_group_ad.status)}")
    for x in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.negative, ad_group_criterion.status
            FROM ad_group_criterion WHERE campaign.id = {REPAIR_CAMP} AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED'"""):
        b["repair_groups"][str(x.ad_group.id)]["kws"].append(f"{x.ad_group_criterion.criterion_id}|{x.ad_group_criterion.negative}|{E(x.ad_group_criterion.status)}")
    for g in b["repair_groups"].values():
        g["ads"].sort(); g["kws"].sort()
    return b


def expected_after(b0):
    import copy
    b = copy.deepcopy(b0)
    b["repair_groups"][HR_AG]["status"] = "PAUSED"
    b["campaigns"][REPAIR_CAMP][3] = 30_000_000
    return b


def recon_evidence():
    """Latest reconciliation file; the evidence numbers are NOT hashed (they move daily), only the rule is."""
    files = sorted(SNAP.glob("cpl-reconciliation-*.json"))
    d = json.loads(files[-1].read_text(encoding="utf-8"))
    pick = lambda pre: next(((k, v) for k, v in d["scopes"].items() if k.startswith(pre)), (None, {}))
    return files[-1].name, {k: pick(k)[1] for k in (f"C {REPAIR_CAMP}", f"G {HR_AG}", f"C {BOILER_CAMP}", f"G {BR_AG}", f"G {GBR_AG}",
                                                    f"G {BREPL_AG}")}


def build(c):
    s = fresh(c)
    base = baseline(c)
    e1, e2 = [], []
    rc = s["campaigns"][REPAIR_CAMP]
    to_micros = 30_000_000
    p1 = {"plan": P1, "target": TARGET, "work_order": str(WO_HR.relative_to(ROOT)).replace("\\", "/"),
          "approval_type": "EXPLICIT APPROVAL (status + budget decrease)",
          "supersedes": {"plan": "AMB-0930-CPL-CONTAIN-1", "fingerprint": "54300C1A3EF4", "why": "approval text corrected (no post-containment allowance, timing) and unrelated-resource baseline added"},
          "rule": "Ad group 204129717007 zero-lead spend >= its stop threshold min($300, $350 - 2 x campaign budget); campaign zero-lead spend above $350",
          "preconditions": {"campaign": {"id": REPAIR_CAMP, "status": rc["status"], "budget_id": rc["budget_id"], "budget_micros": rc["micros"],
                                         "shared": rc["shared"]},
                            "ad_group": {"id": HR_AG, **{k: s["groups"][HR_AG][k] for k in ("name", "status", "enabled_ads")}},
                            "untouched_ad_groups": {g: {k: s["groups"][g][k] for k in ("name", "status")} for g in KEEP_REPAIR},
                            "enabled_daily_total_usd": s["enabled_total"]},
          "operations": [{"op": "UPDATE", "resource": "ad_group", "id": HR_AG, "field": "status", "from": "ENABLED", "to": "PAUSED"},
                         {"op": "UPDATE", "resource": "campaign_budget", "id": rc["budget_id"], "campaign": REPAIR_CAMP,
                          "field": "amount_micros", "from": rc["micros"], "to": to_micros}],
          "effect": {"enabled_daily_total_after_usd": round(s["enabled_total"] - (rc["micros"] - to_micros) / 1e6, 2),
                     "repair_campaign_max_one_day_usd": {"before": 2 * rc["micros"] / 1e6, "after": 2 * to_micros / 1e6}},
          "readback_assertions": ["ad group 204129717007 PAUSED", "budget 15885327972 amount_micros == 30000000",
                                  "every other value in unrelated_resource_baseline identical after execution (all campaigns' status, "
                                  "bidding, ceiling and budget; Repair campaign networks, geo setting, criteria, asset links, shared sets; "
                                  "all Repair ad groups' status, ads and keywords)"],
          "post_containment": "NO further zero-lead allowance is authorized by this plan. Campaign history stays breached (never reset). "
                              "Spend by the four remaining repair ad groups is reported daily beside the full history; any campaign-level "
                              "action (pause, budget) needs a new exact approval.",
          "timing": "Execute promptly once approved, regardless of that day's spend. The ad-group pause takes effect within minutes. "
                    "The budget decrease does not lower the charging limit already set for that day by the higher $85 budget; "
                    "the $30 budget governs from the next day, and the monthly charging limit follows the budget history.",
          "unrelated_resource_baseline": base,
          "restart_rule": "never automatic; needs a verified fix (D6 form, message match, call path), a bounded post-fix test cap "
                          "of $150 zero-lead spend, and a new explicit approval"}
    if rc["micros"] != 85_000_000 or rc["shared"]: e1.append(f"Repair budget precondition drift {rc}")
    if s["groups"][HR_AG]["status"] != "ENABLED": e1.append("Heating Repair ad group not ENABLED")
    if rc["status"] != "ENABLED": e1.append("Repair campaign not ENABLED")
    p2 = {"plan": P2, "target": TARGET, "work_order": str(WO_PROG.relative_to(ROOT)).replace("\\", "/"),
          "approval_type": "STANDBY APPROVAL: executable only when the trigger is confirmed by a fresh reconciliation run",
          "trigger": {"any_of": ["campaign 24132507744 CPL > $350 on complete days with >= 1 verified lead",
                                 "ad group 204129718047 zero-lead spend >= $260 (= min($300, $350 - 2 x $45))"],
                      "evaluated_on": "complete days + reconciled leads; provisional today is exposure only"},
          "preconditions": {"campaign": {"id": BOILER_CAMP, "status": s["campaigns"][BOILER_CAMP]["status"],
                                         "budget_micros": s["campaigns"][BOILER_CAMP]["micros"]},
                            "ad_groups": {g: {k: s["groups"][g][k] for k in ("name", "status", "enabled_ads")} for g in (BR_AG, GBR_AG)},
                            "untouched": {BREPL_AG: {k: s["groups"][BREPL_AG][k] for k in ("name", "status")}}},
          "operations": [{"op": "UPDATE", "resource": "ad_group", "id": g, "field": "status", "from": "ENABLED", "to": "PAUSED"}
                         for g in (BR_AG, GBR_AG)],
          "effect": {"budget_change": "none", "boiler_replacement": "keeps serving on the same $45 budget"},
          "readback_assertions": ["ad groups 204129718047 and 202339087594 PAUSED", "Boiler Replacement 204129718207 unchanged",
                                  "no budget, bid, keyword, ad, asset or conversion change"],
          "restart_rule": "never automatic; same requirements as CONTAIN-1"}
    for g in (BR_AG, GBR_AG):
        if s["groups"][g]["status"] != "ENABLED": e2.append(f"{g} not ENABLED")
    return s, p1, p2, {P1: e1, P2: e2}


def trigger_met():
    _, ev = recon_evidence()
    camp, br = ev.get(f"C {BOILER_CAMP}", {}).get("launch_to_date", {}), ev.get(f"G {BR_AG}", {}).get("launch_to_date", {})
    a = bool(camp.get("leads")) and camp["spend"] / camp["leads"] > 350
    b = (not br.get("leads")) and br.get("spend", 0) >= 260
    return a or b, {"campaign_cpl": round(camp["spend"] / camp["leads"], 2) if camp.get("leads") else None,
                    "boiler_repair_zero_lead_spend": br.get("spend")}


def ops(c, plan):
    out = []
    for o in plan["operations"]:
        m = c.get_type("MutateOperation")
        if o["resource"] == "ad_group":
            u = m.ad_group_operation.update
            u.resource_name = c.get_service("AdGroupService").ad_group_path(CID, o["id"]); u.status = c.enums.AdGroupStatusEnum.PAUSED
            m.ad_group_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
        elif o["resource"] == "campaign_budget":
            u = m.campaign_budget_operation.update
            u.resource_name = c.get_service("CampaignBudgetService").campaign_budget_path(CID, o["id"]); u.amount_micros = o["to"]
            m.campaign_budget_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["amount_micros"]))
        else:
            raise SystemExit(f"unsupported {o}")
        out.append(m)
    return out


def send(c, mops, validate_only):
    rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False; rq.validate_only = validate_only
    rq.mutate_operations.extend(mops)
    return c.get_service("GoogleAdsService").mutate(request=rq)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["plan", "execute"]); ap.add_argument("--plan"); ap.add_argument("--fp")
    a = ap.parse_args()
    c = client(); ident = identity_gate(c, verbose=True)
    cl = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
    for wo in (WO_HR, WO_PROG):
        err = validate_work_order(yaml.safe_load(wo.read_text(encoding="utf-8")), cl)
        if err: sys.exit(f"work order {wo.name} invalid: {err}")
    s, p1, p2, errs = build(c)
    for p in (p1, p2):
        assert_no_embedded_secrets(p); assert_target_matches(p, cl, observed_account_name=ident["descriptive_name"])
    fps = {P1: approval_code(p1), P2: approval_code(p2)}
    if a.cmd == "plan":
        ev_file, ev = recon_evidence()
        for p in (p1, p2):
            try:
                send(c, ops(c, p), True); vo = "VALIDATE_OK"
            except Exception as ex:  # noqa: BLE001
                vo = "VALIDATE_FAIL " + str(ex)[-300:]; errs[p["plan"]].append(vo)
            doc = dict(p, fingerprint=fps[p["plan"]], operation_count=len(p["operations"]), validate_only=vo,
                       errors=errs[p["plan"]], generated_local=datetime.datetime.now(TZ).isoformat(),
                       evidence_not_hashed={"file": ev_file, "scopes": ev})
            (PLANS / f"{p['plan']}.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
            print(f"PLAN {p['plan']} {fps[p['plan']]} ops={len(p['operations'])} {vo} errors={errs[p['plan']]}")
        print("CONTAIN-1 effect:", p1["effect"])
        met, why = trigger_met(); print("CONTAIN-2 trigger met now:", met, why)
        return
    if a.plan == P1:
        sys.exit("WITHDRAWN 2026-09-30d (owner): AMB-0930-CPL-CONTAIN-1R / 4C544E4CE290 must never execute; repair ad groups stay live.")
    if a.plan not in fps or a.fp != fps[a.plan] or errs[a.plan]:
        sys.exit(f"ABORT: {a.plan} fingerprint {fps.get(a.plan)} != {a.fp} or errors {errs.get(a.plan)}")
    if a.plan == P2:
        subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "ambient_0930_cpl_reconcile.py")], check=True,
                       stdout=subprocess.DEVNULL)
        met, why = trigger_met()
        if not met:
            sys.exit(f"ABORT: CONTAIN-2 trigger not met on fresh data {why}")
    plan = p1 if a.plan == P1 else p2
    rec = {"plan": a.plan, "fingerprint": a.fp, "started_local": datetime.datetime.now(TZ).isoformat()}
    out = RECEIPTS / f"{a.plan}-EXECUTED.json"
    try:
        resp = send(c, ops(c, plan), False)
    except Exception as ex:  # noqa: BLE001
        rec["error"] = str(ex)[:1500]; out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        sys.exit(f"STOP: atomic mutate failed, nothing applied: {str(ex)[:400]}")
    rec["results"] = [str(r) for r in resp.mutate_operation_responses]
    s2 = fresh(c); fails = []
    if a.plan == P1:
        if s2["groups"][HR_AG]["status"] != "PAUSED": fails.append("Heating Repair not paused")
        if s2["campaigns"][REPAIR_CAMP]["micros"] != 30_000_000: fails.append("budget not 30")
        after, want = baseline(c), expected_after(p1["unrelated_resource_baseline"])
        if after != want:
            fails.append("unrelated resource drift: " + json.dumps({k: [after[k], want[k]] for k in want if after[k] != want[k]})[:1500])
    else:
        fails += [f"{g} not paused" for g in (BR_AG, GBR_AG) if s2["groups"][g]["status"] != "PAUSED"]
        if s2["groups"][BREPL_AG]["status"] != s["groups"][BREPL_AG]["status"]: fails.append("Boiler Replacement changed")
    rec.update(readback_fail=len(fails), readback_fails=fails, finished_local=datetime.datetime.now(TZ).isoformat())
    out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(f"{a.plan} EXECUTED; readback {'PASS' if not fails else fails}")


if __name__ == "__main__":
    main()
