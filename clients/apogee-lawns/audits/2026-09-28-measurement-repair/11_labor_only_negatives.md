# 11 — The three labor-only / customer-supplied negatives

- **Live read:** 2026-09-28 ≈21:35 CDT (`reports/apogee-lawns/evidence/2026-09-28d-reads.json`). All three are ENABLED
  campaign negatives on 24257151015, and there are 75 negatives in total.
- **Owner answer:** Apogee installs customer-supplied lights (owner-provided; not on the website).
- **Planner:** no data for any of 10 labor-only or own-lights phrasings in the approved area.
- **Probes:** hypothetical strings, no volume; tested with the documented negative-match model in `scripts/apg_negmatch.py`.
- **Nothing was applied.**

| Text | Match | Resource (scope) | Currently excludes | Permanent-installation inquiry it could block (hypothetical) | Verdict | Evidence |
|---|---|---|---|---|---|---|
| `labor only` | PHRASE | `…/campaignCriteria/24257151015~296448593009` (campaign) | any search containing "labor only", e.g. installation labor for lights the customer already has, and labor-only job ads | "permanent christmas light installation labor only" | **REMOVE-CANDIDATE** | The owner confirms that service. Job-seeker variants stay blocked by BROAD `jobs`/`career`/`careers`/`salary` (probe: "…labor only jobs" is still blocked by `jobs`) |
| `my own lights` | PHRASE | `…/campaignCriteria/24257151015~2225874598953` (campaign) | any search containing "my own lights" | "permanent christmas light installation with my own lights" | **REMOVE-CANDIDATE** | Same owner answer. DIY variants stay blocked by `how to`, `diy`, `do it yourself`, `tutorial(s)`, `instructions` (probes: "how to … my own lights" is still blocked by `how to`; "… my own lights diy" by `diy`) |
| `customer supplied` | PHRASE | `…/campaignCriteria/24257151015~573042878059` (campaign) | any search containing "customer supplied" | "permanent christmas light installation customer supplied" | **KEEP** | Contractor or trade jargon; nothing shows homeowners search this way. It no longer describes a service limit, so removing it would be harmless, but no buyer evidence justifies a change |

**Local delta drafted:** `clients/apogee-lawns/plans/APG-0928-NEG-LO.yaml`.
- Contents: **2 removes** (ordinals 1–2 above), 0 creates, 0 other changes; `customer supplied` kept.
- Both resource names, texts, match types and ENABLED status were verified against the live read.
- Fingerprint **`58362D536336`**. **Priority: low** (no measurable volume); approval is optional.
- No ad or landing-page wording about customer-supplied lights is added, and no product compatibility is claimed.
- No narrower compatibility question is needed: the keyword decision does not depend on which products Apogee will
  install.
