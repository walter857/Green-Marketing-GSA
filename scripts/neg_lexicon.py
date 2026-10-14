#!/usr/bin/env python3
"""Per-account search-term lexicon.

Whitelist-first: a term is IN SCOPE only when it carries a core service token for
the account's approved services. Everything else falls to a categorised
out-of-scope bucket. Disqualifiers override the whitelist because they name a
service, audience or intent the client does not sell.

Raw account search terms are never imported here. These patterns are written from
the validated work order and client profile only.
"""
from __future__ import annotations

import re

# Green Marketing policy: never auto-negative these, they are BOFU signals.
PROTECTED = {
    "near me", "near you", "quote", "quotes", "price", "prices", "pricing",
    "cost", "costs", "best", "hire", "local", "emergency", "estimate",
    "estimates", "affordable", "top rated", "reviews",
}

# ---------------------------------------------------------------------------
# Category detectors shared across every local-service account.
# ---------------------------------------------------------------------------
SHARED = {
    "JOBS_CAREERS": r"\b(job|jobs|hiring|hire[sd]\b|career|careers|salary|salaries|"
                    r"wage|wages|pay\s+rate|employment|apprentice\w*|resume|"
                    r"vacanc\w*|recruit\w*|staffing|work\s+for|working\s+at|"
                    r"indeed|ziprecruiter|glassdoor|linkedin)\b",
    "TRAINING_CERT": r"\b(school|schools|class|classes|course|courses|training|"
                     r"certif\w*|licen[cs]\w*|exam|degree|apprenticeship|"
                     r"tutorial|academy|program\s+near|how\s+to\s+become|"
                     r"become\s+a|epa\s*608|osha)\b",
    "DIY_INFORMATIONAL": r"\b(diy|do\s+it\s+yourself|how\s+to|how\s+do|how\s+much\s+does\s+it\s+"
                         r"take|youtube|video|videos|reddit|quora|forum|wikipedia|wiki|"
                         r"tutorial|guide|manual|instructions|diagram|blueprint|"
                         r"template|calculator|estimator|spreadsheet|checklist|"
                         r"step\s+by\s+step|myself|my\s+own|homemade|home\s+made)\b",
    "EQUIPMENT_RETAIL": r"\b(for\s+sale|buy|purchase|shop|store|amazon|ebay|craigslist|"
                        r"facebook\s+marketplace|home\s*depot|lowes|lowe's|menards|"
                        r"walmart|costco|harbor\s+freight|tractor\s+supply|"
                        r"wholesale|distributor|supplier|supply\s+(house|store|co)|"
                        r"parts|part\s+number|replacement\s+parts|accessor\w*|"
                        r"rental|rent\b|rents\b|renting|lease\b|leasing)\b",
    "SOFTWARE_MEDIA": r"\b(software|app\b|apps\b|online\s+tool|website|websites|"
                      r"crm|saas|plugin|ai\s+(tool|generator)|generator|"
                      r"template|clipart|clip\s+art|stock\s+photo|images|"
                      r"pictures|photos|logo|logos|font)\b",
    "BUSINESS_TO_BUSINESS": r"\b(start\s+a|starting\s+a|business\s+(plan|for\s+sale|"
                            r"insurance|licen[cs]\w*|name|card|cards|loan)|"
                            r"franchise|franchis\w*|lead\s+generation|leads\s+for|"
                            r"buy\s+leads|marketing\s+for|seo\s+for|ads\s+for|"
                            r"invoice|invoicing|bookkeeping|payroll|"
                            r"contractor\s+insurance|general\s+liability|"
                            r"bond(ing)?\s+requirements|suppliers?\s+near)\b",
    "FREE_GRANT_ASSISTANCE": r"\b(free\b|freebie|no\s+cost|at\s+no\s+charge|grant|grants|"
                             r"subsid\w*|assistance\s+program|low\s+income|"
                             r"section\s*8|medicaid|charity|donat\w*|"
                             r"government\s+program|rebate\s+program|volunteer)\b",
    "DIRECTORY_RESEARCH": r"\b(yelp|angi\b|angie'?s?\s+list|thumbtack|homeadvisor|"
                          r"home\s+advisor|houzz|nextdoor|bbb\b|better\s+business|"
                          r"yellow\s*pages|craigslist|porch\.com|buildzoom|"
                          r"complaint|complaints|lawsuit|scam|sue\b|report\s+a)\b",
    "REAL_ESTATE_RENTAL": r"\b(for\s+rent|apartments?\s+for|houses?\s+for\s+sale|"
                          r"homes?\s+for\s+sale|realtor|real\s+estate|zillow|"
                          r"redfin|trulia|mls\b|landlord|tenant|"
                          r"property\s+management)\b",
}

