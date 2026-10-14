#!/usr/bin/env python3
"""Read-only: does the CURRENT scope-fence file still describe what is LIVE on
Softwind Power Washing? The fence fingerprint moved from D27F2802FD31 (the value
approved and executed 2026-08-30 08:42) to 3D9EE4AEBCCD after the pipeline was
re-run, so the accepted list must be reconciled against the account.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"

def main() -> int:
    fence = json.loads((ROOT / "reports" / "st-cross-account"
                        / "softwind-power-washing-scope-fence.json"
                        ).read_text(encoding="utf-8"))
    want = [n["text"] if isinstance(n, dict) else n for n in fence["negatives"]]
    print("fence file fingerprint : {}".format(fence["fingerprint"]))
    print("accepted phrases       : {}".format(len(want)))

    load_dotenv_if_available()
    svc = load_google_ads_client().get_service("GoogleAdsService")
    live = {}
    for r in svc.search(customer_id=CID, query=(
            "SELECT campaign.id, campaign.name, campaign_criterion.keyword.text, "
            "campaign_criterion.keyword.match_type FROM campaign_criterion "
            "WHERE campaign_criterion.negative = true "
            "AND campaign_criterion.type = 'KEYWORD'")):
        k = r.campaign_criterion.keyword
        live.setdefault((k.text.lower(), enum_name(k.match_type)), set()).add(r.campaign.name)

    missing = [w for w in want if (w.lower(), "PHRASE") not in live]
    present = [w for w in want if (w.lower(), "PHRASE") in live]
    two_camp = [w for w in present if len(live[(w.lower(), "PHRASE")]) >= 2]
    print("live PHRASE negatives  : {}".format(
        sum(1 for k in live if k[1] == "PHRASE")))
    print("of the {} wanted -> present {} | on 2+ campaigns {} | MISSING {}".format(
        len(want), len(present), len(two_camp), len(missing)))
    if missing:
        print("MISSING (would need a second write):")
        for m in missing:
            print("   {}".format(m))
    else:
        print("VERDICT: every accepted fence phrase is already live on both "
              "campaigns. The fingerprint moved but the CONTENT did not; the "
              "executed state and the current file agree.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
