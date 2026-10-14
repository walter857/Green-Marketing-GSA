#!/usr/bin/env python3
"""MasterGrass - Live copy deck, 2026-09-26. No city names (owner instruction 2026-09-26).

Verified claims only:
  * licensed & insured ............ owner confirmed in chat 2026-09-26
  * 4.9 stars, 83 Google reviews .. Google Business Profile "MasterGrass Landscape & Lawn Care",
                                    read 2026-09-26 (copy says "80+" so it stays true)
  * free quote / free estimate .... every offer landing page
  * services per ad group ......... live keywords, final URLs and landing pages
Held back (unverified): years in business, warranty/guarantee, response or install times,
financing, prices, "best"/"#1".
RSA "A" pins three keyword headlines to position 1; RSA "B" is unpinned, so the pair also tests
pinning. Descriptions <= 90, headlines <= 30, paths <= 15.
"""
from __future__ import annotations

import re

O = "https://offer.mastergrasslawncare.com"
TRUST_A = ["Licensed & Insured Team", "4.9-Star Rated On Google", "80+ Google Reviews",
           "Request Your Free Estimate", "Call For A Free Quote"]
TRUST_B = ["Licensed & Insured Pros", "4.9 Stars From 80+ Reviews", "Schedule A Free Estimate",
           "Free Quote, Clear Next Steps", "Talk To Master Grass Today"]


def ad(pinned, a_rest, brand, b_heads, desc_a, desc_b):
    assert len(pinned) == 3 and len(a_rest) == 6 and len(b_heads) == 10
    return {
        "A": {"headlines": [(h, "HEADLINE_1") for h in pinned] + [(h, None) for h in a_rest + TRUST_A + [brand]],
              "descriptions": desc_a},
        "B": {"headlines": [(h, None) for h in b_heads + TRUST_B], "descriptions": desc_b},
    }


