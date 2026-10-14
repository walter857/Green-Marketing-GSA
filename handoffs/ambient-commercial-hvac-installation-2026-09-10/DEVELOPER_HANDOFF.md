# Developer handoff — Commercial HVAC Installation landing page

**Client:** Ambient Cooling & Heating · Google Ads account `Ambient Cooling - Live` (2401959466)
**Target URL:** `https://offer.ambientcoolingandheating.com/commercial-hvac-installation/`
**Current status:** returns **HTTP 404**. This page does not exist and must be built.
**Prepared:** 2026-09-10 · Green Marketing

> The Google Ads ad group, keywords and ads are already built or drafted and are **paused**.
> They cannot serve until this page returns HTTP 200 and passes the acceptance tests in §7.

---

## 1. Do not publish until these are confirmed

Source access, staging environment, a restorable backup, and deploy authority. If any is
missing, build on staging and stop. Do not publish.

---

## 2. Phone numbers — this is the part most likely to go wrong

The number architecture was measured directly in WhatConverts on 2026-09-10 across 272 lead
records. Roles are **not** interchangeable.

| Number | Role | Use on this page? |
|---|---|---|
| **(410) 705-6354** | WhatConverts **tracking number** assigned to `google` paid traffic | **YES — this is the only number that goes on the page** |
| (410) 761-0932 | **DESTINATION** — Ambient's real line that every tracking number rings to (233 of 272 leads) | **NO. Never render it, and never put it in the HTML source** |
| (410) 914-1456 | WhatConverts **tracking number**, but a mixed/general-purpose one: `google` 4, `GBP` 4, `(direct)` 3, site referral 1 | **NO. Remove it from this page and do not add it** |

**About (410) 914-1456.** It is a real, intentionally configured tracking number in the
WhatConverts profile *Ambient Cooling & Heating* (profile 105803), and it routes correctly to
(410) 761-0932. It is **not** rogue. It is simply **not a paid-source number** — it collects
GBP, direct and organic calls as well. Hard-coding it on a paid landing page pollutes paid
call attribution. It currently appears as `tel:+14109141456` labelled "Call Now" on all five
existing paid pages; that is a defect to fix there, and a defect not to reproduce here.

**Configuration of record (corrected 2026-09-10):**

| Field | Value |
|---|---|
| WhatConverts profile | Ambient Cooling & Heating |
| Profile ID | 105803 |
| Paid tracking number | 410-705-6354 |
| Tracking-number name | **GSA Cooling Traffic** |
| Google Ads call asset | 407995613637 |

*GSA Cooling Traffic is the name of the tracking number, not a profile.* An earlier note in
this handoff described it as a missing profile name; that was wrong and is corrected here.
**All current routing is preserved. No WhatConverts configuration has been altered.**

**Known attribution defect on this number.** The WhatConverts UI shows `Source = Offline` for
410-705-6354. Measured across 371 lead records: 0 of 13 calls on this number carry a GCLID, and
across the whole profile only 0.6% of calls carry one versus 75% of web forms. Eight leads are
labelled `google / cpc` with no landing URL and no click ID at all. See
`clients/ambient-cooling-heating/plans/WC-0910-OFFLINE-SOURCE-1.md`. **Build this page so it
captures and persists the click ID regardless** — DNI alone will not fix call attribution if
the page drops the parameters.

**Requirements:**

- Render **(410) 705-6354** as the static number, with a correct `tel:` link
  (`tel:+14107056354`).
- Let WhatConverts DNI swap it. Do not defeat the swap with a hard-coded override.
- (410) 761-0932 must be absent from rendered text **and** from the HTML source, so it cannot
  flash before the swap runs.
- Do not add (410) 914-1456 anywhere.
- Verify with the `wc_swap` / `wc_client` / `wc_visitor` cookies, not by looking for a
  `whatconverts.com` network request — the script is served from a CDN host.

---

## 3. Copy

Use `source/COMMERCIAL_HVAC_COPY_PASTE.txt` and
`source/Ambient_Commercial_HVAC_Installation_Launch_Pack.docx` **verbatim**.

