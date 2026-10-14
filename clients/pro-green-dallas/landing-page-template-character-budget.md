# Landing-Page Template — Character Budget Map

**Template inspected read-only:** `https://richardb891.sg-host.com/` on 2026-08-11 via browser
DevTools. **Nothing on the template site was edited.**

**Target page:** `https://offer.progreenlandscapesolutions.com/sprinkler-irrigation-repair/`
**Client:** Pro Green Landscape Solutions · **Market:** Dallas–Fort Worth
**Page height inspected:** 5,712 px · **56 text elements** and **20 image slots** captured.

Counts include spaces. "Diff" is final minus template. Target band is ±10% where practical;
where clarity beat symmetry, that is stated.

---

## Structural change required — the false promotion

The template ships a **"Get 10% Off"** banner with an **"Offer Ends in"** countdown.
**Pro Green does not offer 10% off** [USER]. That section must not be reproduced.

**It is replaced, not deleted** — the layout slot is kept and refilled with an evergreen
conversion block. **Recommend the development team remove or disable the countdown timer
entirely**, since there is no real deadline. A countdown with no deadline is a fabricated
urgency signal.

This is the **only** structural deviation from the template.

---

## Section 1 — Header

| Element | Template text | Chars | Target | Max safe | Final copy | Chars | Diff | Desktop wrap | Mobile wrap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Logo | `LOGO-HERE.png` (259×36) | — | — | — | Approved Pro Green Landscape Solutions logo | — | — | none | none |
| Header call button | `CALL: 123-456-7890` | 18 | 16–20 | 24 | `CALL: (214) 300-9564` | 20 | +2 | none | none |

**Phone rule:** the header button renders the **base number (214) 300-9564** so WhatConverts DNI
can swap it. Never hard-code the pool number; never place the Google call-asset number here.

---

## Section 2 — Hero

| Element | Template text | Chars | Target | Max safe | Final copy | Chars | Diff | Desktop wrap | Mobile wrap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Eyebrow | `Request Your Free SHORTCODE Quote` | 33 | 30–36 | 45 | `Request Your Free Repair Estimate` | 33 | 0 | none | none |
| **H1** | `Custom SHORTCODE in SHORTCODE` | 29 | 26–32 | 55 | `Sprinkler & Irrigation Repair in Dallas–Fort Worth` | 49 | **+20** | 2 lines | 3 lines |
| Hero p 1 | `Lorem ipsum … tempor.` | 79 | 71–87 | 110 | `Professional sprinkler, irrigation and irrigation system repair across DFW.` | 74 | −5 | none | 2 lines |
| Hero p 2 | `Lorem ipsum dolor sit amet, consectetur.` | 40 | 36–44 | 60 | `Licensed and insured. Free estimates on every visit.` | 51 | +11 | none | none |
| Form heading | *(form block)* | — | — | — | `Get Your Free Repair Estimate` | 29 | — | none | none |
| Form label 1 | `Full Name*` | 10 | — | 20 | `Full Name*` | 10 | 0 | none | none |
| Form label 2 | `Phone Number*` | 13 | — | 20 | `Phone Number*` | 13 | 0 | none | none |
| Form label 3 | `Email Address*` | 14 | — | 20 | `Email Address*` | 14 | 0 | none | none |
| Form label 4 | `Tell us about your project (optional)*` | 38 | 34–42 | 55 | `What is your system doing? (optional)` | 37 | −1 | none | 2 lines |
| **New field** | — | — | — | 30 | `Service Address or ZIP*` | 23 | new | none | none |
| Form button | `Get My Free Quote` | 17 | 15–19 | 24 | `Get My Free Estimate` | 20 | +3 | none | none |
| Conditional line | *(none in template)* | — | — | 40 | `Same-Day Service May Be Available.` | 34 | new | none | none |

**H1 is deliberately 69% over template length.** The template H1 is a placeholder
(`Custom SHORTCODE in SHORTCODE`) whose real-world expansion would also be long. Ad-to-page
message match requires both head terms and the market. **Recommend the developer reduce the H1
font-size one step at ≤768 px** so it holds at three lines on a 360 px viewport.

**"Service Address or ZIP" is an added field.** It qualifies service area at capture, which
directly serves the out-of-area lead-exclusion policy.

---

## Section 3 — Intro and three benefit cards

