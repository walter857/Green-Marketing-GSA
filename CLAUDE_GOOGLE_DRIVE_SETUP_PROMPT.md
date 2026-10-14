# Claude Code Prompt: Set Up Google Drive for Landing-Page Delivery

Use this prompt once from the root of the Green Marketing repository. Work through it in order. Do not begin any client-specific landing-page work during this setup.

## Goal and exact authorization

Set up a separate, least-privilege Google Drive and Google Docs connection for this repository, then initialize the approved landing-page folder structure.

This prompt authorizes you to:

1. Inspect the local repository and current Google Cloud CLI configuration without exposing secrets.
2. Confirm the active Google account and Google Cloud project with me.
3. Enable exactly these APIs in the confirmed project:
   - `drive.googleapis.com`
   - `docs.googleapis.com`
4. Open the exact Google Cloud Console pages needed for Google Auth Platform and OAuth client setup.
5. Add local scripts, tests, non-secret configuration, `.gitignore` entries, and dependency declarations required for Drive/Docs authorization and publishing.
6. After I personally complete Google sign-in and OAuth consent, create or reuse the exact Google Drive resources listed in this prompt.
7. Read every external resource back and give me its ID, URL, parent, and verification result.

This prompt does **not** authorize you to:

- Create a new Google Cloud project, change billing, change organization policies, or change unrelated APIs.
- Reuse, print, modify, broaden, or replace the existing Google Ads OAuth refresh token or Application Default Credentials.
- Change sharing permissions, make files public, invite users, or use domain-wide delegation.
- Delete or move any Drive resource.
- Edit WordPress, GTM, WhatConverts, Google Ads, DNS, or any live landing page.
- Start client-specific work without the gate in `CLAUDE.md` and `LANDING_PAGE_CONTENT_WORKFLOW.md`.

## 1. Read the repository rules first

From the repository root:

1. Read `CLAUDE.md` completely.
2. Read `LANDING_PAGE_CONTENT_WORKFLOW.md` completely.
3. Inspect the relevant repository structure, `.gitignore`, dependency files, environment examples, and existing Drive-related scripts.
4. Do not read, print, paste, log, or summarize the contents of credential, token, `.env`, or secret files. You may check whether a configured file path exists.
5. Show me the repository root you detected and confirm that both mandatory files are readable.

If either mandatory file is missing or unreadable, stop and report the exact path.

## 2. Inspect Google Cloud identity before making changes

Use read-only commands first. Prefer these where available:

```powershell
gcloud auth list --filter=status:ACTIVE --format="value(account)"
gcloud config get-value project
gcloud services list --enabled --project=PROJECT_ID
```

Replace `PROJECT_ID` only after resolving the configured project. Do not guess it.

Before enabling an API, show me:

- Active Google account.
- Google Cloud project ID.
- Whether Drive API is already enabled.
- Whether Docs API is already enabled.

If no account is active, multiple identities are ambiguous, the project is missing, or you cannot verify that this is the intended Green Marketing project, stop. Open the appropriate sign-in or project-selection page in Chrome through the configured Chrome DevTools MCP and tell me exactly what I need to select. Never enter my password, passkey, recovery code, or two-factor code.

Do not run `gcloud auth application-default login`. Do not overwrite or broaden existing Application Default Credentials.

## 3. Enable only the two approved APIs

Once the account and project are unambiguous, enable only:

```powershell
gcloud services enable drive.googleapis.com docs.googleapis.com --project=PROJECT_ID
```

If the CLI lacks permission, use Chrome DevTools MCP to open these exact project-scoped pages:

```text
https://console.cloud.google.com/apis/library/drive.googleapis.com?project=PROJECT_ID
https://console.cloud.google.com/apis/library/docs.googleapis.com?project=PROJECT_ID
```

You may navigate to the correct **Enable** control because this prompt authorizes these two APIs. Pause for me if Google requires sign-in, reauthentication, account selection, consent, or another security checkpoint.

Afterward, read the service state back and prove that both APIs are enabled. Do not enable any additional API without a new explicit approval.

## 4. Create a separate Drive OAuth desktop client

Use a separate OAuth client and token for this Drive workflow. Never automatically reuse the Google Ads OAuth client, refresh token, or token file.

Preferred client name:

```text
Green Marketing Drive Automation
```

Open the project-scoped Google Auth Platform pages as needed:

