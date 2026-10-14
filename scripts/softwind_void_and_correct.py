#!/usr/bin/env python3
"""Void superseded plans and correct PLAN-I5's incrementality language. Local only."""
from __future__ import annotations

import shutil
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "clients/softwind-power-washing/plans"
SUP = PLANS / "superseded"
SUP.mkdir(exist_ok=True)

VOIDS = {
    "2026-08-26-plan-i2a-c-create-paused-skags.yaml": (
        "D50CDC94927C",
        "All four proposed SKAGs failed the corrected incrementality test. Modern "
        "Phrase Match matches the MEANING of a keyword, not its literal word sequence, "
        "so Keyword Planner volume cannot be credited as incremental. Search-term "
        "history shows enabled keywords are ALREADY matching every one of these query "
        "spaces: power washing service 70 impressions, power washing long island 62, "
        "pressure washing service 17, house washing near me 9. Critically, NO query in "
        "the account's entire history has ever contained the words 'long island', so "
        "that SKAG rests on zero observed demand. Creating four ad groups that add zero "
        "incremental impressions would fragment a 24-impression/day pool for no gain."),
    "2026-08-26-plan-i2a-en-enable-after-qa.yaml": (
        "9ABDF6DDE3F4",
        "Enables the output of PLAN-I2A-C, which is now VOID. Nothing to enable."),
    "2026-08-26-plan-e2-live-negative-keywords.yaml": (
        "09E91EA674C8",
        "PHRASE 'house cleaning' was too broad under modern matching. Replaced by "
        "PLAN-E2A with EXACT [house cleaning services near me]."),
    "2026-08-26-plan-i1-budget-headroom.yaml": (
        "9308DFCF8741",
        "Its $299.93/$88.21 split was derived from a 10:02 snapshot and from PLAN-I2's "
        "demand assumptions, both superseded. Replaced by PLAN-I1B on 16:01 pacing."),
    "2026-08-26-plan-i1a-budget-after-demand-approval.yaml": (
        "5B9BCFA06FD5",
        "Actions-empty specification awaiting demand inputs. Those inputs are now "
        "resolved, so it is replaced by the populated PLAN-I1B. A no-op plan must never "
        "carry an approval command."),
}

for fn, (fp, reason) in VOIDS.items():
    p = PLANS / fn
    if not p.exists():
        print("  already moved: %s" % fn)
        continue
    s = p.read_text(encoding="utf-8")
    doc = yaml.safe_load(s)
    cp = doc["change_plan"]
    cp["approval_status"] = "VOID - DO NOT APPROVE"
    cp["execution_status"] = "VOID - DO NOT EXECUTE"
    cp["void_status"] = {"state": "VOID", "voided_on": "2026-08-26",
                         "fingerprint_voided": fp, "reason": reason}
    p.write_text("# VOID 2026-08-26 - fingerprint %s\n# %s\n\n" % (fp, reason[:200])
                 + yaml.safe_dump(doc, sort_keys=False, width=90, allow_unicode=True),
                 encoding="utf-8")
    shutil.move(str(p), str(SUP / fn))
    print("  VOIDED + moved: %-52s %s" % (fn, fp))

# ---------------- correct PLAN-I5 narrative, actions unchanged ----------------
p5 = PLANS / "2026-08-26-plan-i5-create-paused-expansion.yaml"
d5 = yaml.safe_load(p5.read_text(encoding="utf-8"))
cp = d5["change_plan"]
before = [a["action_id"] for a in cp["actions"]]