| Element | Template text | Chars | Target | Max safe | Final copy | Chars | Diff | Desktop wrap | Mobile wrap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | `Lorem ipsum dolor sit amet.` | 27 | 24–30 | 60 | `Repairs Done Right the First Time` | 33 | +6 | none | none |
| Intro p | `Lorem ipsum … dolore.` | 110 | 99–121 | 160 | `Most DFW sprinkler failures are a repair, not a replacement. We find the real fault and show you.` | 96 | −14 | 2 lines | 3 lines |
| Card 1 h3 | `Lorem ipsum dolor sit amet?` | 27 | 24–30 | 40 | `Licensed & Insured` | 18 | −9 | none | none |
| Card 1 p | `Lorem ipsum … elit sed.` | 60 | 54–66 | 90 | `Fully licensed and insured for every sprinkler and irrigation repair.` | 68 | +8 | none | 2 lines |
| Card 2 h3 | `Lorem ipsum dolor sit amet, consectetur?` | 40 | 36–44 | 40 | `Free Estimates` | 14 | −26 | none | none |
| Card 2 p | `Lorem ipsum … eiusmod tempor.` | 78 | 70–86 | 90 | `We diagnose the problem and quote the repair before any work begins. No charge.` | 78 | **0** | none | 2 lines |
| Card 3 h3 | *(third card)* | ~30 | 24–34 | 40 | `18-Point System Check` | 21 | −9 | none | none |
| Card 3 p | *(third card)* | ~70 | 63–77 | 90 | `Every visit includes a full system inspection, not just the part you noticed.` | 76 | +6 | none | 2 lines |
| Button | `Get Your Free Quote!` | 20 | 18–22 | 26 | `Get Your Free Estimate` | 22 | +2 | none | none |

**Card headings run short by design.** They are verified-claim labels; padding them to match a
Lorem placeholder would add words without meaning.

---

## Section 4 — REPLACED: promotional banner → evergreen conversion block

**Template content, all removed:**

| Template element | Chars | Status |
| --- | --- | --- |
| `Get 10% Off Your Next SHORTCODE Project` | 39 | ❌ **REMOVED — expired, prohibited** |
| Body Lorem paragraph | 207 | replaced |
| `Offer Ends in` + countdown timer | 13 | ❌ **REMOVED — no real deadline** |
| `Get My 10% Discount` | 19 | ❌ **REMOVED** |

**Replacement:**

| Element | Target | Max safe | Final copy | Chars | Desktop wrap | Mobile wrap |
| --- | --- | --- | --- | --- | --- | --- |
| H2 | 35–43 | 60 | `Same-Day Service May Be Available` | 32 | none | none |
| Body | 186–228 | 260 | `Sprinkler problems get worse and more expensive the longer they run. Call and we will tell you the soonest we can be there, and give you a free estimate with a full 18-point system check.` | 186 | 2 lines | 4 lines |
| Button | 17–21 | 26 | `Request Your Free Estimate` | 26 | none | none |

The H2 is the required wording minus the trailing period, which reads correctly as a heading.
**The full sentence with its period appears in the hero, process, and final CTA.**

---

## Section 5 — Image-and-copy service section

| Element | Template text | Chars | Target | Max safe | Final copy | Chars | Diff | Desktop wrap | Mobile wrap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | `Beautiful, Durable SHORTCODEs built for SHORTCODE Living` | 56 | 50–62 | 75 | `Professional Sprinkler & Irrigation System Repair` | 48 | −8 | none | 2 lines |
| Body p | `Lorem ipsum … aliquip.` | 207 | 186–228 | 260 | `A single broken head or leaking valve floods one area, starves another, and quietly raises your water bill for months. We diagnose the actual fault across the whole system, then repair it.` | 187 | −20 | 3 lines | 5 lines |
| Bullet 1 | *(list item)* | ~45 | 40–50 | 65 | `Broken, sunken and misaligned sprinkler heads` | 45 | 0 | none | none |
| Bullet 2 | *(list item)* | ~45 | 40–50 | 65 | `Zones that will not start or will not shut off` | 45 | 0 | none | none |
| Bullet 3 | *(list item)* | ~45 | 40–50 | 65 | `Leaking, stuck and failed valves and solenoids` | 46 | +1 | none | none |
| Bullet 4 | *(list item)* | ~45 | 40–50 | 65 | `Low pressure, dead zones and controller faults` | 46 | +1 | none | none |
| Sub-heading h3 | `Lorem Ipsum Dolor` | 17 | 15–19 | 30 | `Repairs Across DFW` | 18 | +1 | none | none |
| Button | `Plan Your Project` | 17 | 15–19 | 26 | `Book Your Repair Visit` | 22 | +5 | none | none |

---

## Section 6 — Three service cards

**Template heading `One Team for Your Entire Outdoors` (33) is off-scope** — it implies full-service
landscaping. Replaced.

