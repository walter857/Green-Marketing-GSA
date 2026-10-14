#!/usr/bin/env python3
"""Fetch public reference vocabularies used to tell a NAME from an English word.

These are generic public datasets, not client data. They are cached to disk and
used only as local filters. Nothing here touches Google Ads.
"""
from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "lexicons"

SOURCES = {
    "english_words": [
        "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt",
    ],
    "first_names": [
        "https://raw.githubusercontent.com/dominictarr/random-name/master/first-names.txt",
    ],
    "surnames_github": [
        "https://raw.githubusercontent.com/dominictarr/random-name/master/names.txt",
    ],
    "surnames_census": [
        "https://www2.census.gov/topics/genealogy/2010surnames/names.zip",
    ],
}
UA = {"User-Agent": "green-marketing-gsa/1.0 (negative-keyword lexicon build)"}


def get(url, timeout=90):
    r = requests.get(url, headers=UA, timeout=timeout)
    r.raise_for_status()
    return r


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}

    # --- plain text lists -------------------------------------------------
    for key in ("english_words", "first_names", "surnames_github"):
        words = set()
        for url in SOURCES[key]:
            try:
                txt = get(url).text
                words |= {w.strip().lower() for w in txt.splitlines() if w.strip()}
                print("[{}] {} -> {} lines".format(key, url.rsplit("/", 1)[-1], len(words)))
            except Exception as exc:  # noqa: BLE001
                print("[{}] FAILED {} : {}".format(key, url, type(exc).__name__))
        if words:
            (OUT / (key + ".txt")).write_text("\n".join(sorted(words)), encoding="utf-8")
        report[key] = len(words)

    # --- census surnames zip ---------------------------------------------
    census = {}
    for url in SOURCES["surnames_census"]:
        try:
            raw = get(url, timeout=180).content
            zf = zipfile.ZipFile(io.BytesIO(raw))
            name = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
            lines = zf.read(name).decode("utf-8", "replace").splitlines()
            header = lines[0].split(",")
            i_name = header.index("name")
            i_rank = header.index("rank")
            for line in lines[1:]:
                parts = line.split(",")
                if len(parts) <= max(i_name, i_rank):
                    continue
                nm = parts[i_name].strip().lower()
                try:
                    rk = int(parts[i_rank])
                except ValueError:
                    continue
                if nm and nm != "all other names":
                    census[nm] = rk
            print("[surnames_census] {} -> {} surnames with rank".format(name, len(census)))
        except Exception as exc:  # noqa: BLE001
            print("[surnames_census] FAILED {} : {}".format(url, type(exc).__name__))
    if census:
        (OUT / "surnames_census.json").write_text(json.dumps(census), encoding="utf-8")
    report["surnames_census"] = len(census)

    (OUT / "fetch-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nsummary:", json.dumps(report))
    return 0 if report.get("english_words") and (
        report.get("surnames_census") or report.get("surnames_github")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