# ---------------------------------------------------------------------------
# AMBIENT COOLING & HEATING  (2401959466)  heating-cooling
# Approved services: AC Repair, HVAC Repair, HVAC Installation,
#                    HVAC Replacement, Gas Boiler Repair.
# Service area: Severn / Severna Park / Columbia, Maryland (75 geo targets).
# ---------------------------------------------------------------------------
AMBIENT = {
    "slug": "ambient-cooling-heating",
    "customer_id": "2401959466",
    # The client's own brand. Brand traffic is never a negative candidate.
    "brand": r"\b(ambient\s*(cooling|heating|c\s*&\s*h|and\s+heating)?|"
             r"ambientcooling\w*|ambient\s*hvac)\b",
    "core": r"(\bac\b|\ba/?c\b|air\s*condition\w*|\bhvac\b|heat\s*pump|furnace|"
            r"boiler|mini[\s-]*split|ductless|\bheating\b|\bcooling\b|"
            r"air\s+handler|condenser|evaporator\s+coil|\bhvac\b|\bheat\b|"
            r"\bduct\w*|thermostat|central\s+air|\bcompressor\b)",
    "intent": r"\b(repair|repairs|repairing|fix|fixing|service|servicing|"
              r"install\w*|replace\w*|new\b|tune[\s-]*up|maintenance|maintain|"
              r"contractor|contractors|compan\w+|technician|tech\b|"
              r"near\s+me|near\s+you|cost|price|pricing|quote|estimate|"
              r"not\s+working|broken|blowing|leaking|won'?t|stopped|"
              r"no\s+cold|no\s+heat|emergency|same\s+day|24\s*hour)\b",
    "disqualify": {
        "AUTOMOTIVE": r"\b(car|cars|auto|autos|automotive|vehicle|truck|trucks|van\b|"
                      r"boat|boats|marine|rv\b|camper|motorhome|motorcycle|tractor|"
                      r"bmw|mercedes|audi|honda|toyota|ford|chevy|chevrolet|nissan|"
                      r"jeep|dodge|ram\b|hyundai|kia\b|subaru|mazda|volkswagen|vw\b|"
                      r"tesla|lexus|acura|infiniti|gmc\b|buick|cadillac|volvo|"
                      r"recharge\s+car|auto\s*zone|advance\s+auto|pep\s+boys)\b",
        "PORTABLE_WINDOW_UNIT": r"\b(window\s*(unit|ac|air)|portable\s*(ac|air|unit)|"
                                r"swamp\s+cooler|evaporative\s+cooler|"
                                r"through\s+the\s+wall|wall\s+unit|"
                                r"space\s+heater|electric\s+heater|"
                                r"fireplace|pellet\s+stove|wood\s+stove|"
                                r"mini\s+fridge|dehumidifier|humidifier|"
                                r"air\s+purifier|fan\b|fans\b)\b",
        "OTHER_TRADE": r"\b(plumber|plumbing|electrician|electrical\s+(work|contractor)|"
                       r"roof\w*|siding|gutter\w*|window\s+replacement|"
                       r"appliance\s+repair|refrigerator|fridge|freezer|washer|dryer\b|"
                       r"oven|stove\s+repair|dishwasher|microwave|garbage\s+disposal|"
                       r"water\s+heater|tankless|well\s+pump|sump\s+pump|septic|"
                       r"sewer|drain\s+clean\w*|chimney|insulation|generator|"
                       r"solar\s+panel|pest\s+control|mold\s+remediation|"
                       r"dryer\s+vent|air\s+duct\s+clean\w*|duct\s+clean\w*|"
                       r"carpet\s+clean\w*|handyman|garage\s+door|fence\b|"
                       r"landscap\w*|lawn\b|painting|flooring|remodel\w*)\b",
        "COMMERCIAL_INDUSTRIAL": r"\b(chiller|chillers|rooftop\s+unit|\brtu\b|walk[\s-]*in\s+"
                                 r"(cooler|freezer)|ice\s+machine|refrigeration|"
                                 r"cold\s+storage|data\s+center|server\s+room|"
                                 r"industrial|warehouse|manufactur\w*|"
                                 r"cooling\s+tower|boiler\s+plant|steam\s+boiler|"
                                 r"commercial\s+kitchen)\b",
        "EQUIPMENT_SHOPPING": r"\b(trane|carrier|lennox|goodman|rheem|ruud|york\b|amana|"
                              r"bryant|daikin|mitsubishi|fujitsu|gree\b|midea|lg\b|"
                              r"samsung|frigidaire|payne|heil|coleman\s+hvac|"
                              r"weil[\s-]*mclain|burnham|navien|viessmann|buderus|"
                              r"lochinvar|slant[\s/-]*fin)\b.*\b(price|prices|cost|review|"
                              r"reviews|model|models|manual|spec|specs|"
                              r"vs\b|versus|for\s+sale|buy|warranty\s+check|"
                              r"serial|parts|filter|capacitor)\b",
        "PARTS_CONSUMABLE": r"\b(filter|filters|capacitor|contactor|freon|r22\b|r410a?\b|"
                            r"refrigerant\s+(price|buy|for\s+sale)|thermocouple|"
                            r"igniter|blower\s+motor|fan\s+motor|coil\s+cleaner|"
                            r"condensate\s+pump|line\s+set|copper\s+line|"
                            r"vent\s+cover|register|grille|duct\s+tape|"
                            r"filter\s+size|merv|air\s+filter)\b",
    },
    "geo_in": r"\b(severn|severna\s+park|columbia|anne\s+arundel|\baac\b|glen\s+burnie|"
              r"pasadena|millersville|crofton|odenton|gambrills|annapolis|"
              r"ellicott\s+city|elkridge|jessup|laurel|savage|hanover|"
              r"linthicum|arnold|edgewater|davidsonville|bowie|crownsville|"
              r"howard\s+county|maryland|\bmd\b|baltimore|catonsville|"
              r"clarksville|fulton|dayton|highland|west\s+friendship|"
              r"marriottsville|woodbine|sykesville|eldersburg|pikesville|"
              r"towson|parkville|dundalk|essex|white\s+marsh|nottingham|"
              r"perry\s+hall|owings\s+mills|randallstown|reisterstown)\b",
    "geo_out": r"\b(virginia|\bva\b|washington\s*dc|\bdc\b|district\s+of\s+columbia|"
               r"delaware|\bde\b|pennsylvania|\bpa\b|new\s+jersey|\bnj\b|"
               r"new\s+york|\bny\b|florida|\bfl\b|texas|\btx\b|california|\bca\b|"
               r"georgia|north\s+carolina|south\s+carolina|ohio|michigan|"
               r"illinois|chicago|houston|dallas|austin|phoenix|atlanta|"
               r"denver|seattle|portland|boston|philadelphia|pittsburgh|"
               r"richmond|norfolk|virginia\s+beach|alexandria|arlington|"
               r"fairfax|rockville|bethesda|silver\s+spring|gaithersburg|"
               r"frederick|hagerstown|salisbury|ocean\s+city|cumberland)\b",
}

