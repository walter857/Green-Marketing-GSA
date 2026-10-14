# Ambient — 31-service heating expansion: URL map, screening, and budget feasibility

**Account:** `Ambient Cooling - Live` / `2401959466` · **Read-only.** Nothing built, nothing changed.
**Crawl:** 200 URLs rendered from `ambientcoolingandheating.com`, 39 under `/services/`
**Evidence:** `clients/ambient-cooling-heating/snapshots/site-crawl-2026-09-18.json`

---

## 1. The headline problem: there is $1.94/day of room

| | |
|---|---|
| Permanent cap | **$328.94/day** ($10,000 ÷ 30.4) |
| Existing enabled (5 campaigns) | $237.00/day |
| Heating campaigns already built, paused | $90.00/day |
| **Committed total** | **$327.00/day** |
| **Headroom** | **$1.94/day** |

31 separate campaigns cannot be funded. Even at a bare $25/day each — below this account's
observed cost of a *single click* — that is **$775/day = $23,560/month**, 2.4× the cap.

This is not a theoretical limit. **Gas Boiler Repair ran all season at $5.00/day and spent
$0.00** — it never bought a single click, because the budget was under one click's price.
Observed CPCs here: AC Repair $106.27, HVAC Repair $72.40, HVAC Installation $24–36, and the
new heating ceilings are $38 and $24. Splitting the cap 31 ways would reproduce that failure
31 times: lots of campaigns, almost no traffic.

---

## 2. SKAG is an ad-group discipline, not a campaign count

This is the key point. Single Keyword Ad Groups means **one canonical keyword theme per ad
group**, with Phrase + Exact variants and ads written to that theme. It does not require one
campaign per keyword.

Campaign-level budget is the only budget lever Google gives us. **31 campaigns = 31 budgets to
starve.** A small number of campaigns, each holding many SKAG ad groups, gives identical
keyword/ad/landing-page precision *and* lets budget follow demand.

---

## 3. Landing pages that actually exist

Only **five** heating-relevant pages are both service-specific and policy-clean. The
short-path URLs (`/services/furnaces/`, `/services/boilers/`, `/services/heat-pumps/`,
`/services/hvac-repair/`, `/services/oil-replacement/`, `/services/geothermal/`) all render the
**generic site H1** — "HVAC, AIR CONDITIONER REPAIR & HEATING SERVICES" — they are shells, not
landing pages, and must not be used as ad destinations.

| Page | H1 | Content actually covers |
|---|---|---|
| `/services/heating-services/` | Heating Services in Severn… | maintenance, tune-up, replacement, install, inspection, thermostat, emergency |
| `/services/heating-services/furnace-repair/` | Furnace Repair in Severn… | repair, **maintenance**, **replacement** (both named in H2s) |
| `/services/heating-services/boiler-repair/` | Boiler Repair in Severn… | repair **only** |
| `/services/heating-services/oil-furnace-installations/` | …Oil Furnace Installations… | oil furnace installation only |
| `/services/cooling-services/mini-splits/` | Mini Splits in Severn… | installation, maintenance (cooling-framed) |
| `/services/heating-services/heat-pumps/` | Heat Pumps in Severn… | 🔴 **destination policy REJECTED** |
| `/services/hvac/geothermal-hvac/` | Geothermal HVAC in Severn… | service excluded on economics |

---

## 4. All 31 services screened

**19 advertisable · 12 blocked**

| # | Service | Destination | Verdict |
|---|---|---|---|
| 1 | Furnace repair | furnace-repair | ✅ |
| 2 | Furnace replacement | furnace-repair | ✅ H2 names replacement |
| 3 | Furnace installation | oil-furnace-installations | ⚠️ oil only — no general furnace-install page |
| 4 | Furnace maintenance | furnace-repair | ✅ H2 names maintenance |
| 5 | Furnace tune-up | heating-services hub | ⚠️ "tune-up" on hub, not the furnace page |
| 6 | Heat pump repair | — | 🔴 DESTINATION_NOT_WORKING |
| 7 | Heat pump replacement | — | 🔴 DESTINATION_NOT_WORKING |
| 8 | Heat pump installation | — | 🔴 DESTINATION_NOT_WORKING |
| 9 | Heat pump maintenance | — | 🔴 DESTINATION_NOT_WORKING |
| 10 | Boiler repair | boiler-repair | ✅ |
| 11 | Boiler replacement | — | 🔴 no page; boiler page is repair-only |
| 12 | Boiler installation | — | 🔴 no page |
| 13 | Boiler maintenance | — | 🔴 no page |
| 14 | Heating repair | hub | ✅ |
| 15 | Heating replacement | hub | ✅ |
| 16 | Heating installation | hub | ✅ |
| 17 | Heating maintenance | hub | ✅ |
| 18 | Heating tune-up | hub | ✅ |
| 19 | Emergency heating repair | hub | ⚠️ see §5 |
| 20 | No heat repair | hub | ✅ |
| 21 | Thermostat repair | — | 🔴 capability not verified |
| 22 | Thermostat replacement | — | 🔴 capability not verified |
| 23 | Smart thermostat installation | — | 🔴 capability not verified |
| 24 | Ductless heating repair | mini-splits | ⚠️ page is cooling-framed, no repair content |
| 25 | Ductless heating installation | mini-splits | ✅ |
| 26 | Gas furnace repair | furnace-repair | ✅ |
| 27 | Electric furnace repair | — | 🔴 capability not verified |
| 28 | Heating system inspection | hub | ✅ hub names inspection |
| 29 | Heating system replacement | hub | ✅ |
| 30 | Heating system installation | hub | ✅ |
| 31 | Geothermal heat pump | — | 🔴 excluded: $286.60 spend, 0 conversions |

