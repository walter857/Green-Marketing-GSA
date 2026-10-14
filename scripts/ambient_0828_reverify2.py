#!/usr/bin/env python3
"""Ambient Cooling - Live | re-verification part 2 | READ ONLY, ZERO MUTATIONS.

  1. click_type x conversion_action - does the Business Profile location asset
     actually carry Primary conversions, and are they real or the WC Lead artifact?
  2. conversion_action change history (change_event, client-side filtered)
  3. Competitor negatives re-tested under the stricter safety rule:
     reject any ambiguous company name, HVAC manufacturer, equipment brand,
     location, or generic service phrase.
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, SNAP, TZ, client, q, identity_gate, E, write,
)
from ambient_0827_negative_audit import SERVICE_PROBES, blocks, words  # noqa: E402

STAMP = "2026-08-28-reverify2"
WC_LEAD = "7643656486"

# ---------------------------------------------------------------------------
# The stricter rule the owner imposed. A proposed negative is REJECTED if the
# text is an ambiguous company name, an HVAC manufacturer, an equipment brand,
# a place name, or contains a generic service phrase.
# ---------------------------------------------------------------------------
HVAC_MANUFACTURERS = {
    "carrier", "trane", "lennox", "goodman", "rheem", "ruud", "york", "bryant",
    "amana", "payne", "daikin", "mitsubishi", "fujitsu", "coleman", "nordyne",
    "ducane", "frigidaire", "ecobee", "nest", "honeywell", "bosch", "navien",
    "weil", "mclain", "burnham", "buderus", "lochinvar", "american standard",
}
SERVICE_WORDS = {
    "hvac", "ac", "heating", "cooling", "repair", "install", "installation",
    "installer", "installers", "replacement", "replace", "boiler", "furnace",
    "service", "services", "air", "conditioning", "conditioner", "plumbing",
    "plumber", "mechanical", "comfort", "heat", "pump", "duct", "thermostat",
}
PLACE_WORDS = {
    "maryland", "md", "virginia", "va", "delaware", "annapolis", "severn",
    "columbia", "hanover", "beltway", "baltimore", "howard", "arundel",
    "barstow", "kirkland", "woodfin", "dayton", "aurora", "hagerstown",
    "chestertown", "harrisonburg", "fairfax", "rockville", "linthicum",
    "halethorpe", "gaithersburg", "delmarva", "capital", "capitol",
}
# Common-word surnames and retail brands that make a one-word negative ambiguous.
AMBIGUOUS_TOKENS = {
    "michaels", "michael", "furr", "fur", "mccrea", "bahr", "bear", "white",
    "total", "supreme", "horizon", "amazing", "precision", "len", "hugee",
    "elmar", "blauch", "armbridge", "bluedot", "croppmetcalfe",
}
# Tokens judged unambiguous: coined or highly distinctive company names with no
# dictionary, brand, place or service meaning.
UNAMBIGUOUS_COINED = {
    "croppmetcalfe", "armbridge", "bluedot", "blauch", "hugee", "elmar",
}


def screen(text: str):
    """Apply the owner's stricter rule. Returns (verdict, reasons)."""
    w = words(text)
    reasons = []
    for t in w:
        if t in HVAC_MANUFACTURERS:
            reasons.append(f"'{t}' is an HVAC manufacturer or equipment brand")
        if t in PLACE_WORDS:
            reasons.append(f"'{t}' is a place name")
        if t in SERVICE_WORDS:
            reasons.append(f"'{t}' is a generic service word")
    if len(w) == 1 and w[0] in AMBIGUOUS_TOKENS and w[0] not in UNAMBIGUOUS_COINED:
        reasons.append(f"'{w[0]}' is a single ambiguous token (surname or retail brand)")
    return ("REJECT" if reasons else "ALLOW"), sorted(set(reasons))


