Setting GitHub Secrets (gh CLI)

Use the GitHub CLI (`gh`) to add the required repository secrets for automatic Fly deployments.
Ensure you are authenticated with `gh auth login` and have owner/maintainer rights on the repo.

Commands:

```bash
# Set Fly API token (secret value shown interactively)
gh secret set FLY_API_TOKEN --repo hhool/site-ytmp3

# Set Fly app name
gh secret set FLY_APP_NAME --body "your-fly-app-name" --repo hhool/site-ytmp3

# Optional: verify secrets
gh secret list --repo hhool/site-ytmp3
```

Notes:
- `FLY_API_TOKEN` must be a Fly personal API token (see https://fly.io/docs/hands-on/install-flyctl/#get-an-api-token).
- `FLY_APP_NAME` is the application name you created on Fly; the Actions workflow will use it to deploy.
- Do NOT share your secrets in plaintext; use the `gh` interactive command which securely uploads them.

Triggering deploy:
- After adding the secrets, push a commit to `main` (or re-run the workflow) to let Actions build and deploy automatically.