# ---------------------------------------------------------------------------
# PRO GREEN AUSTIN  (7380491929)  hardscaping
# Approved service: outdoor design & build.
# Service area: Austin TX metro (Cedar Park, Georgetown, Leander, Barton Creek...).
# ---------------------------------------------------------------------------
PRO_GREEN = {
    "slug": "pro-green-austin",
    "customer_id": "7380491929",
    "brand": r"\b(pro\s*green|progreen|pro\s*green\s+landscape\s+solutions|"
             r"progreenlandscape\w*)\b",
    "core": r"(landscap\w*|hardscap\w*|\bpatio\w*|\bpaver\w*|retaining\s+wall|"
            r"outdoor\s+(living|kitchen|space|design|lighting|fireplace)|"
            r"pergola\w*|\bpavilion|\bgazebo|\bpalapa\w*|\bramada|\bcabana|"
            r"\barbor\b|\btrellis|walkway\w*|\bdriveway\w*|"
            r"artificial\s+(turf|grass)|synthetic\s+(turf|grass)|"
            r"fire\s*pit|fire\s*place|\bmasonry\b|stone\s+work|stonework|"
            r"flagstone|\btravertine|\bhardscape|backyard|back\s+yard|"
            r"\bcourtyard|pool\s+deck|\bdeck\w*|stamped\s+concrete|"
            r"paver\s+patio|\bcurbing|garden\s+design|yard\s+design)",
    "intent": r"\b(design|designer|build|builder|install\w*|contractor|contractors|"
              r"compan\w+|service|services|near\s+me|near\s+you|cost|price|"
              r"pricing|quote|estimate|repair|replace\w*|renovat\w*|remodel\w*|"
              r"custom|professional|\bpro\b)\b",
    "disqualify": {
        "MAINTENANCE_NOT_BUILD": r"\b(mow\w*|mowing|lawn\s+(care|service|mainten\w*|mowing|"
                                 r"treatment|fertiliz\w*|aeration|aerat\w*)|"
                                 r"weed\s+control|weeding|leaf\s+removal|"
                                 r"tree\s+(trim\w*|remov\w*|service|cutting|pruning)|"
                                 r"stump\s+grind\w*|hedge\s+trim\w*|"
                                 r"gutter\s+clean\w*|snow\s+remov\w*|"
                                 r"pressure\s+wash\w*|power\s+wash\w*|"
                                 r"sprinkler\s+repair|irrigation\s+repair|"
                                 r"pest\s+control|mosquito)\b",
        "MATERIALS_SUPPLY": r"\b(per\s+(square\s+)?(foot|ft|yard)\s+(of\s+)?material|"
                            r"bulk\s+(mulch|gravel|sand|stone|soil|dirt)|"
                            r"topsoil\s+delivery|mulch\s+delivery|gravel\s+delivery|"
                            r"sod\s+delivery|nursery|garden\s+center|"
                            r"plants?\s+for\s+sale|seeds?\b|seedling|"
                            r"stone\s+yard|quarry|landscape\s+supply|"
                            r"\bpallet\b|cubic\s+yard|ton\s+of\b)\b",
        "OTHER_TRADE": r"\b(pool\s+(build\w*|install\w*|compan\w+|contractor|"
                       r"resurfac\w*|clean\w*|service)|"
                       r"fence\s+(install\w*|compan\w+|contractor|repair)|"
                       r"roof\w*|siding|window\s+replacement|"
                       r"home\s+build\w*|house\s+build\w*|custom\s+home|"
                       r"kitchen\s+remodel|bathroom\s+remodel|"
                       r"foundation\s+repair|septic|well\s+drilling|"
                       r"solar\s+panel|hvac|plumb\w*|electric\w+\s+contractor|"
                       r"garage\s+door|driveway\s+seal\w*|asphalt|"
                       r"concrete\s+(truck|delivery|mix))\b",
        "ARCHITECT_STUDY": r"\b(landscape\s+architect\w*\s+(degree|program|school|"
                           r"licen[cs]\w*|salary|exam)|"
                           r"landscape\s+(design|architecture)\s+(school|degree|"
                           r"course|class|program|certificate))\b",
        "IDEAS_INSPIRATION": r"\b(ideas?|inspiration|pinterest|instagram|"
                             r"before\s+and\s+after|gallery|examples?|"
                             r"trends?|styles?|colou?rs?\s+chart|"
                             r"what\s+is\b|meaning|definition|difference\s+between|"
                             r"pros\s+and\s+cons|vs\b|versus)\b",
    },
    "geo_in": r"\b(austin|cedar\s+park|georgetown|leander|round\s+rock|"
              r"barton\s+creek|lakeway|bee\s+cave|west\s+lake\s+hills|westlake|"
              r"steiner\s+ranch|spicewood|dripping\s+springs|liberty\s+hill|"
              r"jonestown|lago\s+vista|pflugerville|hutto|"
              r"travis\s+county|williamson\s+county|\btexas\b|\btx\b|"
              r"north\s+austin|south\s+austin|west\s+austin|downtown\s+austin|"
              r"tarrytown|clarksville|zilker|hyde\s+park|mueller|"
              r"circle\s+c|avery\s+ranch|brushy\s+creek|anderson\s+mill)\b",
    "geo_out": r"\b(dallas|houston|san\s+antonio|fort\s+worth|el\s+paso|"
               r"corpus\s+christi|lubbock|amarillo|waco|tyler|midland|"
               r"college\s+station|plano|frisco|arlington\s+tx|irving|"
               r"mckinney|denton|katy|sugar\s+land|the\s+woodlands|"
               r"california|florida|arizona|colorado|oklahoma|"
               r"new\s+mexico|louisiana|arkansas|georgia|tennessee|"
               r"north\s+carolina|nevada|utah|phoenix|denver|atlanta|"
               r"nashville|las\s+vegas|los\s+angeles|san\s+diego|"
               r"new\s+york|chicago|seattle|portland|miami|orlando|tampa)\b",
}

