#!/usr/bin/env python3
"""Ambient | 2026-09-16 | validate the 6 heating RSA drafts. LOCAL ONLY, no API write."""
from __future__ import annotations
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import ROOT, EXPORTS

HL, DS = 30, 90
BARRED = {
    "licensed/insured": r"licen[cs]ed|\binsured\b",
    "24/7": r"\b24\s*/\s*7\b|\b24.?7\b",
    "emergency": r"\bemergency\b",
    "same-day": r"\bsame.?day\b",
    "response time": r"\b(minutes|hours)\b.*\b(response|arrival)|within \d+",
    "financing": r"\bfinanc(e|ing)\b|\brebate\b|\bapr\b",
    "guarantee/warranty": r"\bguarantee|\bwarrant",
    "superlative": r"#\s*1\b|\bbest\b|\bnumber one\b|\b#1\b",
    # A RATING claim needs a number or a star. The bare verb "review" ("review your
    # options") is ordinary English, not a rating claim - do not flag it.
    "rating/reviews": r"\b\d+(\.\d)?\s*stars?\b|\b\d+\+?\s*reviews?\b|\brated\b"
                      r"|\bfive[- ]star\b|\bstar[- ]rated\b|\btop[- ]rated\b",
    "price": r"\$\s?\d|\b\d+%\s*off\b",
    "years in business": r"\b\d+\+?\s*years\b|\bsince \d{4}\b",
    "certification": r"\bcertified\b|\bnate\b",
    "LSA": r"google guaranteed|local services ad",
    "awkward near me": r"\bnear me\b",
}

RSAS = {
"SKAG | Furnace & Heating Repair": {
 "final_url": "https://offer.ambientcoolingandheating.com/furnace-heating-repair/",
 "path1": "heating", "path2": "repair",
 "A": {"label": "RSA A - keyword-first, 3 openers pinned to HEADLINE_1",
  "pin1": ["Furnace Repair in Central MD", "Furnace & Heating Repair", "Heating Repair Near You"],
  "unpinned": ["Free Heating Repair Estimate", "Furnace Not Heating?", "No Heat? We Can Diagnose It",
   "Gas & Oil Furnace Repair", "Heat Pump Repair Too", "Diagnosis Before Any Work",
   "Honest Repair Assessment", "Qualified Heating Techs", "Homes & Businesses Served",
   "Severn, Columbia & Nearby", "Ambient Cooling & Heating", "Book a Heating Diagnosis"],
  "desc": [
   "Furnace and heating repair for Central Maryland homes and businesses. Free estimate.",
   "Tell us what your system is doing and we will arrange a visit to diagnose the fault.",
   "Qualified technicians test the system, explain what they found, then you choose.",
   "Gas furnaces, oil furnaces, heat pumps, ductwork and controls all diagnosed."]},
 "B": {"label": "RSA B - symptom-led, unpinned control",
  "pin1": [],
  "unpinned": ["Is Your Heat Not Working?", "Heating System Diagnosis", "Furnace Blowing Cold Air?",
   "Uneven Heat in the House?", "Furnace Making Odd Noises?", "Central Maryland Heating Techs",
   "We Find the Actual Fault", "Repair or Replace? We Explain", "Heating Repair for Business",
   "Request a Heating Estimate", "Part Replacement Available", "Trained Heating Technicians",
   "Serving Severna Park & Severn", "Get Your Heat Back On", "Talk to a Heating Technician"],
  "desc": [
   "Heat not working the way it should? Request a free heating repair estimate today.",
   "We trace the fault instead of guessing at parts, so the repair fixes the cause.",
   "Furnace, heat pump, ductwork and control problems diagnosed across Central Maryland.",
   "Clear options after diagnosis. You decide what happens next, before any work starts."]}},

"SKAG | Heat Pump & Ductless": {
 "final_url": "https://offer.ambientcoolingandheating.com/heat-pump-mini-split/",
 "path1": "heat-pump", "path2": "mini-split",
 "A": {"label": "RSA A - keyword-first, 3 openers pinned to HEADLINE_1",
  "pin1": ["Heat Pump Repair & Install", "Ductless Mini-Split Install", "Heat Pump Service Central MD"],
  "unpinned": ["Free Heat Pump Quote", "Mini-Split Installation", "Heat Pump Replacement",
   "Ductless & Central Options", "Old Unit Removed & Replaced", "Installed to Local Codes",
   "New System Tested On Site", "Zoned Comfort for Any Room", "Homes & Businesses Served",
   "Ambient Cooling & Heating", "Request a Heat Pump Quote",
   "Heat Pump Repair Central MD"],
  "desc": [
   "Heat pump and ductless mini-split repair, installation and replacement in Central MD.",
   "Compare ductless mini-splits and central heat pump systems for your property.",
   "We remove the old equipment, set up the new system, and test it before finishing.",
   "Mini-split installation carried out to local codes by trained professionals."]},
 "B": {"label": "RSA B - outcome-led, unpinned control",
  "pin1": [],
  "unpinned": ["Rooms That Never Feel Right?", "Add Comfort Where You Need It", "Heat Pump Not Heating?",
   "Ductless Zones for Any Space", "Replace an Aging Heat Pump", "Heating and Cooling in One",
   "Mini-Splits for Additions", "Central Maryland Installers", "Free Heat Pump Consultation",
   "Sized for Your Property", "Heat Pump Options Compared", "Ductless Heating Installation",
   "Serving Columbia & Annapolis", "Plan Your Mini-Split Project", "Request Your Free Quote"],
  "desc": [
   "A heat pump heats and cools, so a fault shows up all year. We repair and replace them.",
   "Ductless mini-splits bring comfort to additions and rooms ductwork cannot reach well.",
   "Tell us about the space and we will review ductless and central options with you.",
   "Ambient serves Central Maryland homes and businesses with clear, planned installs."]},},

"SKAG | Heating Installation & Replacement": {
 "final_url": "https://offer.ambientcoolingandheating.com/furnace-installation-replacement/",
 "path1": "furnace", "path2": "installation",
 "A": {"label": "RSA A - keyword-first, 3 openers pinned to HEADLINE_1",
  "pin1": ["Furnace Installation in MD", "Furnace Replacement Quote", "New Furnace Installation"],
  "unpinned": ["Free Heating System Quote", "Gas & Oil Furnace Installs", "Heating System Replacement",
   "Heat Load Calculations Done", "Venting Checked and Verified", "Sized for Your Building",
   "Honest Project Timelines", "Tidy, Organised Work Areas", "Homes & Commercial Property",
   "Ambient Cooling & Heating", "Request an Installation Quote",
   "Central Maryland Furnace Team"],
  "desc": [
   "Furnace installation and replacement for Central Maryland homes and businesses.",
   "Heat load calculations and venting checks so the system fits the building properly.",
   "We assess the current system first, then recommend what the replacement should do.",
   "Gas and oil furnace options, with honest timelines and tidy work areas."]},
 "B": {"label": "RSA B - decision-led, unpinned control",
  "pin1": [],
  "unpinned": ["Time to Replace the Furnace?", "Aging Heating System?", "Plan a Heating Replacement",
   "Oil Furnace Installation", "Oil System Replacement", "Compare Furnace & Heat Pump",
   "Uneven Heat Through the House", "Built Around Your Building", "Free Installation Consultation",
   "Central Maryland Installers", "Heating System Options", "Review Options Before You Buy",
   "Serving Severn & Columbia", "Schedule a Site Assessment", "Request Your Free Quote"],
  "desc": [
   "Replacing a heating system is worth getting right. Start with a free consultation.",
   "Older systems work harder for less comfort. We assess before recommending anything.",
   "Oil systems are common here. Ambient installs and replaces them with care for safety.",
   "Discuss equipment options, ductwork, venting and project timing with our team."]}},
}


