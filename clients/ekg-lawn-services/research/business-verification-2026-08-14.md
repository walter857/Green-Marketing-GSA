# EKG Lawn Services — business-fact verification status

Date: 2026-08-14 · Read-only.

## Blocker: no outbound HTTP from this environment

First-party verification against the official website and Google Business Profile **could
not be performed**. Direct outbound HTTPS is refused in this sandbox:

```
WebFetch  https://ekglawn.com/          -> connect ECONNREFUSED 127.0.0.1:443
urllib    https://ekglawn.com/          -> WinError 10061, connection actively refused
```

Web *search* works, but a search-engine snippet is **not** a first-party source and is not
acceptable evidence under §7. Third-party directory listings are likewise not acceptable:
they routinely carry stale phone numbers, call-tracking pool numbers, and outdated hours.

**Nothing below has been promoted into `client.yaml`, the campaign blueprint, the RSAs, or
any landing-page draft.** No business fact has been invented or inferred.

## Verified — from the live Google Ads account only

The account is an authoritative source under §7 item 3. These are the only business facts
currently verified:

| Fact | Value | Evidence |
|---|---|---|
| Main website | `https://ekglawn.com/` | appears in serving ad final URLs |
| Landing-page subdomain | `https://offer.ekglawn.com/` | serving ad final URLs |
| Existing aeration page | `https://offer.ekglawn.com/aeration/` | serving ad final URL |
| Other live offer pages | `/landscaping-brandermill/`, `/landscaping-hallsboro/`, `/lawn-care-brandermill/`, `/lawn-maintenance-brandermill/` | serving ad final URLs |
| Aeration is an advertised service | yes | historical campaign `Leads-Search-Aeration`, ad group evidence, 627 aeration impressions |

Note the account carries **no** verified phone number, offer, guarantee, or review text.

## Unresolved — required before Checkpoint C can be finalised

Each of these must come from the official website or the correct Google Business Profile.

| Fact | Status | Blocks |
|---|---|---|
| Public business name | UNRESOLVED | Drive client folder name, landing-page H1, ad copy |
| Phone number | UNRESOLVED | call asset, click-to-call, landing-page CTA |
| Public service-area wording | UNRESOLVED | landing-page service-area section, ad copy |
| Business hours | UNRESOLVED | landing-page copy |
| Call-answering hours | UNRESOLVED | **ad schedule** — currently an all-hours placeholder |
| Aeration availability | PARTIAL — advertised historically, not confirmed current | ad group 1 |
| Aeration + overseeding bundle availability | UNRESOLVED | **ad group 2 depends entirely on this** |
| Seasonal timing | UNRESOLVED | launch date, ad copy |
| Lawn/grass types served | UNRESOLVED | landing-page copy, FAQs |
| Offers or promotions | UNRESOLVED | promotion asset, landing-page offer block |
| Guarantees or warranties | UNRESOLVED | landing-page trust section |
| Years in business | UNRESOLVED | landing-page trust section |
| Licences or certifications | UNRESOLVED | landing-page trust section |
| Differentiators | UNRESOLVED | RSA-B copy, landing-page copy |
| Approved images | UNRESOLVED | every landing-page image slot |
| Privacy Policy URL | UNRESOLVED | landing-page footer, form compliance |
| Terms URL | UNRESOLVED | landing-page footer |
| Service-relevant GBP reviews | UNRESOLVED | landing-page review section |

## How the drafts were written around this

Because these are unresolved, the Checkpoint C drafts deliberately contain:

- **No phone number** in any headline, description, or asset.
- **No city or neighbourhood name** in any ad copy. The approved coordinates authorise
  Google Ads targeting only, never public-facing place wording.
- **No offer, discount, price, or promotion.**
- **No guarantee, warranty, licence, rating, review count, or years-in-business claim.**
- **No response-time promise.**
- **No promotion asset and no call asset**, since both would need verified inputs.
- An **all-hours ad schedule placeholder**, flagged for narrowing once call-answering hours
  are known.

Every RSA line is service-and-intent copy that stands on the service itself. That keeps the
drafts honest, but it also means the ads are weaker than they should be — trust proof is
exactly what RSA-B is for, and it currently has none.

## Reviews

**Zero verified reviews.** No review has been written, paraphrased, or sourced. Per the
workflow, the landing-page review slots will carry `REAL REVIEW REQUIRED - DO NOT PUBLISH`
and deployment readiness fails until real, traceable GBP reviews are supplied — preferably
ones that discuss aeration, overseeding, seeding, or the resulting lawn improvement.

## To unblock

Either:

1. Run the research from an environment with outbound network access, or
2. Supply the facts directly, or
3. Approve fetching from a specific allow-listed URL set if the sandbox policy can permit it.

Once supplied, `client.yaml` is updated, the ad schedule is narrowed, RSA-B gains real trust
proof, the landing-page drafts are completed, and the plan is re-fingerprinted.
