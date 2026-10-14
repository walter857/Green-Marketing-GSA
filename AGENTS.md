# Repository expectations

Follow `CLAUDE.md` as the project operating policy.

- Keep external writes behind an explicit approval gate.
- Do not begin client work until the exact child account name, 10-digit child customer ID, and exact service are present in a validated work order.
- The only exception is read-only service discovery, which still requires the exact child account name and 10-digit child customer ID and uses its own `service-discovery.yaml`, schema, validator, and command. It never authorizes an audit, draft, build, revamp, or write.
- Keep active work within landscaping, hardscaping, heating-cooling, or an explicitly approved similar local-service vertical.
- Default all new Google Ads entities to paused.
- Run `PYTHONPATH=src python -m unittest discover -s tests -v` before handing off code changes.
- Run `python scripts/validate_work_order.py` for every changed example work order.
- Run `python scripts/validate_service_discovery.py` for every changed service-discovery document.
- Run `python scripts/validate_campaign_plan.py` for any changed example plan.
- Never read, print, commit, or expose `.env` values.
- Update `docs/CHANGELOG.md` when behavior or safeguards change.

- Never use a local fingerprint, a CLI flag, or agent-controlled YAML as production human authorization. Never execute Google Ads write-capable legacy scripts with production credentials. ENABLE is prohibited in the generic executor. Stop on identity or authorization failure.
