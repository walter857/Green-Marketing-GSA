TASK TITLE:

[P2] Softwind Power Washing — Identify process.iconnode.com in the lead path

TASK DESCRIPTION:

**Business impact:** an undocumented third party receives a POST on every page load and
again at form submission, on an endpoint named `/google-ads/`. Nothing in the client records
documents an engagement with this vendor.

**Affected URLs:** https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/ · https://offer.softwindli.com/residential-pressure-washing/ · https://offer.softwindli.com/house-washing-company/ · https://offer.softwindli.com/soft-house-washing/ · https://offer.softwindli.com/driveway-pressure-washing/ · https://offer.softwindli.com/patio-power-washing/ · https://offer.softwindli.com/thank-you/

**Current behavior:** `POST https://process.iconnode.com/google-ads/` — once per page load on all
7 URLs, and again at submission. **Zero occurrences in the rendered page source**, so it is
injected at runtime, consistent with a GTM Custom HTML tag.

**Required:** identify the script owner, who added it, the plugin/theme/GTM source, purpose, data
transmitted, destination, retention, current authorization and whether it is still required.

**Do not remove it before ownership is established.** If authorized, we document it. If not,
removal is raised as its own approved change.

**Acceptance criteria:** vendor and owner identified · source named · data flow documented ·
authorization confirmed · keep/scope/remove recommendation.

## QA required

**Desktop:** render, layout, no regression. **Mobile:** layout, no horizontal scroll, CTA
reachable. **Tracking:** attach a network capture showing tags still fire.

## Regression checks

Form still submits and reaches `/thank-you/`; phone link still dials; no other page affected.

## Rollback

Restore the previous template or plugin revision. No data migration involved.

## Developer signoff

Name: ______________  Date: __________  Release/commit: ______________

