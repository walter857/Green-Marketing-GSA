# Onboard a Green Marketing Client

Read `CLAUDE.md`, `config/agency.yaml`, and `docs/CLIENT_INTAKE_QUESTIONS.md`.

Goal: create a complete client profile and current work order without making any external changes.

1. Ask for the exact child account name, 10-digit child customer ID, and exact service first. State that the MCC ID is not the child ID. Stop if any item is missing.
2. Confirm the vertical is landscaping, hardscaping, heating-cooling, or an explicitly approved similar local service.
3. Search existing project sources for the remaining answers.
4. Ask only unanswered questions required for the requested task, offer, service area, budget, landing page, conversion setup, and approval owners.
5. Never ask for secrets in chat. Ask only where credentials are stored locally.
6. Copy `clients/_template/` to `clients/<client-slug>/` and complete `client.yaml` and `work-order.yaml`.
7. Mark unknown but required fields clearly; do not invent values.
8. Run `python scripts/validate_work_order.py clients/<client-slug>/work-order.yaml --client clients/<client-slug>/client.yaml`.
9. Return a concise gap list. Do not proceed to client work until identity, vertical, service, and task scope are confirmed.
