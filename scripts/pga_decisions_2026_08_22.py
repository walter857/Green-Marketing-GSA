#!/usr/bin/env python3
"""Adjudicated search-term decision table for Pro Green Austin, 2026-08-22.

One entry per normalized search term that carries an expert override. Everything not
listed here falls through to the rule engine in pga_build_negative_plan.py.

Each override records: intent family, verdict, the exact negative phrase (or None),
confidence, and the evidence that supports the call. Evidence for a competitor is a
reliable third-party confirmation that a real business trades under that name in the
landscaping, hardscape, turf or outdoor-lighting trade.
"""

# ---------------------------------------------------------------------------
# Verified competitors. term -> negative phrase
# ---------------------------------------------------------------------------
COMPETITOR_VERIFIED = {
    "terra landscaping": "terra landscaping",
    "biggadike landscape lighting": "biggadike",
    "waterloo turf austin": "waterloo turf",
    "waterloo artificial turf": "waterloo artificial turf",
    "cutters landscaping austin": "cutters landscaping",
    "cutters landscaping austin tx": "cutters landscaping",
    "cooper and company austin": "cooper and company",
    "ground and garden austin": "ground and garden",
    "magnolia turf austin": "magnolia turf",
    "ps landscapes austin": "ps landscapes",
    "ranchers landscaping": "ranchers landscaping",
    "casas landscaping": "casas landscaping",
    "dl landscaping": "dl landscaping",
    "four roots landscaping": "four roots landscaping",
    "the mark landscapes": "the mark landscapes",
    "twelve point landscaping": "twelve point landscaping",
    "allied outdoor solutions austin": "allied outdoor solutions",
    "allied outdoor solutions austin tx": "allied outdoor solutions",
    "allied outdoor solutions san antonio": "allied outdoor solutions",
    "design ecology austin": "design ecology",
    "ecotopes": "ecotopes",
    "hellas turf": "hellas",
    "hellas matrix turf": "hellas",
    "southern turf co austin": "southern turf",
    "southern turf co": "southern turf",
    "waldemar landscaping": "waldemar landscaping",
    "yardzen packages": "yardzen",
    "zeterre": "zeterre",
    "estudio ome": "estudio ome",
    "blingle of central texas": "blingle",
    "blingle lighting": "blingle",
    "outdoor lighting perspectives": "outdoor lighting perspectives",
    "ground guys": "ground guys",
}

