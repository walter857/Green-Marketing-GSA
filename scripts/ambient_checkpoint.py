#!/usr/bin/env python3
"""Ambient Cooling durable checkpoint. READ-ONLY BY DEFAULT.

    python scripts/ambient_checkpoint.py                       # read-only checkpoint
    python scripts/ambient_checkpoint.py --leads leads.csv      # + privacy-safe outcomes
    python scripts/ambient_checkpoint.py --rollback-cpc --confirm-gate-failed
                                                                # ONLY the approved $65 -> $30

Safety contract
  * identity is re-gated before every query; a mismatch aborts before any read
  * partial and settled dates are always distinguished
  * the ONLY mutation this tool can ever perform is HVAC Installation
    target_spend.cpc_bid_ceiling_micros 65000000 -> 30000000, and only with BOTH flags
  * a rollback already recorded in the state file is refused (reboot-safe, no double-execute)
  * lead outcomes are counted, never stored: no name, phone, email or address is written
  * the tool exits when finished; it never loops or daemonises
"""
from __future__ import annotations
import argparse, csv, hashlib, json, sys, datetime
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import (CID, EXACT_NAME, GM_MANAGER, CC_MANAGER, TZ, FIVE, IN5, NAME,
                              CLIENT_DIR, EVID, client, q)  # noqa
from gm_gsa.google_ads import enum_name as E  # noqa

STATE = CLIENT_DIR / "monitoring" / "checkpoint-state.json"
INSTALL = "24132507747"
T0_FILE = CLIENT_DIR / "monitoring" / "cpc-test-T0.json"
ROLLBACK_TO = 30000000
TEST_CEILING = 65000000
THRESHOLDS = [200.00, 280.00, 560.00]
MONTHLY_MAX, DAYS = 13000.0, 30.4


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"created": datetime.datetime.now(TZ).isoformat(), "checkpoints": [],
            "rollback_executed": False, "rollback_receipt": None}


def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=1, default=str), encoding="utf-8")


def gate(c):
    r = q(c, "SELECT customer.id, customer.descriptive_name, customer.manager, "
             "customer.test_account, customer.time_zone, customer.currency_code FROM customer")[0]
    x = r.customer
    ok = (str(x.id) == CID and x.descriptive_name == EXACT_NAME and not x.manager
          and not x.test_account and x.time_zone == "America/New_York"
          and x.currency_code == "USD")
    links = {y.customer_manager_link.manager_customer.split("/")[-1]:
             E(y.customer_manager_link.status)
             for y in q(c, "SELECT customer_manager_link.manager_customer, "
                           "customer_manager_link.status FROM customer_manager_link")}
    ok = ok and links.get(GM_MANAGER) == "ACTIVE" and links.get(CC_MANAGER) == "ACTIVE"
    if not ok:
        sys.exit(f"IDENTITY GATE FAILED for {CID}. No query will run.")
    print(f"  identity gate PASS  {x.descriptive_name} / {x.id} / {x.time_zone} / "
          f"{x.currency_code} / manager={x.manager} / test={x.test_account} / links={links}")
    return {"name": x.descriptive_name, "id": str(x.id), "manager_links": links}


def dates(c):
    t = q(c, "SELECT segments.date FROM customer WHERE segments.date DURING TODAY")
    y = q(c, "SELECT segments.date FROM customer WHERE segments.date DURING YESTERDAY")
    today = t[0].segments.date if t else None
    settled = y[0].segments.date if y else None
    if not settled:
        settled = (datetime.datetime.now(TZ).date() - datetime.timedelta(days=1)).isoformat()
    print(f"  account-local: TODAY(partial)={today or 'no delivery yet'}  "
          f"LATEST SETTLED={settled}")
    return today, settled


