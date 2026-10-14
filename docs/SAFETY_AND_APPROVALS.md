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
