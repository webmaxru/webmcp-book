# Deploying the web edition to Azure Static Web Apps

The free web edition of the book (`python3 tools/build.py site` → `dist/site/`) is hosted on an **Azure Static Web App on the Free plan**. It's uploaded with the app's deployment token, so it doesn't depend on the repo being public, on GitHub Pages, or on Azure's GitHub app. The repo stays private.

## Prerequisites

- An Azure subscription where you can create a resource group (Contributor or Owner).
- **Azure CLI**, a current release (the latest when this was written: 2.91.0; `az upgrade` updates it), logged in with `az login`. The script installs Bicep through `az bicep install` if it's missing.
- **Python 3.11+** for the build (`tools/requirements.txt` is installed into `.venv/` by the script).
- **Node.js 20+** (18 is the minimum) for the upload: the script runs the Static Web Apps CLI `2.1.0` through `npx`, and on its first upload the CLI downloads Microsoft's deployment client (about 70 MB, kept in `~/.swa`).
- Optional: **GitHub CLI** (`gh auth login`) with admin rights on `webmaxru/webmcp-book`, so the script can store the deployment token as a repository secret. Without it, the script prints the two manual steps.
- Windows: use `infra/deploy.ps1` (Windows PowerShell 5.1 or PowerShell 7). macOS/Linux/WSL: `infra/deploy.sh`.

## The one command

```bash
./infra/deploy.sh
```

```powershell
pwsh ./infra/deploy.ps1          # or: powershell -ExecutionPolicy Bypass -File .\infra\deploy.ps1
```

It shows the subscription and asks before changing anything (`--yes` / `-Yes` skips the question). Then: tools and login check → resource group `rg-webmcp-book` → `infra/main.bicep` (Static Web App `swa-webmcp-book`, Free, West Europe) → site build → pre-upload check (`infra/check_site.py`: Free-plan limits, and that the Content-Security-Policy allows exactly what the pages load) → upload to production → GitHub secret → `curl` checks that `/` answers 200 and a missing page answers 404 → prints the URL.

Safe to re-run. Useful options (`--help` lists all):

| bash | PowerShell | What |
| --- | --- | --- |
| `--custom-domain webmcp.salnikov.no` | `-CustomDomain ...` | Bind the domain after checking its CNAME. See [CUSTOM-DOMAIN.md](CUSTOM-DOMAIN.md). |
| `--upload-only` | `-UploadOnly` | App exists: build and upload only. |
| `--no-build` | `-NoBuild` | Upload `dist/site` as it is. |
| `--infra-only` | `-InfraOnly` | Azure resources + GitHub secret, no build or upload. |
| `--build-only` | `-BuildOnly` | Build locally, touch nothing in Azure. |
| `--skip-github` | `-SkipGitHub` | Don't set the GitHub secret. |
| `--budget-email you@example.com` | `-BudgetEmail ...` | Add a monthly budget alert (default 1 per month in your billing currency). |
| `--subscription <id>`, `--location`, `--resource-group`, `--swa-name`, `--repo` | same names | Override the defaults. |

Static Web Apps accepts only `westeurope`, `eastus2`, `centralus`, `westus2` and `eastasia` as the resource's region (West Europe is the closest to Norway). The content itself is served from a global edge.

## What it creates and what it costs

| Resource | Notes |
| --- | --- |
| Resource group `rg-webmcp-book` | Holds everything below; teardown deletes it. |
| Static Web App `swa-webmcp-book`, **Free** plan | No repository link, preview environments off. |
| Custom domain binding (optional) | Free managed TLS certificate. |
| Budget `budget-webmcp-book` (optional) | Email at 80 % actual and 100 % forecast. Alerts only. |
| GitHub secret `AZURE_STATIC_WEB_APPS_API_TOKEN` | On `webmaxru/webmcp-book`. |

