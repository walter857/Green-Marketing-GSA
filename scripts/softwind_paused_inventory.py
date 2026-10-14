#!/usr/bin/env python3
"""Rank every paused in-scope BOFU keyword in the Softwind account. Read-only.

The keyword inventory is byte-identical in both campaigns, so every paused ad
group exists twice. Ranking is done once per ad-group NAME, and ownership is
assigned to a single campaign so the two campaigns never compete for one query.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "paused-inventory-ranking-2026-08-25.json"
GEOS = ["1022729", "1023035", "1023415", "1023482",
        "9051836", "9052792", "9198508", "9214462"]

OUT_OF_SCOPE = re.compile(r"\b(roof|gutter|seal(ing|er)?|masonry|landscap|paint)\b", re.I)


def main() -> int:
    deep = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))
    dm = json.loads((SNAP / "demand-model-2026-08-25.json").read_text(encoding="utf-8"))
    AG = {a["id"]: a for a in deep["ad_groups"]}

    live_texts = {k["text"].lower() for k in deep["keywords"]
                  if k["status"] == "ENABLED" and AG[k["ad_group_id"]]["status"] == "ENABLED"}

    # group paused keyword texts by ad-group name
    paused = defaultdict(lambda: {"texts": set(), "campaigns": {}, "match_types": set()})
    for k in deep["keywords"]:
        g = AG[k["ad_group_id"]]
        if g["status"] == "ENABLED":
            continue
        e = paused[g["name"]]
        e["texts"].add(k["text"])
        e["match_types"].add(k["match_type"])
        e["campaigns"].setdefault(g["campaign_id"],
                                  {"campaign_name": g["campaign_name"],
                                   "ad_group_id": g["id"], "keyword_rows": 0})
        e["campaigns"][g["campaign_id"]]["keyword_rows"] += 1

    # RSA + URL state per paused ad group
    for name, e in paused.items():
        for cid, meta in e["campaigns"].items():
            gid = meta["ad_group_id"]
            ads = [a for a in deep["ads"] if a["ad_group_id"] == gid]
            meta["rsa_total"] = len(ads)
            meta["rsa_enabled_status"] = sum(1 for a in ads if a["status"] == "ENABLED")
            meta["rsa_approved"] = sum(1 for a in ads
                                       if a["approval_status"] == "APPROVED")
            meta["final_urls"] = sorted({u for a in ads for u in a["final_urls"]})

    # Planner demand for every paused text
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    kp = client.get_service("KeywordPlanIdeaService")
    all_texts = sorted({t for e in paused.values() for t in e["texts"]})
    planner = {}
    for i in range(0, len(all_texts), 20):
        req = client.get_type("GenerateKeywordIdeasRequest")
        req.customer_id = CID
        req.language = "languageConstants/1000"
        req.geo_target_constants.extend("geoTargetConstants/%s" % g for g in GEOS)
        req.include_adult_keywords = False
        req.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        req.keyword_seed.keywords.extend(all_texts[i:i + 20])
        want = {t.lower() for t in all_texts[i:i + 20]}
        try:
            for r in kp.generate_keyword_ideas(request=req):
                if r.text.lower() in want and r.text.lower() not in planner:
                    m = r.keyword_idea_metrics
                    planner[r.text.lower()] = {
                        "avg_monthly_searches": int(m.avg_monthly_searches),
                        "competition": enum_name(m.competition),
                        "low_bid": (m.low_top_of_page_bid_micros / 1_000_000
                                    if m.low_top_of_page_bid_micros else None),
                        "high_bid": (m.high_top_of_page_bid_micros / 1_000_000
                                     if m.high_top_of_page_bid_micros else None)}
        except Exception as exc:
            print("  planner batch error:", str(exc)[:160], file=sys.stderr)

    # historical search terms per paused ad group
    st_hist = defaultdict(list)
    met = json.loads((SNAP / "metrics-2026-08-25.json").read_text(encoding="utf-8"))
    for s in met["search_terms"]:
        st_hist[s["ad_group"]].append(s)

    # landing page readiness
    lp = json.loads((SNAP / "landing-pages-2026-08-25.json").read_text(encoding="utf-8"))
    lp_ok = {r["requested_url"].split("?")[0] for r in lp
             if not r.get("error") and r.get("http_status") == 200}

    rows = []
    for name, e in sorted(paused.items()):
        texts = sorted(e["texts"])
        demand = sum(planner.get(t.lower(), {}).get("avg_monthly_searches", 0)
                     for t in texts)
        best = max((planner.get(t.lower(), {}).get("avg_monthly_searches", 0)
                    for t in texts), default=0)
        bids = [planner[t.lower()]["high_bid"] for t in texts
                if planner.get(t.lower(), {}).get("high_bid")]
        overlap = sorted(t for t in texts if t.lower() in live_texts)
        urls = sorted({u for m in e["campaigns"].values() for u in m["final_urls"]})
        url_ready = all(u in lp_ok for u in urls) if urls else False
        hist = st_hist.get(name, [])
        out_of_scope_terms = [h["search_term"] for h in hist
                              if OUT_OF_SCOPE.search(h["search_term"])]
        rsa_ok = all(m["rsa_total"] >= 2 and m["rsa_approved"] == m["rsa_total"]
                     for m in e["campaigns"].values())

        # classification
        if overlap:
            cls, why = ("DUPLICATE",
                        "Keyword text is already live: %s. Enabling would put two ad "
                        "groups in the same auction for one query." % ", ".join(overlap))
        elif not url_ready:
            cls, why = ("LANDING PAGE NOT READY",
                        "Final URL did not return 200 in the browser audit: %s"
                        % ", ".join(urls))
        elif not rsa_ok:
            cls, why = ("LANDING PAGE NOT READY",
                        "Fewer than 2 approved RSAs present.")
        elif best >= 40:
            cls, why = ("ENABLE CANDIDATE",
                        "Best keyword carries %d local searches/month; ad group, "
                        "keywords and 2 approved RSAs already exist." % best)
        elif best >= 10:
            cls, why = ("KEEP PAUSED",
                        "Best keyword carries only %d local searches/month. Real intent, "
                        "too little volume to justify splitting a ~26 impression/day "
                        "pool further." % best)
        else:
            cls, why = ("LOW VOLUME",
                        "No keyword in this ad group reaches a reportable local volume "
                        "bucket (all below the Planner threshold).")
        if out_of_scope_terms and cls == "ENABLE CANDIDATE":
            why += (" CAUTION: historical search terms included out-of-scope queries "
                    "(%s); pair with negatives." % ", ".join(sorted(set(out_of_scope_terms))))

        rows.append({
            "ad_group_name": name,
            "classification": cls, "reason": why,
            "distinct_keyword_texts": len(texts),
            "keyword_texts": texts,
            "match_types": sorted(e["match_types"]),
            "best_keyword_local_monthly_searches": best,
            "summed_local_monthly_searches_uncollapsed": demand,
            "top_of_page_high_max": max(bids) if bids else None,
            "overlaps_live_keyword": overlap,
            "final_urls": urls, "landing_page_200": url_ready,
            "rsa_ok_in_all_campaigns": rsa_ok,
            "historical_impressions": sum(h["impressions"] for h in hist),
            "historical_clicks": sum(h["clicks"] for h in hist),
            "historical_out_of_scope_terms": sorted(set(out_of_scope_terms)),
            "exists_in_campaigns": e["campaigns"],
            "planner_detail": {t: planner.get(t.lower()) for t in texts},
        })

    rows.sort(key=lambda r: (-r["best_keyword_local_monthly_searches"], r["ad_group_name"]))
    result = {"paused_ad_group_count": len(rows),
              "distinct_paused_keyword_texts": len(all_texts),
              "note": ("Keyword inventory is byte-identical in both campaigns, so every "
                       "paused ad group exists twice. Ranking is per ad-group NAME."),
              "rankings": rows}
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("PAUSED AD GROUPS: %d   DISTINCT PAUSED KEYWORD TEXTS: %d"
          % (len(rows), len(all_texts)))
    print()
    for r in rows:
        print("%-36s %-24s best_vol=%-5s bid_high=%-8s texts=%-3d hist_impr=%d"
              % (r["ad_group_name"][:36], r["classification"],
                 r["best_keyword_local_monthly_searches"],
                 ("$%.2f" % r["top_of_page_high_max"]) if r["top_of_page_high_max"] else "-",
                 r["distinct_keyword_texts"], r["historical_impressions"]))
        print("    %s" % r["reason"])
        if r["overlaps_live_keyword"]:
            print("    overlap: %s" % r["overlaps_live_keyword"])
    print()
    from collections import Counter
    print("CLASSIFICATION COUNTS:", dict(Counter(r["classification"] for r in rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