def main():
    fails, rows = [], []
    for ag, d in RSAS.items():
        print(f"\n########## {ag} ##########")
        print(f"  final_url: {d['final_url']}")
        print(f"  paths: /{d['path1']}/{d['path2']}")
        for key in ("A", "B"):
            r = d[key]
            hs = r["pin1"] + r["unpinned"]
            print(f"\n  --- {r['label']} ---")
            if len(hs) != 15:
                fails.append(f"{ag} RSA {key}: {len(hs)} headlines != 15")
            if len(r["desc"]) != 4:
                fails.append(f"{ag} RSA {key}: {len(r['desc'])} descriptions != 4")
            if len(set(hs)) != len(hs):
                fails.append(f"{ag} RSA {key}: duplicate headlines")
            if len(set(r["desc"])) != len(r["desc"]):
                fails.append(f"{ag} RSA {key}: duplicate descriptions")
            for h in hs:
                n = len(h)
                pin = "PIN:H1" if h in r["pin1"] else "      "
                flag = "" if n <= HL else "  <-- OVER"
                if n > HL:
                    fails.append(f"{ag} RSA {key} HEADLINE {n}>{HL}: {h!r}")
                for bk, bp in BARRED.items():
                    if re.search(bp, h, re.I):
                        fails.append(f"{ag} RSA {key} HEADLINE barred '{bk}': {h!r}")
                print(f"    {pin} [{n:>2}/30] {h}{flag}")
                rows.append({"ad_group": ag, "rsa": key, "type": "headline",
                             "pinned": h in r["pin1"], "text": h, "chars": n})
            for x in r["desc"]:
                n = len(x)
                flag = "" if n <= DS else "  <-- OVER"
                if n > DS:
                    fails.append(f"{ag} RSA {key} DESCRIPTION {n}>{DS}: {x!r}")
                for bk, bp in BARRED.items():
                    if re.search(bp, x, re.I):
                        fails.append(f"{ag} RSA {key} DESCRIPTION barred '{bk}': {x!r}")
                print(f"           [{n:>2}/90] {x}{flag}")
                rows.append({"ad_group": ag, "rsa": key, "type": "description",
                             "pinned": False, "text": x, "chars": n})
        a = set(d["A"]["pin1"] + d["A"]["unpinned"])
        b = set(d["B"]["unpinned"])
        ov_h, ov_d = a & b, set(d["A"]["desc"]) & set(d["B"]["desc"])
        print(f"\n  headline overlap A vs B: {sorted(ov_h) or 'NONE'}")
        print(f"  description overlap    : {sorted(ov_d) or 'NONE'}")
        if ov_h or ov_d:
            fails.append(f"{ag}: RSA A and B share copy - must be materially different")

    print("\n" + "=" * 74)
    if fails:
        print(f"VALIDATION FAILED ({len(fails)}):")
        for f in fails:
            print("  FAIL:", f)
    else:
        print("VALIDATION PASSED: 0 character-limit violations, 0 barred claims,")
        print("0 duplicate copy, 0 overlap between the paired RSAs.")
        print(f"6 RSAs | 90 headlines | 24 descriptions")
    import csv
    EXPORTS.mkdir(parents=True, exist_ok=True)
    p = EXPORTS / "heating-rsa-drafts-2026-09-16.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["ad_group", "rsa", "type", "pinned", "text", "chars"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"WROTE {p}")
    print("EXTERNAL WRITES: 0 (local CSV only; nothing created in Google Ads)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
