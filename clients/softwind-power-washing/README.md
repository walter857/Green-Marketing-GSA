# Softwind Power Washing

**Account:** `Softwind Power Washing - Live` · `152-172-5229` / `1521725229`
**MCC:** `3373711342` Green Marketing · **Currency:** USD · **Time zone:** America/New_York
**Vertical:** `similar-local-service` (scope approved — Walter Correa)
**Exact service:** Power Washing

---

## Current state — 2026-08-25

**Mode: READ. No external change has ever been made to this account from this repository.**

The account holds **two enabled Search campaigns**, not one:

| Campaign | ID | Created | Budget | Live ad groups |
|---|---|---|---|---|
| Power Washing | `24103511039` | 2026-08-04 | $41.11/day | 6 |
| Power Washing #2 | `24145053510` | 2026-08-18 | $41.11/day | 6 |

Life-to-date: **107 impressions · 6 clicks · $171.17 · 0 conversions.**
First impression 2026-08-05 · first click 2026-08-17 · first conversion never.

---

## Read this first

| Document | What it answers |
|---|---|
| **`audits/2026-08-25-power-washing-executive-report.md`** | Start here. One page. |
| `audits/2026-08-25-power-washing-full-audit.md` | The complete 35-section audit. |
| `audits/2026-08-25-launch-chronology.md` | Created / enabled / first impression / first click / first spend, and the bid-ceiling history that explains all of it. |
| `audits/2026-08-25-pacing-analysis.md` | The $2,500 question, answered with the demand math. |
| `audits/2026-08-25-conversion-audit.md` | Measurement state, tag inventory, what still needs a live test. |
| `audits/2026-08-25-draft-expansion-plan.md` | **DRAFT ONLY.** Prioritised changes, drafted RSAs, mutation inventory. Nothing implemented. |

CSV evidence: ad-group performance (30) · keyword audit (214) · search-term verdicts (45,
no impression threshold) · RSA audit (54) · landing-page audit (13) · keyword opportunities.

---

## P0 + P1 change plans — built 2026-08-25, NONE APPROVED

Seven separately-fingerprinted plans. **A fingerprint identifies an exact plan; it does not
grant permission.** Every plan is `NOT APPROVED` / `DO NOT EXECUTE`.

| Plan | Fingerprint | Ads mutations | Approve with |
|---|---|---:|---|
| **A** measurement / conversion verification | `701E8E5ED639` | 0 | `APPROVE PLAN-A 701E8E5ED639 FOR 1521725229` |
| **B** Max CPC ceiling $24.00 | `F80E8D398811` | 2 | `APPROVE PLAN-B F80E8D398811 FOR 1521725229` |
| **C** ad schedule to 24/7 | `9E18503B5BEA` | 26 | `APPROVE PLAN-C 9E18503B5BEA FOR 1521725229` |
| **D** enable House Washing Company Near Me | `F61C9F287B82` | 1 | `APPROVE PLAN-D F61C9F287B82 FOR 1521725229` |
| **E** create paused: 2 SKAGs + 3 negatives | `F453AD249497` | 16 | `APPROVE PLAN-E F453AD249497 FOR 1521725229` |
| **F** website / landing page fixes | *(no Ads fingerprint)* | 0 | website approval, separate track |
| **G** pause duplicate ad group; **G-2 deferred** | `EC35724753AE` | 1 | `APPROVE PLAN-G EC35724753AE FOR 1521725229` |
| **H** sitelinks to tracked pages | `1D63EC1EB68D` | 21 | `APPROVE PLAN-H 1D63EC1EB68D FOR 1521725229` |
| | | **67 total** | |

Start with **`plans/2026-08-25-p0-p1-master-plan.md`**.

**Two corrections to the audit are recorded there:** the CPC ceiling should be **$24.00**,
not the audit's $22.00 (the audit used an all-market volume-weighted high; the live keywords
show $28.23, and the account still loses 34.6% of impression share to rank while uncapped);
and the audit conflated `house washing company near me` (no reportable volume) with
`house washing near me` (40/month) — the latter is handled in PLAN-E as a clean SKAG.

**PLAN-G G-2 (full campaign consolidation) must NOT be approved yet** — defer to September.

---

## The three things that matter

1. **The schedule is dark 64% of the week and cuts off at the peak hour.** Mon–Sat
   08:00–18:00, no Sunday. The 17:00 hour is the account's single biggest at 21.5% of all
   impressions, and delivery stops at 18:00.
2. **Bidding is uncapped at $28.53 average CPC** against a local top-of-page range of
   $8.66–$23.91. A $5.00 ceiling existed until 2026-08-16 and produced 12 straight days of
   zero clicks. The account has never been bid correctly.
3. **The market is ~800 BOFU searches/month across the eight targeted cities.** Roughly 26
   a day. The campaign already holds 100% impression share on some days. **$2,500 is not
   spendable on qualified demand** — the defensible ceiling is about **$638**.

---

## Open questions blocking further work

1. **Which towns does Softwind actually serve for power washing?** The campaigns target
   eight fragmented cities, and "Islip" is the hamlet (~18k), not the Town of Islip (~340k).
   *The only lever that materially changes the demand ceiling.*
2. Is (631) 502-7946 answered evenings and Sundays? What is the after-hours callback commitment?
3. Who owns Google Ads account `17878095007`? Its tag fires on every landing page.
4. Average job revenue, gross margin, close rate, target CPL/CPQL — all `null`.
5. Is the $2,500 a performance target or a contractual commitment?
6. Is the "Offer Ends in" countdown tied to a real, dated offer?
7. The reviews page gates by sentiment (HAPPY / NEUTRAL / POOR) — prohibited by
   `config/agency.yaml` and by Google review policy.

---

## Reproducing the audit

All scripts are `SELECT`-only and browser-navigation-only. None constructs an operation or
calls a mutate service.

```bash
python scripts/validate_work_order.py clients/softwind-power-washing/work-order.yaml \
  --client clients/softwind-power-washing/client.yaml
python scripts/verify_setup.py --client clients/softwind-power-washing/client.yaml --online

python scripts/softwind_identity_check.py        # identity gate
python scripts/softwind_deep_read.py             # structural snapshot
python scripts/softwind_chronology.py            # change events + daily metrics
python scripts/softwind_metrics_read.py          # segmentation
python scripts/softwind_geo_resolve.py           # geo target names
python scripts/softwind_bid_history.py           # CPC ceiling history, AI Max, automation
python scripts/softwind_keyword_planner.py       # local demand, exact campaign geo
python scripts/softwind_demand_model.py          # collapse Planner buckets, classify intent
python scripts/softwind_pacing_model.py          # August pacing and scenarios
python scripts/softwind_lp_audit.py --urls clients/softwind-power-washing/research/live-final-urls.txt \
  --out clients/softwind-power-washing/snapshots/landing-pages-2026-08-25.json --gclid-test
python scripts/softwind_hours_probe.py           # published business hours
python scripts/softwind_build_artifacts.py       # CSV artifacts
python scripts/softwind_final_safety_check.py    # 29 assertions: nothing changed
```

`softwind_final_safety_check.py` re-reads the live account and asserts every mutable surface
is identical to the opening snapshot. Last run: **29 checks, 0 changed.**
