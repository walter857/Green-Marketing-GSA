TASK TITLE:

[P0] Softwind Power Washing — Fix duplicate form markup and phone links

TASK DESCRIPTION:

**Problem 1 — the form renders twice with duplicate HTML IDs**

Every offer page renders form#gform_1 twice, producing 22 duplicate HTML IDs per page including
gform_1, gform_wrapper_1, gform_fields_1, gform_submit_button_1, input_1_1, input_1_3,
input_1_4, input_1_7, input_1_9, the field_1_* set, gform_theme_1, and Divi's et-boc. Copy one
renders around 400px, copy two around 5305px. Both are visible and functional.

getElementById returns only the first copy, so any analytics, dynamic-number-insertion or
accessibility tool that binds by ID binds to the wrong element. This is a live
tracking-reliability and accessibility defect.

**Problem 2 — a dead click-to-call link**

Two tel: anchors exist on all seven pages:

- `tel:(631) 502-7946` — correct
- `tel:(631)` — malformed, dials nothing

Selector: a[href="tel:(631)"]. Mobile carries roughly 71% of this account's paid spend.

**Affected URLs**

- https://offer.softwindli.com/driveway-pressure-washing/
- https://offer.softwindli.com/house-pressure-washing-estimate/
- https://offer.softwindli.com/patio-power-washing/
- https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/
- https://offer.softwindli.com/residential-pressure-washing/
- https://offer.softwindli.com/soft-house-washing/
- https://offer.softwindli.com/thank-you/

**Required result**

- Exactly one visible Gravity Form per page
- Exactly one form#gform_1, or each instance carries unique form and field IDs
- Every HTML ID on the page is unique
- The Gravity Forms honeypot (input_9, class gfield--type-honeypot) is preserved, still hidden,
  and still empty — it is the spam guard, do not remove or expose it
- Every tel: href is a complete dialable number: **tel:+16315027946** unless the final
  call-tracking architecture requires an approved dynamic replacement number
- Displayed phone number equals the tel: destination
- No tel:(631), partial, blank or malformed href remains

**Where to look**

The page template or Divi layout emitting the Gravity Forms block twice; a global
header/footer/sidebar module that also injects the form. For the phone: a shared header/footer
or hero component, or a phone shortcode splitting "(631) 502-7946" on the first space.

**Acceptance criteria**

- [ ] One form#gform_1 per page, or all IDs unique
- [ ] Zero duplicate IDs, verified with a document-wide ID audit
- [ ] Honeypot present, display:none, value empty
- [ ] Form still submits successfully and still reaches /thank-you/
- [ ] Zero malformed tel: hrefs on all seven URLs
- [ ] Mobile tap opens the dialer with the full number
- [ ] No desktop or mobile layout regression

**Regression checks:** submit the form on staging and confirm it still reaches /thank-you/;
confirm no other page section shifted.

**Rollback:** restore the previous template or plugin revision.