cp["incrementality_correction_2026_08_26"] = {
    "what_was_wrong": (
        "This plan previously claimed 'pressure washing near me' was genuinely "
        "uncovered because a Phrase keyword \"pressure washing service\" could not "
        "match a query lacking the word 'service'. That reasoning is WRONG under "
        "current Google Ads matching: modern Phrase Match matches the MEANING of the "
        "keyword, and Exact Match matches same-meaning close variants."),
    "what_the_search_term_history_actually_shows": {
        "exact_query_pressure_washing_near_me_observed": 3,
        "impressions_already_covered_by_enabled_keywords": 16,
        "clicks_on_those_impressions": 0,
        "already_matched_by": [
            {"keyword": "power washing services near me",
             "match_types": ["EXACT", "PHRASE"], "impressions": 10, "clicks": 0},
            {"keyword": "residential pressure washing near me",
             "match_types": ["EXACT"], "impressions": 4, "clicks": 0},
            {"keyword": "power washing near me", "match_types": ["EXACT"],
             "impressions": 1, "clicks": 0},
            {"keyword": "power washing company near me", "match_types": ["PHRASE"],
             "impressions": 1, "clicks": 0}]},
    "corrected_classification": "ROUTING / RELEVANCE IMPROVEMENT - not NET-NEW DEMAND",
    "corrected_expected_effect": (
        "ZERO incremental impressions. The query space is already reachable. What "
        "changes is WHICH ad serves: today these 16 impressions are answered by "
        "power-washing copy and have produced 0 clicks. A dedicated pressure-washing "
        "SKAG serves matching copy. Credit it as a CTR and Quality Score fix only."),
    "does_the_70_per_month_planner_volume_still_apply": (
        "NO. It must not be added to the demand model as incremental. It describes the "
        "size of a query space the account can ALREADY reach."),
    "is_the_plan_still_worth_building": (
        "YES, but not for August. It has the strongest routing evidence of the five "
        "candidates - the exact query was observed 3 times and every impression on that "
        "space converted to 0 clicks. But it is create-paused, needs readback QA and a "
        "separate enable approval, and adds no incremental impressions, so it cannot "
        "help the month-end spend objective. Reclassified as a SEPTEMBER structural "
        "improvement."),
    "fingerprint_impact": (
        "NONE. The ad group, both keywords, both RSAs, the Final URL and the display "
        "paths are all unchanged - only the justification and expected-effect language "
        "changed. The normalized action list is byte-identical, so A63D86DB3602 remains "
        "valid."),
}
cp["priority"] = "SEPTEMBER - structural, not part of the August rescue"
cp["recommended_approval_order"] = (
    "NOT IN THE AUGUST PATH - adds zero incremental impressions before 2026-08-31")
p5.write_text("# PLAN-I5 - CREATE PAUSED: PRESSURE WASHING NEAR ME\n#\n"
              "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
              "# CORRECTED 2026-08-26: reclassified from NET-NEW DEMAND to ROUTING /\n"
              "# RELEVANCE IMPROVEMENT. Actions unchanged, so fingerprint A63D86DB3602\n"
              "# is preserved. Moved out of the August path to September.\n\n"
              + yaml.safe_dump(d5, sort_keys=False, width=90, allow_unicode=True),
              encoding="utf-8")
after = [a["action_id"] for a in yaml.safe_load(
    p5.read_text(encoding="utf-8"))["change_plan"]["actions"]]
print()
print("PLAN-I5 corrected. actions before=%s after=%s  identical=%s"
      % (before, after, before == after))

# ---------------- PLAN-G hold ----------------
pg = PLANS / "2026-08-25-plan-g-campaign-consolidation.yaml"
dg = yaml.safe_load(pg.read_text(encoding="utf-8"))
dg["change_plan"]["approval_status"] = "NOT APPROVED - HOLD FOR SEPTEMBER"
dg["change_plan"]["hold_status"] = {
    "state": "HOLD FOR SEPTEMBER", "set_on": "2026-08-26",
    "not_void": True,
    "reason": ("G-1 pauses one duplicate ad group with 1 lifetime impression; G-2 is a "
               "full consolidation that resets learning. Neither helps the month-end "
               "objective, and G-2 risks a delivery gap in the final week. Both wait "
               "for September."),
    "fingerprint_preserved": "EC35724753AE"}
pg.write_text(yaml.safe_dump(dg, sort_keys=False, width=90, allow_unicode=True),
              encoding="utf-8")
print("PLAN-G: %s" % dg["change_plan"]["approval_status"])