COMPETITOR_EVIDENCE = {
    "terra landscaping": "Multiple real landscaping firms trade as Terra Landscaping "
        "(terralandscaping.net; Idaho and Nevada operators). Austin also has Terra Dura "
        "Landscapes and Terrascapes. Navigational intent toward a named landscaping firm "
        "that is not Pro Green. Not a material, neighborhood or product name.",
    "biggadike": "Bill Biggadike & Associates Landscape Lighting Designs (biggadike.com), "
        "New Braunfels TX, explicitly serves Austin. Direct landscape-lighting competitor.",
    "waterloo turf": "Waterloo Turf (waterlooturf.com/austin), Austin artificial-turf "
        "installer. Direct competitor to the Artificial Turf ad groups.",
    "waterloo artificial turf": "Same verified company, second observed spelling. A PHRASE "
        "negative on 'waterloo turf' does not cover it, because negative keywords do not "
        "match close variants.",
    "cutters landscaping": "Cutters Landscaping (cutterslandscape.com), Austin landscape "
        "design, hardscaping and outdoor living. Direct competitor.",
    "cooper and company": "Cooper & Company Landscape Architecture (cooperandco.co), Austin "
        "high-end landscape design-build. Direct competitor.",
    "ground and garden": "Ground & Garden (groundandgarden.com), Austin full-service "
        "landscape design-build, 30+ years. Direct competitor.",
    "magnolia turf": "Magnolia Turf Co (magnoliaturf.com), artificial-grass installer with "
        "an Austin market. Direct competitor.",
    "ps landscapes": "P.S. Landscapes, Inc. (pslandscapes.com), Austin landscape "
        "construction since 1995. Direct competitor.",
    "ranchers landscaping": "Ranchers Fencing & Landscaping "
        "(ranchersfencingandlandscaping.com), Austin since 2010. Direct competitor.",
    "casas landscaping": "Casas Landscaping, Austin/Leander TX, registered Travis County "
        "landscaping business. Direct competitor.",
    "dl landscaping": "D&L Landscaping, Inc. (dllandscaping.com), Leander TX since 1993, "
        "serves Austin, builds custom patios and pergolas. Direct competitor.",
    "four roots landscaping": "Real landscaping firms trade as Four Roots Landscapes / Four "
        "Roots Landscaping. Navigational intent toward a named landscaping firm that is not "
        "Pro Green. Neither confirmed Austin-based.",
    "the mark landscapes": "The Mark Landscapes (themarklandscapes.com), Austin commercial "
        "landscaping across Round Rock, Georgetown and Cedar Park. Competitor, and "
        "commercial rather than residential design-build.",
    "twelve point landscaping": "Twelve Point Landscaping (twelvepointlandscaping.com), "
        "Dripping Springs and greater Austin, founded 2022. Direct competitor.",
    "allied outdoor solutions": "Allied Outdoor Solutions (alliedoutdoorsolutions.com), Texas "
        "outdoor-living remodeler with an Austin location; hardscape overlay, pavers, patio "
        "covers, pergolas, outdoor kitchens, fire features. Direct competitor.",
    "design ecology": "Design Ecology Austin (designecologyaustin.com), Austin landscape "
        "architecture and luxury pool construction. Direct competitor.",
    "ecotopes": "ecotopes (ecotopes.com), Austin landscape design studio, showroom on "
        "Spicewood Springs Road. Direct competitor.",
    "hellas": "Hellas Construction (hellas.com), Austin, synthetic turf and Matrix Turf "
        "systems. Covers both observed spellings 'hellas turf' and 'hellas matrix turf'. "
        "The token has no landscaping meaning in English, so a single PHRASE negative is "
        "narrower in practice than two brittle multi-word ones.",
    "southern turf": "Southern Turf Co (southernturfco.com/austin), Austin artificial-turf "
        "installer founded 2019. Covers 'southern turf co' and 'southern turf co austin'.",
    "waldemar landscaping": "Waldemar Landscape & Design, 7020 Grand Canyon Dr, Austin TX. "
        "Direct competitor.",
    "yardzen": "Yardzen (yardzen.com), national online landscape design-and-build service. "
        "Competitor for landscape-design demand.",
    "zeterre": "Zeterre Landscape Architecture (zeterre.com), San Francisco Bay Area "
        "landscape architecture firm. Competitor brand and wrong market.",
    "estudio ome": "Estudio Ome (estudioome.com), Mexico City landscape architecture "
        "practice. Competitor brand and wrong market.",
    "blingle": "Blingle! Premier Lighting (blingle.com), national outdoor and holiday "
        "lighting franchise. Competitor for landscape-lighting demand. Covers 'blingle "
        "lighting' and 'blingle of central texas'.",
    "outdoor lighting perspectives": "Outdoor Lighting Perspectives "
        "(outdoorlightingfranchise.com), North America's largest outdoor landscape lighting "
        "franchise. PHRASE scope cannot block generic 'outdoor lighting' demand, because the "
        "full three-word phrase must appear.",
    "ground guys": "The Grounds Guys (groundsguys.com), national landscaping franchise "
        "offering landscape design, installation and outdoor lighting. Observed spelling is "
        "the singular 'ground guys'.",
}

# ---------------------------------------------------------------------------
# Wrong market. term -> negative phrase
# ---------------------------------------------------------------------------
WRONG_MARKET = {
    "pavers san antonio texas": "san antonio",
    "retaining wall contractors san antonio": "san antonio",
    "outdoor lighting dfw": "dfw",
    "alpha paving dfw": "dfw",
    "outdoor lighting dallas": "dallas",
    "west texas paving lubbock": "lubbock",
    "waco paving": "waco",
}

WRONG_MARKET_EVIDENCE = {
    "san antonio": "San Antonio is not in the 24 approved Austin-area location targets. "
        "Presence targeting still serves an Austin resident who names another metro. "
        "'pavers san antonio texas' is the single most expensive unblocked leak this month.",
    "dallas": "Dallas is not an approved location target, and Pro Green runs a separate "
        "Dallas child account (8735782888). Blocking it here stops both waste and "
        "cross-market cannibalization.",
    "dfw": "Dallas/Fort Worth abbreviation. Same reasoning as 'dallas'; a PHRASE negative on "
        "'dallas' does not cover the abbreviation.",
    "lubbock": "West Texas, roughly 370 miles from Austin. Not an approved location target.",
    "waco": "Roughly 100 miles from Austin. Not an approved location target and not in the "
        "24-location manifest.",
}

# ---------------------------------------------------------------------------
# Wrong service or material. term -> negative phrase
# ---------------------------------------------------------------------------
WRONG_SERVICE = {
    "asphalt paving austin": "asphalt",
    "asphalt paving austin tx": "asphalt",
    "asphalt and concrete paving": "asphalt",
    "asphalt paving contractors": "asphalt",
    "texas asphalt paving": "asphalt",
    "outdoor handrail installation near me": "handrail",
}