| Element | Template text | Chars | Target | Max safe | Final copy | Chars | Diff |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | `One Team for Your Entire Outdoors` | 33 | 30–36 | 60 | `What We Repair` | 14 | −19 |
| Intro p | `Lorem ipsum … magna aliqua.` | 123 | 111–135 | 160 | `Four core repairs, handled by licensed technicians across Dallas, Fort Worth and Frisco.` | 87 | −36 |
| Card 1 title | `Concrete & Paver Patios` (alt) | 23 | 20–26 | 34 | `Sprinkler Repair` | 16 | −7 |
| Card 1 desc | `Lorem ipsum … incididunt.` | 90 | 81–99 | 120 | `Broken and sunken heads, cracked laterals, and coverage that leaves dry or flooded patches.` | 90 | **0** |
| Card 2 title | *(card 2)* | 23 | 20–26 | 34 | `Irrigation Repair` | 17 | −6 |
| Card 2 desc | *(card 2)* | 90 | 81–99 | 120 | `Mainline and lateral leaks, pressure loss, wiring faults and zones that stopped responding.` | 90 | **0** |
| Card 3 title | *(card 3)* | 23 | 20–26 | 34 | `Sprinkler Head & Valve Repair` | 29 | +6 |
| Card 3 desc | *(card 3)* | 90 | 81–99 | 120 | `Head replacement, nozzle matching, and stuck, leaking or failed valves and valve boxes.` | 86 | −4 |
| Button | `Get My Free Quote!` | 18 | 16–20 | 26 | `Get My Free Estimate` | 20 | +2 |

**The template has three card slots and Pro Green has four services.** Head repair and valve repair
are combined into card 3 rather than adding a fourth card, which would break the template grid.
Both remain separately named for keyword relevance.

---

## Section 7 — Recent project gallery

| Element | Template text | Chars | Target | Max safe | Final copy | Chars | Diff |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | `Recent Project Highlights` | 25 | 22–28 | 45 | `Recent Repairs` | 14 | −11 |
| Sub p | `See the quality of our work and get inspired for your own project.` | 66 | 59–73 | 90 | `Real sprinkler and irrigation repairs completed across the DFW area.` | 67 | +1 |

**"Project" language replaced with "repair"** — the template is written for installation work.
**11 gallery slots. Every image must be a genuine Pro Green photo.** No stock, no invented results.

---

## Section 8 — Three-step process

| Element | Template text | Chars | Target | Max safe | Final copy | Chars | Diff |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | `Your Dream Yard in 3 Simple Steps` | 33 | 30–36 | 55 | `Your Repair in 3 Simple Steps` | 29 | −4 |
| Step 1 title | `1. Request Quote` | 16 | 14–18 | 24 | `1. Call or Request` | 18 | +2 |
| Step 1 desc | `Fill out our form or call us. We'll get back to you to discuss your vision.` | 75 | 67–83 | 100 | `Call or send the form and tell us what the system is doing.` | 58 | −17 |
| Step 2 title | `2. Design & Schedule` | 20 | 18–22 | 24 | `2. Diagnose & Quote` | 19 | −1 |
| Step 2 desc | `We'll create a custom plan and schedule the installation at your convenience.` | 77 | 69–85 | 100 | `We inspect the system, run the 18-point check and give you a free estimate.` | 74 | −3 |
| Step 3 title | `3. Enjoy Your Yard` | 18 | 16–20 | 24 | `3. Repaired & Tested` | 20 | +2 |
| Step 3 desc | `Our professional crew completes the work efficiently, leaving you with a space to love.` | 87 | 78–96 | 100 | `We complete the repair and run every zone so you see it working before we leave.` | 79 | −8 |
| Callback 1 | `Callback <10 min` | 16 | — | — | **❌ REMOVE** | — | — |
| Callback 2 | `Install start ≤7 days` | 21 | — | — | **❌ REMOVE** | — | — |
| Callback 3 | `Project complete on time` | 24 | — | — | **❌ REMOVE** | — | — |

**The three "callback" micro-promises must be deleted, not rewritten.** `Callback <10 min` and
`Install start ≤7 days` are **response-time guarantees that are unverified for Pro Green**, and
`Install start` refers to installation, which is out of scope. If the client later verifies a real
response-time commitment, it can be reinstated in that slot with the verified wording.

---

## Section 9 — Reviews

| Element | Template text | Chars | Status |
| --- | --- | --- | --- |
| H2 | `What Your Neighbors Are Saying` | 30 | Keep as-is — 30 chars, accurate, no claim |
| Review body ×3 | Lorem placeholders | — | **PLACEHOLDER — client must supply real reviews** |
| Attribution | `Jenna K. Fort Dodge` | 19 | **❌ REMOVE — fabricated, and Fort Dodge is in Iowa** |
| Star rating graphic | `star-rating.png` ×9 | — | **Do not display until real reviews exist** |

