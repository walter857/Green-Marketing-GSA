#!/usr/bin/env python3
"""Ambient | 2026-10-02 | AMB-1002-NEG-EXACT-1: campaign-level EXACT negatives from the Sep 1 - Oct 2 review. BUILD / EXECUTE.

  build                      local checks + validate_only (0 writes), plan + fingerprint
  execute <FINGERPRINT> <N>  only after the exact approval line; re-checks, writes one request per campaign, reads back

Every negative is a full observed query, EXACT, campaign scope (each query is unsuitable throughout its campaign; no
intra-campaign routing problem was found). No Phrase/Broad, no shared or account-level list change, nothing removed.
Source: exports/negative-candidates-2026-10-02.json (scripts/ambient_1002_search_terms.py).
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, TZ, PLANS, RECEIPTS, E, CID, EXACT_NAME, CLIENT_DIR  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

NAME = "AMB-1002-NEG-EXACT-1"
C = json.loads((CLIENT_DIR / "exports" / "negative-candidates-2026-10-02.json").read_text(encoding="utf-8"))["valid"]
norm = lambda t: " ".join(re.sub(r"[^\w&'+\- ]", " ", t.lower()).split())


def live_negatives(c):
    have = set()
    ids = ",".join(sorted({x["campaign_id"] for x in C}))
    for r in q(c, f"""SELECT campaign.id, campaign.status, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, campaign_criterion.criterion_id
            FROM campaign_criterion WHERE campaign.id IN ({ids}) AND campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE"""):
        have.add((str(r.campaign.id), norm(r.campaign_criterion.keyword.text), E(r.campaign_criterion.keyword.match_type)))
    status = {str(r.campaign.id): E(r.campaign.status) for r in q(c, f"SELECT campaign.id, campaign.status FROM campaign WHERE campaign.id IN ({ids})")}
    pos = {(str(r.campaign.id), norm(r.ad_group_criterion.keyword.text)) for r in q(c, f"""SELECT campaign.id, ad_group_criterion.keyword.text FROM ad_group_criterion
            WHERE campaign.id IN ({ids}) AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE AND ad_group_criterion.status != 'REMOVED'""")}
    return have, status, pos


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    c = client()
    identity_gate(c, verbose=False)
    have, status, pos = live_negatives(c)
    errs = []
    ops = []
    for x in C:
        t = x["query"]
        if len(t.split()) > 10 or len(t) > 80: errs.append(f"length: {t}")
        if (x["campaign_id"], norm(t), "EXACT") in have: errs.append(f"already exists: {x['campaign_id']} [{t}]")
        if (x["campaign_id"], norm(t)) in pos: errs.append(f"equals a positive keyword: {t}")
        if status.get(x["campaign_id"]) != "ENABLED": errs.append(f"campaign not enabled: {x['campaign_id']}")
        ops.append(dict(op="ADD_CAMPAIGN_NEGATIVE_EXACT", campaign_id=x["campaign_id"], campaign=x["campaign"], text=t, display=x["display"], match="EXACT",
                        scope="campaign", bucket=x["bucket"], reason=x["reason"], confidence=x["confidence"], observed=f"{x['first_seen']}..{x['last_seen']}",
                        impr=x["impr"], clicks=x["clicks"], cost=x["cost"], ad_groups=x["ad_groups"], conflict_check=x["conflict_check"]))
    ops.sort(key=lambda o: (o["campaign_id"], o["bucket"], o["text"]))
    plan = dict(plan_name=NAME, customer_id=CID, exact_account_name=EXACT_NAME, never_write_to_mcc="3373711342", approval_class="negative-keywords",
                work_order="work-orders/work-order-search-terms-sept-oct-2026-10-02.yaml", match_type="EXACT only", scope="campaign level",
                no_phrase_or_broad=True, no_shared_or_account_list_change=True, nothing_removed=True,
                note="EXACT negatives block only the full query (casing/misspellings included per Google); longer, reordered, plural or synonym "
                     "queries remain eligible. No savings are forecast.", operations=ops)
    plan["operation_count"] = len(ops)
    plan["by_campaign"] = {cid: sum(1 for o in ops if o["campaign_id"] == cid) for cid in sorted({o["campaign_id"] for o in ops})}
    plan["fingerprint"] = approval_code({k: v for k, v in plan.items() if k != "fingerprint"})
    if errs:
        sys.exit("HARD STOP:\n  " + "\n  ".join(errs))

    def build_ops():
        out = {}
        for o in ops:
            x = c.get_type("CampaignCriterionOperation"); cr = x.create
            cr.campaign = c.get_service("CampaignService").campaign_path(CID, o["campaign_id"])
            cr.negative = True; cr.keyword.text = o["text"]; cr.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT
            out.setdefault(o["campaign_id"], []).append(x)
        return out

    def send(xs, validate):
        rq = c.get_type("MutateCampaignCriteriaRequest"); rq.customer_id = CID; rq.operations.extend(xs)
        rq.partial_failure = False; rq.validate_only = validate
        return c.get_service("CampaignCriterionService").mutate_campaign_criteria(request=rq)

    if mode == "build":
        pf = {}
        for cid, xs in build_ops().items():
            try:
                send(xs, True); pf[cid] = f"VALIDATED {len(xs)}"
            except Exception as ex:
                pf[cid] = "FAILED " + str(re.findall(r'message: "([^"]+)"', str(ex))[:3])
        print("preflight:", pf)
        if any(v.startswith("FAILED") for v in pf.values()):
            sys.exit("HARD STOP: validate_only failed - no plan written")
        (PLANS / f"{NAME}.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
        print(f"PLAN {NAME}: {plan['fingerprint']} / {plan['operation_count']} ops {plan['by_campaign']}")
        return
    saved = json.loads((PLANS / f"{NAME}.json").read_text(encoding="utf-8")); fp = saved.pop("fingerprint")
    if not (fp == approval_code(saved) == plan["fingerprint"] == sys.argv[2].upper() and int(sys.argv[3]) == len(ops)):
        sys.exit(f"ABORT: fingerprint mismatch (file {fp}, rebuilt {plan['fingerprint']}, approved {sys.argv[2]})")
    out = RECEIPTS / f"{NAME}-EXECUTED.json"
    if out.exists():
        sys.exit("ABORT: receipt exists")
    rec = dict(plan=NAME, fingerprint=fp, started_local=datetime.datetime.now(TZ).isoformat(), created=[])
    for cid, xs in build_ops().items():
        try:
            rec["created"] += [r.resource_name for r in send(xs, False).results]
        except Exception as ex:
            rec["status"] = "PARTIAL" if rec["created"] else "FAILED_NOTHING_WRITTEN"
            rec["failure"] = {"campaign": cid, "error": re.findall(r'message: "([^"]+)"', str(ex))[:3]}
            out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
            sys.exit(f"STOPPED at campaign {cid}: {rec['failure']} (no retry)")
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat()
    have2, _, _ = live_negatives(c)
    missing = [o["text"] for o in ops if (o["campaign_id"], norm(o["text"]), "EXACT") not in have2]
    rec["readback"] = {"expected": len(ops), "found": len(ops) - len(missing), "missing": missing}
    rec["status"] = "EXECUTED" if not missing else "EXECUTED_READBACK_FAIL"
    rec["intervention_timestamp"] = rec["finished_local"]
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(f"{NAME} {fp}: {rec['status']} {rec['readback']['found']}/{len(ops)} at {rec['finished_local']}")


if __name__ == "__main__":
    main()
