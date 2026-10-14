#!/usr/bin/env python3
"""Ambient | 2026-10-02 | EXECUTOR for AMB-1002-EMER-CREATE-1 / AMB-1002-GEO-CREATE-1 (create-paused stage only).

Usage (only after the exact approval line):  python scripts/ambient_1002_launch_execute.py <PLAN> <FINGERPRINT> <OP_COUNT>

Refuses unless: the plan file recomputes to the given fingerprint and op count; the identity gate passes; the live
unrelated-resource baseline hash equals the plan's. Writes with partial_failure=False, one request per resource type.
On any failure after an earlier request succeeded it stops, records every created resource name, and writes a PARTIAL
receipt (no retry). Then reads every changed resource back and re-hashes the baseline. Never enables anything.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, TZ, PLANS, RECEIPTS, E, CID  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from ambient_1002_launch_build import read_state, baseline_hash  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402

ALLOWED = {"AMB-1002-EMER-CREATE-1", "AMB-1002-GEO-CREATE-1"}


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ALLOWED:
        sys.exit(f"usage: {Path(__file__).name} <{'|'.join(sorted(ALLOWED))}> <FINGERPRINT> <OP_COUNT>")
    name, fp_ok, n_ok = sys.argv[1], sys.argv[2].upper(), int(sys.argv[3])
    plan = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8"))
    fp = plan.pop("fingerprint")
    if not (fp == approval_code(plan) == fp_ok and plan["operation_count"] == n_ok == len(plan["operations"])):
        sys.exit(f"ABORT {name}: fingerprint/op-count mismatch (file {fp}, recomputed {approval_code(plan)}, approved {fp_ok})")
    prior = RECEIPTS / f"{name}-EXECUTED.json"
    if prior.exists():
        sys.exit(f"ABORT {name}: a receipt already exists ({prior.name}, status "
                 f"{json.loads(prior.read_text(encoding='utf-8')).get('status')}). No re-execution.")
    c = client()
    identity_gate(c, verbose=True)
    st = read_state(c)
    # Resources created by the SIBLING approved plan (recorded in its receipt) are the only drift tolerated.
    sib_ads, sib_kws = set(), set()
    for other in sorted(ALLOWED - {name}):
        rp = RECEIPTS / f"{other}-EXECUTED.json"
        if rp.exists():
            r_ = json.loads(rp.read_text(encoding="utf-8"))
            if r_.get("status") == "EXECUTED":
                sib_ads |= {x["resource"].split("~")[-1] for x in r_["created"] if x["type"] == "AD_GROUP_AD"}
                sib_kws |= {x["resource"].split("/")[-1] for x in r_["created"] if x["type"] == "AD_GROUP_CRITERION"}
    live_hash = baseline_hash(st, skip_ads=sib_ads, skip_kws=sib_kws)
    if live_hash != plan["unrelated_resource_baseline_sha256_16"]:
        sys.exit(f"ABORT {name}: account drifted since the plan was built (baseline {live_hash} != {plan['unrelated_resource_baseline_sha256_16']})."
                 " Rebuild and re-approve.")
    rec = {"plan": name, "fingerprint": fp, "started_local": datetime.datetime.now(TZ).isoformat(), "created": [], "updated": [],
           "status": "RUNNING"}
    out = RECEIPTS / f"{name}-EXECUTED.json"

    def save(status=None):
        if status:
            rec["status"] = status
        out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")

    def mutate(svc, method, req_type, ops, label):
        rq = c.get_type(req_type); rq.customer_id = CID; rq.operations.extend(ops); rq.partial_failure = False
        try:
            resp = getattr(c.get_service(svc), method)(request=rq)
        except Exception as ex:
            rec["failure"] = {"step": label, "error": re.findall(r'message: "([^"]+)"', str(ex))[:3] or str(ex)[:400]}
            rec["recovery"] = ("Nothing from this step was written (partial_failure=False). Resources created by earlier steps are listed "
                               "under 'created'; they are PAUSED and serve nothing. Do not rerun: rebuild the plan for the remaining steps.")
            out_status = "PARTIAL" if rec["created"] or rec["updated"] else "FAILED_NOTHING_WRITTEN"
            save(out_status)
            sys.exit(f"STOPPED at {label}: {rec['failure']['error']} -> receipt {out.name} ({out_status})")
        return [r.resource_name for r in resp.results]

    rsas = [o for o in plan["operations"] if o["op"] == "CREATE_RSA_PAUSED"]
    ops = []
    for p in rsas:
        o = c.get_type("AdGroupAdOperation"); a = o.create
        a.ad_group = c.get_service("AdGroupService").ad_group_path(CID, p["ad_group_id"])
        a.status = c.enums.AdGroupAdStatusEnum.PAUSED
        a.ad.final_urls.append(p["final_url"])
        r = a.ad.responsive_search_ad
        for coll, items in ((r.headlines, p["headlines"]), (r.descriptions, p["descriptions"])):
            for h in items:
                t = c.get_type("AdTextAsset"); t.text = h["text"]
                if h["pin"] != "UNSPECIFIED":
                    t.pinned_field = getattr(c.enums.ServedAssetFieldTypeEnum, h["pin"])
                coll.append(t)
        r.path1, r.path2 = p["path1"], p["path2"]
        ops.append(o)
    names = mutate("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest", ops, "create RSAs PAUSED")
    rec["created"] += [{"type": "AD_GROUP_AD", "resource": n, "label": p["label"]} for n, p in zip(names, rsas)]
    save()
    kws = [o for o in plan["operations"] if o["op"] == "CREATE_KEYWORD_PAUSED"]
    if kws:
        ops = []
        for k in kws:
            o = c.get_type("AdGroupCriterionOperation"); x = o.create
            x.ad_group = c.get_service("AdGroupService").ad_group_path(CID, k["ad_group_id"])
            x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
            x.keyword.text = k["text"]; x.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, k["match"])
            ops.append(o)
        names = mutate("AdGroupCriterionService", "mutate_ad_group_criteria", "MutateAdGroupCriteriaRequest", ops, "create keyword PAUSED")
        rec["created"] += [{"type": "AD_GROUP_CRITERION", "resource": n, "text": k["text"], "match": k["match"]} for n, k in zip(names, kws)]
        save()
    links = [o for o in plan["operations"] if o["op"] == "PAUSE_AD_GROUP_ASSET_LINK"]
    if links:
        ops = []
        for l in links:
            o = c.get_type("AdGroupAssetOperation"); o.update.resource_name = l["resource_name"]
            o.update.status = c.enums.AssetLinkStatusEnum.PAUSED; o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
            ops.append(o)
        names = mutate("AdGroupAssetService", "mutate_ad_group_assets", "MutateAdGroupAssetsRequest", ops, "pause ad-group asset link")
        rec["updated"] += [{"type": "AD_GROUP_ASSET", "resource": n, "status": "PAUSED"} for n in names]
        save()
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat()

    # ---------------- readback ----------------
    checks = []
    for cr, p in zip([x for x in rec["created"] if x["type"] == "AD_GROUP_AD"], rsas):
        ad_id = cr["resource"].split("~")[-1]
        r = q(c, f"""SELECT ad_group.id, ad_group_ad.status, ad_group_ad.ad.final_urls, ad_group_ad.ad.final_mobile_urls, ad_group_ad.ad.tracking_url_template,
                ad_group_ad.ad.final_url_suffix, ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions,
                ad_group_ad.ad.responsive_search_ad.path1, ad_group_ad.ad.responsive_search_ad.path2, ad_group_ad.policy_summary.approval_status,
                ad_group_ad.policy_summary.review_status FROM ad_group_ad WHERE ad_group_ad.ad.id = {ad_id}""")[0]
        a, rsa = r.ad_group_ad, r.ad_group_ad.ad.responsive_search_ad
        got_h = [(h.text, E(h.pinned_field)) for h in rsa.headlines]
        want_h = [(h["text"], h["pin"]) for h in p["headlines"]]
        got_d = [(d.text, E(d.pinned_field)) for d in rsa.descriptions]
        want_d = [(d["text"], d["pin"]) for d in p["descriptions"]]
        norm = lambda xs: sorted((t, pin if pin not in ("UNSPECIFIED", "UNKNOWN") else "UNSPECIFIED") for t, pin in xs)
        checks += [(f"ad {ad_id} status PAUSED", E(a.status) == "PAUSED"),
                   (f"ad {ad_id} ad group {p['ad_group_id']}", str(r.ad_group.id) == p["ad_group_id"]),
                   (f"ad {ad_id} final URL", list(a.ad.final_urls) == [p["final_url"]]),
                   (f"ad {ad_id} no mobile URL / tracking template / suffix", not a.ad.final_mobile_urls and not a.ad.tracking_url_template and not a.ad.final_url_suffix),
                   (f"ad {ad_id} 15 headlines + pins", norm(got_h) == norm(want_h)),
                   (f"ad {ad_id} 4 descriptions + pins", norm(got_d) == norm(want_d)),
                   (f"ad {ad_id} paths", (rsa.path1, rsa.path2) == (p["path1"], p["path2"]))]
        cr["policy"] = {"approval": E(a.policy_summary.approval_status), "review": E(a.policy_summary.review_status)}
    for cr in [x for x in rec["created"] if x["type"] == "AD_GROUP_CRITERION"]:
        ag, cid = cr["resource"].split("/")[-1].split("~")
        r = q(c, f"""SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.status, ad_group_criterion.negative
                FROM ad_group_criterion WHERE ad_group.id = {ag} AND ad_group_criterion.criterion_id = {cid}""")[0].ad_group_criterion
        checks += [(f"keyword {cid} text/match", (r.keyword.text, E(r.keyword.match_type)) == (cr["text"], cr["match"])),
                   (f"keyword {cid} PAUSED positive", E(r.status) == "PAUSED" and not r.negative)]
    for up in rec["updated"]:
        r = q(c, f"SELECT ad_group_asset.status FROM ad_group_asset WHERE ad_group_asset.resource_name = '{up['resource']}'")[0]
        checks.append((f"asset link {up['resource'].split('/')[-1]} PAUSED", E(r.ad_group_asset.status) == "PAUSED"))
    st2 = read_state(c)
    new_ads = {x["resource"].split("~")[-1] for x in rec["created"] if x["type"] == "AD_GROUP_AD"}
    new_kws = {x["resource"].split("/")[-1] for x in rec["created"] if x["type"] == "AD_GROUP_CRITERION"}
    after = baseline_hash(st2, skip_ads=new_ads | sib_ads, skip_kws=new_kws | sib_kws)
    rec["sibling_resources_excluded_from_baseline"] = {"ads": sorted(sib_ads), "keywords": sorted(sib_kws)}
    checks.append(("unrelated-resource baseline unchanged", after == plan["unrelated_resource_baseline_sha256_16"]))
    checks.append(("nothing ENABLED by this plan", all(st2["ads"][a]["status"] == "PAUSED" for a in new_ads)))
    rec["readback"] = [{"check": k, "pass": v} for k, v in checks]
    fails = [k for k, v in checks if not v]
    save("EXECUTED" if not fails else "EXECUTED_READBACK_FAIL")
    for k, v in checks:
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(f"{name} {fp}: {len(rec['created'])} created, {len(rec['updated'])} updated, readback {len(checks) - len(fails)}/{len(checks)} -> {out.name}")


if __name__ == "__main__":
    main()
