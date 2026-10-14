#!/usr/bin/env python3
"""Read-only field discovery via GoogleAdsFieldService."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client

def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsFieldService")
    for pat in sys.argv[1:]:
        q = f"SELECT name, category, selectable, filterable, sortable, data_type WHERE name LIKE '{pat}'"
        print(f"=== {pat} ===")
        try:
            for r in svc.search_google_ads_fields(query=q):
                print(f"  {r.name:70s} sel={r.selectable} type={r.data_type.name}")
        except Exception as exc:
            print("  ERR", str(exc)[:300])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
