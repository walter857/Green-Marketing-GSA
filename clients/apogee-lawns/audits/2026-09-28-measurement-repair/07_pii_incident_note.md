# 07 — PII incident note (sanitized)

**What the earlier disclosure establishes.**
- **When and what:** during the 2026-09-28 independent audit, one ad-hoc WhatConverts aggregation script printed the
  values of the lead field `phone_number` for about 17 call leads (09-10..09-28). That field holds **caller** phone
  numbers, not Apogee's tracking numbers. The script had used `phone_number or tracking_number`.
- **Scope:** no names, emails, messages or recordings were printed.

**Affected output surface.**
- The command's console output, which was returned to the Claude Code session transcript (tool result).
- The values were **not** written by that script to any file in the repository or the evidence folder, and they do not
  appear in any report, memory file or fixture.
- The package validators scan run B and run C deliverables and evidence for formatted and E.164 phone numbers outside
  the business allowlist. Both passes found none.

**Containment made in this run.**
1. New module `src/gm_gsa/wc_sanitize.py`: an allowlist sanitizer.
   - Contact and PII fields are never emitted: `phone_number`, `caller_*`, `contact_*`, `email_address`, `zip`,
     `message`, `call_transcription`, `recording`, `ip_address`, `user_id`, `lead_analysis`, and others.
   - Business numbers print only if they are on an explicit allowlist.
   - URLs are reduced to host plus path.
   - Click IDs and UTMs are reported only as presence booleans.
   - Nested structures expose field **names** only.
2. `tests/test_wc_sanitize.py`: 9 synthetic-data tests (fake 555-01xx numbers, `example.com` addresses), all passing.
3. Every WhatConverts lead read in this run went through the sanitizer before any count or print. Only sanitized output
   was saved (`reports/apogee-lawns/evidence/2026-09-28c-whatconverts-config-sanitized.json`).
4. Configuration reads (`tracking/numbers`, `tracking/forms`) print allowlisted business fields only.
5. A memory note records that `phone_number` in WhatConverts leads is caller PII.

**What remains unknown.**
- Whether the Claude Code session transcript, the conversation history stored by the client application, or any provider
  or tool logs retain that console output, and for how long. That persistence is outside this repository and was not
  inspected.
- No log was deleted or altered. Doing so would need separate authorization, and this note makes no claim that all copies
  are absent.
- The caller numbers are deliberately **not** repeated here and were not re-retrieved to document the incident.