| Element | Value |
|---|---|
| SEO title | Commercial HVAC Installation \| Ambient Cooling & Heating |
| Meta description | Request commercial HVAC installation or replacement for your Central Maryland property from Ambient Cooling & Heating. |
| H1 | Commercial HVAC Installation in Central Maryland |
| Primary CTA | Request a Free Commercial HVAC Quote |
| Secondary CTA | Call (410) 705-6354 |
| Canonical | `https://offer.ambientcoolingandheating.com/commercial-hvac-installation/` |

Section order: Hero → *Commercial HVAC Planned Around Your Property* → *Commercial HVAC
Systems We Install* (H3s: Rooftop and Packaged Units · Commercial Air Conditioning ·
Commercial Heat Pumps · Ventilation, Ductwork, and Controls) → *Your Commercial HVAC
Installation in 3 Steps* → *Why Businesses Choose Ambient* → *Request Your Commercial HVAC
Consultation*.

### Claims that must not appear

**Licensed & Insured** (withdrawn from this workstream), emergency, 24/7, same-day,
financing, rebates, discounts, warranty, guarantees, guaranteed savings, #1, star ratings,
review counts, certifications.

---

## 4. Images

Four files in `images/`. All are **illustrative generated imagery**.

- `ambient-commercial-rooftop-hvac-installation-1200x628.jpg`
- `ambient-commercial-ground-unit-installation-1200x628.jpg`
- `ambient-commercial-mechanical-room-1200x1200.jpg`
- `ambient-commercial-rtu-ductwork-1200x1200.jpg`

**Never caption, tag, alt-text or otherwise present these as completed Ambient projects, job
sites, or customer installations.** Alt text must describe the equipment generically
("rooftop HVAC unit on a commercial building"), never "our work" or a location. Replace with
verified Ambient-owned project photography when available. SHA-256 hashes are in
`MANIFEST.json`.

---

## 5. Form

Required: Company Name · Contact Name · Phone · Email · Property Address
Optional/qualifying: Property Type · New Installation or Replacement · Current System Type ·
Preferred Project Timeline · Project Details

### Unique DOM IDs — mandatory

The five existing paid landing pages each render **three copies of the same Gravity Form with
identical IDs** — `gform_1` ×3, plus `gform_wrapper_1`, `gform_fields_1`,
`gform_submit_button_1` and 30+ `field_1_*` / `input_1_*` IDs, all tripled. That breaks
label/input association, accessibility, validation and conversion attribution.

**Do not reproduce this.** Either render one form instance, or give every instance a unique
suffix. Verify with `document.querySelectorAll('[id]')` that no ID repeats.

Also required: valid `<label for>` on every field, keyboard access, visible focus states, and
clear inline error messages.

> Some Gravity Forms installs use a honeypot field labelled "Comments". Do not populate or
> reorder fields blindly — verify the field map against the live form before wiring anything.

---

## 6. Tracking

| Requirement | Detail |
|---|---|
| GTM container | `GTM-PQTPQ436` |
| WhatConverts | Preserve the existing script and DNI behaviour |
| Click-ID capture | **GCLID, GBRAID, WBRAID** and all UTM parameters must be captured into hidden form fields **and** persisted (cookie or storage) so a later submission still carries them |
| Lead ID | Capture and pass a unique lead ID for deduplication |
| Conversion | **Exactly one** Google Ads conversion per successful submission |
| Thank-you | Dedicated thank-you route; the conversion must not re-fire on refresh or back-navigation |

**This is a known live defect worth fixing here.** None of the five existing paid landing
pages populates a GCLID or UTM hidden field. Form leads still get attributed because
WhatConverts attaches the click ID from its own visitor session — but **phone calls do not get
that treatment.** Measured 2026-09-10: WhatConverts labels 21 leads `cpc` while only 8 carry a
click identifier, and the 8 unidentified `google/cpc` leads are **all phone calls or texts**,
every one on a day the campaigns took paid clicks. Until call click-ID capture works, cost per
qualified lead cannot be measured accurately. Build this page with capture working from day one.

