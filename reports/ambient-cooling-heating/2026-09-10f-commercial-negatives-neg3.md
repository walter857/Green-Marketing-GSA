# Ambient Cooling - Live (2401959466) — 2026-09-10 session F

**`AMB-0910-COMM-NEG-3 / 51CF5986F18A` — 17 operations — EXECUTED 2026-09-10.**
`EXECUTED_OK: 17 results returned` · one atomic mutate · `partial_failure=False` · **readback
0 FAIL**. Receipt: `receipts/live/AMB-0910-COMM-NEG-3-2026-09-10-EXECUTED.json`.

`AMB-0910-COMM-NEG-2 / A9C9BCBDDD74` was never executed and is superseded. Identity gate PASS
before the write; fingerprint recomputed from the on-disk plan and matched before any operation
was built.

---

## `AMB-0910-COMM-NEG-3` · **`51CF5986F18A`** · **17 operations** · **EXECUTED**

Ad-group scope only, on **199748801029** (`SKAG | Commercial HVAC Installation`, PAUSED).

```
residential  homeowner  house    diy      job     jobs     career
careers      salary     salaries course   courses parts    used
wholesale    supplier   supply
```

**HELD (5):** `school` · `schools` · `rent` · `rental` · **`training`**

Validated first (`VALIDATED_OK`, `validate_only=True`), then executed on approval.
Receipts: `receipts/validate-only/AMB-0910-COMM-NEG-3-2026-09-10.json` and
`receipts/live/AMB-0910-COMM-NEG-3-2026-09-10-EXECUTED.json`.

The delta from NEG-2 is exactly one term. The plan asserts this in code before drafting:
`set(NEG-2) - set(NEG-3) == {"training"}`.

---

## Why dropping `training` is a clean win

BROAD `training` blocks any query carrying the token. Measured against the live PHRASE keyword:

| Phrase | Reachable? | Under NEG-2 | Under NEG-3 |
|---|---|---|---|
| `commercial hvac installation for a training facility` | **yes** | blocked | **allowed** |
| `commercial hvac installation for a training center` | **yes** | blocked | **allowed** |

**Reachable commercial buyer phrases regained: 2.**
**Non-buyer phrases now unblocked: NONE.**

Training facilities and training centres are ordinary commercial buildings. And the removal
costs nothing measurable — `commercial hvac installation course` is still correctly blocked by
`course`, which remains in the list.

---

## Conflict tests — all re-run from scratch

| Test | Result |
|---|---|
| Both positive commercial keywords | **clear** |
| Every ENABLED positive keyword in campaign 24132507747 | **clear** |
| All converting search terms 2026-01-01→09-09 (**28** with Primary or All conversions) | **clear** |
| Property manager / landlord intent (5 phrases) | **clear** |
| Institutional — schools, districts, universities, training facilities, training centres, government, church, hospital, daycare, warehouse (10 phrases) | **clear** |
| Ordinary commercial intent (8 phrases) | **clear** |
| Equipment types (6 phrases) | **clear** |
| Manufacturers (6 phrases) | **clear** |
| Non-buyer controls that *should* be blocked (8 phrases) | **8/8 still blocked** |
| Duplicate sweep — campaign, ad-group, account-level, shared-list | see below |

**43 intent phrases tested. Buyer phrases both reachable and blocked: NONE.**

Testing stays reachability-aware: a phrase counts as a conflict only if it could match a
positive keyword. And it now runs in both directions — the 8 non-buyer controls confirm the
list still does its job:

```
commercial hvac installation jobs near me      -> blocked by jobs
commercial hvac installation salary            -> blocked by salary
commercial hvac installation career            -> blocked by career
commercial hvac installation course            -> blocked by course
commercial hvac installation diy               -> blocked by diy
commercial hvac installation parts supplier    -> blocked by parts, supplier
used commercial hvac installation equipment    -> blocked by used
residential hvac installation near me          -> blocked by residential
```

### Buyer phrases preserved by the five held terms

```
commercial hvac installation for schools              would have been blocked by schools
commercial hvac installation for a school district    would have been blocked by school
commercial hvac installation for my rental building   would have been blocked by rental
commercial hvac installation for a training facility  would have been blocked by training
commercial hvac installation for a training center    would have been blocked by training
```

### Duplicates

