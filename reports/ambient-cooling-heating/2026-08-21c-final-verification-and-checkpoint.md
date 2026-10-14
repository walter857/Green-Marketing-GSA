# Ambient Cooling - Live — Final Verification, Corrected Exact-Match Analysis, Budget Checkpoint
Account: Ambient Cooling - Live | 2401959466 | America/New_York | USD
Run: 2026-08-21 20:35 EDT | Class: READ + DRAFT + VALIDATE-ONLY | External mutations this run: **0**

## 1. Identity gate
PASS. Fresh read-only lookup: name `Ambient Cooling - Live`, id 2401959466, tz America/New_York,
currency USD, manager=False, test=False. Manager links 2815082755 ACTIVE, 3373711342 ACTIVE — both retained.

## 2. RSA swap verification (D441DEFC58EB5643)
820900825560 PAUSED / POOR ; 820900825563 PAUSED / AVERAGE ;
821714108336 ENABLED / APPROVED / EXCELLENT ; 821714108339 ENABLED / APPROVED / EXCELLENT.
No RSA recreated, duplicated, edited or re-enabled. Preserved RSAs untouched.

## 3. Landing-page gate — FAIL
URL https://offer.ambientcoolingandheating.com/gas-boiler-repair/ rendered in headless Chromium,
desktop 1440x900 and mobile 412x915. HTTP 202, 172 KB / 162 KB, 3 forms, GTM-PQTPQ436 present,
WhatConverts present, canonical correct.
H1 correct: "Gas Boiler Repair in Severn, Severna Park & Columbia, MD".
DEFECT STILL LIVE on both viewports: H2 "Your HVAC Replacement in 3 Simple Steps".
Required fix: "Your Gas Boiler Repair in 3 Simple Steps".
Phone: both viewports exposed only tel:(410) 705-6354 / 4107056354 and the approved DNI
+14109141456. The +14107610932 exposure seen earlier did NOT reproduce — that finding is
intermittent (race condition), not constant.
Evidence: snapshots/gas-boiler-lp-gate-2026-08-21T2035.json

## 4. Corrected Exact-match analysis
RETRACTED: the earlier claim that [boiler repair] "can only serve the literal query" and that
oil / steam / commercial / installation / replacement variants "verifiably cannot serve".
CORRECT POSITION: Google Exact match includes close variants — misspellings, plurals, stemming,
abbreviations, accents, reordered same-meaning words, added/removed function words — AND
paraphrases or other searches Google judges to share the same intent. The boundary is unpublished
and changes over time. Exact match REDUCES exposure to unrelated intent; it does not eliminate it.
No guarantee is offered that modifier queries can never match.

## 5. Boiler keyword package — 3D823A10CB3C0B25 — VALIDATED, BLOCKED
1 mutation: create [boiler repair] EXACT, ENABLED, ad group 202339087594. 0 negatives.
validate_only = VALIDATE_OK. Fingerprint reproduces from file.
Zero speculative negatives added. Exposure is controlled by scheduled search-term review at
24 h, 72 h and 7 settled days, with negatives added only from observed query evidence or a
confirmed statement of services Ambient does not provide.
Conflict testing 2026-08-21: account-level set 11252984411 (59 members) does not block; 16 shared
sets examined, none attached to the Gas Boiler campaign; 0 campaign-level and 0 ad-group negatives
on the five; 12 active positive keywords checked; 14 Ambient services reviewed. Verdict CLEAR.
LANDMINE: shared set 11813144900 "General List" (1,111 members) contains 'repair'/'Repair'.
Not attached to the five. Never attach it — it would block every repair keyword in the account.
BLOCKED until the H2 is corrected and re-verified in a real browser.

## 6. Budget checkpoint — inputs FRESH
Captured 2026-08-21 20:35 EDT, after the 11:35 ET gate.
MTD spend $2,756.06 — IDENTICAL to the 20:26 EDT checkpoint, delta $0.00. Not stale.
Per campaign MTD: HVAC Installation $1,100.44 | AC Repair $997.60 | HVAC Repair $605.88 |
HVAC Replacement $52.14 | Gas Boiler $0.00.
Maximum $13,000. Remaining $10,243.94. Remaining calendar days incl. today: 11.
Current total daily budget $427.64. Proposed change: HVAC Installation only, $138.16 -> $176.15.
Post-change total daily $465.63. Worst case 2x for 11 days = $2,756.06 + $10,243.86 = $12,999.92.
Headroom $0.08. 5DA7527B19276C0D superseded (stale MTD). Live: BFB9FD367F639CA4, VALIDATE_OK,
1 mutation, fingerprint reproduces.

## 7. Exact mutations proposed
BFB9FD367F639CA4 — 1 update: campaign budget for campaign 24132507747, amount_micros
138160000 -> 176150000, update_mask ["amount_micros"]. partial_failure=False.
3D823A10CB3C0B25 — 1 create: ad_group_criterion, keyword "boiler repair", EXACT, ENABLED. BLOCKED.
Nothing else. No bid changes, no match-type changes, no location changes, no Search Partners,
no Display, no bidding-strategy change, no conversion-goal change, no Google recommendations.

## 8. Readback verification (on approval)
Budget: assert campaign 24132507747 amount_micros == 176150000; assert the other four budgets
unchanged at 141450000 / 42760000 / 78950000 / 26320000; assert account budget count unchanged;
assert bidding strategy, status and targeting unchanged.
Keyword: assert ad group 202339087594 holds exactly 3 positive keywords; assert the new criterion
is EXACT / ENABLED / negative=false; assert 0 negatives in the ad group; assert account keyword
count 6968 -> 6969; assert set 11252984411 still 59 members; assert no shared set newly attached.

## 9. Unrelated-resource verification — ALL UNCHANGED
campaigns 23 | ad groups 68 | ads 115 | keywords 6968 | campaign criteria 13810 |
ad schedule 139 | campaign assets 283 | customer assets 1 | conversion actions 16 |
IP blocks 2796 | shared sets 16.
Budgets unchanged. Primary+counted conversions exactly {1068114183, 6885463625, 6885576934}.
Sitelinks 4 offer + 4 main on each of the five — retained main-site links NOT removed.
Account callout ["Get Free Online Quote"]. Call asset (410)705-6354 with 6 schedule rows.
ClickCease untouched: 2,796 IP exclusions unchanged, none added or removed.
GTM and WhatConverts unchanged. VERDICT: ZERO MUTATIONS THIS REQUEST.

## 10. Monitoring and rollback
Budget: check HVAC Installation daily spend and budget-lost IS at 24 h, 72 h and 7 settled days.
Roll back with 1 update to 138160000 if CPL degrades or pacing threatens the $13,000 maximum.
Keyword: search-term review at 24 h / 72 h / 7 days. Roll back by removing the single criterion
by resource name (1 mutation).
Landing page: developer handoff only. No publication authority. Re-render in a real browser after
the developer reports completion, on desktop and mobile, before any keyword approval.
