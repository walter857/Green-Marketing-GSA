# Speed-to-Lead Automation Template

## Event contract

Input: lead ID, client ID, source, name, phone/email, service, location, timestamp, click IDs/UTMs, consent, and landing page.

## Workflow

1. Validate and deduplicate.
2. Write to CRM.
3. Assign owner from service/location/schedule rules.
4. Alert owner immediately.
5. Send approved acknowledgment where consent permits.
6. Start 60-second staffed-hours call timer.
7. Escalate to backup owner if missed.
8. Apply approved retry cadence.
9. Stop on reply, booking, disqualification, sale, or opt-out.
10. Record timestamps and failure reasons.

Use test contacts until the user explicitly approves production activation.

