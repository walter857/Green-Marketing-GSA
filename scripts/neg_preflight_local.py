#!/usr/bin/env python3
"""Local preflight. Catches everything that would waste API quota tomorrow.

Checks, per approved layer, per campaign:
  * negative keyword text rules (<=10 words, <=80 chars, no invalid characters)
  * exact duplicates inside the batch
  * duplicates against negatives ALREADY on that campaign (same text+match type)
  * BROAD name negatives that would block a live positive keyword

Rewrites the bundle with any duplicate dropped, so execution is clean.
No API calls.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.safety import approval_code  # noqa: E402

CORPUS = ROOT / "reports" / "st-corpus"
BUNDLES = {
    "ambient-cooling-heating": "clients/ambient-cooling-heating/plans/2026-08-28-negative-expansion.json",
    "pro-green-austin": "clients/pro-green-austin/plans/2026-08-28-negative-expansion.json",
    "softwind-power-washing": "clients/softwind-power-washing/plans/2026-08-28-negative-expansion.json",
    # SLM was quota-blocked on 08-28 and has no bundle from that date. Its
    # corpus, geo gate and plan were built 2026-08-30. The three paths above
    # stay pinned to 08-28 so they keep describing what was actually executed.
    "softwind-landscape-masonry": "clients/softwind-landscape-masonry/plans/2026-08-30-negative-expansion.json",
}
CAMPAIGN_LAYERS = ["NEG_CAMPAIGN_LEVEL", "NEG_NAME_BROAD",
                   "NEG_CROSS_ACCOUNT_FENCE"]
INVALID = set('!@%^*()=[]{};~`<>?\\|"')
TOKEN_RE = re.compile(r"[a-z0-9']+")


def toks(s):
    return TOKEN_RE.findall(s.lower())


def contiguous(sub, seq):
    n = len(sub)
    if not n or n > len(seq):
        return False
    return any(seq[i:i + n] == sub for i in range(len(seq) - n + 1))


def blocks(nt, mt, q):
    if not nt:
        return False
    if mt == "EXACT":
        return nt == q
    if mt == "PHRASE":
        return contiguous(nt, q)
    if mt == "BROAD":
        return all(t in q for t in nt)
    return False


def main() -> int:
    problems = 0
    for slug, rel in BUNDLES.items():
        bpath = ROOT / rel
        bundle = json.loads(bpath.read_text(encoding="utf-8"))
        d = json.loads((CORPUS / (slug + "-corpus.json")).read_text(encoding="utf-8"))
        cid = bundle["target"]["child_customer_id"]

        live_c = {c["id"] for c in d["campaigns"] if c["status"] == "ENABLED"}
        live_ag = {a["id"] for a in d["ad_groups"]
                   if a["status"] == "ENABLED" and a["campaign_id"] in live_c}
        pos_by_campaign = defaultdict(list)
        for p in d["positive_keywords"]:
            if p["ad_group_id"] in live_ag:
                pos_by_campaign[p["campaign_id"]].append(toks(p["text"]))

        existing = defaultdict(set)          # campaign_id -> {(text, match_type)}
        for n in d["campaign_negatives"]:
            if n["campaign_id"] in live_c:
                existing[n["campaign_id"]].add(
                    (" ".join(toks(n["text"])), n["match_type"]))

        print("=" * 78)
        print("{}  {}  ({})".format(slug, bundle["target"]["exact_child_account_name"], cid))
        print("=" * 78)

        changed = False
        for key in CAMPAIGN_LAYERS:
            sub = bundle["subplans"].get(key)
            if not sub or not sub["object_count"]:
                continue
            bad_text, dupes_in_batch, dupes_existing, blocks_pos = 0, 0, 0, 0
            for block in sub["detail"]:
                camp = block["campaign_id"]
                seen = set()
                keep = []
                for n in block["negatives"]:
                    text = " ".join(toks(n["text"]))
                    mt = n["match_type"]
                    tk = toks(text)
                    if not tk or len(tk) > 10 or len(text) > 80 or (set(text) & INVALID):
                        bad_text += 1
                        continue
                    if (text, mt) in seen:
                        dupes_in_batch += 1
                        continue
                    if (text, mt) in existing.get(camp, set()):
                        dupes_existing += 1
                        continue
                    if mt == "BROAD" and any(
                            blocks(tk, mt, pk) for pk in pos_by_campaign.get(camp, [])):
                        blocks_pos += 1
                        continue
                    seen.add((text, mt))
                    keep.append(dict(n, text=text))
                if len(keep) != len(block["negatives"]):
                    changed = True
                block["negatives"] = keep

            objects = sum(len(b["negatives"]) for b in sub["detail"])
            dropped = sub["object_count"] - objects
            sub["object_count"] = objects
            sub["summary"]["object_count"] = objects
            sub["summary"]["match_types"] = dict(Counter(
                n["match_type"] for b in sub["detail"] for n in b["negatives"]))
            sub["summary"]["categories"] = dict(Counter(
                n["category"] for b in sub["detail"] for n in b["negatives"]))
            sub["fingerprint"] = approval_code(sub["summary"]) if objects else ""

            print("  {:<20} objects={:<6} dropped={:<4} "
                  "(bad_text={} dup_in_batch={} already_live={} blocks_keyword={})".format(
                      key, objects, dropped, bad_text, dupes_in_batch,
                      dupes_existing, blocks_pos))
            print("      fingerprint {}".format(sub["fingerprint"]))
            problems += bad_text

        if changed:
            master = approval_code({
                "target": bundle["target"],
                "subplans": {k: v["summary"] for k, v in bundle["subplans"].items()}})
            bundle["master_fingerprint"] = master
            bundle["preflight"] = {
                "ran": "local, no API", "note":
                "duplicates and rule-breaking rows removed; fingerprints reissued"}
            bpath.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
            print("  MASTER {}   bundle rewritten".format(master))
        else:
            print("  MASTER {}   unchanged".format(bundle["master_fingerprint"]))
        total = sum(bundle["subplans"][k]["object_count"] for k in CAMPAIGN_LAYERS
                    if k in bundle["subplans"])
        print("  campaign-level operations for this account: {}\n".format(total))

    print("rule violations remaining: {}".format(problems))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