RSAS = {
    # ---------------- Landscaping Search - BOFU (23905193676) ----------------
    "195877148086": dict(ad_group="Landscaping Contractor", campaign="23905193676",
        url=f"{O}/landscaping-contractor/", path=("Landscaping", "Free-Quote"), **ad(
        ["Landscaping Contractor", "Local Landscaping Company", "Landscape Installation Pros"],
        ["Free Landscaping Quotes", "New Landscape Beds & Borders", "Landscaping + Hardscaping",
         "One Team, Start To Finish", "Get A Clear Project Quote", "Plan Your Yard Upgrade"],
        "Master Grass Landscaping",
        ["Landscaping Services", "Transform Your Yard", "Tired Of A Bare Yard?", "Landscape Design & Install",
         "Fresh Beds, Mulch & Edging", "Upgrade Your Curb Appeal", "Landscapers Near You",
         "Local Landscaping Experts", "Yard Upgrades Done Right", "Plantings, Beds & Borders"],
        ["Landscape installation, new beds, borders and yard upgrades by a licensed, insured team.",
         "Rated 4.9 stars on Google by 80+ customers. Request your free landscaping quote today.",
         "Pair new landscaping with a patio, wall or drainage fix. One local team, one clear plan.",
         "Tell us what you want your yard to look like and get a clear, free quote from our team."],
        ["Turn a tired yard into one you enjoy. Landscaping planned and installed by a local team.",
         "Licensed and insured landscapers with a 4.9-star Google rating. Get your free quote.",
         "From new beds and borders to full yard upgrades, we plan the work around your property.",
         "Call or request a free estimate online and get clear options for your yard project."])),
    "195877148126": dict(ad_group="French Drain Installation", campaign="23905193676",
        url=f"{O}/french-drain/", path=("French-Drains", "Free-Quote"), **ad(
        ["French Drain Installation", "French Drain Contractor", "Yard Drainage Contractor"],
        ["Free French Drain Quote", "Stop Water Pooling In Yard", "Fix Soggy Yard Areas",
         "Yard Drainage Solutions", "Drainage + Yard Grading", "Get A Clear Drainage Plan"],
        "Master Grass Drainage",
        ["Standing Water In Your Yard?", "Soggy Lawn After Every Rain?", "Wet Yard Drainage Help",
         "French Drain Installers", "Move Water Away From Home", "Protect Your Lawn & Beds",
         "Solve Yard Drainage Problems", "Local Drainage Specialists", "Water Pooling By Your Home?",
         "French Drains Done Right"],
        ["We find where water collects and where it needs to go, then quote the right drain for it.",
         "French drains and yard drainage from a licensed, insured team rated 4.9 stars on Google.",
         "Soggy lawn or pooling water? Get a clear drainage plan and a free quote from Master Grass.",
         "Pair a French drain with yard grading to move water away from your home and landscaping."],
        ["Tired of a yard that stays wet for days? Get a French drain planned around your property.",
         "Licensed and insured drainage installers with 80+ Google reviews. Request a free estimate.",
         "Keep water from pooling near your home, beds and walkways with a properly installed drain.",
         "Call or request your free French drain quote online. Clear options, clear next steps."])),
    "195877148286": dict(ad_group="Yard Grading Regrading", campaign="23905193676",
        url=f"{O}/yard-grading/", path=("Yard-Grading", "Free-Quote"), **ad(
        ["Yard Grading Services", "Yard Grading Contractor", "Yard Leveling Services"],
        ["Free Yard Grading Quote", "Fix Low Spots & Uneven Lawns", "Regrade Your Yard",
         "Grading For Better Drainage", "Grading + French Drains", "Get A Clear Grading Plan"],
        "Master Grass Grading",
        ["Uneven Or Sloped Yard?", "Water Flowing Toward Home?", "Level Your Lawn The Right Way",
         "Residential Yard Grading", "Land Grading & Leveling", "Slope Water Away From Home",
         "Yard Regrading Experts", "Smooth, Level Lawn Areas", "Prep Your Yard For New Sod",
         "Grading For New Landscaping"],
        ["Yard grading and regrading to fix low spots, uneven areas and water flowing toward home.",
         "Licensed, insured grading team rated 4.9 stars on Google. Request your free estimate.",
         "Combine grading with a French drain when water needs a clear path away from your house.",
         "Get a clear plan and a free yard grading quote from Master Grass before any work begins."],
        ["Sloped or uneven yard? We regrade it so water drains away and the lawn is easier to use.",
         "Licensed and insured yard grading with 80+ Google reviews behind us. Get a free quote.",
         "Grading, leveling and soil prep before new sod or landscaping, planned around your yard.",
         "Call or request a free grading estimate online and see your options clearly."])),
    "195877148326": dict(ad_group="Mulch & Rock Installation", campaign="23905193676",
        url=f"{O}/mulch-rock-installation/", path=("Mulch-Rock", "Free-Quote"), **ad(
        ["Mulch Installation", "Landscape Rock Installation", "Mulch & Rock Services"],
        ["River Rock Installation", "New Landscape Beds", "Clean Bed Borders & Edging",
         "Free Mulch & Rock Quote", "Refresh Tired Flower Beds", "Rock Borders & Edging"],
        "Master Grass Mulch & Rock",
        ["Tired Of Weedy Flower Beds?", "Fresh Mulch, Clean Beds", "Low-Maintenance Rock Beds",
         "Mulch Or Rock? We Do Both", "Landscape Bed Makeovers", "Crisp Bed Borders & Edging",
         "Mulch & Rock Installers", "River Rock Borders", "Refresh Your Landscaping",
         "Finished Look For Your Yard"],
        ["Mulch, river rock, landscape beds and borders installed by a licensed, insured team.",
         "Rated 4.9 stars on Google by 80+ customers. Request your free mulch or rock quote today.",
         "New beds, clean edging and fresh mulch or rock that make your whole yard look finished.",
         "Tell us about your beds and get a clear, free quote from Master Grass."],
        ["Refresh tired flower beds with new mulch, landscape rock and clean borders.",
         "Licensed and insured installers with a 4.9-star Google rating. Get your free estimate.",
         "Choose mulch, river rock or a mix, and we install it with crisp borders and edging.",
         "Call or request your free estimate online for mulch and rock installation."])),
    # ---------------- Hardscaping Search - BOFU (23914692658) ----------------
    "194944952537": dict(ad_group="Hardscaping Contractor", campaign="23914692658",
        url=f"{O}/hardscaping/", path=("Hardscaping", "Free-Quote"), **ad(
        ["Hardscaping Contractor", "Hardscape Installation", "Local Hardscaping Company"],
        ["Patios, Walls & Fire Pits", "Custom Hardscape Projects", "Free Hardscaping Quote",
         "Outdoor Living Spaces", "Landscaping + Hardscaping", "Get A Clear Project Quote"],
        "Master Grass Hardscapes",
        ["Build Your Outdoor Space", "Hardscape Design & Install", "Pavers, Patios & Walls",
         "Upgrade Your Backyard", "Outdoor Living Contractor", "Backyard Patio Projects",
         "Walkways, Walls & Patios", "Hardscaping Experts", "Fire Pits & Outdoor Kitchens",
         "Plan Your Dream Backyard"],
        ["Patios, pavers, walls, fire pits and outdoor kitchens built by a licensed, insured team.",
         "Rated 4.9 stars on Google by 80+ customers. Request your free hardscaping quote today.",
         "Combine hardscaping with landscaping and drainage. One local team and one clear plan.",
         "Tell us about your outdoor project and get a clear, free quote from Master Grass."],
        ["Turn your backyard into a space you use. Hardscapes planned around your yard and home.",
         "Licensed and insured hardscape contractor with a 4.9-star Google rating. Free estimates.",
         "From paver patios and walkways to walls and fire pits, we plan the whole outdoor space.",
         "Call or request a free hardscaping estimate online and get clear options for your yard."])),
    "194944952577": dict(ad_group="Pavers", campaign="23914692658",
        url=f"{O}/paver/", path=("Pavers", "Free-Quote"), **ad(
        ["Paver Installation", "Paver Patio Installation", "Paver Installers"],
        ["Free Paver Quote", "Paver Patios & Walkways", "Custom Paver Patios",
         "Paver Walkway Installation", "Paver Patio Contractor", "Get A Clear Paver Quote"],
        "Master Grass Pavers",
        ["Upgrade To A Paver Patio", "Paver Patio Builders", "Patio Pavers Installed",
         "Plan Your New Patio", "Backyard Paver Patios", "Paver Walkways & Paths",
         "Outdoor Paver Projects", "Pro Paver Installation", "Patios Built Around Your Yard",
         "Paver Patio Installers"],
        ["Paver patios and walkways installed by a licensed, insured team rated 4.9 stars on Google.",
         "Request a free paver installation quote and get a clear plan for layout, base and borders.",
         "Add a fire pit, wall or new landscaping to your paver project. One team handles it all.",
         "Tell us about your space and get a clear, free paver quote from Master Grass."],
        ["Plan a paver patio or walkway around how you actually use your backyard.",
         "Licensed and insured paver installers with 80+ Google reviews. Request a free estimate.",
         "Pick your layout and pavers, and we plan the base, borders and install start to finish.",
         "Call or request your free paver patio estimate online and see your options clearly."])),
    "194944952617": dict(ad_group="Patios Installation", campaign="23914692658",
        url=f"{O}/patio-installation/", path=("Patios", "Free-Quote"), **ad(
        ["Patio Installation", "Patio Contractor", "Patio Builders"],
        ["Custom Patio Installation", "Free Patio Quote", "Paver Patio Contractors",
         "New Backyard Patio", "Patio Construction", "Get A Clear Patio Quote"],
        "Master Grass Patios",
        ["Ready For A New Patio?", "Build Your Backyard Patio", "Patio Builders Near You",
         "Patio + Fire Pit Projects", "Outdoor Patio Builders", "Paver Patio Installers",
         "Plan Your New Patio", "Patio Design & Install", "More Room To Relax Outside",
         "Custom Backyard Patios"],
        ["Custom patio installation by a licensed, insured team rated 4.9 stars on Google.",
         "Request a free patio quote and get a clear plan for size, layout and materials.",
         "Add a fire pit, wall or new landscaping around your patio. One team, one plan.",
         "Tell us how you want to use your backyard and get a clear, free quote from Master Grass."],
        ["Create more room to relax, eat and gather outside with a patio planned around your yard.",
         "Licensed and insured patio builders with 80+ Google reviews. Request a free estimate.",
         "From layout to final borders, we plan and install your new patio from start to finish.",
         "Call or request your free patio estimate online and see your options clearly."])),
    "194944952777": dict(ad_group="Fire Pits Installation", campaign="23914692658",
        url=f"{O}/fire-pit-installation/", path=("Fire-Pits", "Free-Quote"), **ad(
        ["Fire Pit Installation", "Fire Pit Installer", "Backyard Fire Pit Builders"],
        ["Free Fire Pit Quote", "Custom Backyard Fire Pits", "Fire Pit + Patio Projects",
         "Outdoor Fire Pit Install", "Fire Pit Contractors", "Get A Clear Fire Pit Quote"],
        "Master Grass Fire Pits",
        ["Want A Backyard Fire Pit?", "Gather Around Your Fire Pit", "Built-In Fire Pit Installs",
         "Fire Pit & Seating Areas", "Custom Fire Pit Design", "Fire Pits With Paver Patios",
         "Make Your Yard The Hangout", "Outdoor Fire Pit Builders", "Plan Your Fire Pit Area",
         "Fire Pits For Every Yard"],
        ["Custom fire pit installation by a licensed, insured team rated 4.9 stars on Google.",
         "Request a free fire pit quote and get a clear plan for size, placement and materials.",
         "Pair your fire pit with a paver patio or seating area. One local team handles it all.",
         "Tell us about your backyard and get a clear, free fire pit quote from Master Grass."],
        ["Make your backyard the place everyone gathers with a fire pit planned around your space.",
         "Licensed and insured fire pit builders with 80+ Google reviews. Request a free estimate.",
         "Built-in fire pits with patios and seating, planned and installed from start to finish.",
         "Call or request your free fire pit estimate online and see your options clearly."])),
    "194944952817": dict(ad_group="Retaining Walls", campaign="23914692658",
        url=f"{O}/retaining-walls/", path=("Retaining-Walls", "Free-Quote"), **ad(
        ["Retaining Wall Installation", "Retaining Wall Contractor", "Retaining Wall Builders"],
        ["Free Retaining Wall Quote", "Walls For Slopes & Drainage", "Make Sloped Yards Usable",
         "Landscape Wall Installation", "Walls, Patios & Pavers", "Get A Clear Wall Quote"],
        "Master Grass Hardscapes",
        ["Sloped Yard? Build A Wall", "Walls That Hold Back Slopes", "Retaining Wall Company",
         "Level Out A Sloped Yard", "Block Retaining Walls", "Retaining Wall Experts",
         "Gain Usable Yard Space", "Walls Planned For Drainage", "Plan Your Wall Project",
         "Retaining Walls For Slopes"],
        ["Retaining walls built around your yard layout, slope and drainage by a licensed team.",
         "Rated 4.9 stars on Google by 80+ customers. Request your free retaining wall quote today.",
         "Turn a sloped or washing-out yard into usable space, planned around drainage and access.",
         "Combine your wall with a patio, pavers or new landscaping. One local team, one clear plan."],
        ["Sloped yard or eroding soil? Get a retaining wall planned for your slope and drainage.",
         "Licensed and insured retaining wall builders with a 4.9-star Google rating. Free quotes.",
         "From layout to drainage behind the wall, we plan and build it from start to finish.",
         "Call or request your free retaining wall estimate online and see your options clearly."])),
    "194944952857": dict(ad_group="Outdoor Kitchens", campaign="23914692658",
        url=f"{O}/outdoor-kitchen/", path=("Outdoor-Kitchen", "Free-Quote"), **ad(
        ["Outdoor Kitchen Installation", "Outdoor Kitchen Contractor", "Outdoor Kitchen Builders"],
        ["Custom Outdoor Kitchens", "Free Outdoor Kitchen Quote", "Outdoor Kitchen + Patio",
         "Backyard Kitchen Projects", "Outdoor Kitchen Company", "Get A Clear Project Quote"],
        "Master Grass Hardscapes",
        ["Cook & Entertain Outside", "Build Your Outdoor Kitchen", "Outdoor Kitchen Design",
         "Outdoor Kitchens & Patios", "Outdoor Kitchen Installer", "Plan Your Backyard Kitchen",
         "Kitchen, Patio & Fire Pit", "Outdoor Living Upgrades", "Custom Kitchen Layouts",
         "Your Backyard, Upgraded"],
        ["Custom outdoor kitchen installation by a licensed, insured team rated 4.9 stars on Google.",
         "Request a free outdoor kitchen quote and get a clear plan for layout and materials.",
         "Pair your outdoor kitchen with a paver patio or fire pit. One local team handles it all.",
         "Tell us how you like to cook and entertain and get a clear, free quote from Master Grass."],
        ["Cook, grill and entertain outside with an outdoor kitchen planned around your patio.",
         "Licensed and insured outdoor kitchen builders with 80+ Google reviews. Free estimates.",
         "From layout to the patio underneath, we plan and build your outdoor kitchen start to end.",
         "Call or request your free outdoor kitchen estimate online and see your options clearly."])),
}

