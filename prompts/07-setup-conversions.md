# Set Up and Verify Conversion Measurement

Start with a read-only inventory of existing tags, GTM containers, Google Ads conversion actions, GA4 events, call tracking, WhatConverts, CRM stages, and thank-you behavior.

Validate the work order and selected child account before inventorying anything. Keep conversion names tied to the exact service when service-level reporting is required.

Define a measurement map before changing anything:

- Form lead.
- Qualified call with the approved minimum duration.
- Qualified lead or closed-won offline outcome.
- Secondary diagnostics such as page view, click-to-call, form start, and form error.

Rules:

- One primary event per real business outcome.
- Deduplicate with lead/transaction IDs.
- Keep diagnostic clicks secondary.
- Preserve GCLID, GBRAID, WBRAID and UTMs in the CRM.
- Verify the tag ID and conversion label belong to the selected customer account.
- Never replace an existing tag or trigger without identifying its current consumers.
- Use Tag Assistant or an automated browser test to verify each event.
- Stop if a conversion does not fire; do not mark the setup complete.
- For new offline integrations, use Data Manager API unless legacy eligibility is confirmed.

Present the map and exact proposed changes for approval. Make changes one conversion at a time and verify before moving on.
