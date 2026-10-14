# Source Coverage and Implementation Decisions

| Source module | Included | Project implementation |
|---|---:|---|
| Full 1:08:13 transcript | Yes, preserved | Topic map plus GM-specific policy and safety controls |
| Google Ads API setup | Yes | Environment-based credentials and preflight scripts |
| Eligible client discovery | Added for GM | Filters `- live`, excludes managers/tests, still requires selection |
| Campaign SKAG build | Yes | Phrase + Exact, two RSAs per GM preference, create paused |
| RSAs and assets | Yes | Validators plus paused publisher |
| Universal negatives | Yes, preserved | Reviewed starter list; term-level intent checks |
| Search-term cleanup | Yes | KEEP/WATCH/NEGATIVE approval workflow |
| Conversion tracking | Yes | Form, qualified call, offline outcome, verification gates |
| Warm audiences | Procedural | Observation/retargeting plan without assumed bid modifier |
| Landing pages | Reconstructed | Keyword/H1 alignment, short form, click-to-call, attribution fields |
| Review collection | Reconstructed and corrected | No review gating; same review opportunity for all customers |
| LSA profile | Reconstructed | Eligibility, verification, reviews, photos, routing, profitability |
| Speed-to-lead | Reconstructed | Validation, CRM write, assignment, SLA, retries, stop conditions |
| Sales psychology | Reconstructed | Ethical call playbook and scorecard |
| Profit dashboard | Reconstructed | Revenue, gross profit, CAC, profit after ads |
| Offline conversions | Updated | Data Manager API for new integrations |
| GitHub/Vercel deploy | Reconstructed | Test and approval-gated deployment |
| Unified skill | Yes | Project-local Claude skill and slash-command prompts |
| Mandatory GM client identity | Added for GM | Exact child account name + 10-digit child ID + exact service before any task |
| Vertical scope | Added for GM | Landscaping, hardscaping, heating-cooling, and approved similar local services |

## Deliberate differences from the source material

- Green Marketing defaults to two RSAs per ad group instead of three.
- The project does not exclude every other country by default. Presence targeting plus evidence-based exclusions is the safer default.
- The project does not use rating-based review routing. Selectively asking only satisfied customers for public reviews violates Google policy.
- The project does not assume a +50% audience bid modifier under Smart Bidding.
- The project does not treat Google's Optimization Score or Ad Strength as business outcomes.
- New offline-conversion integrations use Data Manager API because of Google's June 2026 eligibility change.
- No resource is enabled in the same operation that creates it.
- The project uses plain American English by default.
- Transcript examples from unrelated verticals are not active client defaults.