NEW_CALLOUTS = ["Licensed & Insured", "4.9-Star Google Rating", "80+ Google Reviews"]

PMAX_TEXT = {
    "headlines": ["French Drain Installation", "Yard Drainage Solutions", "Fix Soggy Yard Areas",
                  "Free Drainage Quote", "Wet Yard?", "Stop Standing Water", "French Drain Contractor",
                  "Yard Grading & Drainage", "Licensed & Insured Team", "4.9-Star Rated On Google",
                  "80+ Google Reviews", "Drainage Experts", "Request A Free Estimate",
                  "Protect Your Lawn & Beds", "Move Water Away From Home"],
    "long_headlines": [
        "French drain and yard drainage installation from a licensed, insured local team",
        "Standing water or a soggy lawn? Get a free drainage quote from Master Grass",
        "Rated 4.9 stars on Google by 80+ customers. Request your free French drain estimate",
        "Move water away from your home with a French drain planned around your yard",
        "Combine yard grading and a French drain to give water a clear path away"],
    "descriptions": [
        "Free drainage quote. Licensed and insured.",
        "We find where water collects and where it needs to go, then quote the right drain for it.",
        "French drains and yard drainage from a team rated 4.9 stars on Google by 80+ customers.",
        "Soggy lawn after every rain? Get a clear drainage plan and a free estimate today.",
        "Call or request your free French drain estimate online. Clear options, clear next steps."],
    "search_themes": ["french drain installation", "french drain contractor", "french drain installers",
                      "yard drainage solutions", "yard drainage contractor", "backyard drainage solutions",
                      "standing water in yard", "soggy yard fix", "drainage contractor", "yard drainage system",
                      "lawn drainage solutions", "water pooling in yard", "yard grading for drainage",
                      "yard drainage company", "yard regrading", "wet yard solutions", "fix drainage in yard",
                      "french drain near me", "yard drainage near me", "drainage installation"],
}