def leads(path):
    """Count privacy-safe outcomes. Reads only the columns needed; stores NO PII."""
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        print(f"  lead export not found: {p}")
        return None
    agg = defaultdict(lambda: {"unique_qualified": 0, "unqualified": 0, "total": 0})
    seen = set()
    with p.open(newline="", encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            low = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            camp = low.get("campaign") or low.get("campaign name") or "UNKNOWN"
            join = (low.get("gclid") or low.get("lead id") or low.get("lead_id")
                    or low.get("join key") or "")
            qual = (low.get("qualified") or low.get("lead status") or
                    low.get("quality") or "").lower()
            key = hashlib.sha256((join or json.dumps(sorted(low.items()))).encode()).hexdigest()
            a = agg[camp]
            a["total"] += 1
            if key in seen:
                continue
            seen.add(key)
            if qual in ("yes", "true", "qualified", "good", "1"):
                a["unique_qualified"] += 1
            else:
                a["unqualified"] += 1
    print(f"  lead outcomes ingested from {p.name} (counts only, no PII stored):")
    for k, v in agg.items():
        print(f"    {k[:44]:<46} unique_qualified={v['unique_qualified']:<4} "
              f"unqualified={v['unqualified']:<4} rows={v['total']}")
    return {k: dict(v) for k, v in agg.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leads", help="privacy-safe lead export CSV (counts only)")
    ap.add_argument("--rollback-cpc", action="store_true",
                    help="execute ONLY the approved HVAC Installation $65 -> $30 rollback")
    ap.add_argument("--confirm-gate-failed", action="store_true",
                    help="required second flag: an outcome gate objectively failed")
    a = ap.parse_args()

    now = datetime.datetime.now(TZ).isoformat()
    print(f"=== AMBIENT CHECKPOINT {now} ===")
    c = client()
    ident = gate(c)
    today, settled = dates(c)
    st = load_state()
    cp = {"checked_local": now, "today_partial": today, "last_settled": settled,
          "identity": ident}

    print("\n--- CAMPAIGN METRICS, SETTLED ---")
    rowsc = {}
    for r in q(c, f"SELECT campaign.id, metrics.impressions, metrics.clicks, metrics.ctr, "
                  f"metrics.average_cpc, metrics.cost_micros, metrics.conversions, "
                  f"metrics.search_budget_lost_impression_share, "
                  f"metrics.search_rank_lost_impression_share FROM campaign "
                  f"WHERE campaign.id IN ({IN5}) "
                  f"AND segments.date BETWEEN '2026-08-14' AND '{settled}'"):
        m = r.metrics
        rowsc[NAME[str(r.campaign.id)]] = {
            "impressions": m.impressions, "reported_clicks": m.clicks,
            "ctr_pct": round(m.ctr * 100, 2), "avg_cpc": round(m.average_cpc / 1e6, 2),
            "cost": round(m.cost_micros / 1e6, 2),
            "primary_records": round(m.conversions, 2),
            "lost_is_budget_pct": round(m.search_budget_lost_impression_share * 100, 2),
            "lost_is_rank_pct": round(m.search_rank_lost_impression_share * 100, 2)}
    for k, v in rowsc.items():
        cpa = f"{v['cost']/v['primary_records']:.2f}" if v["primary_records"] else "-"
        print(f"  {k:<20} impr={v['impressions']:<6} clicks={v['reported_clicks']:<4} "
              f"CTR={v['ctr_pct']:>5.2f}% CPC=${v['avg_cpc']:<8} cost=${v['cost']:<9} "
              f"records={v['primary_records']:<4.0f} rawCPA=${cpa:<9} "
              f"lostBUD={v['lost_is_budget_pct']:>5.1f}% lostRANK={v['lost_is_rank_pct']:>5.1f}%")
    cp["campaigns"] = rowsc

    print("\n--- PER-ACTION PRIMARY vs ALL CONVERSIONS (records, not leads) ---")
    act = defaultdict(lambda: {"primary": 0.0, "all": 0.0})
    for r in q(c, f"SELECT segments.conversion_action_name, metrics.conversions, "
                  f"metrics.all_conversions FROM campaign WHERE campaign.id IN ({IN5}) "
                  f"AND segments.date BETWEEN '2026-08-14' AND '{settled}'"):
        act[r.segments.conversion_action_name]["primary"] += r.metrics.conversions
        act[r.segments.conversion_action_name]["all"] += r.metrics.all_conversions
    for k, v in sorted(act.items(), key=lambda kv: -kv[1]["all"]):
        if v["primary"] or v["all"]:
            print(f"  {k[:48]:<50} primary={v['primary']:>6.2f}  all={v['all']:>6.2f}")
    cp["conversion_actions"] = {k: {a: round(b, 2) for a, b in v.items()}
                                for k, v in act.items() if v["primary"] or v["all"]}

    print("\n--- BUDGET EXPOSURE ---")
    buds, ceil = {}, {}
    for r in q(c, f"SELECT campaign.id, campaign.campaign_budget, "
                  f"campaign.target_spend.cpc_bid_ceiling_micros FROM campaign "
                  f"WHERE campaign.id IN ({IN5})"):
        ceil[NAME[str(r.campaign.id)]] = r.campaign.target_spend.cpc_bid_ceiling_micros
        buds[NAME[str(r.campaign.id)]] = r.campaign.campaign_budget.split("/")[-1]
    amt = {str(r.campaign_budget.id): r.campaign_budget.amount_micros
           for r in q(c, "SELECT campaign_budget.id, campaign_budget.amount_micros "
                         "FROM campaign_budget WHERE campaign_budget.status = 'ENABLED'")}
    daily = sum(amt[b] / 1e6 for b in buds.values())
    mstart = settled[:7] + "-01"
    spend = q(c, f"SELECT metrics.cost_micros FROM customer "
                 f"WHERE segments.date BETWEEN '{mstart}' AND '{settled}'")
    mtd = round(spend[0].metrics.cost_micros / 1e6, 2) if spend else 0.0
    print(f"  combined daily budget ${daily:.2f}  x30.4 = ${daily*DAYS:,.2f}  "
          f"{'WITHIN' if daily*DAYS <= MONTHLY_MAX else '*** BREACHES ***'} ${MONTHLY_MAX:,.0f}")
    print(f"  month-to-date SERVED cost through {settled}: ${mtd:,.2f}")
    for k, v in ceil.items():
        print(f"    {k:<20} budget ${amt[buds[k]]/1e6:>7.2f}/day  "
              f"CPC ceiling ${v/1e6:>6.2f}")
    cp["budget"] = {"combined_daily": round(daily, 2), "steady_state": round(daily * DAYS, 2),
                    "within_cap": daily * DAYS <= MONTHLY_MAX, "mtd_served": mtd,
                    "ceilings_micros": ceil}

    print("\n--- NEGATIVE-LAYER AND KEYWORD CONFLICT SNAPSHOT ---")
    negcount = defaultdict(int)
    for r in q(c, f"SELECT campaign.id FROM campaign_criterion WHERE campaign.id IN ({IN5}) "
                  f"AND campaign_criterion.type = 'KEYWORD' "
                  f"AND campaign_criterion.negative = TRUE "
                  f"AND campaign_criterion.status = 'ENABLED'"):
        negcount[NAME[str(r.campaign.id)]] += 1
    acct_n = len(q(c, "SELECT shared_criterion.criterion_id FROM shared_criterion "
                      "WHERE shared_set.id = 11252984411"))
    attached = len([r for r in q(c, "SELECT campaign.id, campaign_shared_set.shared_set "
                                    "FROM campaign_shared_set") if str(r.campaign.id) in FIVE])
    livekw = [r for r in q(c, f"SELECT ad_group.status, ad_group_criterion.status, "
                              f"ad_group_criterion.system_serving_status FROM ad_group_criterion "
                              f"WHERE campaign.id IN ({IN5}) "
                              f"AND ad_group_criterion.type = 'KEYWORD' "
                              f"AND ad_group_criterion.negative = FALSE "
                              f"AND ad_group_criterion.status = 'ENABLED'")
              if E(r.ad_group.status) == "ENABLED"]
    elig = sum(1 for r in livekw
               if E(r.ad_group_criterion.system_serving_status) == "ELIGIBLE")
    print(f"  campaign negatives: {dict(negcount)}")
    print(f"  account-level set members: {acct_n}   shared lists attached to the five: {attached}")
    print(f"  live positive keywords: {len(livekw)}  ELIGIBLE: {elig}")
    cp["negatives"] = {"by_campaign": dict(negcount), "account_level": acct_n,
                       "shared_lists_attached": attached,
                       "live_keywords": len(livekw), "eligible": elig}

    print("\n--- NEW SEARCH TERMS SINCE THE LAST CHECKPOINT ---")
    prev = st["checkpoints"][-1]["last_settled"] if st["checkpoints"] else settled
    nt = []
    for r in q(c, f"SELECT campaign.id, search_term_view.search_term, metrics.impressions, "
                  f"metrics.clicks, metrics.cost_micros, metrics.conversions "
                  f"FROM search_term_view WHERE campaign.id IN ({IN5}) "
                  f"AND segments.date BETWEEN '{prev}' AND '{settled}'"):
        nt.append({"camp": NAME[str(r.campaign.id)], "term": r.search_term_view.search_term,
                   "impr": r.metrics.impressions, "clicks": r.metrics.clicks,
                   "cost": round(r.metrics.cost_micros / 1e6, 2),
                   "records": round(r.metrics.conversions, 2)})
    print(f"  window {prev} .. {settled}: {len(nt)} rows, "
          f"{sum(z['clicks'] for z in nt)} reported clicks, "
          f"${sum(z['cost'] for z in nt):.2f}")
    for z in sorted(nt, key=lambda z: -z["cost"])[:12]:
        print(f"    {z['camp']:<20} impr={z['impr']:<4} clk={z['clicks']:<3} "
              f"${z['cost']:<8} rec={z['records']:<4.0f} {z['term']!r}")
    cp["new_search_terms"] = nt

    cp["lead_outcomes"] = leads(a.leads)

    print("\n--- CPC TEST THRESHOLD WATCH ---")
    cur = ceil["HVAC Installation"]
    if cur != TEST_CEILING:
        print(f"  HVAC Installation ceiling is ${cur/1e6:.2f}, not the $65.00 test value. "
              f"The test is not running; no threshold applies.")
        cp["cpc_test"] = {"running": False, "ceiling_micros": cur}
    else:
        t0 = json.loads(T0_FILE.read_text(encoding="utf-8")) if T0_FILE.exists() else None
        if not t0:
            print("  ceiling is $65 but no T0 baseline file exists. Cannot measure incremental "
                  "spend. Treat every gate as FAILED.")
            cp["cpc_test"] = {"running": True, "t0": None, "gate": "FAILED_NO_BASELINE"}
        else:
            s = q(c, f"SELECT metrics.cost_micros FROM campaign WHERE campaign.id = {INSTALL} "
                     f"AND segments.date BETWEEN '{t0['t0_date']}' AND '{settled}'")
            incr = round((s[0].metrics.cost_micros / 1e6) - t0["t0_cost"], 2) if s else 0.0
            ql = 0
            if cp["lead_outcomes"]:
                ql = sum(v["unique_qualified"] for k, v in cp["lead_outcomes"].items()
                         if "install" in k.lower())
            print(f"  incremental spend since T0 ({t0['t0_date']}): ${incr:,.2f}")
            print(f"  verified unique qualified Installation leads: "
                  f"{ql if cp['lead_outcomes'] else 'UNAVAILABLE'}")
            fails = []
            for th, need in ((280.00, 1), (560.00, 2)):
                if incr >= th:
                    if not cp["lead_outcomes"]:
                        fails.append(f"${th:.0f} reached, outcome data UNAVAILABLE -> GATE FAILED")
                    elif ql < need:
                        fails.append(f"${th:.0f} reached with {ql} qualified (need {need}) "
                                     f"-> GATE FAILED")
            if incr >= 200.00 and incr < 280.00:
                print("  EARLY WARNING: $200 incremental spend reached.")
            for f in fails:
                print(f"  {f}")
            if not fails:
                print("  no gate has failed at this checkpoint.")
            cp["cpc_test"] = {"running": True, "incremental_spend": incr,
                              "qualified_leads": ql if cp["lead_outcomes"] else None,
                              "failed_gates": fails}

    if a.rollback_cpc:
        print("\n--- ROLLBACK REQUEST ---")
        if not a.confirm_gate_failed:
            sys.exit("REFUSED: --rollback-cpc requires --confirm-gate-failed.")
        if st.get("rollback_executed"):
            sys.exit(f"REFUSED: rollback already executed. Receipt: {st['rollback_receipt']}")
        if cur != TEST_CEILING:
            sys.exit(f"REFUSED: ceiling is {cur}, not {TEST_CEILING}. Nothing to roll back.")
        from google.protobuf import field_mask_pb2
        op = c.get_type("MutateOperation")
        x = op.campaign_operation.update
        x.resource_name = f"customers/{CID}/campaigns/{INSTALL}"
        x.target_spend.cpc_bid_ceiling_micros = ROLLBACK_TO
        c.copy_from(op.campaign_operation.update_mask,
                    field_mask_pb2.FieldMask(paths=["target_spend.cpc_bid_ceiling_micros"]))
        req = c.get_type("MutateGoogleAdsRequest")
        req.customer_id = CID
        req.mutate_operations.append(op)
        req.partial_failure = False
        resp = c.get_service("GoogleAdsService").mutate(request=req)
        back = q(c, f"SELECT campaign.target_spend.cpc_bid_ceiling_micros FROM campaign "
                    f"WHERE campaign.id = {INSTALL}")[0]
        ok = back.campaign.target_spend.cpc_bid_ceiling_micros == ROLLBACK_TO
        rc = CLIENT_DIR / "receipts" / f"cpc-rollback-{now[:19].replace(':','')}.json"
        rc.parent.mkdir(parents=True, exist_ok=True)
        rc.write_text(json.dumps({"executed_local": now, "from": TEST_CEILING,
                                  "to": ROLLBACK_TO, "readback_ok": ok,
                                  "readback_value":
                                      back.campaign.target_spend.cpc_bid_ceiling_micros},
                                 indent=1), encoding="utf-8")
        print(f"  ROLLBACK EXECUTED. readback ceiling = "
              f"{back.campaign.target_spend.cpc_bid_ceiling_micros} (ok={ok})")
        st["rollback_executed"] = True
        st["rollback_receipt"] = str(rc.relative_to(ROOT))
        cp["rollback"] = {"executed": True, "readback_ok": ok}

    st["checkpoints"].append(cp)
    save_state(st)
    p = EVID / f"checkpoint-{now[:10]}-{now[11:19].replace(':','')}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cp, indent=1, default=str), encoding="utf-8")
    print(f"\n  checkpoint saved: {p.relative_to(ROOT)}")
    print(f"  state file: {STATE.relative_to(ROOT)}  (checkpoints recorded: "
          f"{len(st['checkpoints'])})")
    print("  DONE. This tool does not stay resident.")


if __name__ == "__main__":
    main()