```text
https://console.cloud.google.com/auth/overview?project=PROJECT_ID
https://console.cloud.google.com/auth/clients?project=PROJECT_ID
```

Use an OAuth client of type **Desktop app**. If the consent configuration is not complete:

- Use **Internal** only if this is a Google Workspace project and the app is meant solely for users in that organization.
- Otherwise use **External** and add only my Google account as a test user during setup.
- Do not publish the app or add other users without my explicit approval.

Chrome DevTools MCP may navigate and fill non-secret setup fields. I must personally handle Google sign-in, account selection, reauthentication, consent, and any warning or security checkpoint.

Ask me to download the desktop OAuth JSON to this default local location, or a different outside-repository path I approve:

```text
D:\MG\secrets\green-marketing-drive-client.json
```

The separate token should default to:

```text
D:\MG\secrets\green-marketing-drive-token.json
```

Never place either file inside the repository. Never print their contents. If the paths differ on this machine, use environment variables rather than hard-coding personal paths.

## 5. Implement the local authorization and Drive setup tools

Create or update a small, testable Drive integration that follows the repository's existing language and dependency conventions. If no convention exists, use Python and the official Google client libraries:

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

At minimum, provide equivalent functions or scripts for:

1. `setup_google_drive_oauth` — runs Google's installed-app local-server OAuth flow and stores only the separate Drive token outside the repository.
2. `verify_google_drive_access` — reports the authorized Google account, granted scopes, API availability, and access to the configured root/template without exposing tokens.
3. `initialize_landing_page_drive` — dry-run by default, with an explicit `--apply` mode. Dry-run must write nothing to Drive, Docs, or local configuration.
4. A master-template pipeline that copies the canonical document to a temporary name, scrubs the copy, validates it, and only then renames it. See section 7.
5. Tests for exact-name lookup, duplicate detection, dry-run behavior, folder creation, the temporary-name copy, scrub validation, refusal to create the final master name directly, rename-after-validation ordering, partial-failure reporting, and secret redaction.

Use these configuration names:

```text
GOOGLE_DRIVE_LANDING_PAGE_ROOT_FOLDER_ID
GOOGLE_DOC_LANDING_PAGE_TEMPLATE_ID
GOOGLE_DRIVE_CREDENTIALS_FILE
GOOGLE_DRIVE_TOKEN_FILE
```

Use this canonical source template ID unless the repository already has the same value configured:

```text
1bQR5wLIF47fd-wNOaNxtjlun1ch8Fc5kmfCA93vuFuc
```

Add credential and token filename patterns to `.gitignore`. Put only placeholders and documentation in `.env.example` or equivalent. Do not edit `.env` unless I explicitly approve it during this session.

### OAuth scope rule

Start with the narrow Drive per-file scope and the Docs scope needed to create and edit landing-page documents:

```text
https://www.googleapis.com/auth/drive.file
https://www.googleapis.com/auth/documents
```

Test access to the canonical source template before applying any Drive setup. The narrow `drive.file` scope may not be able to copy a pre-existing template that was not opened or created through this OAuth app.

If the template cannot be accessed because of the scope:

1. Stop before changing scopes or deleting the token.
2. Report the exact API error in redacted form.
3. Offer two explicit choices:
   - Keep least privilege and implement a Google Picker-based one-time template selection/grant.
   - Request my separate approval to use the broader `https://www.googleapis.com/auth/drive` scope and reauthorize only this Drive token.
4. Do not silently escalate to full Drive access.

## 6. Run the user-controlled OAuth step

Run the authorization script only after the implementation and secret-handling checks pass. It should open the Google authorization page in my browser.

Then pause and tell me:

- Which Google account should be selected.
- The exact scopes being requested.
- Why each scope is required.
- That approval applies only to this separate local Drive integration.

I will personally select the account and accept or reject consent. Never ask me to paste a password, authorization code, client secret, access token, refresh token, or downloaded JSON content into chat or the terminal.

After consent, verify without revealing secrets:

- Authorized Google account identity.
- Actual granted scopes.
- Drive API connectivity.
- Docs API connectivity.
- Access result for the canonical template.

Stop if the authorized account is not the account I confirm.

## 7. Preview and initialize the Drive hierarchy

Default to **My Drive** unless I explicitly identify an approved Shared Drive and root. Do not create anything until authorization succeeds and the account is confirmed.

Dry-run is the default. Nothing is written without an explicit `--apply` flag.

First produce a dry-run preview for exactly this structure:

