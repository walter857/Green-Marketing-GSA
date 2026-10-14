# List Eligible Live Client Accounts

Run the read-only client discovery workflow using the Green Marketing MCC.

Before querying the MCC, require the user's intended exact child account name, 10-digit child customer ID, and exact service. Use the list only to verify that identity, never to choose a client by guesswork.

- Filter descriptive names containing `- live`, case-insensitive.
- Exclude manager and test accounts.
- Return account name, 10-digit customer ID, hierarchy level, currency, and time zone where available.
- Do not select an account automatically.
- Compare the observed target name and ID with the validated work order and client profile.
- Do not make any Google Ads changes.