# ---------------------------------------------------------------------------
# SOFTWIND POWER WASHING  (1521725229)  similar-local-service (approved)
# Approved service: Power Washing (+ pressure / house / soft / driveway / patio).
# Explicitly EXCLUDED by the work order: roof cleaning, gutter cleaning,
# paver sealing, landscaping, masonry, painting, shrink wrapping,
# party rentals, lawn care.
# Service area: Long Island NY (Nassau / Suffolk).
# ---------------------------------------------------------------------------
SOFTWIND_PW = {
    "slug": "softwind-power-washing",
    "customer_id": "1521725229",
    "brand": r"\b(softwind|soft\s*wind|softwindli|"
             r"softwind\s+(power|pressure)\s*wash\w*)\b",
    "core": r"(power\s*wash\w*|powerwash\w*|pressure\s*wash\w*|pressurewash\w*|"
            r"soft\s*wash\w*|softwash\w*|house\s*wash\w*|"
            r"exterior\s+clean\w*|siding\s+clean\w*|driveway\s+clean\w*|"
            r"concrete\s+clean\w*|patio\s+clean\w*|deck\s+clean\w*|"
            r"fence\s+clean\w*|walkway\s+clean\w*|"
            r"mildew\s+remov\w*|algae\s+remov\w*|"
            r"\bwash\s+(house|siding|deck|patio|driveway|fence))",
    "intent": r"\b(service|services|compan\w+|contractor|contractors|near\s+me|"
              r"near\s+you|cost|price|pricing|quote|estimate|"
              r"residential|home|house|professional|\bpro\b|"
              r"hire|book|schedule)\b",
    "disqualify": {
        "EXCLUDED_SERVICE": r"\b(roof\s*(clean\w*|wash\w*|soft\s*wash)|"
                            r"gutter\s*(clean\w*|guard|wash\w*|repair|install\w*)|"
                            r"paver\s*seal\w*|seal\s*(coat\w*|ing\s+paver)|"
                            r"landscap\w*|lawn\s+(care|mow\w*|service)|"
                            r"mow\w*|masonry|brick\s+(repair|point\w*)|"
                            r"paint\w*|shrink\s*wrap\w*|"
                            r"party\s+rental|tent\s+rental|bounce\s+house|"
                            r"chimney|window\s+clean\w*|"
                            r"carpet\s+clean\w*|duct\s+clean\w*|"
                            r"junk\s+remov\w*|maid|housekeep\w*|"
                            r"snow\s+remov\w*|tree\s+service)\b",
        "VEHICLE_WASH": r"\b(car\s*wash|auto\s*(wash|detail\w*)|truck\s*wash|"
                        r"boat\s*(wash|clean\w*|detail\w*)|fleet\s+wash\w*|"
                        r"mobile\s+detail\w*|rv\s+wash|trailer\s+wash|"
                        r"engine\s+clean\w*)\b",
        "EQUIPMENT_SHOPPING": r"\b(karcher|kärcher|ryobi|simpson|generac|dewalt|"
                              r"greenworks|sun\s*joe|craftsman|briggs|"
                              r"honda\s+pressure|electric\s+pressure\s+washer|"
                              r"gas\s+pressure\s+washer|pressure\s+washer\s+"
                              r"(pump|hose|nozzle|gun|wand|tip|tips|parts|repair|"
                              r"psi|reviews?|comparison|best|buy|sale|rental|rent)|"
                              r"surface\s+cleaner\s+attachment|"
                              r"\bpsi\b|\bgpm\b|foam\s+cannon|"
                              r"soap|detergent|chemical|bleach|"
                              r"sodium\s+hypochlorite|\bsh\s+mix)\b",
        "COMMERCIAL_B2B": r"\b(commercial\s+(pressure|power)\s+wash|"
                          r"parking\s+(lot|garage)|dumpster\s+pad|"
                          r"drive\s*thru|restaurant\s+hood|kitchen\s+exhaust|"
                          r"graffiti\s+remov\w*|industrial\s+clean\w*|"
                          r"warehouse|municipal|government\s+contract|"
                          r"rfp\b|bid\s+(request|opportunit))\b",
    },
    "geo_in": r"\b(long\s+island|nassau|suffolk|bellmore|merrick|wantagh|"
              r"seaford|massapequa|levittown|hicksville|garden\s+city|"
              r"mineola|westbury|hempstead|freeport|baldwin|rockville\s+cent\w*|"
              r"lynbrook|valley\s+stream|oceanside|long\s+beach|"
              r"farmingdale|bethpage|plainview|syosset|jericho|"
              r"huntington|melville|commack|smithtown|hauppauge|"
              r"islip|babylon|lindenhurst|amityville|copiague|"
              r"deer\s+park|bay\s+shore|patchogue|ronkonkoma|"
              r"port\s+washington|manhasset|great\s+neck|roslyn|"
              r"east\s+meadow|uniondale|garden\s+city|new\s+hyde\s+park)\b",
    "geo_out": r"\b(manhattan|brooklyn|queens|bronx|staten\s+island|"
               r"new\s+jersey|\bnj\b|connecticut|\bct\b|"
               r"westchester|yonkers|white\s+plains|"
               r"philadelphia|boston|florida|\bfl\b|california|"
               r"texas|\btx\b|georgia|north\s+carolina|"
               r"virginia|maryland|pennsylvania|\bpa\b|"
               r"upstate|albany|buffalo|rochester|syracuse|"
               r"atlanta|charlotte|tampa|orlando|miami|houston|dallas)\b",
}

