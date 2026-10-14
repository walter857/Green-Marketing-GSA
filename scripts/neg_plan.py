#!/usr/bin/env python3
"""Build the negative-keyword plan.

Produces, per account:
  * spend coverage of the mined roots and of each residual tier
  * per-SCOPE redundancy elimination (account list + linked lists + that exact
    campaign's negatives + that exact ad group's negatives) - never pooled
  * LAYER A  campaign-level placement (agency recommendation)
  * LAYER B  ad-group-level placement (as requested by the owner)
  * LAYER X  evidence-backed ad-group cross-negatives (theme steering)
  * evidence on how Google actually sets the search-term "Excluded" label

Aggregates only to stdout. Plan objects go to disk.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from neg_lexicon import ACCOUNTS, PROTECTED  # noqa: E402

CORPUS = ROOT / "reports" / "st-corpus"
VERD = ROOT / "reports" / "st-verdicts"
OUT = ROOT / "reports" / "st-plans"

TOKEN_RE = re.compile(r"[a-z0-9']+")


def toks(s):
    return TOKEN_RE.findall(s.lower())


def contiguous(sub, seq):
    n = len(sub)
    if not n or n > len(seq):
        return False
    return any(seq[i:i + n] == sub for i in range(len(seq) - n + 1))


def blocks(neg_tokens, match_type, query_tokens):
    if not neg_tokens:
        return False                      # malformed criterion blocks nothing
    if match_type == "EXACT":
        return neg_tokens == query_tokens
    if match_type == "PHRASE":
        return contiguous(neg_tokens, query_tokens)
    if match_type == "BROAD":
        return all(t in query_tokens for t in neg_tokens)
    return False                          # UNSPECIFIED / non-keyword criterion


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    grand = {}

    for slug, cfg in ACCOUNTS.items():
        corpus_path = CORPUS / (slug + "-corpus.json")
        if not corpus_path.exists():
            print("[{}] SKIP: no corpus on disk yet".format(slug))
            continue
        d = json.loads(corpus_path.read_text(encoding="utf-8"))
        rp = json.loads((VERD / (slug + "-negative-roots.json")).read_text(encoding="utf-8"))

        live_c = {c["id"]: c for c in d["campaigns"] if c["status"] == "ENABLED"}
        live_ag = {a["id"]: a for a in d["ad_groups"]
                   if a["status"] == "ENABLED" and a["campaign_id"] in live_c}

        terms = {}
        with (VERD / (slug + "-verdicts.csv")).open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                terms[r["search_term"]] = {
                    "verdict": r["verdict"], "category": r["category"],
                    "impr": int(r["impressions"]), "clicks": int(r["clicks"]),
                    "cost": float(r["cost_usd"]), "conv": float(r["conversions"]),
                    "live_rows": int(r["rows_on_live_ad_groups"]),
                }
        neg_terms = {t: v for t, v in terms.items() if v["verdict"] == "NEGATIVE"}
        neg_cost_total = sum(v["cost"] for v in neg_terms.values())

        # ---- safety reference sets ------------------------------------------
        keep_watch = {t: toks(t) for t, v in terms.items()
                      if v["verdict"] in ("KEEP", "WATCH")}
        converting = {t: toks(t) for t, v in terms.items() if v["conv"] > 0}
        live_pos = {p["text"].lower(): toks(p["text"]) for p in d["positive_keywords"]
                    if p["ad_group_id"] in live_ag}
        protected_tok = [toks(p) for p in PROTECTED]

        def is_safe(text, mt):
            nt = toks(text)
            if not nt:
                return False, "empty"
            # Google Ads negative keyword limits: max 10 words, max 80 characters.
            if len(nt) > 10:
                return False, "over_10_words"
            if len(text) > 80:
                return False, "over_80_chars"
            if text.strip().lower() in PROTECTED or any(nt == p for p in protected_tok):
                return False, "protected_phrase"
            for tt in keep_watch.values():
                if blocks(nt, mt, tt):
                    return False, "blocks_keep_or_watch"
            for tt in converting.values():
                if blocks(nt, mt, tt):
                    return False, "blocks_converting_term"
            for pt in live_pos.values():
                if blocks(nt, mt, pt):
                    return False, "blocks_live_keyword"
            return True, "ok"

        # =====================================================================
        # Existing negatives, kept PER SCOPE. Malformed rows are dropped.
        # =====================================================================
        def clean(text, mt):
            tk = toks(text)
            return (tk, mt) if tk and mt in ("EXACT", "PHRASE", "BROAD") else None

        acct_ids = {s["id"] for s in d["shared_sets"]
                    if s["type"] == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"}
        account_wide = [c for c in
                        (clean(m["text"], m["match_type"]) for m in d["shared_members"]
                         if m["shared_set_id"] in acct_ids) if c]

        lists_by_campaign = defaultdict(set)
        for l in d["campaign_shared_sets"]:
            if l["campaign_id"] in live_c:
                lists_by_campaign[l["campaign_id"]].add(l["shared_set_id"])
        members_by_set = defaultdict(list)
        for m in d["shared_members"]:
            c = clean(m["text"], m["match_type"])
            if c:
                members_by_set[m["shared_set_id"]].append(c)

        cneg_by_c = defaultdict(list)
        for n in d["campaign_negatives"]:
            if n["campaign_id"] in live_c:
                c = clean(n["text"], n["match_type"])
                if c:
                    cneg_by_c[n["campaign_id"]].append(c)
        agneg_by_ag = defaultdict(list)
        for n in d["ad_group_negatives"]:
            if n["ad_group_id"] in live_ag:
                c = clean(n["text"], n["match_type"])
                if c:
                    agneg_by_ag[n["ad_group_id"]].append(c)

        def campaign_existing(cid):
            out = list(account_wide) + list(cneg_by_c.get(cid, []))
            for sid in lists_by_campaign.get(cid, ()):
                out += members_by_set.get(sid, [])
            return out

        def adgroup_existing(agid):
            cid = live_ag[agid]["campaign_id"]
            return campaign_existing(cid) + list(agneg_by_ag.get(agid, []))

        def redundant(text, mt, existing):
            q = toks(text)
            return any(blocks(et, emt, q) for et, emt in existing)

        # =====================================================================
        # EVIDENCE: what actually sets search_term_view.status = EXCLUDED
        # =====================================================================
        excl_rows = [t for t in d["search_terms"]
                     if t["st_status"] == "EXCLUDED" and t["ad_group_id"] in live_ag]
        by_ag = by_c_only = by_list_only = by_none = 0
        for t in excl_rows:
            q = toks(t["term"])
            if any(blocks(nt, mt, q) for nt, mt in agneg_by_ag.get(t["ad_group_id"], [])):
                by_ag += 1
            elif any(blocks(nt, mt, q) for nt, mt in cneg_by_c.get(t["campaign_id"], [])):
                by_c_only += 1
            elif any(blocks(nt, mt, q)
                     for sid in lists_by_campaign.get(t["campaign_id"], ())
                     for nt, mt in members_by_set.get(sid, [])):
                by_list_only += 1
            else:
                by_none += 1

        # =====================================================================
        # Candidate universe: safe roots + tiered residual exacts
        # =====================================================================
        roots, rejected = [], []
        for r in rp["roots"]:
            ok, why = is_safe(r["text"], "PHRASE")
            if ok:
                roots.append(r)
            else:
                rejected.append({"text": r["text"], "reason": why})
        root_tok = [toks(r["text"]) for r in roots]

        def covered_by_roots(term):
            q = toks(term)
            return any(contiguous(rt, q) for rt in root_tok)

        cov_cost = sum(v["cost"] for t, v in neg_terms.items() if covered_by_roots(t))
        cov_n = sum(1 for t in neg_terms if covered_by_roots(t))
        residual = {t: v for t, v in neg_terms.items() if not covered_by_roots(t)}

        tiers = {"T1_spent": [], "T2_clicked": [], "T3_impressed": [], "T4_tail": []}
        for t, v in residual.items():
            if v["cost"] > 0:
                tiers["T1_spent"].append(t)
            elif v["clicks"] > 0:
                tiers["T2_clicked"].append(t)
            elif v["impr"] >= 2:
                tiers["T3_impressed"].append(t)
            else:
                tiers["T4_tail"].append(t)

        tier_safe = {}
        for name, tl in tiers.items():
            keep = []
            for t in tl:
                ok, why = is_safe(t, "EXACT")
                if ok:
                    keep.append(t)
                else:
                    rejected.append({"text": t, "reason": why})
            tier_safe[name] = keep

        def build(tier_names):
            cands = [{"text": " ".join(toks(r["text"])), "match_type": "PHRASE",
                      "category": r["category"], "evidence_hits": r["corpus_hits"],
                      "tier": "ROOT"} for r in roots]
            for name in tier_names:
                for t in tier_safe[name]:
                    cands.append({"text": " ".join(toks(t)), "match_type": "EXACT",
                                  "category": neg_terms[t]["category"],
                                  "evidence_hits": 1, "tier": name})
            seen, uni = set(), []
            for c in cands:
                k = (c["text"], c["match_type"])
                if k not in seen:
                    seen.add(k)
                    uni.append(c)
            cost = sum(v["cost"] for t, v in neg_terms.items()
                       if any(blocks(toks(c["text"]), c["match_type"], toks(t)) for c in uni))
            return uni, cost

        core, core_cost = build(("T1_spent", "T2_clicked"))
        hardened, hard_cost = build(("T1_spent", "T2_clicked", "T3_impressed"))
        universe, blocked_cost = core, core_cost

        # =====================================================================
        # Placement
        # =====================================================================
        layer_a, a_objs, a_red = [], 0, 0
        for cid, c in live_c.items():
            ex = campaign_existing(cid)
            negs = [n for n in universe if not redundant(n["text"], n["match_type"], ex)]
            a_red += len(universe) - len(negs)
            a_objs += len(negs)
            layer_a.append({"campaign_id": cid, "campaign_name": c["name"],
                            "negatives": negs})

        layer_b, b_objs, b_red = [], 0, 0
        for agid, a in live_ag.items():
            ex = adgroup_existing(agid)
            negs = [n for n in universe if not redundant(n["text"], n["match_type"], ex)]
            b_red += len(universe) - len(negs)
            b_objs += len(negs)
            layer_b.append({"ad_group_id": agid, "ad_group_name": a["name"],
                            "campaign_id": a["campaign_id"],
                            "campaign_name": a["campaign_name"], "negatives": negs})

        # =====================================================================
        # LAYER X - evidence-backed cross-negatives between sibling ad groups
        # =====================================================================
        theme = {}
        for agid, a in live_ag.items():
            ts = [p["text"].lower() for p in d["positive_keywords"]
                  if p["ad_group_id"] == agid]
            if not ts:
                continue
            theme_counter = Counter()
            for t in ts:
                tk = [x for x in toks(t) if x not in ("near", "me", "you", "in", "the", "a")]
                if 1 <= len(tk) <= 4:
                    theme_counter[" ".join(tk)] += 1
            if theme_counter:
                theme[agid] = theme_counter.most_common(1)[0][0]

        st_by_ag = defaultdict(set)
        for t in d["search_terms"]:
            if t["ad_group_id"] in live_ag:
                st_by_ag[t["ad_group_id"]].add(t["term"])

        layer_x, x_objs = [], 0
        for agid, a in live_ag.items():
            own = theme.get(agid)
            own_tok = toks(own) if own else []
            sibs = [(oid, th) for oid, th in theme.items()
                    if oid != agid and live_ag[oid]["campaign_id"] == a["campaign_id"]]
            props = []
            for oid, th in sibs:
                tht = toks(th)
                if own_tok and contiguous(tht, own_tok):
                    continue
                if contiguous(own_tok, tht):
                    continue
                hits = [q for q in st_by_ag.get(agid, ()) if contiguous(tht, toks(q))]
                if not hits:
                    continue
                ok, why = is_safe(th, "PHRASE")
                if not ok and why != "blocks_keep_or_watch":
                    continue
                if any(blocks(tht, "PHRASE", pt) for k, pt in live_pos.items()
                       if k in {p["text"].lower() for p in d["positive_keywords"]
                                if p["ad_group_id"] == agid}):
                    continue
                if redundant(th, "PHRASE", adgroup_existing(agid)):
                    continue
                props.append({"text": " ".join(tht), "match_type": "PHRASE",
                              "category": "CROSS_NEGATIVE_STEER",
                              "steers_to_ad_group": live_ag[oid]["name"],
                              "observed_leak_terms": len(hits)})
            if props:
                layer_x.append({"ad_group_id": agid, "ad_group_name": a["name"],
                                "campaign_name": a["campaign_name"], "negatives": props})
                x_objs += len(props)

        # =====================================================================
        # Report
        # =====================================================================
        print("=" * 84)
        print("{}  {}  ({})".format(slug, d["account_name"], cfg["customer_id"]))
        print("=" * 84)
        print("live campaigns={}  live ad groups={}".format(len(live_c), len(live_ag)))
        print("\nHOW THE 'Excluded' LABEL IS SET on this account's live ad groups:")
        print("  EXCLUDED search-term rows observed      : {}".format(len(excl_rows)))
        print("    set by an AD GROUP negative           : {}".format(by_ag))
        print("    set by a CAMPAIGN negative only       : {}".format(by_c_only))
        print("    set by a linked SHARED LIST only      : {}".format(by_list_only))
        print("    unexplained (account-level list)      : {}".format(by_none))

        print("\nNEGATIVE-VERDICT TERMS: {}   wasted spend ${:,.2f}".format(
            len(neg_terms), neg_cost_total))
        print("  safe PHRASE roots             : {}".format(len(roots)))
        print("  waste blocked by roots alone  : ${:,.2f} ({:.1f}%) over {} terms".format(
            cov_cost, 100 * cov_cost / neg_cost_total if neg_cost_total else 0, cov_n))
        print("  residual negative terms       : {}".format(len(residual)))
        for name in ("T1_spent", "T2_clicked", "T3_impressed", "T4_tail"):
            c = sum(residual[t]["cost"] for t in tiers[name])
            print("    {:<14} terms={:<5} cost=${:>10,.2f}  safe EXACTs {}".format(
                name, len(tiers[name]), c, len(tier_safe[name])))
        print("  candidates rejected by safety : {}".format(len(rejected)))
        for reason, n in Counter(r["reason"] for r in rejected).most_common():
            print("      {:<26} {}".format(reason, n))

        print("\n  SET CORE     (roots + terms that actually spent) : {:>5} objects "
              "blocks ${:,.2f} ({:.1f}%)".format(
                  len(core), core_cost,
                  100 * core_cost / neg_cost_total if neg_cost_total else 0))
        print("  SET HARDENED (core + impressed-but-never-clicked): {:>5} objects "
              "blocks ${:,.2f} ({:.1f}%)".format(
                  len(hardened), hard_cost,
                  100 * hard_cost / neg_cost_total if neg_cost_total else 0))
        print("  -> hardening adds {} objects for ${:,.2f} extra blocked spend".format(
            len(hardened) - len(core), hard_cost - core_cost))
        print("  CORE by category:")
        for cat, n in Counter(c["category"] for c in core).most_common():
            print("      {:<34} {}".format(cat, n))

        print("\n  PLACEMENT (after per-scope redundancy elimination)")
        print("    LAYER A campaign-level : {:>6} new objects across {} campaigns "
              "({} already covered)".format(a_objs, len(live_c), a_red))
        print("    LAYER B ad-group-level : {:>6} new objects across {} ad groups "
              "({} already covered)".format(b_objs, len(live_ag), b_red))
        print("    LAYER X cross-negatives: {:>6} new objects across {} ad groups".format(
            x_objs, len(layer_x)))
        print("    B/A multiplication     : {:.1f}x".format(
            b_objs / a_objs if a_objs else 0))

        plan = {
            "slug": slug, "customer_id": cfg["customer_id"],
            "account_name": d["account_name"],
            "negative_universe_core": core,
            "negative_universe_hardened_extra": [c for c in hardened if c not in core],
            "layer_a_campaign_level": layer_a,
            "layer_b_ad_group_level": layer_b,
            "layer_x_cross_negatives": layer_x,
            "counts": {"universe_core": len(core), "universe_hardened": len(hardened),
                       "layer_a_objects": a_objs,
                       "layer_b_objects": b_objs, "layer_x_objects": x_objs,
                       "live_campaigns": len(live_c), "live_ad_groups": len(live_ag)},
            "coverage": {"negative_terms": len(neg_terms),
                         "wasted_spend_usd": round(neg_cost_total, 2),
                         "spend_blocked_usd": round(blocked_cost, 2),
                         "roots": len(roots),
                         "tiers": {k: len(v) for k, v in tiers.items()},
                         "rejected": len(rejected)},
            "excluded_label_evidence": {
                "excluded_rows": len(excl_rows), "by_ad_group_negative": by_ag,
                "by_campaign_negative_only": by_c_only,
                "by_shared_list_only": by_list_only, "unexplained": by_none},
        }
        p = OUT / (slug + "-negative-plan.json")
        p.write_text(json.dumps(plan, indent=2), encoding="utf-8")
        print("    plan -> {}\n".format(p.relative_to(ROOT)))
        grand[slug] = plan["counts"] | plan["coverage"] | plan["excluded_label_evidence"]

    (OUT / "portfolio-summary.json").write_text(json.dumps(grand, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