# Place names in and around the service area, plus every Iowa town inside the targets.
CITY = re.compile(r"\b(ames|ankeny|altoona|des moines|dsm|johnston|urbandale|grimes|waukee|clive|"
                  r"nevada|huxley|slater|polk city|colo|elkhart|maxwell|story city|roland|gilbert|"
                  r"cambridge|alleman|zearing|hubbard|radcliffe|ellsworth|mccallsburg|saylorville|"
                  r"boone|marshalltown|bondurant|pleasant hill|central iowa)\b", re.I)
BARRED = re.compile(r"24/7|24-7|same[- ]day|emergenc|guarantee|warrant|financ|\$\d|% off|discount|"
                    r"years? (of )?(experience|in business)|#1|\bbest\b|cheapest|fastest|"
                    r"within \d+ (min|hour|day)|near me", re.I)


def check_all():
    errs = []
    for ag, g in RSAS.items():
        if len(g["path"][0]) > 15 or len(g["path"][1]) > 15:
            errs.append(f"{g['ad_group']}: path >15")
        for k in ("A", "B"):
            hs = [h for h, _ in g[k]["headlines"]]
            ds = g[k]["descriptions"]
            if len(hs) != 15 or len({h.lower() for h in hs}) != 15:
                errs.append(f"{g['ad_group']} {k}: need 15 distinct headlines, got {len(set(hs))}")
            if len(ds) != 4 or len({d.lower() for d in ds}) != 4:
                errs.append(f"{g['ad_group']} {k}: need 4 distinct descriptions")
            errs += [f"{g['ad_group']} {k}: H {len(h)}>30 '{h}'" for h in hs if len(h) > 30]
            errs += [f"{g['ad_group']} {k}: D {len(d)}>90 '{d}'" for d in ds if len(d) > 90]
            for t in hs + ds:
                if CITY.search(t):
                    errs.append(f"{g['ad_group']} {k}: city '{t}'")
                if BARRED.search(t):
                    errs.append(f"{g['ad_group']} {k}: barred '{t}'")
    p = PMAX_TEXT
    if len(p["headlines"]) != 15 or len(set(p["headlines"])) != 15 or any(len(h) > 30 for h in p["headlines"]):
        errs.append("pmax headlines")
    if not any(len(h) <= 15 for h in p["headlines"]):
        errs.append("pmax: no headline <=15")
    if len(p["long_headlines"]) != 5 or any(len(h) > 90 for h in p["long_headlines"]):
        errs.append("pmax long headlines")
    if len(p["descriptions"]) != 5 or any(len(d) > 90 for d in p["descriptions"]) or not any(len(d) <= 60 for d in p["descriptions"]):
        errs.append("pmax descriptions")
    for t in p["headlines"] + p["long_headlines"] + p["descriptions"] + NEW_CALLOUTS:
        if CITY.search(t) or BARRED.search(t):
            errs.append(f"pmax/callout wording '{t}'")
    if any(len(c) > 25 for c in NEW_CALLOUTS):
        errs.append("callout >25")
    if len(p["search_themes"]) > 25:
        errs.append("search themes >25")
    return errs


if __name__ == "__main__":
    e = check_all()
    n_h = sum(len(g[k]["headlines"]) for g in RSAS.values() for k in "AB")
    n_d = sum(len(g[k]["descriptions"]) for g in RSAS.values() for k in "AB")
    print(f"RSAs {len(RSAS) * 2} | headlines {n_h} | descriptions {n_d} | errors {len(e)}")
    for x in e:
        print("  ", x)