# ---------------------------------------------------------------------------
# SOFTWIND LANDSCAPE & MASONRY  (2429758629)  hardscaping
# Identity gate PASS 2026-08-29 (snapshots/identity-gate-2026-08-29-0928.json).
# Approved service: Pavers (primary) + Patio. Expected campaigns: Patio, Pavers.
# Sibling account Softwind Power Washing (1521725229) owns ALL exterior-cleaning
# intent. Mutual exclusion, owner instruction 2026-08-28:
#   "patio cleaning" -> 1521725229 ; "patio installation" -> 2429758629.
# Paver SEALING belongs here (SLM-Q4), paver CLEANING belongs to the sibling.
#
# geo_verified is True as of 2026-08-30: the service area was read from THIS
# account's own campaign_criterion (scripts/slm_geo_read.py), not inferred from
# the sibling. It independently resolves to Nassau/Suffolk, Long Island NY --
# the same region the sibling targets, but now on this account's own evidence.
#
# core deliberately includes landscaping and masonry: the account name and the
# owner's own wording assert them, and a broader core mints FEWER negatives.
# Narrow it only if the campaign read shows Patio and Pavers alone.
# ---------------------------------------------------------------------------
SOFTWIND_LM = {
    "slug": "softwind-landscape-masonry",
    "customer_id": "2429758629",
    # Verified 2026-08-30 by scripts/slm_geo_read.py, read from THIS account's
    # campaign_criterion. See the geo_in note at the foot of this entry.
    "geo_verified": True,
    "brand": r"\b(softwind|soft\s*wind|softwindli|"
             r"softwind\s+(landscap\w*|masonry|paver\w*))\b",
    "core": r"(\bpaver\w*|paving\s+stone\w*|\bpatio\w*|hardscap\w*|"
            r"retaining\s+wall|\bwalkway\w*|\bdriveway\w*|\bstoop\b|"
            r"front\s+steps|\bstepping\s+stone|pool\s+(deck|patio)|"
            r"\bmasonry\b|stone\s*work|brick\s*(work|lay\w*|repair|point\w*)|"
            r"\bflagstone|\btravertine|\bbluestone|\bcobblestone|"
            r"stamped\s+concrete|concrete\s+patio|\bveneer\b|"
            r"outdoor\s+(living|kitchen|space|fireplace|lighting)|"
            r"fire\s*pit|\bpergola\w*|\bpavilion|\bgazebo|"
            r"landscap\w*|\bcurbing|\bcurb\s+appeal|"
            r"seal\w*\s+paver\w*|paver\s+seal\w*|"
            # Paver manufacturers are DEMAND, not competitors. See the
            # broad-name-negative-guards rule: never negative these.
            # 2026-08-30: these were brand+product ("cambridge paver"), so
            # Cambridge WALL products fell through and "cambridge block wall"
            # and "cambridge wall stone" were minted as negatives. This account
            # installs those products and shows real brand demand
            # ("cambridge pavers near me" $44.60 KEEP). Match the bare brand:
            # protecting a term only ever mints FEWER negatives, so a false
            # positive here is the safe direction.
            r"\bcambridge\b|\bnicolock|\btecho\s*-?\s*bloc|\bunilock|"
            r"\bep\s+henry|\bbelgard|\bnicolia)",
    "intent": r"\b(install\w*|installer|build|builder|design|designer|"
              r"contractor|contractors|compan\w+|service|services|"
              r"near\s+me|near\s+you|cost|price|pricing|quote|estimate|"
              r"repair|replace\w*|redo|resurfac\w*|extend|extension|"
              r"custom|professional|\bpro\b|\bhire\b|per\s+square\s+foot)\b",
    "disqualify": {
        # ---- the cross-account fence. This intent belongs to 1521725229. ----
        "SIBLING_EXTERIOR_CLEANING": r"\b((power|pressure|soft|house)\s*wash\w*|"
                                     r"powerwash\w*|pressurewash\w*|softwash\w*|"
                                     r"housewash\w*|"
                                     r"roof\s*(clean\w*|wash\w*)|"
                                     r"gutter\s*(clean\w*|guard|wash\w*)|"
                                     r"window\s+clean\w*|"
                                     r"(patio|paver|driveway|deck|concrete|siding|"
                                     r"fence|walkway|brick|stone)\s+clean\w*|"
                                     r"clean\s+(my\s+)?(patio|pavers?|driveway|deck)|"
                                     r"(mildew|algae|moss)\s+remov\w*|"
                                     r"exterior\s+clean\w*)\b",
        "OTHER_TRADE": r"\b(pool\s+(build\w*|install\w*|compan\w+|contractor|"
                       r"resurfac\w*|liner|service)|"
                       r"fence\s+(install\w*|compan\w+|contractor|repair)|"
                       r"roof\w*\s+(repair|replac\w*|install\w*|contractor)|"
                       r"siding\s+(install\w*|repair|contractor)|"
                       r"window\s+replacement|kitchen\s+remodel|"
                       r"bathroom\s+remodel|foundation\s+repair|"
                       r"chimney\s+(repair|sweep|clean\w*)|"
                       r"septic|well\s+drilling|solar\s+panel|hvac|plumb\w*|"
                       r"garage\s+door|asphalt\s+(driveway|paving)|"
                       r"blacktop|driveway\s+seal\s*coat\w*)\b",
        "MATERIALS_SUPPLY": r"\b(bulk\s+(mulch|gravel|sand|stone|soil|dirt|topsoil)|"
                            r"topsoil\s+delivery|mulch\s+delivery|"
                            r"gravel\s+delivery|sod\s+delivery|"
                            r"stone\s+yard|quarry|landscape\s+supply|"
                            r"nursery|garden\s+cent(er|re)|"
                            r"\bpallet\s+of\b|cubic\s+yard|\bton\s+of\b|"
                            r"paver\s+(calculator|weight|size\s+chart))\b",
        "IDEAS_INSPIRATION": r"\b(ideas?|inspiration|pinterest|instagram|"
                             r"before\s+and\s+after|gallery|examples?|"
                             r"trends?|colou?rs?\s+chart|"
                             r"what\s+is\b|meaning|definition|"
                             r"difference\s+between|pros\s+and\s+cons|"
                             r"\bvs\b|versus)\b",
    },
    # ---- READ FROM campaign_criterion 2026-08-30, NOT from the sibling. ----
    # scripts/slm_geo_read.py against 2429758629. All six campaigns carry an
    # identical 110-criterion footprint, 660/660 criteria in New York, zero
    # location exclusions, positive+negative geo target type PRESENCE.
    # Receipt: snapshots/geo-read-2026-08-30.json
    # 52 place names + 58 postal codes, Nassau and Suffolk counties.
    "geo_in": r"\b(long\s+island|\bli\b|nassau|suffolk|"
              r"amityville|babylon|bay\s*shore|bayport|bellmore|"
              r"blue\s+point|bohemia|brightwaters|centereach|commack|"
              r"copiague|deer\s+park|dix\s+hills|islip|northport|"
              r"farmingdale|garden\s+city|glenwood\s+landing|great\s+river|"
              r"hauppauge|hicksville|holbrook|huntington|kings\s+park|"
              r"lake\s+grove|lindenhurst|massapequa|melville|merrick|"
              r"nesconset|hempstead|wantagh|oakdale|patchogue|"
              r"pine\s+aire|plainview|ronkonkoma|saint\s+james|st\s+james|"
              r"salisbury|sayville|smithtown|stony\s+brook|syosset|"
              r"11050|11501|11530|11542|11545|11554|11560|11566|11568|"
              r"11576|11579|11590|11701|11702|11706|11710|11714|11716|"
              r"11721|11724|11726|11730|11731|11732|11735|11738|11739|"
              r"11740|11742|11743|11746|11747|11749|11751|11752|11753|"
              r"11755|11756|11757|11758|11762|11763|11765|11767|11769|"
              r"11771|11779|11780|11783|11787|11790|11791|11793|11795|"
              r"11797|11798|11803|11804)\b",
    # Only unambiguously-outside markers. Nassau/Suffolk places that are simply
    # untargeted (e.g. Long Beach, Freeport) are in NEITHER list on purpose:
    # classify() mints a negative only on a geo_out hit, so omitting them mints
    # nothing rather than risking a destructive block. Conservative by design.
    "geo_out": r"\b(manhattan|brooklyn|queens|bronx|staten\s+island|"
               r"new\s+jersey|\bnj\b|connecticut|\bct\b|"
               r"westchester|yonkers|white\s+plains|rockland|"
               r"philadelphia|boston|florida|\bfl\b|california|"
               r"texas|\btx\b|georgia|north\s+carolina|"
               r"virginia|maryland|pennsylvania|\bpa\b|"
               r"upstate|albany|buffalo|rochester|syracuse|"
               r"atlanta|charlotte|tampa|orlando|miami|houston|dallas)\b",
}

