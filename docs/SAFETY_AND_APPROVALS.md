# Safety and Approval Model

| Stage | External writes | Required evidence | Approval |
|---|---:|---|---|
| Intake gate | No | Exact child account name + 10-digit child ID + exact service | None |
| Service discovery | No | Validated service-discovery document + exact identity match + manager link + non-manager, non-test account | None; the service is not yet known and no other stage may start |
| Read/audit | No | Validated work order + exact identity match + fresh account snapshot | None |
| Draft | No | Validated work order + client profile + validated plan | None |
| Validate-only | No durable write | API validation response | Exact target confirmed |
| Create paused | Yes | Approved plan fingerprint | Explicit approval code |
| QA readback | No | IDs and fields returned by API | None |
| Enable | Yes | Passed QA report | Separate explicit approval |
| Budget increase | Yes | Current pacing + proposed amount | Separate explicit approval |
| Delete/replace | Destructive | Exact resource inventory + recovery impact | Destructive-action approval |

The approval code is a short SHA-256 fingerprint of the normalized plan. Any change to the child customer ID, exact service, budget, location, URL, keywords, ads, or other plan field produces a new code and invalidates the prior approval.

`- live` means only that an account is eligible to appear in the candidate list. It never grants write access.

Service discovery waives exactly one requirement, the exact service, and only for itself. It cannot be re-used to authorize a later stage: its document is rejected unless `task.type` is `service-discovery`, `task.mode` is `read`, and `authorization.read_only_service_discovery` is `true`, and it is rejected outright if it names a service, vertical, scope approval, or plan. Its command runs GAQL `SELECT` statements only and reads landing pages with GET only.
