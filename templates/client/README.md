# Client Folder

Create one folder per client under `clients/<client-slug>/` by copying `clients/_template/`. Complete `client.yaml` and one `work-order.yaml` per task.

Do not begin client work until the work order contains the exact child account name, 10-digit child customer ID, and exact service and passes `scripts/validate_work_order.py`.

Never store secrets in a client folder. Use environment-variable names for webhooks and tokens. Keep account snapshots and exports in the ignored `snapshots/` and `exports/` subfolders.
