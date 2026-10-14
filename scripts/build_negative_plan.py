#!/usr/bin/env python3
"""Build the Pro Green Austin negative-keyword plan.

Local files only. Proposes; never applies. Every proposed negative is conflict-checked
against live positive keywords, every query that ever converted, and the Green Marketing
protected-term list before it is allowed into the plan.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

CID = "7380491929"
PROTECTED_RE = re.compile(
    r"\b(near\s+me|quotes?|prices?|pricing|costs?|best|hire|local|emergency|free)\b", re.I)


def norm(t: str) -> str:
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------------------
# A. Proposed ADDITIONS, drawn from queries actually observed on the two live
#    campaigns. Each entry: (text, match_type, family, evidence)
# ---------------------------------------------------------------------------
# ADD now: only terms with observed spend on a live campaign and zero conversions.
ADD_NOW = [
    ("agave landscaping", "competitor_brand"),
    ("agc turf", "competitor_brand"),
    ("astoria lighting", "competitor_brand"),
    ("garden goat", "competitor_brand"),
    ("mcdugald steele", "competitor_brand"),
    ("mirror lake landscaping", "competitor_brand"),
    ("spring texas", "wrong_market_houston_area"),
    ("ulm austin", "competitor_brand"),
]

# WATCH: recorded with evidence, NOT proposed for addition in this round.
# Competitor names seen only as impressions, with no click and no cost yet.
WATCH_TERMS = [
    ("allied outdoor solutions", "competitor_brand", "impressions only, no click, no cost"),
    ("casas landscaping", "competitor_brand", "impressions only, no click, no cost"),
    ("cedarcrest", "competitor_brand", "impressions only, no click, no cost"),
    ("clean scapes", "competitor_brand", "impressions only, no click, no cost"),
    ("cooper and company", "competitor_brand", "impressions only, no click, no cost"),
    ("cutters landscaping", "competitor_brand", "impressions only, no click, no cost"),
    ("ground and garden", "competitor_brand", "impressions only, no click, no cost"),
    ("ps landscapes", "competitor_brand", "impressions only, no click, no cost"),
    ("stallion paving", "competitor_brand", "impressions only, no click, no cost"),
    ("stevens paving", "competitor_brand", "impressions only, no click, no cost"),
    ("waterloo turf", "competitor_brand", "impressions only, no click, no cost"),
    ("asphalt", "wrong_material_asphalt_is_not_pavers",
     "impressions only, no click, no cost. A PHRASE negative on 'asphalt' would already "
     "cover 'asphalt paving', so adding both is redundant. Neither is proposed."),
    ("asphalt paving", "wrong_material_asphalt_is_not_pavers",
     "redundant with the broader single-word 'asphalt'; impressions only, no click, no cost"),
]

# ---------------------------------------------------------------------------
# B. Proposed REMOVALS of existing negatives that block real design-and-build
#    demand or violate Green Marketing protected-term policy.
# ---------------------------------------------------------------------------
# 'emergency' is deliberately NOT in this list. Emergency intent is not supported for
# outdoor design-and-build work, so the existing negative is correct and is retained.
REMOVALS = [
    ("cost", "BROAD", "account-level negative keywords list", "11260450591",
     "protected_term_blocked_account_wide",
     "Green Marketing policy protects 'cost'. As a BROAD account-level negative it blocks "
     "every cost query on every campaign, including 'paver patio cost' and 'outdoor "
     "kitchen cost austin'. For a design-and-build business with large tickets, cost "
     "queries are buyers, not researchers. Invisible in the campaign UI."),
    ("hire", "PHRASE", "General", "10670796064",
     "protected_term_blocked_on_live_campaigns",
     "Green Marketing policy protects 'hire'. Blocks 'hire a hardscape contractor' and "
     "'hire landscape designer' on both live campaigns."),
    ("shade", "PHRASE", "General", "10670796064",
     "blocks_verified_service_demand",
     "Blocks 'shade structure', 'shade sail' and 'patio shade cover'. Those are direct "
     "pergola and shade-structure queries and both live campaigns run Pergolas ad groups."),
    ("oasis", "BROAD", "account-level negative keywords list", "11260450591",
     "blocks_verified_service_demand",
     "Blocks 'backyard oasis' and 'backyard oasis design', a common outdoor-living "
     "buying phrase, on every campaign."),
    ("keystone", "BROAD", "account-level negative keywords list", "11260450591",
     "blocks_verified_service_demand",
     "Keystone is a mainstream retaining-wall block brand. Blocks 'keystone retaining "
     "wall installation' account-wide while Retaining Walls ad groups are live."),
    ("black", "BROAD", "account-level negative keywords list", "11260450591",
     "blocks_verified_service_demand",
     "Blocks common Austin hardscape material queries such as 'black star gravel' and "
     "'black limestone patio' account-wide."),
    ("replacement", "BROAD", "account-level negative keywords list", "11260450591",
     "blocks_verified_service_demand",
     "Blocks 'paver replacement', 'patio replacement' and 'driveway replacement', all "
     "of which are design-and-build rebuild work."),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--term-csv", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    S = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    LIVE = {c["id"]: c["name"] for c in S["campaigns"] if c["status"] == "ENABLED"}
    terms = list(csv.DictReader(Path(args.term_csv).open(encoding="utf-8")))

    live_pos = [k for k in S["keywords"]
                if not k["negative"] and k["campaign_id"] in LIVE and k["status"] == "ENABLED"]
    converting = sorted({norm(r["original_search_term"]) for r in terms
                         if float(r["conversions"]) > 0})

    # Evidence lookup: which observed live queries does each proposed negative cover?
    live_terms = [r for r in terms if r["campaign_id"] in LIVE]

    def evidence_for(text: str):
        rx = re.compile(r"\b" + re.escape(norm(text)) + r"\b")
        hits = [r for r in live_terms if rx.search(norm(r["original_search_term"]))]
        cost = sum(float(r["cost"]) for r in hits)
        clicks = sum(int(r["clicks"]) for r in hits)
        impr = sum(int(r["impressions"]) for r in hits)
        conv = sum(float(r["conversions"]) for r in hits)
        return len(hits), impr, clicks, round(cost, 2), conv

    def conflicts(text: str, match_type: str):
        n = norm(text)
        rx = re.compile(r"\b" + re.escape(n) + r"\b")
        out = []
        for k in live_pos:
            kt = norm(k["text"])
            blocked = (n == kt if match_type == "EXACT"
                       else bool(rx.search(kt)) if match_type == "PHRASE"
                       else all(tok in kt.split() for tok in n.split()))
            if blocked:
                out.append(f"live keyword {k['criterion_id']} {k['text']!r}")
        for q in converting:
            blocked = (n == q if match_type == "EXACT"
                       else bool(rx.search(q)) if match_type == "PHRASE"
                       else all(tok in q.split() for tok in n.split()))
            if blocked:
                out.append(f"converting query {q!r}")
        return out

    rows = []
    action = 0

    def add_row(**kw):
        nonlocal action
        action += 1
        rows.append({"action_id": f"NEG-{action:03d}", "customer_id": CID, **kw})

    for group, items in (("A_ADD", ADD_NOW),):
        for text, family in items:
            n_hits, impr, clicks, cost, conv = evidence_for(text)
            confl = conflicts(text, "PHRASE")
            protected = bool(PROTECTED_RE.search(norm(text)))
            gate = "READY"
            if protected:
                gate = "BLOCKED_protected_term"
            elif confl:
                gate = "BLOCKED_conflict"
            elif n_hits == 0:
                gate = "PREVENTIVE_no_observed_query"
            for cid, cname in LIVE.items():
                add_row(
                    approval_category="EXISTING_RESOURCES",
                    operation="ADD_CAMPAIGN_NEGATIVE_KEYWORD",
                    resource_type="campaign_criterion (negative keyword)",
                    target_resource_id=cid, target_resource_name=cname,
                    level="campaign",
                    negative_text=text, match_type="PHRASE",
                    family=family,
                    current_state="not present as a campaign negative on this campaign",
                    proposed_state=f'campaign negative PHRASE "{text}"',
                    observed_live_rows=n_hits, observed_impressions=impr,
                    observed_clicks=clicks, observed_cost=cost,
                    observed_conversions=conv,
                    protected_term="YES" if protected else "",
                    conflict_check=("; ".join(confl) if confl else "no conflict detected"),
                    gate=gate,
                    confidence="high" if clicks else "medium",
                    expected_effect=("Stops paid clicks on this query family in the two "
                                     "design-and-build campaigns. Does not guarantee a "
                                     "lower cost per lead."),
                    risk=("Low. Phrase scope only, campaign level only, so no other "
                          "campaign and no future service is affected."),
                    rollback="Remove the campaign_criterion by its returned criterion_id.",
                    object_count=1,
                )

    for text, family, note in WATCH_TERMS:
        n_hits, impr, clicks, cost, conv = evidence_for(text)
        confl = conflicts(text, "PHRASE")
        add_row(
            approval_category="NONE_WATCH_ONLY",
            operation="WATCH_NO_ACTION",
            resource_type="(none - recorded for monitoring only)",
            target_resource_id="", target_resource_name="both live campaigns",
            level="", negative_text=text, match_type="PHRASE (if ever added)",
            family=family,
            current_state="not present as a campaign negative on either live campaign",
            proposed_state="NO CHANGE. Monitor and re-evaluate when a click or cost appears.",
            observed_live_rows=n_hits, observed_impressions=impr,
            observed_clicks=clicks, observed_cost=cost, observed_conversions=conv,
            protected_term="", conflict_check=("; ".join(confl) if confl else "no conflict detected"),
            gate="WATCH",
            confidence="medium",
            expected_effect="None. Nothing is added.",
            risk=("Adding a negative on impression-only evidence risks blocking demand that has "
                  "never been shown to be worthless. " + note),
            rollback="n/a - no change is made.",
            object_count=0)

    for text, mt, set_name, set_id, family, why in REMOVALS:
        n_hits, impr, clicks, cost, conv = evidence_for(text)
        member = next((m for m in S["shared_criteria"]
                       if m["shared_set_id"] == set_id
                       and norm(m["keyword_text"]) == norm(text)
                       and m["match_type"] == mt), None)
        add_row(
            approval_category="EXISTING_RESOURCES",
            operation="REMOVE_SHARED_LIST_NEGATIVE",
            resource_type="shared_criterion (negative keyword list member)",
            target_resource_id=(member["criterion_id"] if member else "NOT_FOUND"),
            target_resource_name=f"{set_name} (shared_set {set_id})",
            level=("account-wide list" if "account" in set_name else "shared list"),
            negative_text=text, match_type=mt, family=family,
            current_state=f'{mt} negative "{text}" is a member of "{set_name}"',
            proposed_state="member removed",
            observed_live_rows=n_hits, observed_impressions=impr,
            observed_clicks=clicks, observed_cost=cost, observed_conversions=conv,
            protected_term="YES" if PROTECTED_RE.search(norm(text)) else "",
            conflict_check="removal cannot block traffic; it restores eligibility",
            gate="READY" if member else "BLOCKED_member_not_found",
            confidence="high",
            expected_effect=why,
            risk=("Restores eligibility for the described queries on every campaign the "
                  "list is attached to. All such campaigns except the two design-and-build "
                  "campaigns are PAUSED, so no other live spend can change."),
            rollback=f'Re-add "{text}" [{mt}] to shared set {set_id}.',
            object_count=1,
        )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    adds = [r for r in rows if r["operation"].startswith("ADD")]
    rems = [r for r in rows if r["operation"].startswith("REMOVE")]
    watch = [r for r in rows if r["operation"] == "WATCH_NO_ACTION"]
    blocked = [r for r in rows if r["gate"].startswith("BLOCKED")]
    print(f"negative plan rows: {len(rows)}  additions={len(adds)}  removals={len(rems)}  "
          f"watch={len(watch)}")
    print(f"  READY: {sum(1 for r in rows if r['gate'] == 'READY')}")
    print(f"  PREVENTIVE (no observed query yet): "
          f"{sum(1 for r in rows if r['gate'].startswith('PREVENTIVE'))}")
    print(f"  BLOCKED by conflict or policy: {len(blocked)}")
    for r in blocked:
        print(f"    {r['action_id']} {r['negative_text']!r}: {r['gate']} | {r['conflict_check'][:110]}")
    print(f"\nADDITION families:")
    fams: dict[str, int] = {}
    for r in adds:
        fams[r["family"]] = fams.get(r["family"], 0) + 1
    for k, v in sorted(fams.items()):
        print(f"    {k}: {v} rows ({v // 2} distinct terms x 2 campaigns)")
    print(f"\nREMOVALS proposed:")
    for r in rems:
        print(f"    {r['action_id']} {r['negative_text']!r} [{r['match_type']}] "
              f"from {r['target_resource_name']}  id={r['target_resource_id']}  {r['gate']}")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
