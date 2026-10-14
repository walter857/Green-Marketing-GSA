#!/usr/bin/env python3
"""2026-09-26 READ-ONLY: do Master Grass calls reach a person or an automated greeting?

Counts fixed phrase signals inside WhatConverts call transcriptions, grouped by duration bucket
and half-month. Prints COUNTS ONLY: no transcript text, no caller data, nothing written to disk.
"""
from __future__ import annotations

import datetime
import os
import re
import sys
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import requests  # noqa: E402
from requests.auth import HTTPBasicAuth  # noqa: E402
from gm_gsa.config import load_dotenv_if_available  # noqa: E402

load_dotenv_if_available(ROOT / ".env")
AUTH = HTTPBasicAuth(os.environ["WHATCONVERTS_API_TOKEN"].strip(), os.environ["WHATCONVERTS_SECRET"].strip())
NY = ZoneInfo("America/New_York")

SIGNALS = {
    "voicemail_prompt": r"leave (a|your) (message|name)|after the (tone|beep)|voice ?mail|mailbox|record your message",
    "unavailable": r"(not|un)available|can't (take|get to) (your|the) (call|phone)|unable to (take|answer)|away from",
    "ivr_menu": r"\bpress (one|two|three|1|2|3)\b|for (sales|service|billing).{0,20}press",
    "text_us": r"\btext (us|me)\b|send (us )?a text",
    "office_hours": r"office hours|business hours|we are (currently )?closed|our hours",
    "ai_receptionist": r"virtual (assistant|receptionist)|\bai\b|automated assistant",
    "human_greeting": r"(this is|you'?ve reached|speaking)\b.{0,40}(master ?grass)|how can i help|how may i help",
    "appointment_or_quote": r"\b(estimate|quote|schedule|appointment|come out|take a look)\b",
}
RX = {k: re.compile(v, re.I) for k, v in SIGNALS.items()}


def pull(**extra):
    out, page = [], 1
    while True:
        r = requests.get("https://app.whatconverts.com/api/v1/leads", auth=AUTH, timeout=60, params=dict(
            account_id=64716, profile_id=94840, start_date="2026-06-01", end_date="2026-09-26",
            lead_type="phone_call", leads_per_page=250, page_number=page, **extra))
        r.raise_for_status()
        b = r.json().get("leads", [])
        out += b
        if len(b) < 250:
            return out
        page += 1


seen = {}
for ex in ({}, {"duplicate": "true"}):
    for l in pull(**ex):
        assert str(l.get("account_id")) == "64716"
        seen[l["lead_id"]] = l
calls = list(seen.values())
with_tx = [l for l in calls if str(l.get("call_transcription") or "").strip()]
print(f"calls (non-spam, incl. duplicates): {len(calls)} | with a transcription: {len(with_tx)}")


def bucket(d):
    d = d or 0
    return "45-49s" if 45 <= d <= 49 else "<45s" if d < 45 else "50s+"


def half(l):
    t = datetime.datetime.fromisoformat(l["date_created"].replace("Z", "+00:00")).astimezone(NY)
    return f"{t:%m}{'a' if t.day <= 15 else 'b'}"


tot = Counter()
hit = Counter()
for l in with_tx:
    tx = str(l.get("call_transcription"))
    b = bucket(l.get("call_duration_seconds"))
    tot[b] += 1
    for k, rx in RX.items():
        if rx.search(tx):
            hit[(b, k)] += 1
print("\nshare of transcribed calls containing each signal, by duration bucket:")
for b in ("<45s", "45-49s", "50s+"):
    if tot[b]:
        print(f"  {b:<7} n={tot[b]:>3}  " + "  ".join(f"{k}={hit[(b, k)]}" for k in SIGNALS))
tl = Counter()
vm = Counter()
for l in with_tx:
    tl[half(l)] += 1
    if RX["voicemail_prompt"].search(str(l.get("call_transcription"))) or RX["unavailable"].search(str(l.get("call_transcription"))):
        vm[half(l)] += 1
print("\nvoicemail/unavailable signal by half-month (transcribed calls):")
for k in sorted(tl):
    print(f"  {k}: {vm[k]}/{tl[k]}")
lens = Counter(bucket(l.get("call_duration_seconds")) for l in with_tx)
wc = [len(str(l.get("call_transcription")).split()) for l in with_tx if bucket(l.get("call_duration_seconds")) == "45-49s"]
if wc:
    wc.sort()
    print(f"\n45-49s transcripts: word count median {wc[len(wc)//2]}, min {wc[0]}, max {wc[-1]}")