**Cost: 0.** The Free plan has no charge, and overage bandwidth is listed as unavailable on Free, so there is nothing that can be billed. Free plan limits ([quotas](https://learn.microsoft.com/en-us/azure/static-web-apps/quotas), [plans](https://learn.microsoft.com/en-us/azure/static-web-apps/plans), read 2026-11-02):

- 100 GB bandwidth per month per subscription, overage "unavailable" on Free
- 250 MB storage per environment (500 MB across all environments), 15,000 files, 30 MB request size
- 2 custom domains per app, free auto-renewing SSL certificates
- 10 Free apps per subscription, 3 preview environments per app
- No SLA

The current site is about 14 MB and 90 files, well inside these limits; `infra/check_site.py` fails the upload before a limit is hit.

## Secrets

Exactly one: **`AZURE_STATIC_WEB_APPS_API_TOKEN`**, the Static Web App's deployment token, as a GitHub Actions repository secret.

- The script reads it with `az staticwebapp secrets list` into memory and pipes it to `gh secret set`. It's never printed, never on a command line, never in a file.
- By hand: `az staticwebapp secrets list -n swa-webmcp-book -g rg-webmcp-book --query properties.apiKey -o tsv | pbcopy` (Windows: `| Set-Clipboard`), or Portal → the Static Web App → Overview → **Manage deployment token** → copy. Then GitHub → repo Settings → Secrets and variables → Actions → **New repository secret**, name `AZURE_STATIC_WEB_APPS_API_TOKEN`.
- If it ever leaks: Portal → Manage deployment token → **Reset token**, then re-run `./infra/deploy.sh --infra-only` to store the new one.

No other secrets, variables or Azure credentials are used. The workflow uses only this token.

## How GitHub deploys after the first run

`.github/workflows/deploy-swa.yml` builds the site and uploads it with `Azure/static-web-apps-deploy@v1` (pinned to a commit). **Production serves released editions only.** Its first job, `published-source`, decides what may be deployed before anything is built, from the GitHub Releases and tags (`tools/book_release.py`). It runs on:

- **A release.** **Release book** dispatches `deploy-swa` with `ref=vX.Y.Z` right after it publishes a stable version that is the highest one, waits for that run, and checks that its smoke test actually passed. Prereleases do not deploy.
- **A push to `main`.** It deploys `main` only while its book content equals the latest published release. What counts as book content is defined once, in `tools/release_policy.py`, not as path patterns in the workflow. A theme, tooling or infrastructure change therefore deploys, and unreleased manuscript content does not: when a content PR was merged by hand, the run is skipped (green, with a notice) until a catch-up release publishes it. See [RELEASING.md](RELEASING.md#10-a-manual-merge-by-mistake).
- **Run workflow** in the Actions tab, with the required `ref`: a published release tag or the full SHA of its commit. Branches, drafts, prereleases and unreleased commits are refused.

The [approved content flow](RELEASING.md) does not rely on a bot merge or tag push triggering another workflow, which is why **Release book** dispatches the deploy itself.

Without the secret (a fork, a fresh clone), `deploy-swa` skips with a notice. The release controller treats a skipped smoke test as a failed deployment. Runs never overlap (concurrency group `swa-production`). The run summary shows the URL and the status codes of `/` and a missing page.

## Rolling back

Actions → **deploy-swa** → **Run workflow** → `ref` = the release tag to go back to (for example `v2.0.0`), or the full SHA of its commit → Run. It checks that the ref is a published release, checks it out, builds it and uploads it to production. A branch, a draft, a prerelease, a bare tag or an unreleased commit is refused. Only refs that contain `tools/build.py` (v2.0.0 and later) can be built by this workflow; v1.0.0 was the old GitHub Pages site and has a tag but no release, so it is refused.

A rollback lasts until the next deploy: the next release, or a push to `main` that the gate allows (its content equals the latest release, as after a tooling merge). Roll forward by running the workflow with a newer release tag. A push to `main` does not roll forward while `main` carries unreleased content, because the gate skips it. The lasting fix for a bad edition is a new version ([RELEASING.md](RELEASING.md#15-a-published-release-is-wrong)).

Locally: `git checkout v2.0.0 && ./infra/deploy.sh --upload-only`.

## Tear down

```bash
./infra/teardown.sh                          # lists the group's contents, asks you to type its name
./infra/teardown.sh --remove-github-secret   # also removes the GitHub secret
```

```powershell
pwsh ./infra/teardown.ps1 [-RemoveGitHubSecret]
```

It deletes the resource group `rg-webmcp-book` with the Static Web App, its domain binding and the budget. Your DNS record isn't touched: delete the `webmcp` CNAME in Cloudflare yourself.

## Files

| File | What |
| --- | --- |
| `infra/deploy.sh`, `infra/deploy.ps1` | The one command (bash / PowerShell twins). |
| `infra/teardown.sh`, `infra/teardown.ps1` | Delete everything. |
| `infra/main.bicep` | Static Web App (Free) + optional custom domain + optional budget module. |
| `infra/budget.bicep` | Monthly budget with email alerts. |
| `infra/main.bicepparam` | Parameters for a direct `az deployment group create` without the script. |
| `infra/check_site.py` | Pre-upload check (limits, CSP vs. pages); `--update-csp` refreshes the inline-script hashes. |
| `staticwebapp.config.json` | Headers (CSP, HSTS, nosniff, referrer and permissions policy), caching, the 404 page, MIME types. Copied into `dist/site/` by the build. |
| `.github/workflows/deploy-swa.yml` | The `published-source` gate, then build + upload: a release's own tag, a push to `main` whose content is released, or a manual run of a released ref. |
| `.github/workflows/infra.yml` | No-login validation of the infra files: Bicep build + lint, PowerShell parse (5.1 and 7), PSScriptAnalyzer, ShellCheck. |
| `CUSTOM-DOMAIN.md` | webmcp.salnikov.no step by step. |