WRONG_SERVICE_EVIDENCE = {
    "asphalt": "Confirmed 2026-08-22 against the live first-party page "
        "https://progreenlandscapesolutions.com/austin/: the word 'asphalt' appears nowhere, "
        "and the 23 named Austin services are irrigation, sprinkler repair, outdoor living "
        "spaces, hardscaping, landscaping, artificial turf, landscape design, landscape "
        "lighting, retaining walls, fire pits, patios, pavers, fertilization and weed "
        "control, driveways, walkways, irrigation repair, irrigation winterization, masonry, "
        "outdoor kitchens, sod installation, concrete, pergolas and deck construction. "
        "Asphalt paving is a different trade with different equipment and crews. A PHRASE "
        "negative on 'asphalt' cannot block 'paving contractors near me', which stays "
        "eligible.",
    "handrail": "'handrail' and 'railing' appear nowhere on the live first-party Austin "
        "page, and neither is in the client profile's verified service lists. Metal "
        "handrail fabrication is a different trade.",
}

# ---------------------------------------------------------------------------
# Explicit WATCH decisions. term -> (intent_family, reason)
# ---------------------------------------------------------------------------
WATCH_OVERRIDES = {
    "apollo pergola": ("MANUFACTURER_PRODUCT",
        "Apollo Opening Roof (apolloopeningroof.com) is a louvered-pergola MANUFACTURER in "
        "Roseville CA that sells through builders, not an Austin landscaping competitor. "
        "Pergolas are a verified Pro Green service, so this carries real pergola-buying "
        "intent. Blocking it would suppress a qualified design-and-build prospect. This "
        "reverses the previous plan, which classified it as a competitor brand."),
    "apollo louvered roof": ("MANUFACTURER_PRODUCT",
        "Same verified manufacturer as 'apollo pergola'. Product-brand research with genuine "
        "pergola intent."),
    "struxure pergola": ("MANUFACTURER_PRODUCT",
        "StruXure is a louvered-pergola manufacturer brand, not a landscaping contractor. "
        "Pergolas are a verified Pro Green service."),
    "austin aluminum pergolas": ("SERVICE_MATERIAL_VARIANT",
        "Material qualifier on a verified service. Not a brand and not out of scope."),
    "synlawn bocce": ("MANUFACTURER_PRODUCT",
        "SYNLawn is an artificial-turf manufacturer brand. Artificial turf is a verified "
        "Pro Green service, so product-brand intent is adjacent, not categorically waste."),
    "vuba stone installer near me": ("MANUFACTURER_PRODUCT",
        "Vuba is a resin-bound stone surfacing manufacturer. Adjacent to verified hardscape "
        "work; no first-party evidence Pro Green installs it either way."),
    "system pavers": ("COMPETITOR_UNVERIFIED",
        "Brand-shaped, but no reliable confirmation was obtained. 'system pavers' is also "
        "close to generic paving-system vocabulary, so a block carries avoidable risk."),
    "is system pavers expensive": ("COMPETITOR_UNVERIFIED",
        "Same unverified brand, with price-research intent. 'price' and 'cost' family "
        "intent is protected by Green Marketing policy."),
    "cedarcrest landscaping": ("COMPETITOR_UNVERIFIED",
        "No company by this name could be confirmed. 'Cedarcrest' is a common subdivision "
        "and street name, so the query may be a resident asking for landscaping IN "
        "Cedarcrest, which is exactly the customer this campaign wants. Removed from the "
        "plan the previous version proposed."),
    "stones and scapes": ("COMPETITOR_UNVERIFIED",
        "Not confirmed. The nearest verified firm is 'Scapes and Stones' in North Las Vegas, "
        "a different name in a different market. Removed from the plan the previous version "
        "proposed."),
    "curbing company near me": ("AMBIGUOUS_ADJACENT_SERVICE",
        "Decorative concrete landscape curbing and edging is a plausible component of "
        "verified design-and-build hardscape work, and 'Concrete' and 'Masonry' are both "
        "verified first-party Austin services. The word 'curbing' does not appear on the "
        "site, so the evidence is ambiguous. 5 impressions, 0 clicks, $0.00 this month. "
        "Removed from the plan the previous version proposed."),
    "drop curb contractors near me": ("AMBIGUOUS_ADJACENT_SERVICE",
        "A drop curb is a driveway apron or curb cut, usually a municipal-permit paving job. "
        "Adjacent to verified driveway work but not confirmed in scope."),
    "clean scapes near me": ("COMPETITOR_WITH_CONVERSION_EVIDENCE",
        "Clean Scapes, LP is a verified Austin landscape construction and maintenance firm, "
        "so the brand classification itself is sound. It is NOT proposed as a negative "
        "because the conflict check found counter-evidence: the all-time query 'clean scapes "
        "austin texas' recorded all_conversions = 1.0 on a $4.91 click (primary conversions "
        "= 0.0, in the paused legacy Patio Installation campaign). A PHRASE negative on "
        "'clean scapes' would block that family. The signal is a single secondary engagement "
        "rather than a qualified lead, but 'clean scapes near me' produced 4 impressions, 0 "
        "clicks and $0.00 this month, so overriding a documented conflict buys nothing. "
        "Ambiguous evidence therefore resolves to WATCH. Removed from the plan the previous "
        "version proposed."),
    "bingle lighting": ("COMPETITOR_UNVERIFIED",
        "Probable misspelling of the verified Blingle! brand, but 'bingle' is an unrelated "
        "word and surname. Negative keywords do not match close variants, so blocking "
        "'blingle' leaves this untouched by design. 2 impressions, 0 clicks, $0.00."),
    "lago vista landscaping": ("LOCAL_SERVICE_IN_TARGET_AREA",
        "Lago Vista is an Austin-metro city. This reads as a local service search, not a "
        "brand. Must stay eligible."),
    "toll brothers landscaping": ("COMPETITOR_UNVERIFIED",
        "Toll Brothers is a national homebuilder, not a landscaping firm. The query may mean "
        "landscaping for a Toll Brothers home, which would be a qualified prospect."),
    "hursthouse landscape architects & contractors": ("COMPETITOR_UNVERIFIED",
        "Brand-shaped and apparently an Illinois firm, but not verified in this pass."),
}

