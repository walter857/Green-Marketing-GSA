#!/usr/bin/env python3
"""Wait for the basic-access MUTATE budget, then run the approved negative
rollout -- Ambient first, per the owner's 2026-08-29 instruction.

Why this does not gate on a read
--------------------------------
Proven twice on 2026-08-29:
  09:57 EDT  a one-row `FROM customer` read passed; the executor died seconds
             later on its pre-write snapshot.
  20:54 EDT  the executor's heaviest read passed TWICE, five minutes apart; the
             run then died on its FIRST mutate batch with 0 objects created.
Read capacity and mutate capacity recover separately. Only a mutate can prove a
mutate will work, so this runner stops guessing: it attempts the real run, and
when the API refuses it, it sleeps for exactly the `Retry in <n> seconds` the API
returned, plus a margin, then tries again.

Safety
------
An attempt is retried ONLY when it created zero objects. If any object was
created the run stops for a human: the remaining set has to be re-derived
against a fresh readback, and a blind rerun would double-write.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "Scripts" / "python.exe"

# Owner priority 2026-08-29: Ambient first. Fingerprints approved 2026-08-28,
# re-verified unchanged by neg_preflight_local.py on 2026-08-29.
QUEUE = [
    ("ambient-cooling-heating", 5652, [
        "NEG_CAMPAIGN_LEVEL=A8E3523F7521",
        "NEG_NAME_BROAD=5580D132851B"]),
    ("pro-green-austin", 1224, [
        "NEG_CAMPAIGN_LEVEL=6E1A7584E482",
        "NEG_NAME_BROAD=41F1B766F07A"]),
    ("softwind-power-washing", 170, [
        "NEG_CAMPAIGN_LEVEL=1D954F45E2E6",
        "NEG_NAME_BROAD=E71C78C77203",
        "NEG_CROSS_ACCOUNT_FENCE=D27F2802FD31"]),
]

LOG = None
RETRY_RE = re.compile(r"Retry in (\d+) seconds")


def eastern_now():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(timezone.utc).astimezone(ZoneInfo("America/New_York"))
    except Exception:
        return datetime.now()


def say(msg):
    line = "[{}] {}".format(eastern_now().strftime("%Y-%m-%d %H:%M:%S %Z"), msg)
    print(line, flush=True)
    if LOG:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def newest_partial(slug, since):
    """Newest PARTIAL receipt for slug written after `since` (epoch)."""
    pats = sorted(glob.glob(str(ROOT / "clients" / slug / "receipts"
                                / "neg-exec-PARTIAL-*.json")))
    best = None
    for p in pats:
        if Path(p).stat().st_mtime >= since - 5:
            best = p
    return best


def execute(slug, approvals):
    """Run the executor once. Returns (rc, created_count_or_None, retry_secs)."""
    cmd = [str(PY), str(ROOT / "scripts" / "neg_execute.py"), "--slug", slug]
    for a in approvals:
        cmd += ["--approve", a]
    cmd.append("--execute")
    started = time.time()
    say("RUNNING: {}".format(" ".join(cmd[2:])))
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    for line in (r.stdout or "").splitlines():
        say("   | " + line)
    if r.returncode == 0:
        return 0, None, None

    for line in (r.stderr or "").strip().splitlines()[-4:]:
        say("   ! " + line[:200])

    created, retry = None, None
    p = newest_partial(slug, started)
    if p:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        created = len(d.get("created", []))
        m = RETRY_RE.search(d.get("stop_reason", "") or "")
        if m:
            retry = int(m.group(1))
        say("   receipt {} -> created={}".format(Path(p).name, created))
    if retry is None:
        m = RETRY_RE.search((r.stderr or "") + (r.stdout or ""))
        retry = int(m.group(1)) if m else None
    return r.returncode, created, retry


def main() -> int:
    global LOG
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-attempts", type=int, default=8)
    ap.add_argument("--margin", type=int, default=120,
                    help="seconds added to the API's retry-after (default 120)")
    ap.add_argument("--fallback-wait", type=int, default=900)
    ap.add_argument("--only", action="append", default=[])
    args = ap.parse_args()

    stamp = eastern_now().strftime("%Y-%m-%d-%H%M")
    (ROOT / "reports").mkdir(exist_ok=True)
    LOG = ROOT / "reports" / "neg-autorun-{}.log".format(stamp)

    queue = [q for q in QUEUE if not args.only or q[0] in args.only]
    say("autorun armed (mutate-gated). queue: {}".format(
        ", ".join("{} ({} ops)".format(s, n) for s, n, _ in queue)))
    say("log -> {}".format(LOG.relative_to(ROOT)))

    for slug, ops, approvals in queue:
        say("=" * 70)
        say("{}  ({} operations)".format(slug, ops))
        for attempt in range(1, args.max_attempts + 1):
            say("attempt {}/{}".format(attempt, args.max_attempts))
            rc, created, retry = execute(slug, approvals)
            if rc == 0:
                say("{} COMPLETE.".format(slug))
                break
            if created:
                say("STOPPING: {} created {} objects then stopped. A blind rerun "
                    "would double-write. Re-derive the remaining set against a "
                    "fresh readback.".format(slug, created))
                return 1
            wait = (retry + args.margin) if retry else args.fallback_wait
            opens = eastern_now() + timedelta(seconds=wait)
            say("quota refused the mutate, 0 objects created. sleeping {}s "
                "(~{:.0f} min), next attempt ~{}".format(
                    wait, wait / 60, opens.strftime("%H:%M %Z")))
            if attempt == args.max_attempts:
                say("STOPPING: out of attempts for {}.".format(slug))
                return 2
            time.sleep(wait)
        else:
            return 2

    say("=" * 70)
    say("ALL QUEUED ACCOUNTS COMPLETE.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
