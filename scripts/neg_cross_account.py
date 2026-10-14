#!/usr/bin/env python3
"""Cross-account scope fence between the two Softwind accounts.

Owner instruction 2026-08-28: same company, two child accounts, deliberately
non-overlapping service scope.

    Softwind Power Washing      1521725229  -> exterior CLEANING intent
    Softwind Landscape & Masonry 2429758629 -> BUILD / INSTALL / SEAL / MASONRY

Each account gets campaign-level PHRASE negatives for the other's services. This
is a scope boundary, so it is applied preventively rather than waiting for waste.

The hard part is that both accounts legitimately use the same nouns. "patio
cleaning" is Power Washing; "patio installation" is Landscape & Masonry. So the
fence is built from intent-qualified PHRASES, never from bare nouns, and every
candidate is tested against the account's own live keywords and KEEP terms.

Local only. No API calls. The Landscape & Masonry side is emitted as a prepared
set to apply once its corpus has been pulled and its identity gate passed.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.safety import approval_code  # noqa: E402

CORPUS = ROOT / "reports" / "st-corpus"
VERD = ROOT / "reports" / "st-verdicts"
OUT = ROOT / "reports" / "st-cross-account"

TOKEN_RE = re.compile(r"[a-z0-9']+")

# --- what Power Washing (1521725229) must NOT absorb ------------------------
# Build / install / seal / masonry / landscape intent -> belongs to 2429758629.
PW_BLOCKS = [
    # paver sealing - explicitly excluded on PW and reconfirmed by the owner
    "paver sealing", "paver seal", "sealing pavers", "seal pavers",
    "paver sealer", "sealing paver patio", "patio sealing", "concrete sealing",
    "sealcoating", "seal coating",
    # paver + patio construction
    "paver installation", "paver installer", "install pavers", "pavers installation",
    "paver contractor", "paver patio installation", "paver patio cost",
    "patio installation", "patio installer", "install patio", "patio contractor",
    "patio builder", "build a patio", "new patio", "patio construction",
    "patio design", "paver design", "brick patio installation",
    # wider hardscape
    "hardscape", "hardscaping", "retaining wall", "retaining walls",
    "walkway installation", "driveway installation", "driveway pavers",
    "paver driveway", "paver walkway", "stamped concrete", "concrete patio installation",
    "outdoor kitchen", "fire pit", "firepit", "pergola", "outdoor living",
    "pool deck installation", "stone patio", "flagstone patio",
    # masonry
    "masonry", "mason contractor", "brick work", "brickwork", "brick repair",
    "brick pointing", "repointing", "stone work", "stonework", "chimney repair",
    "block wall", "stucco",
    # landscape
    "landscaping", "landscaper", "landscape design", "landscape installation",
    "landscape contractor", "lawn care", "lawn mowing", "lawn service",
    "sod installation", "mulch delivery", "tree service", "garden design",
    "irrigation installation", "sprinkler installation", "grading", "excavation",
    "drainage installation", "artificial turf",
]

# --- what Landscape & Masonry (2429758629) must NOT absorb ------------------
# Exterior cleaning intent -> belongs to 1521725229.
LM_BLOCKS = [
    "power washing", "power wash", "powerwashing", "powerwash", "power washer",
    "pressure washing", "pressure wash", "pressurewashing", "pressure washer",
    "soft washing", "soft wash", "softwash", "softwashing",
    "house washing", "house wash", "wash my house", "home washing",
    "siding cleaning", "siding washing", "vinyl siding cleaning",
    "roof cleaning", "roof washing", "roof wash", "shingle cleaning",
    "gutter cleaning", "gutter cleaner", "gutter whitening",
    "window cleaning", "window washing",
    "deck cleaning", "deck washing", "fence cleaning", "fence washing",
    "driveway cleaning", "driveway washing", "concrete cleaning",
    "patio cleaning", "patio washing", "paver cleaning", "paver washing",
    "walkway cleaning", "sidewalk cleaning",
    "exterior cleaning", "exterior washing", "house exterior cleaning",
    "mildew removal", "algae removal", "moss removal", "rust removal",
    "oil stain removal", "graffiti removal", "dumpster pad cleaning",
]

ACCOUNTS = {
    "softwind-power-washing": {
        "customer_id": "1521725229",
        "name": "Softwind Power Washing - Live",
        "blocks": PW_BLOCKS,
        "reason": "hardscape / masonry / landscape build intent belongs to 2429758629",
        "corpus_available": True,
    },
    "softwind-landscape-masonry": {
        "customer_id": "2429758629",
        "name": "Softwind Landscape & Masonry - Live",
        "blocks": LM_BLOCKS,
        "reason": "exterior cleaning intent belongs to 1521725229",
    },
}

# corpus_available was hardcoded, so it went stale the moment a corpus was
# pulled and the fence stayed "PREPARED" with an unknown campaign count.
# Derive it from what is actually on disk instead.
for _slug, _cfg in ACCOUNTS.items():
    _cfg["corpus_available"] = (
        (CORPUS / (_slug + "-corpus.json")).exists()
        and (VERD / (_slug + "-verdicts.csv")).exists())


def toks(s):
    return TOKEN_RE.findall(s.lower())


def contiguous(sub, seq):
    n = len(sub)
    if not n or n > len(seq):
        return False
    return any(seq[i:i + n] == sub for i in range(len(seq) - n + 1))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    result = {}

    for slug, cfg in ACCOUNTS.items():
        print("=" * 78)
        print("{}  ({})".format(cfg["name"], cfg["customer_id"]))
        print("=" * 78)

        accepted, held = [], []

        if cfg["corpus_available"]:
            d = json.loads((CORPUS / (slug + "-corpus.json")).read_text(encoding="utf-8"))
            live_c = {c["id"]: c for c in d["campaigns"] if c["status"] == "ENABLED"}
            live_ag = {a["id"] for a in d["ad_groups"]
                       if a["status"] == "ENABLED" and a["campaign_id"] in live_c}
            own_kw = [toks(p["text"]) for p in d["positive_keywords"]
                      if p["ad_group_id"] in live_ag]
            keep_terms = []
            with (VERD / (slug + "-verdicts.csv")).open(encoding="utf-8") as fh:
                for r in csv.DictReader(fh):
                    if r["verdict"] == "KEEP" or float(r["conversions"]) > 0:
                        keep_terms.append(toks(r["search_term"]))
            existing = {(" ".join(toks(n["text"])), n["match_type"])
                        for n in d["campaign_negatives"] if n["campaign_id"] in live_c}
        else:
            live_c, own_kw, keep_terms, existing = {}, [], [], set()

        for phrase in cfg["blocks"]:
            tk = toks(phrase)
            text = " ".join(tk)
            if len(tk) > 10 or len(text) > 80:
                held.append({"text": text, "reason": "over_length"})
                continue
            hit_kw = next((k for k in own_kw if contiguous(tk, k)), None)
            if hit_kw:
                held.append({"text": text, "reason": "blocks_own_live_keyword"})
                continue
            if any(contiguous(tk, t) for t in keep_terms):
                held.append({"text": text, "reason": "blocks_own_KEEP_or_converting_term"})
                continue
            if (text, "PHRASE") in existing:
                held.append({"text": text, "reason": "already_live_on_this_account"})
                continue
            accepted.append({"text": text, "match_type": "PHRASE",
                             "category": "CROSS_ACCOUNT_SCOPE_FENCE"})

        per_campaign = len(accepted)
        objects = per_campaign * len(live_c) if live_c else None

        payload = {
            "slug": slug, "customer_id": cfg["customer_id"],
            "account_name": cfg["name"],
            "fence_reason": cfg["reason"],
            "owner_instruction": "2026-08-28 mutual exclusion between the two "
                                 "Softwind accounts",
            "match_type": "PHRASE",
            "placement": "campaign level",
            "negatives": accepted,
            "held_back": held,
            "per_campaign_objects": per_campaign,
            "live_campaigns": len(live_c) if live_c else None,
            "total_objects": objects,
            "status": "READY" if cfg["corpus_available"]
                      else "PREPARED - apply after identity gate + corpus pull",
        }
        payload["fingerprint"] = approval_code({
            "customer_id": cfg["customer_id"], "subplan": "NEG_CROSS_ACCOUNT_FENCE",
            "negatives": accepted, "per_campaign": per_campaign})

        p = OUT / (slug + "-scope-fence.json")
        p.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        print("  fence blocks : {}".format(cfg["reason"]))
        print("  candidates   : {}".format(len(cfg["blocks"])))
        print("  accepted     : {} PHRASE negatives".format(len(accepted)))
        print("  held back    : {}".format(len(held)))
        for h in held:
            print("      {:<34} {}".format(h["text"][:34], h["reason"]))
        if objects is not None:
            print("  objects      : {} x {} campaigns = {}".format(
                per_campaign, len(live_c), objects))
        else:
            print("  objects      : {} per campaign, campaign count UNKNOWN "
                  "until the corpus pull".format(per_campaign))
        print("  status       : {}".format(payload["status"]))
        print("  fingerprint  : {}".format(payload["fingerprint"]))
        print("  file -> {}\n".format(p.relative_to(ROOT)))
        result[slug] = {"accepted": len(accepted), "held": len(held),
                        "objects": objects, "fingerprint": payload["fingerprint"]}

    (OUT / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
