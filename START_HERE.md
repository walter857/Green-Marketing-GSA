# Start Here

This folder is the Green Marketing Google Ads operating system for Claude Code and ChatGPT Projects.

## Before any client work

Claude Code or ChatGPT must collect these three items first:

1. The exact child account name shown in Google Ads.
2. The 10-digit child customer ID. Do not use the Green Marketing MCC ID.
3. The exact service being worked on, such as landscape design, paver patios, retaining walls, AC repair, furnace replacement, or another approved local service.

No audit, campaign draft, landing-page build, or Google Ads change may start until all three are present. The account name and ID must also match a fresh read-only Google Ads lookup.

## When the service is not known yet

If you have the exact account name and child ID but not the service, run read-only service discovery first:

```bash
python scripts/validate_service_discovery.py clients/<client-slug>/service-discovery.yaml
python scripts/discover_services.py \
  --discovery clients/<client-slug>/service-discovery.yaml \
  --output clients/<client-slug>/snapshots/service-discovery-<date>.json
```

Discovery reads the live account and the public landing pages and proposes candidate services with evidence and a confidence level. It waives only the service requirement, and only for itself. It cannot audit, draft, build, revamp, or write. Confirm the exact service, put it in `work-order.yaml`, and then continue.

## Use with ChatGPT Projects

1. Create a ChatGPT Project named `Green Marketing GSA`.
2. Copy `project-instructions/CHATGPT_PROJECT_INSTRUCTIONS.md` into Project settings.
3. Keep `project-instructions/CLIENT_START_QUESTIONS.md` available as a Project source.
4. Start every client chat with `project-instructions/NEW_CLIENT_STARTER_PROMPT.md`.
5. Have ChatGPT produce a completed work order before asking Claude Code to act.

## Use with Claude Code

1. Unzip this folder and open `green-marketing-gsa` in VS Code.
2. Start Claude Code in this folder.
3. Copy `clients/_template/` to `clients/<client-slug>/`.
4. Complete `client.yaml` and `work-order.yaml` with the client.
5. Run:

   ```bash
   python -m pip install -r requirements.txt
   python scripts/validate_work_order.py \
     clients/<client-slug>/work-order.yaml \
     --client clients/<client-slug>/client.yaml
   python scripts/verify_setup.py --client clients/<client-slug>/client.yaml
   ```

6. Ask Claude Code to read `CLAUDE.md` and handle the approved work order.

## Safe operating sequence

`intake -> identity check -> (service discovery if the service is unknown) -> confirmed exact service -> fresh read-only snapshot -> draft -> validation -> exact approval -> create paused -> readback QA -> separate enablement approval`

The `- live` name marker identifies candidate client accounts. It is never permission to change an account.
