#!/usr/bin/env python3
"""Ambient | incremental heating search-term negatives (re-runnable, e.g. weekly).

Re-reads every search term on the seven heating Search campaigns since 2026-09-17, classifies with the
same whitelist as AMB-0926-NEG-HEAT-1, and finds OUT_OF_SCOPE / COOLING terms that NO existing negative
blocks yet (campaign criteria, account-level list, and both heating shared lists). New ones are added
as EXACT to list 12252013691 and as PHRASE to list 12249470554, after the same protection tests
(test searches, geo grid, converting terms, keywords, on-target corpus). Raw terms stay on disk;
stdout is aggregates only.

    python ambient_0927_heating_neg_increment.py plan | execute --fp X
"""
from __future__ import annotations
import sys, json, re, argparse, datetime, hashlib, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS
from gm_gsa.safety import approval_code
import ambient_0926_heating_st_negatives as st
import ambient_0926_heating_neg_phrase as ph

EXACT_LIST, PHRASE_LIST = "12252013691", "12249470554"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["plan", "execute"]); ap.add_argument("--fp")
    a = ap.parse_args()
    c = client(); identity_gate(c, verbose=False)
    today = datetime.datetime.now(TZ).date().isoformat()
    geo = set(json.loads(st.GEO.read_text()))
    rows, ever, kws, negs, acct, _ = st.gather(c)
    st.PROTECTED.clear()
    for t in list(ever) + list(kws): st.PROTECTED.update(x for x in re.split(r"[^a-z0-9/']+", t) if x)
    lists = collections.defaultdict(list)
    for r in q(c, f"""SELECT shared_criterion.keyword.text, shared_criterion.keyword.match_type, shared_set.id FROM shared_criterion
            WHERE shared_set.id IN ({EXACT_LIST}, {PHRASE_LIST})"""):
        lists[str(r.shared_set.id)].append((r.shared_criterion.keyword.text.lower(), E(r.shared_criterion.keyword.match_type)))
    shared = lists[EXACT_LIST] + lists[PHRASE_LIST]
    buckets = {t: st.classify(t, geo, d["conv"] + ever.get(t, 0)) for t, d in rows.items()}
    latest = max((d.get("last", "") for d in rows.values()), default="")
    new_bad = sorted(t for t, b in buckets.items() if b in ("OUT_OF_SCOPE", "COOLING") and t not in kws
                     and len(t) <= 80 and len(t.split()) <= 10
                     and not any(st.blocked_by(t, negs[cid] + acct + shared) for cid in rows[t]["camps"]))
    # protection tests for the PHRASE versions
    places = sorted({r.geo_target_constant.name.lower() for r in q(c, f"""SELECT geo_target_constant.name FROM geo_target_constant
                     WHERE geo_target_constant.resource_name IN ({','.join(repr(r.campaign_criterion.location.geo_target_constant) for r in q(c,
                     "SELECT campaign_criterion.location.geo_target_constant, campaign.id FROM campaign_criterion WHERE campaign.id = 24257819466 AND campaign_criterion.type = 'LOCATION'"))})""")
                     if not r.geo_target_constant.name.isdigit()})
    probes = [m.format(s=s) for s in ph.SERVICES for m in ph.MODS] + ph.EXTRA
    probes += [f"{s} {p}" for s in ph.SERVICES[:12] for p in places] + [f"{s} in {p} md" for s in ph.SERVICES[:12] for p in places]
    probes = [re.sub(r"\s+", " ", p.lower()).strip() for p in probes]
    keep_terms = [t for t, b in buckets.items() if b in ("KEEP", "KEEP_CONV", "DEFERRED")]
    phrase_add, exact_add = [], []
    for t in new_bad:
        exact_add.append(t)
        if not any(ph.blocks(t, "PHRASE", x) for x in probes + list(ever) + list(kws) + keep_terms):
            phrase_add.append(t)
    unblocked_hold = sum(1 for t, b in buckets.items() if b == "HOLD" and not any(st.blocked_by(t, negs[cid] + acct + shared) for cid in rows[t]["camps"]))
    agg = collections.defaultdict(lambda: [0, 0, 0, 0.0])
    for t, d in rows.items():
        x = agg[buckets[t]]; x[0] += 1; x[1] += d["impr"]; x[2] += d["clicks"]; x[3] += d["cost"]
    plan = {"customer_id": CID, "exact_account_name": EXACT_NAME, "plan_name": f"AMB-{today}-NEG-HEAT-INC",
            "built_local": today, "window": f"{st.SINCE}..{today}", "exact_add": exact_add, "phrase_add": phrase_add,
            "sha1": hashlib.sha1("\n".join(exact_add + ["|"] + phrase_add).encode()).hexdigest()[:12]}
    fp = approval_code(plan)
    print(f"window {st.SINCE}..{today} | distinct terms {len(rows)} | buckets:",
          {k: {"terms": v[0], "impr": v[1], "clicks": v[2], "cost": round(v[3], 2)} for k, v in sorted(agg.items())})
    print(f"off-topic terms NOT yet blocked: {len(new_bad)} -> EXACT adds {len(exact_add)}, PHRASE adds {len(phrase_add)} | "
          f"still-unblocked HOLD terms: {unblocked_hold} | fp {fp}")
    if a.mode == "plan":
        (PLANS / f"{plan['plan_name']}.json").write_text(json.dumps({**plan, "fingerprint": fp}, indent=1), encoding="utf-8")
        return
    if a.fp != fp: sys.exit(f"ABORT fp {fp} != {a.fp}")
    if not exact_add and not phrase_add:
        print("nothing to add"); return
    ops = []
    for t in exact_add:
        m = c.get_type("MutateOperation"); cr = m.shared_criterion_operation.create
        cr.shared_set = c.get_service("SharedSetService").shared_set_path(CID, EXACT_LIST)
        cr.keyword.text = t; cr.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT; ops.append(m)
    for t in phrase_add:
        m = c.get_type("MutateOperation"); cr = m.shared_criterion_operation.create
        cr.shared_set = c.get_service("SharedSetService").shared_set_path(CID, PHRASE_LIST)
        cr.keyword.text = t; cr.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE; ops.append(m)
    ga = c.get_service("GoogleAdsService")
    rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False; rq.mutate_operations.extend(ops)
    rq.validate_only = True; ga.mutate(request=rq)
    rq.validate_only = False; resp = ga.mutate(request=rq)
    (RECEIPTS / f"{plan['plan_name']}-EXECUTED.json").write_text(json.dumps({"plan": plan["plan_name"], "fingerprint": fp,
        "created": len(resp.mutate_operation_responses), "executed_local": datetime.datetime.now(TZ).isoformat()}, indent=1), encoding="utf-8")
    print("EXECUTED", len(resp.mutate_operation_responses))


if __name__ == "__main__":
    main()
