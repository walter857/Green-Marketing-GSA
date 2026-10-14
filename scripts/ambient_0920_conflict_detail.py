#!/usr/bin/env python3
"""Ambient | 2026-09-20 | Two follow-ups to the reachability test.

READ-ONLY. EXTERNAL WRITES: 0.

  1. The 2026-09-18 pass claimed shared list "General List" carries a BROAD
     negative "repair" that would block "boiler repair". Prove whether that list
     is attached to the campaign that will host the Boiler Repair ad group
     (24132507744). If it is not, the alarm was false and must be retracted.
     Also list, by name, every negative reaching 24132507744 that contains the
     token "boiler" or the token "repair", so the PASS verdict is inspectable
     rather than asserted.

  2. Characterise the 8 historically converting heating queries that no proposed
     ad group can serve, WITHOUT printing raw query text. Each is reduced to the
     service tokens it contains, so a coverage gap can be named as a service
     rather than as a search term.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21"
PLAN = "AMB-0921-HEAT-EXPAND-1"
BOILER_CAMPAIGN = "24132507744"
TOK = re.compile(r"[a-z0-9']+")


def toks(s):
    return TOK.findall(s.lower())


def blocks(nt, nm, qq):
    qv, nv = toks(qq), toks(nt)
    if not nv:
        return False
    if nm == "EXACT":
        return qv == nv
    if nm == "PHRASE":
        return any(qv[i:i + len(nv)] == nv for i in range(len(qv) - len(nv) + 1))
    return all(t in qv for t in nv)


def main():
    c = client()
    identity_gate(c, verbose=False)
    plan = json.loads((PLANS / f"{PLAN}.json").read_text(encoding="utf-8"))
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0}

    # ---------------------------------------------------------------- part 1
    print(f"=== 1. WHAT IS ATTACHED TO CAMPAIGN {BOILER_CAMPAIGN}? ===")
    att = []
    for r in q(c, f"""SELECT campaign.id, campaign.name, shared_set.id, shared_set.name,
                      shared_set.type, campaign_shared_set.status
                      FROM campaign_shared_set
                      WHERE campaign.id = {BOILER_CAMPAIGN}"""):
        att.append({"shared_set_id": str(r.shared_set.id), "name": r.shared_set.name,
                    "type": E(r.shared_set.type_),
                    "link_status": E(r.campaign_shared_set.status)})
    for a in att:
        print(f"   {a['shared_set_id']}  {a['link_status']:8s} {a['type']:20s} {a['name']}")
    out["shared_sets_on_boiler_campaign"] = att

    names = {a["name"] for a in att if a["link_status"] == "ENABLED"}
    print(f"\n   'General List' attached to {BOILER_CAMPAIGN}? "
          f"{'YES' if 'General List' in names else 'NO'}")
    print(f"   'General' attached to {BOILER_CAMPAIGN}?      "
          f"{'YES' if 'General' in names else 'NO'}")
    out["general_list_attached_to_boiler_campaign"] = "General List" in names

    # every negative reaching that campaign, filtered to the two tokens of interest
    reaching = []
    for r in q(c, f"""SELECT campaign_criterion.keyword.text,
                      campaign_criterion.keyword.match_type
                      FROM campaign_criterion
                      WHERE campaign.id = {BOILER_CAMPAIGN}
                        AND campaign_criterion.type = 'KEYWORD'
                        AND campaign_criterion.negative = TRUE"""):
        reaching.append((f"campaign:{BOILER_CAMPAIGN}",
                         r.campaign_criterion.keyword.text,
                         E(r.campaign_criterion.keyword.match_type)))
    ids = [a["shared_set_id"] for a in att if a["link_status"] == "ENABLED"]
    # account-level negatives apply even though they attach to no campaign
    for r in q(c, """SELECT shared_set.id, shared_set.name, shared_set.type
                     FROM shared_set
                     WHERE shared_set.type = 'ACCOUNT_LEVEL_NEGATIVE_KEYWORDS'
                       AND shared_set.status != 'REMOVED'"""):
        ids.append(str(r.shared_set.id))
    for sid in set(ids):
        for r in q(c, f"""SELECT shared_set.id, shared_set.name,
                          shared_criterion.keyword.text,
                          shared_criterion.keyword.match_type
                          FROM shared_criterion
                          WHERE shared_set.id = {sid}
                            AND shared_criterion.type = 'KEYWORD'"""):
            reaching.append((f"shared:{r.shared_set.name[:26]}",
                             r.shared_criterion.keyword.text,
                             E(r.shared_criterion.keyword.match_type)))
    print(f"\n   negatives reaching {BOILER_CAMPAIGN}: {len(reaching)}")
    interesting = [(s, t, m) for s, t, m in reaching
                   if "boiler" in t.lower() or "repair" in t.lower()]
    print(f"   of those, containing 'boiler' or 'repair': {len(interesting)}")
    for s, t, m in sorted(interesting)[:60]:
        hit = [k for k in plan["new_ad_groups"]["SKAG | Boiler Repair"]["phrase"]
               + plan["new_ad_groups"]["SKAG | Boiler Repair"]["exact"] if blocks(t, m, k)]
        print(f"      {m:7s} '{t[:46]}'  from {s}"
              + (f"   >>> BLOCKS {hit}" if hit else ""))
    out["boiler_or_repair_negatives_reaching"] = [
        {"source": s, "text": t, "match": m} for s, t, m in interesting]
    out["any_of_them_blocks_a_boiler_keyword"] = any(
        blocks(t, m, k) for s, t, m in interesting
        for k in plan["new_ad_groups"]["SKAG | Boiler Repair"]["phrase"]
        + plan["new_ad_groups"]["SKAG | Boiler Repair"]["exact"])
    print(f"\n   VERDICT blocked: {out['any_of_them_blocks_a_boiler_keyword']}")

    # ---------------------------------------------------------------- part 2
    print("\n=== 2. CONVERTING HEATING QUERIES WITH NO ELIGIBLE AD GROUP ===")
    terms = {}
    for r in q(c, """SELECT search_term_view.search_term, metrics.conversions,
                     metrics.cost_micros, metrics.clicks
                     FROM search_term_view
                     WHERE segments.date BETWEEN '2024-01-01' AND '2026-09-19'
                       AND metrics.conversions > 0"""):
        t = r.search_term_view.search_term.lower()
        a = terms.setdefault(t, {"conv": 0.0, "cost": 0.0, "clicks": 0})
        a["conv"] += r.metrics.conversions
        a["cost"] += r.metrics.cost_micros / 1e6
        a["clicks"] += r.metrics.clicks
    heatwords = ("furnace", "boiler", "heat pump", "heatpump", "mini split", "minisplit",
                 "ductless", "geothermal", "tankless", "oil heat", "heating", "radiator",
                 "baseboard", "water heater")
    EXISTING_NEG = {
        "SKAG | Furnace Repair": plan["cross_negatives"]["SKAG | Furnace Repair"]["negatives"],
        "SKAG | Mini Split Installation": plan["cross_negatives"]["SKAG | Mini Split Installation"]["negatives"],
        "SKAG | Gas Boiler Repair": plan["cross_negatives"]["SKAG | Gas Boiler Repair"]["negatives"],
    }
    EXISTING_KW = {}
    for ag, agid in (("SKAG | Furnace Repair", 199797580706),
                     ("SKAG | Mini Split Installation", 199797580746),
                     ("SKAG | Gas Boiler Repair", 202339087594)):
        ks = []
        for r in q(c, f"""SELECT ad_group_criterion.keyword.text,
                          ad_group_criterion.keyword.match_type
                          FROM ad_group_criterion
                          WHERE ad_group.id = {agid}
                            AND ad_group_criterion.type = 'KEYWORD'
                            AND ad_group_criterion.negative = FALSE
                            AND ad_group_criterion.status != 'REMOVED'"""):
            ks.append((r.ad_group_criterion.keyword.text,
                       E(r.ad_group_criterion.keyword.match_type)))
        EXISTING_KW[ag] = ks

    # Service tokens only. Raw query text is never printed or written.
    SERVICE_TOKENS = ("furnace", "boiler", "gas", "oil", "heat pump", "mini split",
                      "ductless", "geothermal", "tankless", "water heater", "radiator",
                      "baseboard", "heating", "repair", "install", "replace", "service",
                      "maintenance", "tune up", "emergency", "cost", "near me")
    uncovered, covered = [], 0
    for t, a in terms.items():
        if not any(w in t for w in heatwords):
            continue
        homes = []
        for ag, d in plan["new_ad_groups"].items():
            if any(blocks(n, "PHRASE", t) for n in plan["cross_negatives"][ag]["negatives"]):
                continue
            if any(blocks(k, "PHRASE", t) for k in d["phrase"]) or t in d["exact"]:
                homes.append(ag)
        for ag, negs in EXISTING_NEG.items():
            if any(blocks(n, "PHRASE", t) for n in negs):
                continue
            if any(blocks(k, "PHRASE", t) if m == "PHRASE" else toks(k) == toks(t)
                   for k, m in EXISTING_KW[ag]):
                homes.append(ag + " (existing)")
        if homes:
            covered += 1
        else:
            uncovered.append({"service_tokens": sorted(w for w in SERVICE_TOKENS if w in t),
                              "word_count": len(toks(t)),
                              "conversions": round(a["conv"], 2),
                              "cost": round(a["cost"], 2), "clicks": a["clicks"]})
    uncovered.sort(key=lambda x: -x["conversions"])
    print(f"   covered by at least one ad group: {covered}")
    print(f"   NOT covered: {len(uncovered)}  (shown as service tokens only)")
    for u in uncovered:
        print(f"      conv {u['conversions']:5.2f}  ${u['cost']:8.2f}  {u['clicks']:3d}cl  "
              f"tokens={u['service_tokens']}")
    out["uncovered_converting_heating_queries"] = uncovered
    out["covered_count"] = covered
    out["raw_terms_retained"] = False

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"conflict-detail-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
