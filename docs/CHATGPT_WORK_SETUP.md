# Recommended ChatGPT Setup

## Best setting for the initial build

- Surface: **ChatGPT Work**, inside a project.
- Model: **GPT-5.6 Sol**.
- Reasoning effort: **Extra High**.
- Speed: **Standard/normal**, not Fast.

Use Ultra only for a portfolio-wide audit or a large, divisible migration. Use Max only when one very difficult decision needs more depth than speed. For daily account work, GPT-5.6 Sol at Medium or High is usually enough.

## Why Work instead of Chat

Use Chat for questions, explanations, brainstorming, or one short draft. This system needs a persistent project, many source files, local code, generated artifacts, verification, and multi-step workflows, so Work is the correct surface.

## Project creation

1. Create a project named `GM | Google Ads Operating System`.
2. In the desktop app, add the unzipped folder as a local project and make it the primary folder.
3. Paste `project-instructions/CHATGPT_PROJECT_INSTRUCTIONS.md` into Project instructions.
4. Keep one chat per distinct outcome, for example:
   - `Example Landscape | Account audit`
   - `Example Landscape | Paver patio campaign build`
   - `Example HVAC | AC repair conversion QA`
5. Keep credentials only in the local `.env`; do not upload them as project sources.
6. Attach the Google Drive plugin when the task depends on client Docs or reports.

Start each client chat with `project-instructions/NEW_CLIENT_STARTER_PROMPT.md`. The chat must collect the exact child account name, 10-digit child customer ID, and exact service before doing any client work.

A regular web ChatGPT Project can share uploaded files and instructions, but it does not automatically provide access to a folder on the computer. Use a local Work project or run Claude Code from the unzipped directory when file and code execution is required.

## Recommended settings by task

| Task | Model | Effort | Speed |
|---|---|---|---|
| Initial system setup and source synthesis | GPT-5.6 Sol | Extra High | Standard |
| New client architecture or full account rebuild | GPT-5.6 Sol | High or Extra High | Standard |
| Routine audits, reports, QA, and code edits | GPT-5.6 Sol | Medium or High | Standard |
| Repetitive extraction or formatting | GPT-5.6 Terra | Medium | Fast if available |
| Portfolio-wide parallel audit | GPT-5.6 Sol | Ultra | Standard |

## Permissions

Start with the default sandbox and approval settings. Give write access only to this project folder. External Google Ads writes should remain approval-gated even if the local folder is trusted.
