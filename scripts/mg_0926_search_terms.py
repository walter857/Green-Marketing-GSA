#!/usr/bin/env python3
"""2026-09-26 Master Grass search-term classification. LOCAL ONLY, no API calls.

Raw terms stay on disk. stdout carries aggregates, category labels and town names only.
Reuses the agency SHARED disqualifiers and PROTECTED list from neg_lexicon without
modifying that module (other accounts' pending plans fingerprint its outputs).

Writes:
  reports/mastergrass-lawn-care/st/verdicts.csv          one row per unique term (live campaigns)
  reports/mastergrass-lawn-care/st/negative-candidates.csv  proposed negatives + guard results
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from neg_lexicon import PROTECTED, classify, compile_account  # noqa: E402

SNAP = ROOT / "clients" / "mastergrass-lawn-care" / "snapshots" / "audit-2026-09-26"
OUT = ROOT / "reports" / "mastergrass-lawn-care" / "st"
OUT.mkdir(parents=True, exist_ok=True)

LIVE = {"23905193676": "Landscaping Search - BOFU", "23914692658": "Hardscaping Search - BOFU"}

# Towns inside the live campaigns' location targets (Ames + 21 ZIPs, read 2026-09-26), plus
# Des Moines-metro names the advertiser already bids on or names in ads. Recorded, not guessed.
GEO_IN = (r"\b(ames|ankeny|altoona|des moines|dsm|west des moines|johnston|urbandale|grimes|"
          r"alleman|cambridge|colo|elkhart|ellsworth|gilbert|hubbard|huxley|mccallsburg|maxwell|"
          r"nevada|polk city|radcliffe|roland|slater|story city|zearing|saylorville|"
          r"central iowa|story county|polk county|iowa|ia)\b")
# Out-of-area names only where they are unambiguous and far from the target ZIPs.
GEO_OUT = (r"\b(cedar rapids|iowa city|davenport|sioux city|waterloo|cedar falls|council bluffs|"
           r"dubuque|mason city|fort dodge|ottumwa|burlington|omaha|minneapolis|st paul|"
           r"kansas city|chicago|nebraska|minnesota|missouri|illinois|wisconsin|south dakota|"
           r"kansas|colorado|texas|florida|california)\b")

MASTERGRASS = {
    "slug": "mastergrass-lawn-care",
    "customer_id": "9487471092",
    "geo_verified": True,
    "brand": r"\bmaster ?grass\b",
    # Whitelist: services these two live campaigns actually sell (keywords + ads + final URLs).
    "core": (r"\b(landscap\w*|hardscap\w*|paver\w*|patio\w*|retaining|wall|walls|fire ?pits?|"
             r"firepits?|outdoor kitchens?|outdoor living|french drains?|drain\w*|grading|grade|"
             r"regrad\w*|leveling|levelling|level|mulch\w*|rock|rocks|landscape beds?|"
             r"flower beds?|borders?|edging|walkways?)\b"),
    "intent": (r"\b(contractors?|compan(y|ies)|services?|install\w*|builders?|build|construction|"
               r"near me|nearby|quotes?|estimates?|costs?|prices?|pricing|hire|best|local|pros?|"
               r"professionals?|residential|experts?|specialists?|landscapers?|installers?|"
               r"design|designers?|solutions?|fix|repair)\b|" + GEO_IN),
    "disqualify": {
        # Kept deliberately narrow; anything uncertain falls to WATCH, never NEGATIVE.
        "MATERIALS_SUPPLY": (r"\b(supply|supplies|supplier|suppliers|wholesale|quarry|menards|"
                             r"home depot|lowes|for sale|per ton|by the ton|bulk)\b"),
        "IDEAS_INSPIRATION": r"\b(ideas?|inspiration|pictures?|photos?|images?|pinterest)\b",
    },
    "geo_in": GEO_IN,
    "geo_out": GEO_OUT,
}
# Services Master Grass may sell but these two campaigns do not advertise. Never a NEGATIVE
# verdict here: routed to a separate owner decision.
OTHER_MG_SERVICE = re.compile(
    r"\b(lawn|mow\w*|fertiliz\w*|weed\w*|aerat\w*|overseed\w*|seeding|sod|irrigation|"
    r"sprinklers?|snow|leaf|leaves|christmas lights?|tree|trees|shrubs?|bush\w*|hedge\w*)\b", re.I)

TOKEN_RE = re.compile(r"[a-z0-9']+")


def toks(s):
    return TOKEN_RE.findall(s.lower())


def contiguous(sub, seq):
    n = len(sub)
    return any(seq[i:i + n] == sub for i in range(len(seq) - n + 1)) if n and n <= len(seq) else False


def blocks(neg, mt, q):
    if mt == "EXACT":
        return neg == q
    if mt == "PHRASE":
        return contiguous(neg, q)
    return set(neg) <= set(q)


comp = compile_account(MASTERGRASS)
rows = json.loads((SNAP / "search_terms_all.json").read_text(encoding="utf-8"))
WIN = {"all": ("2000-01-01", "2099-01-01"), "l90": ("2026-06-28", "2026-09-26"),
       "l30": ("2026-08-27", "2026-09-26"), "l7": ("2026-09-19", "2026-09-26")}

agg = defaultdict(lambda: defaultdict(lambda: [0, 0, 0.0, 0.0]))  # term -> win -> [imp, clk, cost, conv]
term_camps = defaultdict(set)
mt_cost = Counter()
acct_cost = 0.0
for r in rows:
    cid = r["campaign"]["id"]
    m = r["metrics"]
    cost = int(m.get("cost_micros", 0)) / 1e6
    acct_cost += cost
    if cid not in LIVE:
        continue
    t = r["search_term_view"]["search_term"].lower().strip()
    d = r["segments"]["date"]
    term_camps[t].add(cid)
    for w, (a, b) in WIN.items():
        if a <= d <= b:
            x = agg[t][w]
            x[0] += int(m.get("impressions", 0)); x[1] += int(m.get("clicks", 0))
            x[2] += cost; x[3] += m.get("conversions", 0)
    if WIN["l90"][0] <= d:
        mt_cost[r["segments"].get("search_term_match_type", "?")] += cost

verdict = {}
for t, w in agg.items():
    if OTHER_MG_SERVICE.search(t) and not comp["core"].search(t):
        v, cat = "WATCH", "OTHER_MASTER_GRASS_SERVICE"
    else:
        v, cat = classify(t, comp)
    if w["all"][3] > 0 and v == "NEGATIVE":
        v, cat = "KEEP", "CONVERSION_GUARD_OVERRIDE"
    verdict[t] = (v, cat)

print(f"search-term rows on disk: {len(rows)} | live-campaign unique terms: {len(agg)}")
print(f"account search-term cost all-time ${acct_cost:,.2f}")
for w in ("all", "l90", "l30", "l7"):
    tot = [0, 0, 0.0, 0.0]
    by = defaultdict(lambda: [0, 0, 0, 0.0, 0.0])
    for t, x in agg.items():
        if x[w][0] == 0 and x[w][2] == 0:
            continue
        v, cat = verdict[t]
        b = by[(v, cat)]
        b[0] += 1; b[1] += x[w][0]; b[2] += x[w][1]; b[3] += x[w][2]; b[4] += x[w][3]
        for i in range(4):
            tot[i] += x[w][i]
    print(f"\n=== window {w}: terms {sum(b[0] for b in by.values())} imp {tot[0]} clk {tot[1]} "
          f"cost ${tot[2]:,.2f} conv {tot[3]:g} ===")
    for (v, cat), b in sorted(by.items(), key=lambda kv: -kv[1][3]):
        share = (b[3] / tot[2] * 100) if tot[2] else 0
        print(f"  {v:<8} {cat:<30} terms {b[0]:>5} imp {b[1]:>6} clk {b[2]:>4} "
              f"${b[3]:>9,.2f} ({share:4.1f}%) conv {b[4]:g}")

print("\n=== live-campaign search-term cost by match type, last 90 days ===")
for k, v in mt_cost.most_common():
    print(f"  {k:<14} ${v:,.2f}")

# Towns named inside terms (town names are allowed on stdout).
town = Counter()
town_cost = Counter()
for t, x in agg.items():
    for mt in re.finditer(GEO_IN + "|" + GEO_OUT, t):
        town[mt.group(0)] += 1
        town_cost[mt.group(0)] += x["all"][2]
print("\n=== place names inside live-campaign terms (all-time): terms / cost ===")
for k, v in town.most_common(25):
    print(f"  {k:<18} {v:>4}  ${town_cost[k]:,.2f}")

# ---- write verdicts ------------------------------------------------------------
with (OUT / "verdicts.csv").open("w", newline="", encoding="utf-8") as fh:
    wr = csv.writer(fh)
    wr.writerow(["term", "verdict", "category", "campaigns", "imp_all", "clk_all", "cost_all", "conv_all",
                 "clk_l30", "cost_l30", "clk_l7", "cost_l7"])
    for t, x in sorted(agg.items(), key=lambda kv: -kv[1]["all"][2]):
        v, cat = verdict[t]
        wr.writerow([t, v, cat, "|".join(LIVE[c] for c in sorted(term_camps[t])),
                     x["all"][0], x["all"][1], round(x["all"][2], 2), x["all"][3],
                     x["l30"][1], round(x["l30"][2], 2), x["l7"][1], round(x["l7"][2], 2)])

# ---- negative candidates ---------------------------------------------------------
keepish = {t for t, (v, _) in verdict.items() if v in ("KEEP", "WATCH")}
conv_terms = {t for t, x in agg.items() if x["all"][3] > 0}
kw = json.loads((SNAP / "keywords.json").read_text(encoding="utf-8"))
live_pos = {r["ad_group_criterion"]["keyword"]["text"].lower() for r in kw
            if r["campaign"]["id"] in LIVE and not r["ad_group_criterion"].get("negative")
            and r["ad_group_criterion"].get("status") == "ENABLED"}
# Negatives already present on the live campaigns (campaign + ad-group level).
existing = set()
for r in json.loads((SNAP / "campaign_criteria.json").read_text(encoding="utf-8")):
    cc = r["campaign_criterion"]
    if r["campaign"]["id"] in LIVE and cc.get("negative") and cc.get("keyword"):
        existing.add((cc["keyword"]["text"].lower().strip('"[] '), cc["keyword"].get("match_type")))
for r in kw:
    a = r["ad_group_criterion"]
    if r["campaign"]["id"] in LIVE and a.get("negative"):
        existing.add((a["keyword"]["text"].lower().strip('"[] '), a["keyword"].get("match_type")))

keep_tok = {t: toks(t) for t in keepish}
conv_tok = {t: toks(t) for t in conv_terms}
pos_tok = [toks(p) for p in live_pos]
prot_tok = [toks(p) for p in PROTECTED]


def guard(neg, mt):
    nt = toks(neg)
    if not nt or len(nt) > 10 or len(neg) > 80:
        return "length"
    if neg in PROTECTED or any(nt == p for p in prot_tok):
        return "protected_phrase"
    if any(blocks(nt, mt, tt) for tt in keep_tok.values()):
        return "blocks_keep_or_watch"
    if any(blocks(nt, mt, tt) for tt in conv_tok.values()):
        return "blocks_converting_term"
    if any(blocks(nt, mt, pt) for pt in pos_tok):
        return "blocks_live_keyword"
    if any(neg == e[0] for e in existing):
        return "already_negative"
    return "ok"


cands = {}
for t, (v, cat) in verdict.items():
    if v != "NEGATIVE":
        continue
    x = agg[t]["all"]
    # (a) phrase root = the disqualifier / shared-lexicon span that fired
    root = None
    for rx in list(comp["disqualify"].values()) + list(comp["shared"].values()) + [comp["geo_out"]]:
        mt_ = rx.search(" " + t + " ")
        if mt_ and cat != "OUT_OF_SCOPE_NO_CORE_SERVICE":
            root = mt_.group(0).strip()
            break
    if root:
        c = cands.setdefault((root, "PHRASE"), {"cat": cat, "terms": 0, "cost": 0.0, "clk": 0})
        c["terms"] += 1; c["cost"] += x[2]; c["clk"] += x[1]
    elif x[2] > 0:
        # (b) out-of-scope with spend: exact negative on the full query only
        c = cands.setdefault((t, "EXACT"), {"cat": cat, "terms": 0, "cost": 0.0, "clk": 0})
        c["terms"] += 1; c["cost"] += x[2]; c["clk"] += x[1]

res = Counter()
res_cost = Counter()
with (OUT / "negative-candidates.csv").open("w", newline="", encoding="utf-8") as fh:
    wr = csv.writer(fh)
    wr.writerow(["negative", "match_type", "category", "guard", "terms_blocked", "clicks_all", "cost_all"])
    for (neg, mt), c in sorted(cands.items(), key=lambda kv: -kv[1]["cost"]):
        g = guard(neg, mt)
        res[(c["cat"], mt, g)] += 1
        res_cost[(c["cat"], mt, g)] += c["cost"]
        wr.writerow([neg, mt, c["cat"], g, c["terms"], c["clk"], round(c["cost"], 2)])
print("\n=== negative candidates (category, match, guard): count / all-time cost ===")
for k, v in sorted(res.items(), key=lambda kv: -res_cost[kv[0]]):
    print(f"  {k[0]:<30} {k[1]:<6} {k[2]:<24} {v:>4}  ${res_cost[k]:,.2f}")
print(f"\nexisting negatives on live campaigns (campaign + ad group): {len(existing)}")
print(f"live enabled positive keywords: {len(live_pos)}")
print("wrote", (OUT / "verdicts.csv").relative_to(ROOT), "and", (OUT / "negative-candidates.csv").relative_to(ROOT))
