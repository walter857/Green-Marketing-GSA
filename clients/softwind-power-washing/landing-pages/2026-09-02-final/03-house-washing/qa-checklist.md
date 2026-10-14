# QA checklist — House Washing

**URL:** https://offer.softwindli.com/house-washing-company/

## Desktop
- [ ] HTTP 200, HTTPS, no redirect
- [ ] Browser title reads `House Washing Long Island | Free Quote`
- [ ] H1 reads `House Washing Across Long Island`
- [ ] Hero copy matches `final-copy.md`
- [ ] Countdown module gone
- [ ] No layout regression

## Mobile
- [ ] Layout renders, no horizontal scroll
- [ ] CTA reachable without pinch-zoom
- [ ] Form usable
- [ ] Page speed not worse than the current build

## Phone
- [ ] Displayed number is (631) 502-7946
- [ ] Every `tel:` href is `tel:+16315027946`
- [ ] No `tel:(631)` or other malformed href remains
- [ ] Mobile tap opens the dialer with the full number

## Form
- [ ] Exactly ONE `form#gform_1` on the page
- [ ] Zero duplicate HTML IDs
- [ ] Honeypot `input_9` present, hidden and empty
- [ ] Submits successfully and reaches `/thank-you/`

## Tracking
- [ ] GA4 `G-D4BZM40RYD` fires
- [ ] GTM `GTM-P3LD97NN` loads ONCE
- [ ] WhatConverts still sets `wc_client` with the GCLID
- [ ] Softwind conversion still fires on a real submission
- [ ] GCLID, GBRAID, WBRAID and all UTMs survive to the form POST

## Keyword-message
- [ ] `house washing` appears naturally in title, H1, hero and body
- [ ] Copy matches the live RSAs `823152917209` and `823152917212`
- [ ] No keyword stuffing

## Review
- [ ] No unverified review published
- [ ] No rating or review count published

## Image
- [ ] No stock image used without explicit approval
- [ ] No AI image used as project proof
- [ ] Every published image is client-owned and rights-cleared

## No placeholder / no false claim
- [ ] No lorem ipsum or TODO text
- [ ] No price, discount, licence, insurance, warranty, guarantee, years in business,
      response-time promise or emergency-service claim
