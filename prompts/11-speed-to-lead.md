# Design Speed-to-Lead Automation

Validate the current work order first and keep routing tied to the exact client, service, location, and staffed schedule.

Target: acknowledge and route a new lead immediately. Use a 60-second human-call goal only when the client confirms it can be met during staffed hours.

Flow:

1. Receive form/call/LSA lead.
2. Validate, normalize, deduplicate, and assign a unique lead ID.
3. Write the lead and attribution fields to the CRM.
4. Route by client, service, location, language, and business hours.
5. Notify the assigned owner.
6. Trigger the approved immediate SMS/email acknowledgment with consent-compliant language.
7. Start the human-call SLA timer.
8. Escalate unanswered leads according to approved retry rules.
9. Stop automation on reply, booking, opt-out, disqualification, or sale.
10. Log timestamps, owner, attempts, outcome, revenue, and failure reason.

Ask for CRM, webhook, owners, schedules, phone/SMS provider, consent language, retry limits, and after-hours policy. Never send real messages while drafting or testing. Use test contacts and explicit approval before enabling.
