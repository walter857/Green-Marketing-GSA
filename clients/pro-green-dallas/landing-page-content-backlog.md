# Landing-Page Content Backlog — Pro Green Dallas

**Date:** 2026-08-11 · Prioritised from **live Google Ads evidence** [FRESH-API], not opinion.

---

## 1. Priority page — build first

**`https://offer.progreenlandscapesolutions.com/sprinkler-irrigation-repair/`**

A single combined page serving all three live ad groups. Full copy, character budget, tracking and
QA are in **`landing-page-template-character-budget.md`** and
**`clickup-wordpress-landing-page-task.md`**.

**Why combined first, not four separate pages:**

| Reason | Evidence |
| --- | --- |
| All three live ad groups need a page **now** | They currently split across Page A / Page B with a ~50/50 Nelio randomiser [RUNTIME] |
| Volume does not yet justify four pages | 190 clicks / 90 days total [FRESH-API] |
| Head-repair and valve-repair demand is **unmeasured** | Those keywords were blocked by negatives until 2026-08-11 and are still PAUSED |
| One page can be QA'd, verified and cut over quickly | Four pages multiply the tracking surface before anything is proven |

---

## 2. Ad-group → page mapping

### Now (cutover target)

| Ad group | ID | 30-day spend | Conv | Page after cutover |
| --- | --- | --- | --- | --- |
| Sprinkler Repair Near Me | `151125103616` | $356.45 | 1 | `/sprinkler-irrigation-repair/` |
| Irrigation Repair Near Me | `190202910461` | $346.39 | 2 | `/sprinkler-irrigation-repair/` |
| Sprinkler System Repair | `191996690566` | $317.14 | 0 | `/sprinkler-irrigation-repair/` |

### Future (only if volume justifies it)

| Ad group | Dedicated page | Trigger to build |
| --- | --- | --- |
| Sprinkler Repair | `/sprinkler-repair/` | ≥ 300 impressions/month sustained on sprinkler-repair keywords |
| Irrigation Repair | `/irrigation-repair/` | Same, on irrigation-repair keywords |
| Sprinkler Head Repair | `/sprinkler-head-repair/` | ≥ 100 impressions/month once keywords `sprinkler head repair` / `sprinkler head replacement` are enabled |
| Sprinkler Valve Repair | `/sprinkler-valve-repair/` | ≥ 100 impressions/month once `sprinkler valve repair` / `irrigation valve repair` are enabled |

**Do not build a dedicated page before its trigger fires.** Thin pages with no traffic dilute
Quality Score and add tracking surface for no return.

---

## 3. Prioritised backlog

| # | Page | Priority | Depends on | Status |
| --- | --- | --- | --- | --- |
| **1** | **Combined sprinkler + irrigation repair** | **P0 — build now** | Dev team, `offer.` DNS | Content complete, ready for handoff |
| 2 | Thank-you page | **P0 — same build** | Page 1 | Spec in handoff §9 |
| 3 | Sprinkler Repair (dedicated) | P2 | 30 days post-cutover data | Brief below |
| 4 | Irrigation Repair (dedicated) | P2 | Same | Brief below |
| 5 | Sprinkler Head Repair | P3 | New keywords enabled + 30 days | Brief below |
| 6 | Sprinkler Valve Repair | P3 | Same | Brief below |

---

## 4. Content briefs for future pages

All four inherit the same **non-negotiables**: base number **(214) 300-9564** in source with
WhatConverts DNI · no pool number hard-coded · no Google call-asset number · no
`tel:%91phone%93` · full hidden attribution field set · GTM-NZSMS9RB + AW-11237210508 +
G-5JMRW1LBMF only · no Austin tags · no Nelio · no deferred measurement · no 10% OFF · no
unverified claims · same-day only as **"Same-Day Service May Be Available."**

### Brief 3 — Sprinkler Repair

| Field | Value |
| --- | --- |
| URL | `/sprinkler-repair/` |
| Target keywords | `sprinkler repair`, `sprinkler repair services`, `sprinkler repair near me`, `lawn sprinkler repair` |
| H1 | `Sprinkler Repair in Dallas, Fort Worth & Frisco, TX` |
| Focus | Broken, sunken, clogged and misaligned heads; cracked laterals; uneven coverage |
| Must exclude | Irrigation-system design, installation, winterization |
| Proof needed | 2–3 real sprinkler-repair photos |

### Brief 4 — Irrigation Repair

| Field | Value |
| --- | --- |
| URL | `/irrigation-repair/` |
| Target keywords | `irrigation repair services`, `irrigation repair near me`, `irrigation companies near me`, `irrigation leak repair` |
| H1 | `Irrigation Repair in Dallas, Fort Worth & Frisco, TX` |
| Focus | Mainline and lateral leaks, pressure loss, wiring faults, unresponsive zones |
| Note | This ad group produced **all conversions** in the 90-day window — highest-value dedicated page |
| Proof needed | 2–3 real leak / mainline repair photos |

### Brief 5 — Sprinkler Head Repair

| Field | Value |
| --- | --- |
| URL | `/sprinkler-head-repair/` |
| Target keywords | `sprinkler head repair`, `sprinkler head replacement` |
| H1 | `Sprinkler Head Repair & Replacement in DFW` |
| Focus | Head replacement, nozzle matching, spray-pattern correction, sunken and blocked heads |
| Status | **Demand unmeasured.** These keywords were blocked by a negative until 2026-08-11 |
| Proof needed | Close-up before/after head photos |

### Brief 6 — Sprinkler Valve Repair

| Field | Value |
| --- | --- |
| URL | `/sprinkler-valve-repair/` |
| Target keywords | `sprinkler valve repair`, `irrigation valve repair`, `sprinkler valve replacement` |
| H1 | `Sprinkler & Irrigation Valve Repair in DFW` |
| Focus | Stuck, leaking and failed valves; solenoid faults; valve-box access |
| Status | Same — the EXACT negative `sprinkler valve replacement cost` was removed on 2026-08-11 |
| Proof needed | Valve box / solenoid repair photos |

---

## 5. Verified service-area pages — the only linkable ones

```
/dfw/service-areas/dallas/          /dfw/service-areas/fort-worth/
/dfw/service-areas/frisco/          /dfw/service-areas/irving/
/dfw/service-areas/arlington/       /dfw/service-areas/plano/
/dfw/service-areas/allen/           /dfw/service-areas/university-park/
/dfw/service-areas/grand-prairie/   /dfw/service-areas/richardson/
/dfw/service-areas/preston-hollow/
```

**Do not fabricate URLs** for Highland Park, Lakewood, Farmers Branch, Balch Springs, Duncanville,
Coppell, Grapevine or Vickery Meadow. Name them as plain text only.

---

## 6. Superseded

**`clients/pro-green-dallas/landing-page-draft/`** — the earlier standalone HTML draft. **Retained
for historical reference. Never deployed. Superseded** by this WordPress-template content workflow,
which targets the client's actual Divi template rather than a generic page.
