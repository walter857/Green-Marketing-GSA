# Call measurement architecture — DNI conflict decision

**2026-09-16 · Apogee Lawns LLC - Live · 8164626278**

Triggered by the owner disclosure that `402-526-5754` is a **WhatConverts tracking
number**, not Apogee's carrier line.

---

## 1. The facts, and what is not a fact

| Fact | Source |
|---|---|
| `402-526-5754` is a WhatConverts tracking number assigned to the permanent-lighting campaign | Owner, 2026-09-16 |
| It forwards to `402-202-7261`, answered by a receptionist | Owner, 2026-09-16 |
| `402-202-7261` is **also the number published sitewide** on apogeelawns.com today | Verified, 5 pages |
| WhatConverts account **119788 "Apogee Lawns LLC"** exists, with one profile **174313** | WhatConverts API, read-only |
| **No WhatConverts script is present anywhere on apogeelawns.com today** | Verified: 5 pages + all 17 enqueued JS files |
| The PPC landing page does not exist (HTTP 404) | Verified |

**Will WhatConverts DNI run on the PPC landing page? UNDETERMINED — and it is not
discoverable.** The page does not exist and no WhatConverts script is deployed anywhere on
the site. This is a **decision the owner and developer have not yet made**, not a fact that
can be observed. The WhatConverts v1 API exposes accounts, profiles and leads, but not
tracking-number or DNI configuration, so it cannot settle it either.

Per the standing instruction, the website-call tag is therefore **held** pending that
decision.

## 2. Why the conflict is real

Google Ads "Calls from website" conversion works by **Google Forwarding Number (GFN)
replacement**: the GTM tag rewrites the displayed number in the DOM with a Google-owned
number, per session, for ad traffic only. WhatConverts DNI does **the same thing** with a
WhatConverts number.

Two swappers on one DOM element produces:

- **A race.** Whichever script executes last wins, and execution order is not deterministic
  across loads, devices or cache states. The loser silently records nothing.
- **Double forwarding.** One system can swap the *other's* number, producing
  GFN → WhatConverts → destination (or the reverse). The call connects, so it looks fine,
  but caller ID and session binding are mangled at both ends.
- **Split, uncomparable reporting.** Neither system sees the whole picture, and the two
  totals will never reconcile.

## 3. Recommendation — WhatConverts owns call measurement; do NOT build the website-call tag

1. **`402-526-5754` is already a WhatConverts number assigned to this campaign.** The
   architecture is WhatConverts-first before we start. Adding GFN on top fights it.
2. **GFN eligibility is doubtful at launch anyway.** A brand-new account with zero lifetime
   delivery is unlikely to qualify for Google forwarding numbers on day one.
3. **One measurement owner, one number, one source of truth.** WhatConverts can push call
   conversions into Google Ads through its own integration when ready.
4. **It avoids the double-count trap.** A native Google tag plus a WhatConverts upload for
   the same interaction double-counts one lead.

**Effect on Stage A:** none. `Call | Permanent Lights | Website | 60s` is still created as
a Secondary conversion action — creating the action reserves the name and issues the
identifiers. What is held is the **GTM tag that would feed it**. It simply stays Secondary
and unfed until the architecture is settled and tested.

## 4. The bigger risk nobody has raised yet: a fixed number cannot carry a click ID

The owner described `402-526-5754` as **"assigned to: Apogee Lawns permanent-lighting
campaign"**. That is a **fixed-assignment** pattern, not a DNI pool — and it is a known,
measured failure mode on another Green Marketing account:

> A fixed-source tracking number stamps **every** call with that source and never binds to
> the visitor session. On Ambient Cooling this produced **0.6% of calls carrying a GCLID
> versus 75% of forms.**

Applied here, a single static `402-526-5754` on the PPC page means:

- Every call to it is stamped "permanent-lighting campaign" **whether the caller came from
  paid search, organic, the GBP listing, or a yard sign.**
- **No GCLID binding**, so Google Ads cannot attribute any call to a keyword, ad or click.
- CPQL for calls becomes an upper bound, never a measured figure.

**If click-level call attribution matters, the PPC page needs a WhatConverts DNI *pool*,
not one static number.** If a static number is acceptable, then say so explicitly and we
report website calls at campaign level only — but that must be a deliberate choice, not a
discovery made in November.

## 5. Calls-from-ads is unaffected, and is the reliable one

`Call | Permanent Lights | Ads | 60s` (`AD_CALL`) does **not** touch the page DOM. Google
substitutes its forwarding number inside the ad itself and carries full click attribution.
No GTM tag. No conflict with WhatConverts. **This is the call conversion to trust at
launch.**

### One caveat on the call asset

The owner authorised the call asset to use `402-526-5754`, subject to routing verification.
Note the resulting chain:

```
searcher -> Google forwarding number -> 402-526-5754 (WhatConverts) -> 402-202-7261 (Apogee)
```

That is **two forwarding hops**. It will connect, but WhatConverts will see the call
arriving from Google's forwarding number rather than the real caller, which can degrade
WhatConverts' own caller ID and attribution.

**Cleaner alternative to consider:** point the Google call asset directly at
`402-202-7261` and let Google's own forwarding handle ads-call attribution, keeping
WhatConverts out of the ads-call path entirely. Recorded as a recommendation only — the
owner's instruction to use `402-526-5754` stands unless they change it.

## 6. Routing verification still required before the call asset is created

A live test call to `402-526-5754`, inside live-answer hours, confirming it rings
`402-202-7261` and a receptionist answers. Claude cannot place a phone call. **Owner action.**

## 7. Decision required

| # | Question | Blocks |
|---|---|---|
| 1 | Will WhatConverts DNI run on the PPC landing page — yes or no? | website-call GTM tag |
| 2 | If yes: DNI **pool** (click-level attribution) or single **static** number (campaign-level only)? | call attribution quality |
| 3 | Confirm WhatConverts as sole call-measurement owner, so the Google website-call tag is not built? | GTM workspace scope |
| 4 | Call asset target: keep `402-526-5754` (two hops) or point at `402-202-7261` (one hop)? | call asset creation |
| 5 | Routing test result for `402-526-5754` | call asset creation |
