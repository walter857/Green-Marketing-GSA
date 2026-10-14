# Build a Policy-Compliant Review Collection Flow

Validate the current work order first. Use the exact client account, service, CRM, and verified Google review URL.

Do not implement review gating. Google prohibits discouraging negative reviews or selectively soliciting positive reviews.

Build a simple customer feedback page:

- Ask for a 1–5 experience rating and optional written feedback.
- Send every completed response to the CRM or approved webhook.
- Offer the same optional Google review link to every genuine customer, regardless of rating.
- For low scores, also create an internal service-recovery alert. Do not hide the review link.
- Do not offer incentives for reviews.
- Add privacy notice, consent, rate limiting, spam protection, and a unique job/customer reference.
- Store only the minimum PII required.
- Track feedback completion and review-link click as secondary analytics, not Google Ads conversions.

Test all five rating paths and prove the Google review opportunity is equal.
