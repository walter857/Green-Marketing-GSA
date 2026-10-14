# MasterGrass - WhatConverts vs Google Ads attribution, 2026-01-01..2026-09-28

Read-only. 581 WhatConverts leads (default 393 + duplicate 122 + spam 66 - the API hides the last two by default)
checked against Google Ads call_view (36 forwarding-number calls in 2026), 90 days of click_view gclids (183),
and conversions by conversion date. Script: `scripts/mg_0928_wc_attribution.py`.

| Finding | Count | Evidence |
|---|---|---|
| Google Ads leads correctly labelled paid in WhatConverts | 59 | paid numbers / gclid |
| Google Ads calls WhatConverts relabelled "GBP Traffic" or "google/organic" | 7 | on paid numbers; 4 also in Google's call log |
| ...of which the Aug 27 tester (rang every number) | 2 | same caller, 5 numbers, 2 days |
| Google forwarding-number calls that never reached WhatConverts | 5 | all 47 s or shorter |
| Offer-page "direct" web forms | 31 | only 2 contacts, all on the offer home page, all Repeat - tests |
| Website-number contacts on offer pages, labelled direct (unprovable) | 3 | Apr 1 x2, May 13 |
| Maps-ad calls possibly under "GBP Traffic" | at most 4 | Google "Clicks to call" days |
| Labelled Google/cpc without Google Ads evidence | 3 | May 11 GBP number, Jun 29 website number, Sep 9 LSA number |

All 7 relabelled paid calls were marked duplicate/Repeat and inherited the caller's earlier source; every one hit
"voicemail not set up", no answer or a hang-up. Google Ads still counted WC Call Lead conversions on Aug 20/26/27.

Real Google Ads leads (forms + calls 60 s+ that reached a person) vs the Google Ads Conversions column:
Mar 3 vs 0, Apr 12 vs 5, May 9 vs 3, Jun 9 vs 4, Jul 7 vs 7, Aug 0 vs 9, Sep 1 vs 4.
Google Ads under-counted real paid leads Mar-Jun and over-counted Aug-Sep.

New since PMax went live: 2026-09-27 18:55 ET call on the paid-search number, labelled Google/cpc correctly,
19 s, hit "voicemail not set up".
