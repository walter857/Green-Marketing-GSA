# CONV-2 — controlled duplicate-conversion test

**Status: PROCEDURE ONLY. This test has NOT been run.**

The QA gate asks for a controlled test with a unique test-lead identifier to
prove whether one form submission produces one credit or several. That test
requires submitting a live form, which would create a real record in the client's
CRM and fire real conversion events. Two things block it:

1. **No approval exists** for a live form submission on the client's site.
2. **The form's field map is unverified.** `input_9` is a visible, unlabelled
   text field whose only `label[for]` matches are "Facebook" and "LinkedIn". On
   the sibling Softwind account the same index was a honeypot that silently fakes
   a failed submission when filled. Running a blind test could produce a
   false negative and waste the one clean shot at the evidence.

So the procedure is documented here, and the decision in `PLAN-SLM-CONV-2` rests
on the observational evidence in section 3 below instead.

---

## 1. The test, if approved

**Prerequisites**
- Written approval for one live test submission.
- Confirmation of what `input_9` is (question SLM-Q13).
- WhatConverts read access, so the third leg can be observed (SLM-Q8).

**Unique identifier.** Use a single token in the message field that appears
nowhere else in the client's data, e.g. `GMQA-20260904-7F3A`. Do not use a real
person's name, phone number or email. Use an agency-controlled mailbox and an
agency-controlled phone number.

**Steps**
1. Open `https://offer.softwindli.com/patio/?gclid=<a fresh synthetic gclid>&utm_source=google&utm_medium=cpc&utm_campaign=GMQA_TEST&utm_term=GMQA_TEST_TERM` in a clean browser profile.
2. Record `wc_visitor`, `wc_client` and the `_gcl_aw` cookie values before submitting.
3. Complete only the labelled fields: Full Name, Phone Number, Email Address, and
   "Tell us about your project (optional)" — which is `input_7`, **not** `input_9`.
   Leave `input_9` untouched.
4. Submit once. Record the exact timestamp in America/New_York.
5. Repeat on `/pavers/` with a second distinct token.

**What to read back, at least 24 hours later**

| Where | Query / view | What proves duplication |
|---|---|---|
| Google Ads | `segments.date` × `segments.conversion_action` for the test date | `Softwind Submit lead form` **and** `(web) form_submission` both incremented by 1 for one submission |
| Google Ads | same query | whether `WC Leads` also incremented, making it three |
| GA4 | realtime / DebugView, `form_submission` event | one event, not two |
| WhatConverts | lead detail for the token | one lead, and whether campaign/keyword are populated |
| CRM | search the token | one record, not two |

**Decision rule.** If one submission increments two or more actions that all
count into the Conversions column, duplication is proven at event level and
`PLAN-SLM-CONV-2` is confirmed. If each action increments on a *different*
submission, they are separate lead actions and the plan must be withdrawn.

## 2. Why the test was not simply run anyway

Submitting a form on a client's live site writes a real record into their sales
pipeline and may trigger a call-back to an agency tester. That is an outward-
facing action with a real-world effect, not a read. It needs the client's
explicit yes, and it should be scheduled so their team knows to ignore the lead.

## 3. The observational evidence the plan actually rests on

Day-level firing, `segments.date` × `segments.conversion_action`, all recorded
history (`17-conv-evidence.json`):

| Metric | Form pair |
|---|---|
| Days `Softwind Submit lead form` (7461619140) fired | 6 |
| Days `(web) form_submission` (7480764700) fired | 10 |
| Days **both** fired | **6** |
| Days 7461619140 fired **alone** | **0** |
| Days 7480764700 fired alone | 4 |
| Overlapping days with **identical counts** | **5 of 6** |

| Date | 7461619140 | 7480764700 | WC Leads |
|---|---|---|---|
| 2026-03-27 | 1.0 | 1.0 | 0.0 |
| 2026-04-01 | 2.0 | 2.0 | 0.0 |
| 2026-04-28 | 1.0 | 3.0 | 0.0 |
| 2026-05-14 | 1.0 | 1.0 | 0.0 |
| 2026-06-17 | 1.0 | 1.0 | 1.0 |
| 2026-07-15 | 2.0 | 2.0 | 2.0 |

Supporting attributes:

- Both carry `category = SUBMIT_LEAD_FORM` and `origin = WEBSITE`.
- Lag profile: 8.0 of 8.0 all-conversions for 7461619140 and 12.0 of 13.0 for
  7480764700 land in `LESS_THAN_ONE_DAY`.
- 7461619140 is `ONE_PER_CLICK`; 7480764700 is `MANY_PER_CLICK`. That explains
  2026-04-28 exactly — one click, three submissions, the ONE_PER_CLICK action
  capped at one.

**Strength of this evidence.** The demoted action has never once fired on a day
the retained action did not. Its events are a strict subset across six months.
For these to be genuinely separate lead actions, six independent coincidences
would be required, five of them at identical counts, with the WEBPAGE action
never once catching a lead the GA4 action missed.

**Its limit, stated plainly.** Day-level co-occurrence is not event-level ID
matching. Two different leads on the same day at the same count is possible. The
test in section 1 is what would remove that residual doubt, and it has not been
run.

## 4. Campaign-learning impact — assessed

**None.** Both Patio and Pavers run `TARGET_SPEND` (Maximize Clicks), which does
not consume conversion data for bidding. No learning period exists to disturb.
This is also why the change is safe to make *before* the P2 Smart Bidding
readiness gate rather than after it: the account will have a clean, deduplicated
conversion history by the time bidding could ever use it.

## 5. Rollback

Set `conversion_action.primary_for_goal = true` on `7461619140`. One field, one
object, no dependencies. Historic reported figures are not restated in either
direction — a credit already counted stays counted — so the rollback restores
future counting only.