**No shared set is attached to any of the five campaigns** — verified directly, so every
shared-list match is inert. Of the 17, fourteen appear in unattached shared sets only. Three —
`job`, `jobs`, `supplier` — exist as campaign-level **PHRASE** negatives on 24132507747; for
single-token negatives PHRASE and BROAD behave the same, so those three ad-group copies are
redundant. Retained so the commercial ad group stays self-contained and portable.

**None** of the 17 is on account-level list 11252984411 (271 members), and `commercial` is
confirmed absent from it. No campaign-level or account-level negative is created by this plan.

---

## Residual monitoring note

Course-seeker queries containing `training` are no longer blocked by this list. If `hvac
training` style non-buyer queries appear at volume in the commercial search-term report, add a
narrower **PHRASE** negative such as `"hvac training"` under a new fingerprint — not BROAD
`training`, which is what caused this supersession.

---

## Plan lineage

| Plan | Fingerprint | Terms | Status |
|---|---|---|---|
| `AMB-0910-COMM-NEG-1` | `C4142D5D5DE0` | 18 | SUPERSEDED |
| `AMB-0910-COMM-NEG-1-FULL` | `A774B9C14896` | 22 | **REJECTED** |
| `AMB-0910-COMM-NEG-2` | `A9C9BCBDDD74` | 18 | **SUPERSEDED — do not execute** |
| **`AMB-0910-COMM-NEG-3`** | **`51CF5986F18A`** | **17** | **EXECUTED, readback 0 FAIL** |

---

## Readback — 0 FAIL

17 ad-group negatives live on 199748801029, all BROAD, all ENABLED, all KEYWORD type, exact
term set matched, zero duplicates. All five held terms confirmed **absent**: `school`,
`schools`, `rent`, `rental`, `training`.

**Ad group unchanged otherwise:** still PAUSED · still 0 ads · cpc_bid 10000 · both positive
keywords intact (`commercial hvac installation` PHRASE + EXACT) · campaign 24132507747.

**Unrelated resources verified:** residential ad group 202339087634 still ENABLED with **0**
ad-group negatives and its two ENABLED+APPROVED ads (821319509197, 821319509200) untouched ·
all five campaigns ENABLED, PRESENCE geo · ceilings $25/$25/$30/$25/$30 · budgets $421.55/day =
**$12,815.12**, headroom **$184.88** · campaigns 23 · ad groups 69 · geo 375 · IP blocks 2,796 ·
shared sets 17 · conversion actions 16 · **campaign-level negatives still 6,158** · account-level
list still 271 with `commercial` absent · ClickCease template intact.

No campaign-level or account-level negative was created.

---

## Consolidated approval block

| Plan | Fingerprint | Ops | Status |
|---|---|---|---|
| ~~`AMB-0910-COMM-NEG-3`~~ | `51CF5986F18A` | 17 | **EXECUTED — readback 0 FAIL** |
| `AMB-0910-RSA-ACR-2` | `1F166DE17017` | 1 | ready — AC Repair challenger, create-paused |
| `AMB-0910-COMM-RSA-2` | `41C183D15C93` | 2 | GATED — landing page 404 |
| `AMB-0910-COMM-XNEG-1` | `A70260017DAD` | 1 | GATED — commercial group must serve first |

**Next approval line — the AC Repair challenger, the only ungated item left:**

```
APPROVE AMB-0910-RSA-ACR-2 1F166DE17017 1 operation FOR 2401959466
```

Everything else is blocked on the commercial landing page returning HTTP 200.

### Do not execute

`AMB-0910-COMM-NEG-2 A9C9BCBDDD74` · `AMB-0910-COMM-NEG-1 C4142D5D5DE0` ·
`AMB-0910-COMM-NEG-1-FULL A774B9C14896` · `AMB-0909C-CPC-INST-2 5D57E0EF3B70` ·
`AMB-0910-RSA-ACR-1 19E2F2FFC311` · `AMB-0910-COMM-RSA-1 30312BC45992` · `46C39C6B7091` ·
`D448BFDE4650` · `23BE8FF0F24C` · `CE289F3508A2` · `A435FA09AC97` · `DE376F91F449`

## Evidence

```
receipts/validate-only/AMB-0910-COMM-NEG-3-2026-09-10.json
reports/ambient-cooling-heating/evidence/2026-09-10f-neg3-conflict-tests.json
clients/ambient-cooling-heating/plans/AMB-0910-COMM-NEG-3.json
clients/ambient-cooling-heating/plans/AMB-0910-COMM-NEG-2.SUPERSEDED.json
```
