# Client Intake Questions

Ask only questions that are unanswered in the client's existing profile or source files, except that the exact account name, child ID, and service must always be present in the current validated work order.

## 0. Mandatory task identity

Do not begin an audit, account lookup, draft, build, or change until all three answers are confirmed:

1. What is the exact child account name shown in Google Ads?
2. What is the 10-digit child customer ID? This is not Green Marketing's manager/MCC ID.
3. What exact service are we working on?

Then confirm the vertical: landscaping, hardscaping, heating-cooling, or an explicitly approved similar local service. For a similar local service, record the approver and rationale.

## A. One-time agency setup

1. What is the Green Marketing MCC customer ID?
2. Where are the Google Ads OAuth credentials stored locally? Do not paste them into chat.
3. What API access tier does the developer token have?
4. Which Google Cloud project owns OAuth and the enabled APIs?
5. Is Data Manager API enabled for new offline-conversion uploads?
6. Which CRM is the system of record for leads, qualified leads, sales, revenue, and gross profit?
7. Which tools are used for forms, call tracking, speed-to-lead, and attribution: WhatConverts, GTM, GA4, Make.com, GoHighLevel, another CRM, or custom webhooks?
8. Which GitHub organization and Vercel team own landing pages?
9. Who can approve campaign creation, enablement, budget changes, conversion changes, and deletion?

## B. Required client identity

1. Exact client/business name.
2. Exact 10-digit Google Ads child customer ID and exact displayed child account name.
3. Confirm whether the account name contains `- live`.
4. Website and service-specific landing page URLs.
5. Primary phone number and call-tracking number, if different.
6. Primary contact/owner for approvals.
7. Currency and account time zone.

## C. Offer and sales economics

1. Which exact primary service is this work order for, and which related services should generate new customers?
2. Which services must never be advertised?
3. What are the highest-margin services?
4. Average job revenue, gross margin, and close rate by service.
5. What makes a lead qualified?
6. Target CPL, qualified CPL, CAC, monthly lead goal, and revenue goal.
7. Monthly budget and maximum daily budget.
8. Verified USPs, licenses, warranties, guarantees, ratings, review count, response time, offers, and financing.
9. Competitor names to monitor and whether competitor conquesting is allowed.

## D. Service area and schedule

1. Country, state/province, cities, ZIP/postal codes, or radius actually served.
2. Locations to exclude.
3. Are crews dispatched from one address or multiple locations?
4. Days and hours someone can answer calls within 60 seconds.
5. Can the business service after-hours or emergency leads?
6. Languages supported by ads, landing pages, and sales staff.

## E. Campaign architecture

1. New build, revamp, or audit only?
2. Campaign names that must be preserved.
3. Services and cities that need their own campaigns or ad groups.
4. Confirm default structure: one canonical intent per ad group, Phrase + Exact, two RSAs.
5. Existing profitable keywords/search terms that must be preserved.
6. Existing negatives or shared lists that must not be duplicated.
7. Ad schedule and budget constraints.
8. Final URLs to use until dedicated landing pages are ready.

## F. Landing pages and creative

1. Required template and whether its structure must remain unchanged.
2. H1, offer, CTA, phone, form fields, reviews, images, and legal text.
3. Which testimonials and photos are verified for this client and service?
4. Which services/locations may be mentioned?
5. What is the thank-you URL and form webhook?
6. Hosting, domain, repository, and deployment ownership.

## G. Measurement and automation

1. Existing conversion actions and which are Primary versus Secondary.
2. Form-submit tracking method and deduplication ID.
3. Call-conversion definition: minimum duration and source.
4. Where GCLID, GBRAID, WBRAID, and UTMs are stored.
5. CRM stages and which stage is sent back as qualified lead, sold job, and revenue.
6. Consent/privacy requirements for customer data and retargeting.
7. Speed-to-lead owner, routing rules, SLA, retries, and after-hours behavior.
8. Google review URL and the approved review-request process.

## H. Final approval checklist

Before any create-paused operation, reconfirm the exact child account name, child customer ID, exact service, campaign names, budgets, locations, schedule, final URLs, conversion goals, keyword/ad counts, and approval owner. Before enabling, read the created resources back and obtain a second approval.
