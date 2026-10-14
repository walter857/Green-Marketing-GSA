#!/usr/bin/env python3
"""Classify the all-time search-term corpus and mine safe negative roots.

Everything term-level is written to disk. Only aggregates print to stdout.

Safety invariants enforced here, not later:
  * a candidate negative may never block a KEEP term
  * a candidate negative may never block a term that produced a conversion
  * a candidate negative may never equal a Green Marketing PROTECTED phrase
  * a candidate negative may never block a live positive keyword
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

from neg_lexicon import ACCOUNTS, PROTECTED, classify, compile_account  # noqa: E402

CORPUS = ROOT / "reports" / "st-corpus"
OUT = ROOT / "reports" / "st-verdicts"

TOKEN_RE = re.compile(r"[a-z0-9']+")
STOP = {"a", "an", "the", "in", "on", "of", "for", "to", "and", "or", "my", "me",
        "is", "it", "at", "by", "with", "near", "you", "i", "do", "does", "can"}


def toks(s: str) -> list[str]:
    return TOKEN_RE.findall(s.lower())


def contiguous(sub: list[str], seq: list[str]) -> bool:
    n = len(sub)
    if not n or n > len(seq):
        return False
    return any(seq[i:i + n] == sub for i in range(len(seq) - n + 1))


def blocks(neg_tokens: list[str], match_type: str, query_tokens: list[str]) -> bool:
    if match_type == "EXACT":
        return neg_tokens == query_tokens
    if match_type == "PHRASE":
        return contiguous(neg_tokens, query_tokens)
    return all(t in query_tokens for t in neg_tokens)  # BROAD


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {}

    for slug, cfg in ACCOUNTS.items():
        corpus_path = CORPUS / (slug + "-corpus.json")
        if not corpus_path.exists():
            print("[{}] SKIP: no corpus on disk yet".format(slug))
            continue
        try:
            comp = compile_account(cfg)
        except ValueError as exc:
            print("[{}] SKIP: {}".format(slug, exc))
            continue
        d = json.loads(corpus_path.read_text(encoding="utf-8"))

        live_c = {c["id"] for c in d["campaigns"] if c["status"] == "ENABLED"}
        live_ag = {a["id"]: a for a in d["ad_groups"]
                   if a["status"] == "ENABLED" and a["campaign_id"] in live_c}

        # ---- roll the corpus up to one row per unique term -------------------
        agg = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0,
                                   "value": 0.0, "live_rows": 0, "all_rows": 0,
                                   "live_ags": set(), "statuses": set()})
        for t in d["search_terms"]:
            a = agg[t["term"]]
            a["impr"] += t["impressions"]
            a["clicks"] += t["clicks"]
            a["cost"] += t["cost"]
            a["conv"] += t["conversions"]
            a["value"] += t["conv_value"]
            a["all_rows"] += 1
            a["statuses"].add(t["st_status"])
            if t["ad_group_id"] in live_ag:
                a["live_rows"] += 1
                a["live_ags"].add(t["ad_group_id"])

        # ---- classify --------------------------------------------------------
        verdicts = {}
        for term, a in agg.items():
            v, cat = classify(term, comp)
            # conversion guard overrides everything
            if a["conv"] > 0 and v == "NEGATIVE":
                v, cat = "KEEP", "CONVERSION_GUARD_OVERRIDE"
            verdicts[term] = (v, cat)

        keep_terms = {t for t, (v, _) in verdicts.items() if v == "KEEP"}
        watch_terms = {t for t, (v, _) in verdicts.items() if v == "WATCH"}
        neg_terms = {t for t, (v, _) in verdicts.items() if v == "NEGATIVE"}
        conv_terms = {t for t, a in agg.items() if a["conv"] > 0}

        # protected set: never blockable
        protected_tok = [toks(p) for p in PROTECTED]
        # live positive keywords must never be blocked
        live_pos = {p["text"].lower() for p in d["positive_keywords"]
                    if p["ad_group_id"] in live_ag}

        keep_tok = {t: toks(t) for t in keep_terms | watch_terms}
        conv_tok = {t: toks(t) for t in conv_terms}
        pos_tok = {p: toks(p) for p in live_pos}

        def is_safe(neg_text: str) -> tuple[bool, str]:
            nt = toks(neg_text)
            if not nt:
                return False, "empty"
            if len(nt) > 10:
                return False, "over_10_words"
            if len(neg_text) > 80:
                return False, "over_80_chars"
            if neg_text.strip().lower() in PROTECTED:
                return False, "protected_phrase"
            for pt in protected_tok:
                if nt == pt:
                    return False, "protected_phrase"
            for t, tt in keep_tok.items():
                if blocks(nt, "PHRASE", tt):
                    return False, "blocks_keep_or_watch"
            for t, tt in conv_tok.items():
                if blocks(nt, "PHRASE", tt):
                    return False, "blocks_converting_term"
            for p, pt in pos_tok.items():
                if blocks(nt, "PHRASE", pt):
                    return False, "blocks_live_keyword"
            return True, "ok"

        # ---- mine candidate roots -------------------------------------------
        # (a) the literal span each disqualifier actually matched in the query
        span_counter = Counter()
        span_cat = {}
        for term in neg_terms:
            tl = " " + term.lower().strip() + " "
            hit = None
            cat = verdicts[term][1]
            for name, rx in list(comp["disqualify"].items()) + list(comp["shared"].items()):
                m = rx.search(tl)
                if m:
                    hit = m.group(0).strip()
                    cat = name
                    break
            if hit is None and comp["geo_out"].search(tl):
                m = comp["geo_out"].search(tl)
                hit = m.group(0).strip()
                cat = "GEO_OUT_OF_AREA"
            if hit:
                span_counter[hit] += 1
                span_cat[hit] = cat

        # (b) tokens / bigrams that appear ONLY in out-of-scope terms
        oos = [t for t in neg_terms
               if verdicts[t][1] == "OUT_OF_SCOPE_NO_CORE_SERVICE"]
        safe_vocab = set()
        for t in keep_terms | watch_terms:
            safe_vocab.update(toks(t))
        for p in live_pos:
            safe_vocab.update(toks(p))
        gram_counter = Counter()
        for t in oos:
            tt = [x for x in toks(t) if x not in STOP]
            for x in tt:
                if x not in safe_vocab and len(x) > 2:
                    gram_counter[x] += 1
            for i in range(len(tt) - 1):
                bg = tt[i] + " " + tt[i + 1]
                if not (set(tt[i:i + 2]) & safe_vocab):
                    gram_counter[bg] += 1

        candidates = []
        for span, n in span_counter.items():
            candidates.append((span, n, span_cat[span], "matched_span"))
        for gram, n in gram_counter.items():
            if n >= 2:
                candidates.append((gram, n, "OUT_OF_SCOPE_NO_CORE_SERVICE", "mined_gram"))

        roots, rejected = [], []
        seen = set()
        for text, n, cat, src in sorted(candidates, key=lambda x: (-x[1], x[0])):
            key = " ".join(toks(text))
            if not key or key in seen:
                continue
            ok, why = is_safe(key)
            if ok:
                # skip if an already-accepted shorter root subsumes it
                if any(contiguous(toks(r["text"]), toks(key)) for r in roots):
                    continue
                seen.add(key)
                roots.append({"text": key, "match_type": "PHRASE", "category": cat,
                              "source": src, "corpus_hits": n})
            else:
                rejected.append({"text": key, "category": cat, "reason": why,
                                 "corpus_hits": n})

        # ---- residual: negative terms no root covers -> EXACT ----------------
        root_tok = [(toks(r["text"]), r) for r in roots]
        covered, residual = set(), []
        for term in neg_terms:
            tt = toks(term)
            if any(contiguous(rt, tt) for rt, _ in root_tok):
                covered.add(term)
            else:
                residual.append(term)

        exacts = []
        for term in residual:
            ok, why = is_safe(term)
            if ok:
                exacts.append({"text": " ".join(toks(term)), "match_type": "EXACT",
                               "category": verdicts[term][1], "source": "residual_exact",
                               "corpus_hits": 1})
            else:
                rejected.append({"text": term, "category": verdicts[term][1],
                                 "reason": why, "corpus_hits": 1})

        # ---- write term-level verdict table ---------------------------------
        vpath = OUT / (slug + "-verdicts.csv")
        with vpath.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["search_term", "verdict", "category", "impressions", "clicks",
                        "cost_usd", "conversions", "conv_value", "rows_all",
                        "rows_on_live_ad_groups", "live_ad_group_ids", "st_status"])
            for term, a in sorted(agg.items(), key=lambda x: -x[1]["cost"]):
                v, cat = verdicts[term]
                w.writerow([term, v, cat, a["impr"], a["clicks"], round(a["cost"], 2),
                            round(a["conv"], 2), round(a["value"], 2), a["all_rows"],
                            a["live_rows"], "|".join(sorted(a["live_ags"])),
                            "|".join(sorted(a["statuses"]))])

        npath = OUT / (slug + "-negative-roots.json")
        npath.write_text(json.dumps({
            "slug": slug, "customer_id": cfg["customer_id"],
            "roots": roots, "exacts": exacts, "rejected": rejected,
        }, indent=2), encoding="utf-8")

        # ---- aggregates ------------------------------------------------------
        by_cat = defaultdict(lambda: [0, 0, 0.0, 0.0])
        for term, a in agg.items():
            v, cat = verdicts[term]
            b = by_cat[(v, cat)]
            b[0] += 1
            b[1] += a["clicks"]
            b[2] += a["cost"]
            b[3] += a["conv"]

        print("=" * 84)
        print("{}  {}  ({})".format(slug, d["account_name"], cfg["customer_id"]))
        print("=" * 84)
        print("unique terms all-time: {}   total cost ${:,.2f}   conversions {:.2f}".format(
            len(agg), sum(a["cost"] for a in agg.values()),
            sum(a["conv"] for a in agg.values())))
        print("\n  VERDICT / CATEGORY                          terms  clicks       cost   conv")
        for (v, cat), b in sorted(by_cat.items(), key=lambda x: (x[0][0], -x[1][2])):
            print("  {:<8} {:<34} {:>5} {:>7} ${:>9,.2f} {:>6.2f}".format(
                v, cat[:34], b[0], b[1], b[2], b[3]))
        tot_neg_cost = sum(b[2] for (v, _), b in by_cat.items() if v == "NEGATIVE")
        tot_cost = sum(a["cost"] for a in agg.values())
        print("\n  NEGATIVE share of spend: ${:,.2f} of ${:,.2f}  ({:.1f}%)".format(
            tot_neg_cost, tot_cost, 100 * tot_neg_cost / tot_cost if tot_cost else 0))
        print("  candidate roots accepted : {} PHRASE".format(len(roots)))
        print("  residual exacts accepted : {} EXACT".format(len(exacts)))
        print("  candidates rejected      : {}".format(len(rejected)))
        rej = Counter(r["reason"] for r in rejected)
        for reason, n in rej.most_common():
            print("      rejected/{:<24} {}".format(reason, n))
        print("  negative terms covered by a root: {} of {}".format(
            len(covered), len(neg_terms)))
        print("  verdict table -> {}".format(vpath.relative_to(ROOT)))
        print("  root plan     -> {}\n".format(npath.relative_to(ROOT)))

        summary[slug] = {
            "unique_terms": len(agg), "roots": len(roots), "exacts": len(exacts),
            "negative_terms": len(neg_terms), "keep": len(keep_terms),
            "watch": len(watch_terms), "negative_cost": round(tot_neg_cost, 2),
            "total_cost": round(tot_cost, 2), "live_ad_groups": len(live_ag),
        }

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