### The 12 blocked, and what unblocks each

- **Heat pump ×4** — `/services/heating-services/heat-pumps/` is rejected by Google with
  `DESTINATION_NOT_WORKING`, re-verified 2026-09-18. It is the **only** one of seven heating
  URLs that fails, so this is page-specific, not bot protection. Added to the developer task.
  **I will not point heat-pump ads at a different URL to bypass this** — you ruled that out and
  it would send heat-pump searchers to a page about something else.
- **Thermostat ×3 + electric furnace** — `client.yaml → services_capability_not_verified`.
  One sentence from the client confirming they perform these unblocks all four.
- **Boiler replacement / installation / maintenance** — the boiler page covers repair only.
  Needs page content, or fold into the hub.
- **Geothermal heat pump** — `services_excluded`: $286.60 across two campaigns, zero
  conversions. Advertising it again repeats a settled loss. Reversible if you want it back.

---

## 5. "Emergency heating repair" — bid yes, claim no

`same_day_or_emergency_availability` is a **barred claim** in `client.yaml`. We can bid on
emergency terms (agency policy explicitly forbids blanket-negativing "emergency"), but the ad
copy and landing page cannot promise emergency or same-day response. That is a real
expectation gap: someone searching "emergency heating repair" at 11pm wants a promise we are
not allowed to make, and the landing page does not make it either.

**Recommendation:** hold this one until the client confirms actual after-hours availability. If
confirmed, it is a strong BOFU theme and the bar can be lifted with evidence.

---

## 6. Recommended architecture — 5 campaigns, 19 SKAG ad groups

One campaign per distinct landing page, so budget follows intent and every ad group still has
its own canonical keyword theme, its own RSAs, and its own matching destination.

| Campaign | Landing page | SKAG ad groups |
|---|---|---|
| **C1 Furnace** | furnace-repair | furnace repair · gas furnace repair · furnace maintenance · furnace replacement *(4)* |
| **C2 Heating System** | heating-services hub | heating repair · heating replacement · heating installation · heating maintenance · heating tune-up · furnace tune-up · no heat repair · heating system inspection · heating system replacement · heating system installation *(10)* |
| **C3 Boiler** | boiler-repair | boiler repair *(1)* |
| **C4 Ductless** | mini-splits | ductless heating installation · mini split installation *(2)* |
| **C5 Oil Furnace** | oil-furnace-installations | oil furnace installation *(1)* |

Two of these already exist, built and approved: the current Heating Repair campaign is C1 and
Heating Installation is C4. The expansion is **+3 campaigns and ~+15 ad groups**, not a rebuild.

### What it costs to actually deliver

At ~$35/day per heating campaign — roughly one click per day at the $24–38 ceilings:

| Scenario | Existing 5 | Heating | Total/day | Total/month | vs $10,000 cap |
|---|---|---:|---:|---:|---|
| Today (as built) | $237 | $90 (2 campaigns) | $327 | $9,940 | ✅ fits |
| 5 heating campaigns | $237 | $175 | $412 | $12,525 | ❌ over by $2,525 |
| 5 heating campaigns, existing trimmed to $150 | $150 | $175 | $325 | $9,880 | ✅ fits |
| All 19 as separate campaigns | $237 | $665 | $902 | $27,421 | ❌ over by $17,421 |

---

## 7. The decision I need from you

**Recommended: option B.** It launches every advertisable service this season, inside the
existing cap, with no new money.

- **A — Stay at $10,000 and keep today's split.** Launch the 2 built campaigns now; add C2/C3/C5
  only as budget frees up. Safest, slowest.
- **B — Stay at $10,000, rebalance.** Trim the five cooling-season campaigns from $237 to ~$150
  (AC Repair is the obvious donor: worst CPA in the account, $106 CPC, and demand falling into
  winter) and fund all five heating campaigns at ~$175/day. **All 19 services live, cap intact.**
- **C — Raise the cap to ~$12,500/month.** Keep cooling budgets intact and fund heating fully.
  The only option that needs new money.

Whichever you pick, I will build it as **create-paused with a fresh fingerprint**, and the
existing enablement gates still apply — nothing goes live until the website fixes ship and the
post-deployment test passes.

---

## 8. Not claimed

No CPL, CPQL, lead-volume, Quality Score or revenue improvement is projected here. The budget
table is a *delivery capacity* estimate from observed CPCs, not a performance forecast. Actual
combined settled delivery across the five enabled campaigns is currently ~$96.76/day, well
below even today's budgets — so budget is a ceiling, not a spend prediction.
