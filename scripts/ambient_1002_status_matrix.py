#!/usr/bin/env python3
"""Ambient | 2026-10-02 | Status matrix for every ad group in the ENABLED Search campaigns. Reads snapshot-2026-10-02.json only.

Category per ad group (zero impressions is never read as 'paused'):
  ENABLED_ELIGIBLE, ENABLED_NO_SERVABLE_ADS, ENABLED_NO_ENABLED_KEYWORDS, PENDING_APPROVAL, DISAPPROVED, PAUSED,
  HELD (holding label with a business/page reason), LOW_VOLUME (eligible but keywords rarely served / tiny demand).
Writes reports/ambient-cooling-heating/2026-10-02-status-matrix.md.
"""
from __future__ import annotations
import json, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / "clients" / "ambient-cooling-heating" / "snapshots" / "snapshot-2026-10-02.json").read_text(encoding="utf-8"))
C, G = S["campaigns"], S["ad_groups"]
ENABLED = [k for k, v in C.items() if v["status"] == "ENABLED" and v["channel"] == "SEARCH"]
HOLD_REASON = {"WAITING_LP": "landing page missing or defective", "WAITING_AVAILABILITY": "availability unverified", "DEFERRED_BUDGET": "owner budget deferral 2026-09-25",
               "EVALUATE_DUCTLESS": "owner: evaluate ductless before launch", "GEOTHERMAL_TEST": "$20/day geothermal test", "CORE_ACTIVE": "core service",
               "WAITING_TRACKING": "tracking gate", "WAITING_POLICY": "policy gate"}
perf = S["performance"]["ad_group_daily"]


def served(gid, a, b):
    t = collections.Counter()
    for k, v in perf.items():
        g, d = k.split("|")
        if g == gid and a <= d <= b:
            t.update({m: v[m] for m in ("impr", "clicks", "cost")})
    return t


rows = []
for cid in sorted(ENABLED, key=lambda k: C[k]["name"]):
    camp = C[cid]
    sched = len(S["campaign_criteria"].get(cid, {}).get("AD_SCHEDULE", []))
    tab = [d for d in S["campaign_criteria"].get(cid, {}).get("DEVICE", []) if d["device"] == "TABLET"]
    tablet = "tablet -100%" if tab and tab[0]["bid_modifier_set"] and tab[0]["bid_modifier"] == 0.0 else "TABLET NOT EXCLUDED"
    for gid, g in sorted(((k, v) for k, v in G.items() if v["campaign"] == cid), key=lambda kv: kv[1]["name"]):
        kws = [k for k in S["keywords"] if k["ad_group"] == gid and not k["negative"]]
        ads = [a for a in S["ads"] if a["ad_group"] == gid]
        en_kw = [k for k in kws if k["status"] == "ENABLED"]
        en_ads = [a for a in ads if a["status"] == "ENABLED"]
        appr = [a for a in en_ads if a["approval"] in ("APPROVED", "APPROVED_LIMITED")]
        review = [a for a in ads if a["review"] in ("REVIEW_IN_PROGRESS",) or a["approval"] == "UNKNOWN"]
        disap = [a for a in en_ads if a["approval"] == "DISAPPROVED"]
        urls = sorted({u for a in en_ads for u in a["urls"]})
        low = [k for k in en_kw if k["serving"] in ("RARELY_SERVED",) or "LOW_SEARCH_VOLUME" in " ".join(k["reasons"]) or "RARELY_SERVED" in " ".join(k["reasons"])]
        s30 = served(gid, "2026-09-24", "2026-10-01")
        sep = served(gid, "2026-09-01", "2026-09-30")
        labels = [l for l in g["labels"]]
        if g["status"] != "ENABLED":
            cat = "PAUSED"
        elif camp["primary"] == "NOT_ELIGIBLE" and not en_ads and any(l in ("WAITING_LP", "WAITING_AVAILABILITY", "DEFERRED_BUDGET", "EVALUATE_DUCTLESS") for l in labels):
            cat = "HELD"
        elif not en_ads and review:
            cat = "PENDING (new ads paused, under review)"
        elif not en_ads:
            cat = "HELD" if any(l in HOLD_REASON and l != "CORE_ACTIVE" for l in labels) else "ENABLED_NO_SERVABLE_ADS"
        elif disap and not appr:
            cat = "DISAPPROVED"
        elif not en_kw:
            cat = "ENABLED_NO_ENABLED_KEYWORDS"
        elif low and len(low) == len(en_kw):
            cat = "ENABLED_ELIGIBLE - LOW SEARCH VOLUME"
        else:
            cat = "ENABLED_ELIGIBLE"
        rows.append(dict(campaign=camp["name"][18:58], cid=cid, camp_status=f"{camp['status']}/{camp['primary']}", camp_reasons=camp["reasons"],
                         budget=camp["budget"], ceiling=camp["ceiling"], ad_group=g["name"][7:], gid=gid, ag_status=f"{g['status']}/{g['primary']}",
                         ag_reasons=g["reasons"], kw=f"{len(en_kw)}/{len(kws)} enabled" + (f", {len(low)} low-volume" if low else ""),
                         kw_status=sorted({(k['serving'], ','.join(k['reasons'][:2])) for k in en_kw})[:3],
                         ads=f"{len(en_ads)} enabled ({len(appr)} approved){', ' + str(len(review)) + ' under review' if review else ''}", urls=urls,
                         labels=labels, schedule=f"{sched} rows Mon-Fri 08-16", device=tablet, s30=dict(s30), sep=dict(sep), category=cat))
lines = [f"# Ad-group status matrix - Ambient Cooling - Live (2401959466), snapshot read {S['read_local'][:16].replace('T', ' ') + ' ET'}", "",
         "Every ad group in the 8 ENABLED Search campaigns. Serving evidence: impressions / clicks / cost 2026-09-24..10-01 (Sept total in brackets).",
         "Google primary-status reasons are quoted as returned. Zero impressions alone is never treated as 'paused'.", "",
         "| Campaign | Ad group (ID) | Category | Campaign status / reasons | Ad group status / reasons | Keywords | Ads | Final URL | Labels | 09-24..10-01 (Sept) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    s, sp = r["s30"], r["sep"]
    lines.append(f"| {r['campaign']} ({r['cid']}) ${r['budget']} ceil ${r['ceiling']} | {r['ad_group']} ({r['gid']}) | **{r['category']}** | {r['camp_status']} {r['camp_reasons']} | "
                 f"{r['ag_status']} {r['ag_reasons']} | {r['kw']} {r['kw_status']} | {r['ads']} | {', '.join(u.replace('https://offer.ambientcoolingandheating.com', 'offer') for u in r['urls']) or '-'} | "
                 f"{', '.join(r['labels']) or '-'} | {s.get('impr', 0)} / {s.get('clicks', 0)} / ${s.get('cost', 0):.2f} ({sp.get('impr', 0)} / ${sp.get('cost', 0):.2f}) |")
(ROOT / "reports" / "ambient-cooling-heating" / "2026-10-02-status-matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(collections.Counter(r["category"] for r in rows))
for r in rows:
    print(f"{r['cid'][-4:]} {r['ad_group'][:30]:30s} {r['category'][:38]:38s} kw {r['kw']:28s} ads {r['ads']:38s} lbl {r['labels']} ag {r['ag_reasons'][:3]} s {r['s30'].get('impr',0)}i/${r['s30'].get('cost',0):.0f} sep {r['sep'].get('impr',0)}i")
