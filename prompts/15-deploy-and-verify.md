# Deploy a Landing Page and Verify It

Validate the current work order first and confirm the deployment is for the exact client and service.

Read the repository, hosting ownership, domain, environment variables, and approval boundaries.

Before deployment:

- Run lint, type checks, tests, production build, accessibility checks, mobile review, and broken-link checks.
- Verify no secrets or test PII are committed.
- Verify robots/canonical behavior matches the intended paid landing-page strategy.
- Verify form webhook, click-to-call, thank-you redirect, GCLID/UTM persistence, consent, and conversion deduplication.
- Confirm the final URL returns 200 over HTTPS and loads on mobile.
- Create a Git checkpoint and show the deployment plan.

Pushing to GitHub, connecting Vercel, changing DNS, or publishing a production deployment are external actions and require explicit approval. After deployment, verify live tracking with test data and mark test leads so they can be excluded.