ACCOUNTS = {a["slug"]: a for a in (AMBIENT, PRO_GREEN, SOFTWIND_PW, SOFTWIND_LM)}


def compile_account(cfg: dict) -> dict:
    # classify() turns a geo_out hit into a GEO_OUT_OF_AREA negative, so an
    # unverified service area is a destructive object. Refuse rather than guess.
    if not cfg.get("geo_verified", True):
        raise ValueError(
            "{}: geo_in/geo_out are unverified. Read the service area from "
            "campaign_criterion for {} and set geo_verified: True in "
            "neg_lexicon.py before classifying.".format(
                cfg["slug"], cfg["customer_id"]))
    out = {
        "slug": cfg["slug"],
        "customer_id": cfg["customer_id"],
        "core": re.compile(cfg["core"], re.I),
        "intent": re.compile(cfg["intent"], re.I),
        "brand": re.compile(cfg["brand"], re.I),
        "geo_in": re.compile(cfg["geo_in"], re.I),
        "geo_out": re.compile(cfg["geo_out"], re.I),
        "disqualify": {k: re.compile(v, re.I) for k, v in cfg["disqualify"].items()},
        "shared": {k: re.compile(v, re.I) for k, v in SHARED.items()},
    }
    return out


def classify(term: str, comp: dict) -> tuple[str, str]:
    """Return (verdict, category). Verdict is KEEP, WATCH or NEGATIVE."""
    t = " " + term.lower().strip() + " "

    # 0. The client's own brand is always in scope, whatever else it carries.
    if comp["brand"].search(t):
        return "KEEP", "BRAND_PROTECTED"

    # 1. Hard disqualifiers first: they name something the client does not sell.
    for cat, rx in comp["disqualify"].items():
        if rx.search(t):
            return "NEGATIVE", cat
    for cat, rx in comp["shared"].items():
        if rx.search(t):
            return "NEGATIVE", cat
    if comp["geo_out"].search(t) and not comp["geo_in"].search(t):
        return "NEGATIVE", "GEO_OUT_OF_AREA"

    # 2. Whitelist: must carry a core service token.
    has_core = bool(comp["core"].search(t))
    if not has_core:
        return "NEGATIVE", "OUT_OF_SCOPE_NO_CORE_SERVICE"

    # 3. In scope. Commercial intent decides KEEP vs WATCH.
    if comp["intent"].search(t):
        return "KEEP", "IN_SCOPE_COMMERCIAL"
    return "WATCH", "IN_SCOPE_NO_CLEAR_INTENT"