---

## 7. Acceptance tests — all must pass before the ad group can be enabled

1. **HTTP 200** at the exact URL, desktop and mobile, real browser, JS enabled.
2. Copy matches the pack. H1, title, meta description, canonical correct.
3. **(410) 705-6354** rendered and dialable; **(410) 761-0932 absent from text and source**;
   **(410) 914-1456 absent entirely**.
4. DNI verified under paid-click parameters
   (`?gclid=…&utm_source=google&utm_medium=cpc&campaignid=24132507747`) — correct number, no
   flash of any other number.
5. **No duplicate DOM IDs.**
6. **Privacy and Terms links present.** *(None of the five existing paid pages has either. The
   offer subdomain does have a Privacy Policy page — it appears in the 404 page navigation — so
   this is a linking gap, not a missing document.)*
7. GCLID / GBRAID / WBRAID / UTM captured into the form and persisted.
8. **Every distinct visible form submitted once through an approved non-production/test path**,
   producing exactly one lead and **exactly one** Google Ads conversion. Verify the count in
   Google Ads, not only in the tag debugger.
9. Mobile layout verified at 390px width; no horizontal scroll; tap targets adequate.
10. Claim check: none of the barred claims in §3 appears anywhere on the page.
11. **No Local Services Ads references anywhere** — no LSA badge, "Google Guaranteed" mark,
    LSA phone number, or LSA-sourced review widget. LSA is run by a different department on a
    different budget and must not appear on this page.
12. Page content is **commercial HVAC installation and replacement messaging only** — no
    residential-only offers, and no repair-only or maintenance-plan messaging that would pull
    the page off the commercial installation intent the ad group targets.

> **An approved test path does not exist yet.** Testing on production would create a real
> customer lead and fire a real Google Ads conversion, contaminating the conversion data the
> bidding decisions depend on. Provide a staging clone or an approved test path before step 8.

---

## 8. What is already built in Google Ads

| Resource | ID | Status |
|---|---|---|
| Campaign | 24132507747 — `Search \| NonBrand \| HVAC Installation \| Central MD \| BOFU \| 2026-08` | ENABLED (pre-existing) |
| **Ad group** | **199748801029 — `SKAG \| Commercial HVAC Installation`** | **PAUSED, created 2026-09-10** |
| Keyword | `"commercial hvac installation"` PHRASE | ENABLED (inside the paused ad group) |
| Keyword | `[commercial hvac installation]` EXACT | ENABLED (inside the paused ad group) |
| Ads | none yet | drafted, gated on this page |

Inherits from the campaign: 75 Maryland Presence-only targets, the approved schedule,
conversion configuration, the account ClickCease tracking template, the call asset
(410) 705-6354, and the $30.00 Maximize Clicks ceiling.

Paths for both ads: `commercial-hvac` / `installation`.
Final URL for both ads: `https://offer.ambientcoolingandheating.com/commercial-hvac-installation/`

---

## 9. Sequence after the page is live

1. Re-run desktop and mobile browser QA against the published URL.
2. Complete acceptance test 8 through the approved test path.
3. Revalidate the RSA package against the final URL and current account state; re-fingerprint
   if anything drifted.
4. Approve and execute the RSAs **create-paused**; read them back.
5. Approve and execute the commercial ad-group negatives.
6. Separate approval to **enable** the ad group.
7. Only after the commercial ad group is enabled and eligible, add BROAD `commercial` as an
   **ad-group** negative on the residential SKAG 202339087634. Never at campaign or account
   level. Applied earlier it suppresses commercial demand instead of redirecting it.
8. Check at 24 and 72 hours for configuration and serving faults. Judge performance only after
   14 settled days, excluding conversion-lag days.

**Success is not a lower CPC or a higher CTR.** It is more unique qualified commercial
installation leads at or below the **$280** CPQL guardrail, without breaching the **$13,000**
Search-only monthly maximum.
