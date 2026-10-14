TASK TITLE:

[P2] Softwind Power Washing — Vendor, security and cleanup investigations

TASK DESCRIPTION:

**These are P2. They must not block the launch build.**

---

**5a. Identify process.iconnode.com in the lead path**

An undocumented third party receives `POST https://process.iconnode.com/google-ads/` on every
page load of all seven pages, and again at form submission. It has zero occurrences in the
rendered page source, so it is injected at runtime — consistent with a GTM Custom HTML tag.
Nothing in Green Marketing's records documents an engagement with this vendor.

Please identify: script owner, who added it, plugin/theme/GTM source, purpose, what data is
transmitted, destination, retention, current authorization, and whether it is still required.

**Do not remove it before ownership is established.**

---

**5b. SG-Captcha behaviour**

SiteGround SG-Captcha was observed intercepting a paid landing page once (HTTP 202, request
chain through /.well-known/sgcaptcha/). On a later check all seven pages returned HTTP 200 with
no sgcaptcha request, and it did not block a controlled form submission. It is intermittent.

Please document: trigger conditions, affected traffic sources, false-positive rate, whether an
exclusion or allowlist is available for paid landing pages, and evidence about whether real
Google Ads visitors are ever challenged.

**Do not disable SG-Captcha.** It is a security control and there is no evidence it is harming
genuine visitors.

---

**5c. Internal test-lead cleanup**

Green Marketing submitted one clearly labelled internal test lead to verify conversion
tracking.

| Field | Value |
|---|---|
| Name | GM TEST DO NOT CONTACT |
| Timestamp | 2026-09-02 09:24:37 America/New_York |
| Phone | (631) 555-0147 — NANP reserved fictitious range, cannot ring a real person |
| Page | /power-washing-services-islip-west-islip-dix-hills/ |

Check Gravity Forms (form ID 1), WhatConverts (account number appears to be 158931), and any
CRM or webhook destination. Mark it as an internal test, suppress any follow-up, and report
back which systems contained it.

**Preserve the record until Green Marketing confirms measurement QA is complete**, then delete
or archive. There is nothing to clean in Google Ads.

---

**5d. Rights-cleared project images**

To add project images and reviews to the landing pages we need client-supplied, rights-cleared
photographs of completed Power Washing work, and verified service-relevant reviews. No stock
landscaping imagery, no fabricated project photos, and no AI-generated images presented as
completed work.