> **REVIEW PLACEHOLDER — DO NOT PUBLISH AS-IS**
> Insert three real, verifiable Pro Green reviews. For each: review text, first name and last
> initial, and a **DFW** city. Only display star graphics if the underlying rating is real.
> **If no verified reviews are available, delete this entire section rather than filling it.**
> Fabricated testimonials are prohibited.

---

## Section 10 — FAQ and second form

| Element | Template text | Chars | Target | Max safe | Final copy | Chars | Diff |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | `Frequently Asked Questions` | 26 | keep | 40 | `Frequently Asked Questions` | 26 | 0 |
| Form heading | `Get a Free Estimate` | 19 | 17–21 | 30 | `Get a Free Estimate` | 19 | 0 |
| FAQ 1 q | `Lorem ipsum dolor sit amet, consectetur adipiscing?` | 51 | 46–56 | 70 | `Do you charge for an estimate?` | 30 | −21 |
| FAQ 1 a | — | — | — | 200 | `No. Estimates are free, and every visit includes an 18-point system check.` | 73 | — |
| FAQ 2 q | — | 46–56 | 70 | `Can you come out today?` | 23 | — |
| FAQ 2 a | — | — | 200 | `Same-Day Service May Be Available. Call and we will tell you the soonest we can be there.` | 88 | — |
| FAQ 3 q | — | 46–56 | 70 | `Are you licensed and insured?` | 29 | — |
| FAQ 3 a | — | — | 200 | `Yes. Pro Green Landscape Solutions is licensed and insured.` | 58 | — |
| FAQ 4 q | — | 46–56 | 70 | `Do you repair systems you did not install?` | 42 | — |
| FAQ 4 a | — | — | 200 | `Yes. We repair existing sprinkler and irrigation systems regardless of who installed them.` | 89 | — |
| FAQ 5 q | — | 46–56 | 70 | `What if the repair does not solve it?` | 37 | — |
| FAQ 5 a | — | — | 200 | `Our work is backed by a customer satisfaction guarantee. Tell us and we will make it right.` | 90 | — |
| FAQ 6 q | — | 46–56 | 70 | `Which areas do you cover?` | 25 | — |
| FAQ 6 a | — | — | 200 | `Dallas, Fort Worth, Frisco and the surrounding DFW area. Call to confirm your address.` | 85 | — |

**FAQ questions run shorter than the 51-char Lorem placeholder deliberately.** Real questions are
short; padding them would hurt scannability, which matters more than symmetry here.

---

## Section 11 — Satisfaction guarantee CTA

| Element | Template text | Chars | Target | Max safe | Final copy | Chars | Diff |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | `Our 100% Satisfaction Guarantee` | 31 | 28–34 | 50 | `Our Customer Satisfaction Guarantee` | 35 | +4 |
| Body | `If you're not 100% thrilled, we'll fix it at no extra charge.` | 61 | 55–67 | 90 | `If the repair does not solve the problem, tell us and we will make it right.` | 75 | +14 |

**"100%" was dropped from both.** The verified claim is a *customer satisfaction guarantee*;
"100% thrilled" is an unverified absolute.

---

## Section 12 — Footer

| Element | Target | Max safe | Final copy | Chars |
| --- | --- | --- | --- | --- |
| Business name | — | 60 | `Pro Green Landscape Solutions` | 29 |
| Descriptor | 80–110 | 140 | `Sprinkler and irrigation repair in Dallas, Fort Worth, Frisco, TX and surrounding areas.` | 87 |
| Trust line | 20–30 | 40 | `Licensed & Insured` | 18 |
| Phone | — | 30 | `Call (214) 300-9564` | 19 |
| Legal | — | 30 | `Privacy Policy` | 14 |

---

## Summary of deviations from template length

| Deviation | Section | Justification |
| --- | --- | --- |
| **H1 +20 chars (+69%)** | Hero | Ad-to-page message match needs both head terms plus the market. Requires a mobile font-size step-down |
| **Card 2 h3 −26** | Benefits | Verified-claim labels are naturally short |
| **Intro p −36** | Services | Removing installation language shortens it; padding would reintroduce off-scope content |
| **H2 −19** | Services | `One Team for Your Entire Outdoors` is off-scope |
| Three callbacks **deleted** | Process | Unverified response-time promises |
| Promo banner **replaced** | Section 4 | Expired 10% offer and a countdown with no deadline |
| Review attribution **deleted** | Reviews | Fabricated testimonial |

Everything else lands within ±10% of the template, or within a stated max-safe bound.