# ---------------------------------------------------------------------------
# Brand-shaped terms found this month that were NOT in the previous written
# competitor summary and are NOT verified in this pass. Reported, not blocked.
# ---------------------------------------------------------------------------
COMPETITOR_UNVERIFIED_RESIDUE = [
    "512 paving austin tx", "alpha paving texas", "amy hovis", "applewood landscaping",
    "artificial grass pros", "artificial grass pros austin", "atx decks and pergolas",
    "atx luxury turf", "austin creative landscaping", "austin eischeid",
    "austin landscapes co", "austin native landscaping austin tx", "b and b landscaping near me",
    "b jane gardens", "beauty scapes", "bennett paving leander tx", "big bully turf cost",
    "bolt landscape design", "breaux's landscaping and custom concrete", "busby landscaping",
    "camilleri solutions landscaping", "canopy collective landscaping", "casey boyter gardens",
    "ciel design for gardens", "cornerstone hardscape", "daniels landscaping",
    "dh landscape design", "double t design and development", "dragonscapes landscaping",
    "drake landscaping austin", "eden garden design austin", "el bambis pavers",
    "envy landscape design", "fertile ground austin", "forge outdoor design",
    "furrow studio austin", "golden hour landscaping", "greenscapes landscaping",
    "h&m landscape and sprinkler", "henrys hardscape", "heroes landscaping",
    "herrera landscaping near me", "ivan landscaping", "jackson broussard austin",
    "jurado landscaping", "jxc landscaping", "leons landscaping", "lisa lapaso",
    "luxe landscape design", "madrone landscape austin", "mario landscaping",
    "mario's landscape service", "mathis landscape design", "new native gardens austin",
    "orca landscape", "peachtree landscaping austin", "perfect cuts landscaping",
    "praetorian landscaping", "proscape landscaping austin tx", "rdc paving hutto tx",
    "s o s masonry and landscaping", "signature pavers",
    "silver leaf landscaping and construction", "southern landscape austin", "stallion paving",
    "stevens paving", "sublime patio austin", "sunscape austin", "the greener side landscaping",
    "the hillbilly hardscapers", "tillman austin tx", "tillman walls", "turf hub cedar park",
    "umana landscaping", "vera lawn", "wetzel landscaping",
]

# ---------------------------------------------------------------------------
# Families that must stay eligible (sections 14 and 15 of the operating brief)
# ---------------------------------------------------------------------------
GENERIC_LANDSCAPING = [
    "landscaper near me", "landscapers near me", "landscape companies near me",
    "landscaping companies near me", "landscaping services near me", "landscaping near me",
    "landscape near me", "best landscaping companies near me", "best landscapers near me",
    "best landscapers in my area", "landscapers in my area", "landscaping company near me",
    "landscaping contractors near me", "landscaping near my location",
    "landscaping companies near me near me", "local landscapers",
    "highly rated landscapers near me", "luxury landscaping near me",
    "high end landscaping near me", "urban landscaping near me",
    "creative landscaping near me", "garden landscaping companies near me",
    "hispanic landscaping companies near me", "backyard landscaping services",
    "residential landscaping services", "home landscaping services",
    "full service residential landscaping", "austin residential landscaping",
    "masonry landscaping near me", "stone landscaping companies near me",
]

CLIENT_BRAND_TOKENS = ["progreen", "pro green"]

PROTECTED_TERMS = ["near me", "quote", "quotes", "price", "prices", "pricing", "cost",
                   "costs", "best", "hire", "local", "emergency"]
