# Claude Code Start Guide for Windows

1. Extract the ZIP to a dedicated folder such as:

   ```text
   C:\GreenMarketing\green-marketing-gsa
   ```

2. Open PowerShell in that folder.

3. Create the local environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   py -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

4. Open `.env` locally and add the Green Marketing agency credentials. Do not paste them into Claude or ChatGPT.

5. Create the first client folder:

   ```powershell
   Copy-Item -Recurse clients\_template clients\example-landscape
   ```

6. Complete the non-secret client facts in `client.yaml` and `work-order.yaml`. The exact child account name, 10-digit child customer ID, and exact service are mandatory.

7. Run the offline checks:

   ```powershell
   $env:PYTHONPATH = "src"
   py -m unittest discover -s tests -v
   py scripts\validate_work_order.py clients\example-landscape\work-order.yaml --client clients\example-landscape\client.yaml
   py scripts\verify_setup.py --client clients\example-landscape\client.yaml
   ```

8. Start Claude Code from the repository root:

   ```powershell
   claude
   ```

9. First prompt:

   ```text
   Read CLAUDE.md and use the green-marketing-gsa skill. Validate
   clients/example-landscape/work-order.yaml against client.yaml. If the exact
   child account name, 10-digit child customer ID, or exact service is missing,
   ask for it and stop. Make no external changes.
   ```

10. After the work order and profile are complete, run read-only identity verification and snapshot workflows before planning a campaign.

Keep the project in version control so every plan, script, and safety-rule change can be reviewed and reverted. Never commit `.env`, OAuth files, downloaded credentials, snapshots containing lead PII, or production webhooks.
