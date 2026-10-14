#!/usr/bin/env python3
"""Ambient | 2026-09-25 | LOCAL build payloads for funded services whose page is not publishable.

Geothermal Heat Pump (204129719007, $20 test): /geothermal-heat-pump/ returns 404.
Boiler Installation (204129718247, core): /boiler-installation/ shows Boiler MAINTENANCE content.
Nothing is submitted: sending a broken destination to policy review is not allowed. When the page
passes QA, create these RSAs PAUSED, read back, then enable (max 3 enabled RSAs per ad group).
Copy uses only verified claims: free quote, Mon-Fri 8-4 hours, service area, trained technicians.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, PLANS
from gm_gsa.safety import approval_code

O = "https://offer.ambientcoolingandheating.com"
BARRED = re.compile(r"24/7|24-7|same[- ]day|emergenc|licens|insured|guarantee|warrant|financ|\$\d|% off|discount|"
                    r"years? (of )?experience|\d\.\d ?star|certified|fast response|within \d+ (min|hour)|rebate|tax credit|"
                    r"propert|maint|tune", re.I)
PAYLOADS = {
    "204129719007": dict(ad_group="SKAG | Geothermal Heat Pump", final_url=f"{O}/geothermal-heat-pump/", path1="Geothermal", path2="Heat-Pump",
        gate="publish /geothermal-heat-pump/ from the Drive package; page QA must pass", rsas=[
        dict(h=["Geothermal Heat Pump", "Geothermal Heat Pump Service", "Geothermal HVAC Central MD", "Severn Geothermal Service",
                "Columbia Geothermal Heating", "Severna Park Geothermal", "Ground Source Heat Pump", "Discuss Your Geothermal System",
                "Request a Free Quote", "Trained HVAC Technicians", "Geothermal System Review", "Talk To A Technician",
                "Central Maryland Service", "Clear Service Options", "Geothermal Heating Help"],
             d=["Geothermal heat pump service for homes in Severn, Severna Park and Columbia, MD.",
                "Trained technicians review your geothermal system and explain the options clearly.",
                "Request a free quote from Ambient Cooling and Heating.",
                "Call Mon-Fri, 8 a.m. to 4 p.m., or request your quote online."]),
        dict(h=["Geothermal System Problems?", "Geothermal Not Heating?", "Geothermal Heat Pump Help", "Book A Geothermal Visit",
                "Geothermal Service Near You", "Severn Geothermal Heat Pump", "Columbia Geothermal Service", "Anne Arundel Geothermal",
                "Geothermal Specialists", "Request Geothermal Service", "Clear Repair Options", "Talk To A Technician",
                "Free Geothermal Quote", "Central Maryland Geothermal", "Plan Your Geothermal Project"],
             d=["Changes in noise, cycling or comfort? Request a geothermal system review.",
                "We discuss your current setup and walk you through the options clearly.",
                "Geothermal heat pump service across Central Maryland from Ambient Cooling and Heating.",
                "Request a free geothermal quote online or call Mon-Fri, 8 a.m. to 4 p.m."])]),
    "204129718247": dict(ad_group="SKAG | Boiler Installation", final_url=f"{O}/boiler-installation/", path1="Boiler", path2="Installation",
        gate="developer D2: /boiler-installation/ must carry installation content (H1 + every H2)", rsas=[
        dict(h=["Boiler Installation", "Boiler Installation Severn", "Severna Park Boiler Install", "Columbia Boiler Installation",
                "New Boiler Installation", "Boiler Installation Near You", "Request a Free Quote", "Trained HVAC Technicians",
                "Central Maryland Boilers", "Plan Your New Boiler", "Boiler Installation Quote", "Talk To A Technician",
                "Clear Installation Options", "Maryland Boiler Installs", "Boiler Install Central MD"],
             d=["Boiler installation for homes in Severn, Severna Park and Columbia, Maryland.",
                "Trained technicians assess your home and explain boiler installation options clearly.",
                "Request a free boiler installation quote from Ambient Cooling and Heating.",
                "Call Mon-Fri, 8 a.m. to 4 p.m., or request your free quote online."]),
        dict(h=["Need A New Boiler?", "Replace An Old Boiler", "New Boiler Installation", "Boiler Installation Quote",
                "Boiler Install Near You", "Severn Boiler Installation", "Columbia Boiler Install", "Anne Arundel Boilers",
                "Boiler Installation Team", "Request Boiler Installation", "Clear Installation Options", "Talk To A Technician",
                "Free Installation Quote", "Central Maryland Boiler", "Plan Your Boiler Project"],
             d=["Planning a new boiler? Request a free installation quote today.",
                "We assess your heating needs and walk you through the installation options.",
                "Boiler installation across Central Maryland from Ambient Cooling and Heating.",
                "Request a free boiler quote online or call Mon-Fri, 8 a.m. to 4 p.m."])]),
}


def check():
    errs = []
    for g, p in PAYLOADS.items():
        if len(p["path1"]) > 15 or len(p["path2"]) > 15: errs.append(f"{g} path")
        for i, r in enumerate(p["rsas"]):
            if len(r["h"]) != 15 or len({x.lower() for x in r["h"]}) != 15: errs.append(f"{g}#{i} headlines")
            if len(r["d"]) != 4 or len({x.lower() for x in r["d"]}) != 4: errs.append(f"{g}#{i} descriptions")
            errs += [f"{g}#{i} H{len(x)}>30 {x}" for x in r["h"] if len(x) > 30]
            errs += [f"{g}#{i} D{len(x)}>90 {x}" for x in r["d"] if len(x) > 90]
            errs += [f"{g}#{i} barred '{x}'" for x in r["h"] + r["d"] if BARRED.search(x)]
    return errs


if __name__ == "__main__":
    errs = check()
    plan = {"plan_name": "AMB-0925-HELD-RSA-PAYLOADS", "built_local": datetime.datetime.now(TZ).date().isoformat(),
            "submitted": False, "payloads": PAYLOADS, "errors": errs}
    plan["fingerprint"] = approval_code({k: v for k, v in plan.items() if k != "fingerprint"})
    (PLANS / "AMB-0925-HELD-RSA-PAYLOADS.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
    print("payload", plan["fingerprint"], "errors:", errs or 0)