```text
Green Marketing Landing Pages/
  Templates/
    Landing Page Content Template - Master
```

There is no `Clients/` level. `create_clients_folder` remains `false`. Client folders sit
directly under the approved root, so the eventual shape is:

```text
Green Marketing Landing Pages/
  Templates/
  <Client Name>/
    Landing Pages/
```

Creation rules:

1. Search for each exact name only under its expected parent.
2. Reuse one unambiguous matching folder or file.
3. Stop on duplicates, unexpected parents, or ambiguity.
4. Never search or write outside the approved root after its ID is established.
5. Never delete, move, share, or make a resource public.
6. Create the master template by copying the canonical **native Google Doc**, not by rebuilding it as a blank Doc or importing DOCX.
7. Make the operation idempotent so rerunning it does not create duplicates.

### The master template must never be copied straight to its final name

Copying the canonical document directly to `Landing Page Content Template - Master` is
**prohibited**. The canonical document is a completed client example. Its final name is a
promise that every source-client fact has been removed and the structure verified, and that
promise may only be earned by renaming a copy that has already passed both validations.

Required sequence, each step gated by the one before it:

1. Copy the protected canonical document into `Templates/` under the temporary name
   `TEMP - Master Template Scrub In Progress`.
2. Scrub only the TEMP copy.
3. Re-read the TEMP copy from the API. The request list is not proof.
4. Verify zero residual source-client facts.
5. Verify the structural fingerprint against the canonical source.
6. Rename to `Landing Page Content Template - Master` only after both validations pass.
7. Record the verified root-folder ID and master-document ID in `config/google-drive.yaml`.
   Non-secret Drive IDs only, and only after step 6 succeeds.

If a validation fails, stop and leave the copy under its TEMP name. If a TEMP copy already
exists with no validated master, stop and report it for review rather than copying again.
Never delete, trash, move, rename sight unseen, or re-permission anything to recover.

This prompt authorizes `--apply` for only the resources shown above — the root folder, the
Templates folder, and one document that is born as `TEMP - Master Template Scrub In
Progress` and renamed after validation — after the dry-run matches exactly and the account
and project were confirmed. If any extra resource would be created or modified, stop and
request approval.

After creation or reuse, read back and report:

- Resource name and MIME type.
- Resource ID.
- Web URL.
- Parent ID.
- Created versus reused.
- Template native-Doc status.
- Confirmation that no document remains under the TEMP name.
- Verification result.

Save the non-secret root folder ID and scrubbed master template ID in the repository's established non-secret configuration location, as step 7 of the sequence above, and only after both validations pass. Do not save tokens or secrets there.

Future client work must create content only below:

```text
Green Marketing Landing Pages/
  <Client Business Name>/
    Landing Pages/
      <Campaign Name>/
        <Ad Group Name>/
          <Client> - <Campaign> - <Ad Group> - Landing Page Content
          Images/
```

Client folders are direct children of the approved root. Do not insert a `Clients/` level.

Do not create a future client hierarchy during this one-time setup.

## 8. Image behavior

Prepare future Drive publishing to upload approved image files into the ad group's `Images` folder and add the Drive link, filename, dimensions, crop guidance, usage, and alt text to the content document.

Do not make a private image public merely to force inline insertion. Google Docs inline image insertion requires an image URL that Google's fetcher can retrieve. When secure inline insertion is unavailable, use the Drive link and full image brief. Never claim an image was embedded unless document readback confirms an inline image object.

## 9. Verification and final report

Before declaring setup complete:

1. Run relevant tests.
2. Run the authorization verifier.
3. Run the initializer again in dry-run mode and prove it now plans zero new resources.
4. Check `git status` and confirm no credential or token file is tracked.
5. Confirm the existing Google Ads auth and Application Default Credentials were not changed.
6. Confirm no sharing permission, public link, client folder, live site, tracking, or Google Ads resource changed.

Give me a concise final report containing:

- Confirmed Google account and project ID.
- Enabled API readback.
- OAuth client type and granted scopes.
- Local files added or changed.
- Tests and results.
- Drive root, Templates folder, and master template IDs/URLs, plus confirmation that no `Clients` folder was created.
- Any manual step I completed.
- Any blocker, especially a least-privilege template-access limitation.
- The exact command Claude should use later to dry-run a client landing-page Drive delivery.

If a write partially succeeds, stop immediately, inventory every created resource ID, and propose a recovery plan. Do not blindly rerun.
