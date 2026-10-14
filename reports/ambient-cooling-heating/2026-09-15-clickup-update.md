# Ambient Cooling — 2026-09-15 activity update

**Account:** Ambient Cooling - Live | 2401959466 | Commercial HVAC Installation
**Mode:** read-only analysis, browser QA, plan drafting. **Zero external writes.**

## Done

- Identity gate **PASS** (10/10). Both work orders validate. Created a dedicated
  Commercial HVAC Installation work order; added the service to `client.offer.services_in_scope`
  (recording the owner's written 2026-09-10 confirmation).
- Full before-state snapshot of the five campaigns. Every anchor matches: budgets $421.55/day
  → **$12,815.12/month**, headroom **$184.88**; ceilings $25/$25/$30/$30/$25; schedule 6 rows;
  75 geo targets, PRESENCE; Search Partners, Display, AI Max, DSA, URL expansion all off.
- **17/17 commercial negatives verified.** `AMB-0910-COMM-NEG-3 / 51CF5986F18A` =
  ALREADY_EXECUTED. Zero negative changes made or proposed.
- Real-browser QA (desktop + mobile) of the new commercial page and all five existing pages.
- Two fingerprinted create-paused plans built and validated. `validate_only` = **VALIDATED_OK**.

## Three things the client needs to know

**1. The commercial ad group was switched ON by hand this morning.**
2026-09-15 08:42:16, `access@greenmarketingfl.com`, Google Ads web UI, PAUSED → ENABLED.
It has 0 ads so it cannot serve and has never had an impression — no harm done. But it means any
ad created ENABLED would serve instantly with no approval gate. Both planned RSAs are created
PAUSED for exactly this reason.

**2. Form attribution is broken across all six landing pages — and this is the big one.**
The attribution fields are written into the page server-side, then the page is cached by the
host's proxy. The cached copy carries *one visitor's* click ID and serves it to everyone else.
**0 of 24 test loads captured the visitor's own GCLID.** Real form leads are being credited to the
wrong click, wrong campaign and wrong keyword — or to nothing. This is the root cause of the
account's long-running measurement problems, and it means current conversion data cannot be
trusted for optimisation. Needs a web-dev fix: purge the cache, then populate those fields with
client-side JavaScript instead.

**3. The new commercial page has four launch blockers.**
- Developer instruction text published as live body copy: *"Use them for the page layout without
  presenting them as completed Ambient projects."*
- The gallery section it sits under contains **zero images**.
- An **"Offer Ends in 15 DAY 10 HRS…" countdown for an offer that does not exist** — no discount,
  no price, no promotion anywhere on the page. Unverified promotional claim and a Google Ads
  policy risk.
- The form renders three times per page with duplicate IDs (duplicate-conversion risk).

Everything else on the page passes: HTTP 200, correct H1, 100% commercial content, zero banned
claims, Privacy + Terms present (a defect open since August, now closed), correct paid phone
number displayed, no forwarding-number leak, mobile sticky call bar correct.

## Why the account went quiet — answered

Spend fell **96%** at **2026-09-04 16:56**, when the CPC ceilings were set in the UI.
Sept 5–14 ran at **$21.60/day against $421.55/day available — 5.1% of budget.**
Lost impression share to **rank** doubled to 75–86%. Lost impression share to **budget** went to
**0.00%**. Budget is not the constraint.

**The decisive number:** every click that has ever converted in this account cost between $6.16 and
$153.06 — and **12 of those 13 clicks cost more than every ceiling now in place.** The caps did not
trim waste; they removed the exact price band where this account converts, and left the cheap
non-converting traffic behind.

Also found: 10 conversion actions are set as Primary, so one phone call can be counted up to four
times. "All conversions" reads 81 where real Primary records are 14. **Zero Primary conversions in
the last 14 settled days.**

## Awaiting approval

```
APPROVE AMB-0915-COMM-RSA-1 6C32B210CF5B 2 operations FOR 2401959466
APPROVE AMB-0915-COMM-ASSET-1 02F6EECCCDF8 7 operations FOR 2401959466
```

**Recommendation: approve the RSA plan now, ahead of the web fixes.** The ads are created PAUSED
and cannot serve, so there is no delivery risk, and it starts Google's policy review in parallel
with the developer work rather than after it. Enablement remains gated on policy APPROVED **and**
the four page blockers being closed.

## Needs a business decision

The CPC-ceiling test size on HVAC Repair. The safe +20% step ($25 → $30) almost certainly will not
work — the clearing price is ~$106. A test at **$25 → $65 with a $250 no-lead stop-loss** has a real
chance. That is a risk call for the owner, so it is not drafted.

## Next

1. Owner approval on the RSA plan → create paused → readback → await Google policy.
2. Web dev: cache purge + client-side attribution capture; remove the countdown, the developer
   note and the empty gallery; de-duplicate the form.
3. Separate enablement plan and approval once both clear.
4. Residential routing negative only after the commercial route proves it can serve.
