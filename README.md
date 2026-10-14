# Green Marketing GSA Automation

A safety-first Google Ads operating system for Green Marketing's local-service clients. It converts the supplied full video transcript and eight Google Docs into one Claude Code-ready project, plus a small set of files for a ChatGPT Project.

The active scope is landscaping, hardscaping, heating and cooling, and closely related local-service verticals approved by Green Marketing. The system covers client intake, account audits, BOFU keyword research, focused Phrase + Exact ad groups, two RSAs per ad group, ad assets, landing pages, conversion tracking, Local Services Ads planning, review collection, speed-to-lead, search-term cleanup, offline outcomes, and profit reporting.

Start with `START_HERE.md`.

## What is safe by default

- Accounts whose names contain `- live` are discovered, then shown for manual selection.
- Every task requires the exact child account name, 10-digit child customer ID, and exact service before work begins.
- The one exception is read-only service discovery, which still requires the exact account name and child ID and exists only to propose the service for the user to confirm. It cannot audit, draft, build, revamp, or write.
- No account is selected from its name alone. The child ID and exact name must match the client profile and a fresh read-only lookup.
- API planning and validation are read-only.
- New campaigns, ad groups, and ads are created `PAUSED`.
- Publishing requires an approval code tied to the exact plan contents.
- Enabling delivery is a separate human-approved operation and is intentionally not automated here.
- Secrets stay in `.env`; they are never written into plans, reports, or prompts.

## Recommended Claude Code setup

1. Unzip this folder.
2. Open the folder as a local ChatGPT Work project or start Claude Code from this directory.
3. Copy `.env.example` to `.env` and add the agency credentials locally. Never paste secrets into chat.
4. Copy `clients/_template/` to `clients/<client-slug>/` and complete both YAML files.
5. Validate the client work order, then run the preflight:

   ```bash
   python -m pip install -r requirements.txt
   python scripts/validate_work_order.py \
     clients/<client-slug>/work-order.yaml \
     --client clients/<client-slug>/client.yaml
   python scripts/verify_setup.py --client clients/<client-slug>/client.yaml
   ```

   If the exact service is not known yet, discover it read-only first:

   ```bash
   python scripts/validate_service_discovery.py \
     clients/<client-slug>/service-discovery.yaml
   python scripts/discover_services.py \
     --discovery clients/<client-slug>/service-discovery.yaml \
     --output clients/<client-slug>/snapshots/service-discovery-<date>.json
   ```

6. List eligible accounts without changing anything:

   ```bash
   python scripts/list_live_accounts.py \
     --work-order clients/<client-slug>/work-order.yaml \
     --client clients/<client-slug>/client.yaml
   ```

7. Generate and validate a campaign plan:

   ```bash
   python scripts/build_campaign_draft.py \
     --client clients/<client-slug>/client.yaml \
     --work-order clients/<client-slug>/work-order.yaml \
     --brief templates/campaigns/search-skag.example.yaml \
     --output work/campaign-plan.yaml

   python scripts/validate_campaign_plan.py work/campaign-plan.yaml
   ```

8. Review the plan and request its approval code:

   ```bash
   python scripts/approval_code.py work/campaign-plan.yaml
   ```

9. Only after approval, create the paused build:

   ```bash
   python scripts/publish_campaign.py work/campaign-plan.yaml \
     --client clients/<client-slug>/client.yaml \
     --work-order clients/<client-slug>/work-order.yaml \
     --approval-code <CODE> --execute
   ```

Run the local safety tests after changing project code:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## ChatGPT Project setup

Copy `project-instructions/CHATGPT_PROJECT_INSTRUCTIONS.md` into the Project instructions. Use `project-instructions/NEW_CLIENT_STARTER_PROMPT.md` to begin a client chat. ChatGPT Projects keep files and instructions together for repeatable work, but the local Claude Code folder remains the execution workspace.

For Claude Code, use:

```text
Read CLAUDE.md. Validate the selected client's work-order.yaml against client.yaml. If the exact account name, 10-digit child customer ID, or exact service is missing, ask for it and stop. Do not make any external changes.
```

## Important 2026 measurement note

For new offline-conversion integrations, use Google Data Manager API. As of June 15, 2026, Google Ads API upload requests can fail for developer tokens that had not previously used offline-conversion uploads. The project treats the legacy Google Ads upload route as grandfathered-only.

## Source coverage

The full supplied transcript is preserved under `source-material/video/`. The eight supplied Google Docs are preserved under `source-material/google-docs/`. The package does not include any client-specific images, reviews, offers, CRM fields, or website code; the intake requires those only when a requested task needs them.


## Estado de seguridad de producción (octubre de 2026)

**Las escrituras de Google Ads NO están habilitadas.** Los comandos
`scripts/execute_approved_plan.py --execute`,
`scripts/publish_campaign.py --execute` y `scripts/neg_execute.py --execute`
rechazan la ejecución real mientras no exista una autoridad de aprobación
independiente del agente y una separación verificable de credenciales.

La huella SHA-256 generada por `scripts/approval_code.py` es un
**identificador de integridad, no una aprobación humana**. No confiere
autorización ni siquiera cuando coincide con el plan.

El ejecutor de subplanes tiene modo seguro sin `--execute` (sin red)
y `--validate-only` para validación de API (sin escrituras persistentes).
`ENABLE` no está permitido en su flujo genérico bajo ninguna modalidad.

**ADVERTENCIA SOBRE SCRIPTS HISTÓRICOS:** El repositorio contiene
ejecutores específicos de clientes que pueden instanciar Google Ads SDK y
llamar métodos `mutate_*` directamente. Estos programas no han pasado una
migración universal a un punto de escritura protegido. **No ejecutarlos con
credenciales de producción**, aunque tengan flags de aprobación, hashes o
mensajes de confirmación. Para inspeccionarlos sin ejecutarlos:

```bash
python scripts/security_inventory.py
```

Se necesita antes de habilitar producción: identidad de aprobador no controlada
por el agente, firma/verificación o autoridad remota de aprobación, vinculación
al hash SHA-256 completo + cliente + servicio + operación + caducidad + nonce,
registro y prevención de reutilización, y credenciales de escritura disponibles
solo a un componente de ejecución aislado. La revisión de un PR no concede
por sí sola permisos de Google Ads.

Los scripts de lectura y planificación siguen siendo la vía recomendada.
No fusionar ni declarar ejecución autónoma segura hasta cerrar los scripts
históricos o retirarlos del entorno con permisos de escritura.
