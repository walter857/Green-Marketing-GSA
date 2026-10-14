#!/usr/bin/env python3
"""Reconcile the supplied 'Ambient Searched Terms.csv' against the live API, and answer the
out-of-state question. Aggregates to stdout; detail to disk."""
from __future__ import annotations
import sys, json, csv, re, hashlib
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa

SRC = Path(r"C:\Users\walte\Downloads\Ambient Searched Terms.csv")
print("source:", SRC)
print("sha256:", hashlib.sha256(SRC.read_bytes()).hexdigest())

raw = SRC.read_text(encoding="utf-8-sig").splitlines()
print("physical lines:", len(raw))
print("line0 (report name):", raw[0])
print("line1 (date range):", raw[1])

rdr = csv.DictReader(raw[2:])
rows = list(rdr)
print("parsed data rows:", len(rows))


def num(s):
    if s is None:
        return 0.0
    s = s.strip().replace(",", "").replace("$", "").replace("%", "")
    if s in ("", "--", "-"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


total_row = [r for r in rows if (r.get("Search term") or "").strip().lower().startswith("total")]
data_rows = [r for r in rows if r not in total_row]
print("\nGoogle 'Total' rows found:", len(total_row))
for t in total_row:
    print("   ", {k: v for k, v in t.items() if v not in (None, "")})
print("displayed search-term rows:", len(data_rows))

sums = {
    "clicks": sum(num(r.get("Clicks")) for r in data_rows),
    "impressions": sum(num(r.get("Impr.")) for r in data_rows),
    "cost": round(sum(num(r.get("Cost")) for r in data_rows), 2),
    "conversions": round(sum(num(r.get("Conversions")) for r in data_rows), 2),
}
print("\nSUM OF DISPLAYED ROWS:", sums)
if total_row:
    t = total_row[0]
    gt = {"clicks": num(t.get("Clicks")), "impressions": num(t.get("Impr.")),
          "cost": round(num(t.get("Cost")), 2), "conversions": round(num(t.get("Conversions")), 2)}
    print("GOOGLE TOTAL ROW      :", gt)
    print("DELTA (google - sum)  :", {k: round(gt[k] - sums[k], 2) for k in gt})

print("\nby campaign (displayed rows):")
bc = defaultdict(lambda: {"rows": 0, "clicks": 0.0, "impr": 0.0, "cost": 0.0, "conv": 0.0})
for r in data_rows:
    b = bc[(r.get("Campaign") or "?")[:46]]
    b["rows"] += 1
    b["clicks"] += num(r.get("Clicks"))
    b["impr"] += num(r.get("Impr."))
    b["cost"] += num(r.get("Cost"))
    b["conv"] += num(r.get("Conversions"))
for k, v in sorted(bc.items()):
    print(f"   {k:<48} rows={v['rows']:<5} impr={int(v['impr']):<6} clicks={int(v['clicks']):<4} "
          f"${v['cost']:.2f} conv={v['conv']:.1f}")

print("\nby Added/Excluded status (displayed rows):")
print("  ", dict(Counter((r.get("Added/Excluded") or "").strip() for r in data_rows)))
print("by Match type:")
print("  ", dict(Counter((r.get("Match type") or "").strip() for r in data_rows)))
print("by Ad group:")
print("  ", dict(Counter((r.get("Ad group") or "").strip()[:44] for r in data_rows)))
print("by Keyword:")
print("  ", dict(Counter((r.get("Keyword") or "").strip()[:44] for r in data_rows)))

# ------------------------------------------------------------------
# THE OUT-OF-STATE QUESTION: is the geography in the QUERY TEXT?
# ------------------------------------------------------------------
STATES = {
    "florida": r"\b(florida|fl)\b", "new york": r"\b(new york|ny|nyc|brooklyn|queens|bronx|manhattan)\b",
    "tennessee": r"\b(tennessee|tn|nashville|memphis|knoxville|chattanooga)\b",
    "texas": r"\b(texas|tx|houston|dallas|austin|san antonio|fort worth)\b",
    "california": r"\b(california|ca|los angeles|san diego|san francisco|sacramento)\b",
    "virginia": r"\b(virginia|va|richmond|norfolk|arlington|alexandria)\b",
    "pennsylvania": r"\b(pennsylvania|pa|philadelphia|pittsburgh)\b",
    "new jersey": r"\b(new jersey|nj|newark|jersey city)\b",
    "delaware": r"\b(delaware|de)\b",
    "north carolina": r"\b(north carolina|nc|charlotte|raleigh)\b",
    "south carolina": r"\b(south carolina|sc|charleston|columbia sc)\b",
    "georgia": r"\b(georgia|ga|atlanta|savannah)\b",
    "ohio": r"\b(ohio|oh|columbus|cleveland|cincinnati)\b",
    "illinois": r"\b(illinois|il|chicago)\b",
    "arizona": r"\b(arizona|az|phoenix|tucson)\b",
    "washington dc": r"\b(washington dc|dc|district of columbia)\b",
    "west virginia": r"\b(west virginia|wv)\b",
    "massachusetts": r"\b(massachusetts|ma|boston)\b",
    "michigan": r"\b(michigan|mi|detroit)\b",
    "colorado": r"\b(colorado|co|denver)\b",
    "nevada": r"\b(nevada|nv|las vegas)\b",
    "missouri": r"\b(missouri|mo|kansas city|st louis)\b",
    "minnesota": r"\b(minnesota|mn|minneapolis)\b",
    "wisconsin": r"\b(wisconsin|wi|milwaukee)\b",
    "indiana": r"\b(indiana|in|indianapolis)\b",
    "alabama": r"\b(alabama|al|birmingham|montgomery)\b",
    "louisiana": r"\b(louisiana|la|new orleans|baton rouge)\b",
    "oklahoma": r"\b(oklahoma|ok|tulsa)\b",
    "oregon": r"\b(oregon|or|portland)\b",
    "utah": r"\b(utah|ut|salt lake)\b",
    "kentucky": r"\b(kentucky|ky|louisville|lexington)\b",
    "connecticut": r"\b(connecticut|ct|hartford)\b",
}
MD = re.compile(r"\b(maryland|md|annapolis|arnold|bowie|catonsville|crofton|edgewater|elkridge|"
                r"ellicott|meade|fulton|gambrills|glen burnie|gwynn oak|halethorpe|hanover|jessup|"
                r"laurel|linthicum|timonium|odenton|pasadena|severn|severna|columbia|baltimore|"
                r"howard county|anne arundel|millersville|riva|davidsonville|clarksville|"
                r"hunt valley|lutherville|towson|dundalk|essex|parkville|pikesville|owings mills|"
                r"randallstown|reisterstown|windsor mill|woodlawn|middle river|white marsh|"
                r"perry hall|nottingham|rosedale|brooklyn park|curtis bay|ferndale|harmans|"
                r"harwood|lothian|shady side|churchton|deale|galesville|west river|mayo|"
                r"cape st claire|crownsville|gibson island|sherwood forest|highland|"
                r"savage|maryland city|north laurel|scaggsville|simpsonville|west friendship|"
                r"woodbine|dayton|glenelg|glenwood|lisbon|marriottsville|cooksville|"
                r"waterloo|hollofield|oella|relay|arbutus|lansdowne|baltimore highlands)\b", re.I)

geo_hits = defaultdict(lambda: {"rows": 0, "clicks": 0.0, "impr": 0.0, "cost": 0.0})
md_hits = {"rows": 0, "clicks": 0.0, "cost": 0.0}
no_geo = {"rows": 0, "clicks": 0.0, "cost": 0.0}
detail = []
for r in data_rows:
    term = (r.get("Search term") or "").strip().lower()
    cl, co, im = num(r.get("Clicks")), num(r.get("Cost")), num(r.get("Impr."))
    hit = None
    for st, pat in STATES.items():
        if re.search(pat, term):
            hit = st
            break
    if MD.search(term):
        md_hits["rows"] += 1
        md_hits["clicks"] += cl
        md_hits["cost"] += co
    elif hit:
        g = geo_hits[hit]
        g["rows"] += 1
        g["clicks"] += cl
        g["cost"] += co
        g["impr"] += im
        detail.append({"state": hit, "term": term, "campaign": r.get("Campaign"),
                       "clicks": cl, "impr": im, "cost": co})
    else:
        no_geo["rows"] += 1
        no_geo["clicks"] += cl
        no_geo["cost"] += co

print("\n=== GEOGRAPHY *INSIDE THE QUERY TEXT* (not user location) ===")
print(f"  rows naming a Maryland place  : {md_hits['rows']:<5} clicks={int(md_hits['clicks']):<4} ${md_hits['cost']:.2f}")
print(f"  rows naming NO place          : {no_geo['rows']:<5} clicks={int(no_geo['clicks']):<4} ${no_geo['cost']:.2f}")
print("  rows naming a NON-Maryland place:")
for st, v in sorted(geo_hits.items(), key=lambda kv: -kv[1]["rows"]):
    print(f"     {st:<18} rows={v['rows']:<4} impr={int(v['impr']):<5} clicks={int(v['clicks']):<3} ${v['cost']:.2f}")
tot_oos = sum(v["rows"] for v in geo_hits.values())
tot_oos_clicks = sum(v["clicks"] for v in geo_hits.values())
tot_oos_cost = sum(v["cost"] for v in geo_hits.values())
print(f"  TOTAL non-Maryland-named rows : {tot_oos} rows, {int(tot_oos_clicks)} clicks, ${tot_oos_cost:.2f}")

outp = EVID / "2026-09-09-out-of-state-query-text-detail.json"
outp.write_text(json.dumps(detail, indent=1), encoding="utf-8")
print("  detail written:", outp.relative_to(ROOT), "rows:", len(detail))

write(EVID / "2026-09-09-csv-reconciliation.json", {
    "source_file": str(SRC), "sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
    "report_name": raw[0], "date_range": raw[1],
    "parsed_rows": len(rows), "displayed_rows": len(data_rows),
    "google_total_rows": len(total_row),
    "google_total": ({k: num(total_row[0].get(v)) for k, v in
                      [("clicks", "Clicks"), ("impressions", "Impr."), ("cost", "Cost"),
                       ("conversions", "Conversions")]} if total_row else None),
    "sum_of_displayed": sums,
    "by_campaign": {k: v for k, v in bc.items()},
    "query_text_geography": {"maryland_named": md_hits, "no_place_named": no_geo,
                             "non_maryland_named": dict(geo_hits),
                             "non_maryland_totals": {"rows": tot_oos, "clicks": tot_oos_clicks,
                                                     "cost": round(tot_oos_cost, 2)}},
})
