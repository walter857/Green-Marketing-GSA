#!/usr/bin/env python3
"""Ambient | 2026-09-24 | Overlapping native vs WhatConverts conversions: evidence-based plan.

validate_only ONLY. EXTERNAL WRITES: 0. WC Lead (7643656486) and WC Calls (7643656075) stay
PRIMARY by owner instruction and are not touched.

Verified coverage (2026-09-24):
  FORMS  offer gform_1: every submission creates exactly one WhatConverts lead (tests
         259911044, 260010083; failed submissions create none). WhatConverts reads gclid,
         gbraid and wbraid in the browser, and one real paid offer-form lead (2026-09-01)
         was uploaded (Success) and credited as WC Lead. The native 6885463625 counted the
         same lead too, so 2026-09-01 double-counted it. Main-site forms are NOT covered by
         WhatConverts (NitroPack), so the native tag stays Primary while any paid click can
         land there.
  CALLS  call-asset calls go through Google forwarding numbers and Google counts 100% of them
         natively ("Calls from ads" 1068114183). WhatConverts also uploaded both such calls as
         WC Lead, credited 1 of 2, so the native action is the complete path and stays Primary.
         The duplicate is removed on the WhatConverts side (stop sending Phone Calls to Google
         Ads) once the WC UI is reachable - not by demoting any Google Ads action.
"""
from __future__ import annotations
import sys, json, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, PLANS
from gm_gsa.safety import approval_code
from google.protobuf import field_mask_pb2

c = client()
identity_gate(c, verbose=False)
cur = {str(r.conversion_action.id): r.conversion_action for r in q(c, """
    SELECT conversion_action.id, conversion_action.name, conversion_action.primary_for_goal,
           conversion_action.status, conversion_action.type FROM conversion_action
    WHERE conversion_action.id IN (6885463625, 1068114183, 7643656486, 7643656075)""")}
for k, v in sorted(cur.items()):
    print(f"  {k} {E(v.status):8s} primary={v.primary_for_goal!s:5s} {E(v.type_):16s} {v.name}")
assert cur["7643656486"].primary_for_goal and cur["7643656075"].primary_for_goal, "WC must stay Primary"

plan = {
    "customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342",
    "built_local": "2026-09-24", "plan_name": "AMB-0924-CONV-FORM-2", "revised_from": "AMB-0924-CONV-FORM-1 00E5791B8506 (gate replaced per owner 2026-09-24: do not wait for 3 new paid leads)",
    "approval_class": "update-conversion-action-primary-flag",
    "supersedes": "AMB-0923B-CONV-B 346D8583F5E8 (form half; its call half is withdrawn)",
    "unchanged": {"7643656486": "WC Lead PRIMARY", "7643656075": "WC Calls PRIMARY",
                  "1068114183": "Calls from ads PRIMARY - complete native path for call-asset calls"},
    "operations": [{"op": "SET_CONVERSION_ACTION_PRIMARY_FLAG", "conversion_action_id": "6885463625",
                    "name": cur["6885463625"].name, "from": "primary_for_goal=True",
                    "to": "primary_for_goal=False", "field_mask": "primary_for_goal"}],
    "preconditions_met": [
        "GTM v16 live: native form conversion counts only confirmed submissions, with transaction_id",
        "AMB-0924-LP-SWAP-2 executed: no enabled ad or sitelink sends paid clicks to the main site",
        "WhatConverts captures #gform_1 on every live offer page (tests 259911044, 260010083, 260044129, 260045995; Sep-23 captures on 5 pages)",
        "WC Lead click upload proven end-to-end on the offer template (2026-09-01 paid form lead: Success + credited)"],
    "fallback": "6885463625 keeps recording as Secondary (All conversions); re-promote in one step if WC Lead stops crediting",
    "effect": "One paid form lead counts once (WC Lead) instead of twice. The native tag "
              "keeps recording as a Secondary diagnostic, so nothing is lost if WC fails.",
}
plan["operation_count"] = 1
o = c.get_type("ConversionActionOperation")
o.update.resource_name = c.get_service("ConversionActionService").conversion_action_path(CID, "6885463625")
o.update.primary_for_goal = False
o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["primary_for_goal"]))
rq = c.get_type("MutateConversionActionsRequest"); rq.customer_id = CID
rq.operations.append(o); rq.validate_only = True
try:
    c.get_service("ConversionActionService").mutate_conversion_actions(request=rq)
    plan["preflight"] = "VALIDATED 1"
except Exception as ex:
    plan["preflight"] = "FAILED " + str(re.findall(r'message: "([^"]+)"', str(ex))[:2])
plan["fingerprint"] = approval_code({k: v for k, v in plan.items() if k != "fingerprint"})
(PLANS / "AMB-0924-CONV-FORM-2.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
print(f"PLAN AMB-0924-CONV-FORM-2: {plan['fingerprint']} / 1 op / preflight {plan['preflight']} "
      f"")