# k-anonymous phrase check: only 4-word phrases that occur in >= 20 DISTINCT 45-49s calls are
# printed. A phrase shared by that many different callers is a recording, not personal data.
grams = Counter()
tok = re.compile(r"[a-z']+")
for l in with_tx:
    if bucket(l.get("call_duration_seconds")) != "45-49s":
        continue
    w = tok.findall(str(l.get("call_transcription")).lower())
    grams.update({" ".join(w[i:i + 4]) for i in range(len(w) - 3)})
common = [(g, n) for g, n in grams.most_common(40) if n >= 20]
print(f"\n4-word phrases present in >=20 distinct 45-49s calls: {len(common)}")
for g, n in common[:20]:
    print(f"  {n:>3}  {g}")

# Which phrase precedes the failure message (k-anonymous: >= 20 distinct calls only)
pre = Counter()
for l in with_tx:
    w = tok.findall(str(l.get("call_transcription")).lower())
    s = " ".join(w)
    i = s.find("has not been set up")
    if i > 0:
        pre[" ".join(s[:i].split()[-4:])] += 1
print("\nphrase immediately before 'has not been set up' (>=20 calls):", [(p, n) for p, n in pre.most_common(5) if n >= 20])

FAIL = re.compile(r"not been set up yet|try your call again later", re.I)
by_half = Counter(); by_half_fail = Counter(); by_num = Counter(); by_num_fail = Counter()
first_fail = None
for l in calls:
    tx = str(l.get("call_transcription") or "")
    f = bool(FAIL.search(tx))
    by_half[half(l)] += 1; by_num[l.get("phone_name")] += 1
    if f:
        by_half_fail[half(l)] += 1; by_num_fail[l.get("phone_name")] += 1
        t = l["date_created"]
        first_fail = t if first_fail is None or t < first_fail else first_fail
print("\n'not set up / try again later' calls by half-month:", {k: f"{by_half_fail[k]}/{by_half[k]}" for k in sorted(by_half)})
print("by tracking number (since 2026-06-01):", {k: f"{by_num_fail[k]}/{by_num[k]}" for k in by_num})
print("first failing call (UTC):", first_fail)
recent = sorted([l for l in calls if l["date_created"] >= "2026-09-12"], key=lambda l: l["date_created"])
print("\ncalls since 09-12 (NY time, number, duration, answer, failure-message):")
for l in recent:
    t = datetime.datetime.fromisoformat(l["date_created"].replace("Z", "+00:00")).astimezone(NY)
    print(f"  {t:%m-%d %a %H:%M} {str(l.get('phone_name')):<15} {l.get('call_duration_seconds')}s {l.get('answer_status'):<13} fail={'YES' if FAIL.search(str(l.get('call_transcription') or '')) else '-'}")

# Destination (business) numbers, masked to the last 4 digits, failing vs not.
def m4(n):
    d = "".join(ch for ch in str(n or "") if ch.isdigit())
    return f"...{d[-4:]}" if len(d) >= 4 else "(none)"


dest = Counter(); dest_fail = Counter(); dest_first = {}; dest_last = {}
for l in calls:
    k = (m4(l.get("destination_number")), l.get("phone_name"))
    dest[k] += 1
    if FAIL.search(str(l.get("call_transcription") or "")):
        dest_fail[k] += 1
    dest_first[k] = min(dest_first.get(k, l["date_created"]), l["date_created"])
    dest_last[k] = max(dest_last.get(k, l["date_created"]), l["date_created"])
print("\ndestination (masked) x tracking number: failing/total, first..last (UTC date)")
for k in sorted(dest, key=lambda k: (k[0], str(k[1]))):
    print(f"  dest {k[0]:<8} via {str(k[1]):<15} {dest_fail[k]:>3}/{dest[k]:<3} {dest_first[k][:10]}..{dest_last[k][:10]}")
print("tracking numbers (masked):", sorted({(l.get('phone_name'), m4(l.get('tracking_number'))) for l in calls}, key=str))

since = [l for l in calls if l["date_created"] >= "2026-07-28T21:00:00Z"]
f = [l for l in since if FAIL.search(str(l.get("call_transcription") or ""))]
print(f"\ncalls since first failure (2026-07-28 17:43 ET): {len(since)} | failing {len(f)} = {len(f)/len(since):.0%}")
paid = [l for l in since if l.get("phone_name") in ("GSA's Traffic", "GLE Traffic")]
print("paid-number calls since then:", len(paid), "| failing:", sum(1 for l in paid if FAIL.search(str(l.get("call_transcription") or ""))))
real = [l for l in since if not FAIL.search(str(l.get("call_transcription") or "")) and (l.get("call_duration_seconds") or 0) >= 60]
print("calls since then that were >=60 s and not the failure message:", len(real))