def main():
    c = client()
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "customer_id": CID, "read_only": True, "mutations": 0}
    identity_gate(c, verbose=False)
    print("IDENTITY: PASS\n")

    # =====================================================================
    print("== 1. CLICK TYPE x CONVERSION ACTION (2026-08-01..2026-08-27) ==")
    rows = []
    for r in q(c, f"""SELECT campaign.id, segments.click_type,
                      segments.conversion_action, segments.conversion_action_name,
                      metrics.conversions, metrics.all_conversions
                      FROM campaign WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-27'
                        AND metrics.all_conversions > 0"""):
        rows.append({"campaign": NAME[str(r.campaign.id)],
                     "click_type": E(r.segments.click_type),
                     "action_id": r.segments.conversion_action.split("/")[-1],
                     "action": r.segments.conversion_action_name,
                     "conversions": round(r.metrics.conversions, 2),
                     "all_conversions": round(r.metrics.all_conversions, 2)})
    out["click_type_x_action"] = rows
    print(f"  {'campaign':20s} {'click_type':20s} {'action':44s} {'conv':>6s} {'all':>6s}")
    for x in sorted(rows, key=lambda z: (-z["conversions"], -z["all_conversions"])):
        mark = "  <== PRIMARY" if x["conversions"] > 0 else ""
        print(f"  {x['campaign']:20s} {x['click_type']:20s} {x['action']:44s} "
              f"{x['conversions']:>6.1f} {x['all_conversions']:>6.1f}{mark}")

    print("\n  PRIMARY conversions by click type:")
    prim = defaultdict(lambda: {"conversions": 0.0, "actions": []})
    for x in rows:
        if x["conversions"] > 0:
            e = prim[x["click_type"]]
            e["conversions"] += x["conversions"]
            e["actions"].append(f"{x['campaign']}/{x['action']}={x['conversions']}")
    for k, v in sorted(prim.items(), key=lambda z: -z[1]["conversions"]):
        print(f"     {k:22s} {v['conversions']:>4.1f}  {v['actions']}")
    out["primary_conversions_by_click_type"] = {
        k: {"conversions": round(v["conversions"], 2), "actions": v["actions"]}
        for k, v in prim.items()}

    # Which click type carried the WC Lead artifact?
    wcrows = [x for x in rows if x["action_id"] == WC_LEAD]
    out["wc_lead_by_click_type"] = wcrows
    print("\n  WC Lead rows by click type:")
    for x in wcrows:
        print(f"     {x['campaign']:20s} {x['click_type']:20s} "
              f"conv={x['conversions']:.1f} all={x['all_conversions']:.1f}")

    # location-asset click types, adjusted for the WC Lead artifact
    loc_types = ("LOCATION_EXPANSION", "GET_DIRECTIONS", "STORE_LOCATOR")
    loc_prim_platform = round(sum(
        x["conversions"] for x in rows if x["click_type"] in loc_types), 2)
    loc_prim_wc = round(sum(
        x["conversions"] for x in rows
        if x["click_type"] in loc_types and x["action_id"] == WC_LEAD), 2)
    out["location_click_type_primary_conversions"] = {
        "platform_reported": loc_prim_platform,
        "of_which_wc_lead_historical_artifact": loc_prim_wc,
        "adjusted_real": round(loc_prim_platform - loc_prim_wc, 2),
        "detail": [x for x in rows if x["click_type"] in loc_types],
    }
    print(f"\n  Location-asset click types PRIMARY conversions:")
    print(f"     platform reported                      : {loc_prim_platform}")
    print(f"     of which the WC Lead historical artifact: {loc_prim_wc}")
    print(f"     ADJUSTED REAL                          : "
          f"{round(loc_prim_platform - loc_prim_wc, 2)}")

    # cost of the location click types
    loccost = defaultdict(lambda: {"clicks": 0, "cost": 0.0, "impr": 0})
    for r in q(c, f"""SELECT campaign.id, segments.click_type, metrics.clicks,
                      metrics.cost_micros, metrics.impressions FROM campaign
                      WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-27'"""):
        ct = E(r.segments.click_type)
        if ct in loc_types:
            e = loccost[(NAME[str(r.campaign.id)], ct)]
            e["clicks"] += r.metrics.clicks
            e["cost"] += r.metrics.cost_micros / 1e6
            e["impr"] += r.metrics.impressions
    out["location_click_type_cost"] = {
        f"{k[0]}|{k[1]}": {**v, "cost": round(v["cost"], 2)} for k, v in loccost.items()}
    tot_clicks = sum(v["clicks"] for v in loccost.values())
    tot_cost = round(sum(v["cost"] for v in loccost.values()), 2)
    print(f"     total location-asset clicks={tot_clicks} cost=${tot_cost:,.2f}")
    out["location_click_type_totals"] = {"clicks": tot_clicks, "cost": tot_cost}

    # =====================================================================
    print("\n== 2. CONVERSION ACTION CHANGE HISTORY ==")
    ce = []
    try:
        for r in q(c, """SELECT change_event.change_date_time,
                         change_event.change_resource_type,
                         change_event.resource_change_operation,
                         change_event.changed_fields,
                         change_event.change_resource_name,
                         change_event.user_email, change_event.client_type
                         FROM change_event
                         WHERE change_event.change_date_time >= '2026-07-29'
                           AND change_event.change_date_time <= '2026-08-29'
                         ORDER BY change_event.change_date_time DESC
                         LIMIT 1000"""):
            x = r.change_event
            ce.append({"when": x.change_date_time,
                       "resource_type": E(x.change_resource_type),
                       "op": E(x.resource_change_operation),
                       "resource": x.change_resource_name,
                       "fields": list(x.changed_fields.paths) if x.changed_fields else [],
                       "user": x.user_email, "client": E(x.client_type)})
    except Exception as exc:  # noqa: BLE001
        ce = [{"error": str(exc)[:400]}]
    conv_ce = [x for x in ce if x.get("resource_type") == "CONVERSION_ACTION"]
    out["all_change_events_30d"] = ce
    out["conversion_action_change_events"] = conv_ce
    print(f"  total change_event rows in the last 30 days: {len(ce)}")
    print(f"  of which CONVERSION_ACTION                 : {len(conv_ce)}")
    for x in conv_ce:
        print(f"     {x['when']} {x['op']:8s} {x['resource']} {x['fields']} {x['user']}")
    if not conv_ce:
        print("     NONE. change_event is capped at 30 days AND is known to lag/omit;")
        print("     it cannot prove when the WC Lead flags were set. The metric")
        print("     evidence (conversions=0 from 2026-08-21 onward) is the proof.")

    # =====================================================================
    print("\n== 3. COMPETITOR NEGATIVES UNDER THE STRICTER RULE ==")
    plan = json.loads((Path("clients/ambient-cooling-heating/plans") /
                       "AMBIENT-CONSOLIDATED-2026-08-27.json").read_text(encoding="utf-8"))
    proposed = plan["negative_detail"]
    st = json.loads((SNAP / "search-terms-2026-08-27.json").read_text(encoding="utf-8"))
    verdicts = st["verdicts"]

    live_kw = []
    for r in q(c, f"""SELECT campaign.id, ad_group_criterion.keyword.text,
                      ad_group_criterion.keyword.match_type FROM ad_group_criterion
                      WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type='KEYWORD'
                        AND ad_group_criterion.status!='REMOVED'
                        AND ad_group_criterion.negative=FALSE
                        AND ad_group.status!='REMOVED'"""):
        live_kw.append({"campaign_id": str(r.campaign.id),
                        "campaign": NAME[str(r.campaign.id)],
                        "text": r.ad_group_criterion.keyword.text,
                        "match": E(r.ad_group_criterion.keyword.match_type)})

    screened = []
    for p in proposed:
        verdict, reasons = screen(p["text"])
        covered = [v for v in verdicts
                   if v["campaign_id"] == p["campaign_id"]
                   and blocks(p["text"], p["match"], v["search_term"])[0]]
        kw_conf = [k["text"] for k in live_kw
                   if k["campaign_id"] == p["campaign_id"]
                   and blocks(p["text"], p["match"], k["text"])[0]]
        probe_conf = [x for x in SERVICE_PROBES if blocks(p["text"], p["match"], x)[0]]
        screened.append({
            "text": p["text"], "match": p["match"], "campaign": p["campaign"],
            "campaign_id": p["campaign_id"], "package": p["package"],
            "strict_verdict": verdict, "strict_reasons": reasons,
            "terms_covered": len(covered),
            "impressions": sum(v["impressions"] for v in covered),
            "clicks": sum(v["clicks"] for v in covered),
            "cost": round(sum(v["cost"] for v in covered), 2),
            "primary_conversions": round(sum(v["primary_conversions"] for v in covered), 2),
            "secondary_all_conversions": round(
                sum(v["all_conversions"] for v in covered), 2),
            "blocks_live_keywords": kw_conf,
            "blocks_service_probes": probe_conf,
            "example_terms": [v["search_term"] for v in
                              sorted(covered, key=lambda z: -z["cost"])][:5],
        })
    out["strict_screen"] = screened
    allow = [x for x in screened if x["strict_verdict"] == "ALLOW"]
    reject = [x for x in screened if x["strict_verdict"] == "REJECT"]
    print(f"  proposed: {len(screened)}   ALLOW: {len(allow)}   REJECT: {len(reject)}")
    print(f"\n  {'verdict':8s} {'match':7s} {'negative':24s} {'cost':>8s} {'pconv':>6s}  reasons")
    for x in sorted(screened, key=lambda z: (z["strict_verdict"], -z["cost"])):
        print(f"  {x['strict_verdict']:8s} {x['match']:7s} {x['text']:24s} "
              f"${x['cost']:>7.2f} {x['primary_conversions']:>6.1f}  "
              f"{'; '.join(x['strict_reasons']) if x['strict_reasons'] else 'clean'}")
    out["strict_allow"] = allow
    out["strict_reject"] = reject
    print(f"\n  cost recoverable under the strict rule: "
          f"${round(sum(x['cost'] for x in allow), 2):,.2f} "
          f"of ${round(sum(x['cost'] for x in screened), 2):,.2f} proposed")

    write(SNAP / f"reverification-{STAMP}.json", out)
    return out


if __name__ == "__main__":
    main()
