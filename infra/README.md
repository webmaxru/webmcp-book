# infra/

Azure Static Web Apps hosting for the web edition. **Start with [../DEPLOY.md](../DEPLOY.md)** (the one command, cost, secrets, rollback, teardown) and [../CUSTOM-DOMAIN.md](../CUSTOM-DOMAIN.md) (webmcp.salnikov.no).

```bash
./infra/deploy.sh                     # macOS / Linux / WSL
pwsh ./infra/deploy.ps1               # Windows (PowerShell 5.1 or 7)
```

## Editing the headers

`staticwebapp.config.json` (repo root) sets a strict Content-Security-Policy: everything from the site itself, no third-party hosts, and the one inline script (the theme bootstrap in `<head>` that applies the saved light/dark choice before the first paint) allowed by its SHA-256 hash. When the theme changes that inline script, the hash changes and `check_site.py` stops the upload. Fix it with:

```bash
python3 tools/build.py site && python3 infra/check_site.py dist/site --update-csp
```

then commit `staticwebapp.config.json`. If the theme starts loading something from another host (a font CDN, an analytics script), add that host to the matching CSP directive; the check names the directive.

## How it was tested (2026-11-02, before any real Azure run)

- `bicep build` and `bicep lint` (Bicep CLI 0.48.1) on `main.bicep` and `budget.bicep`, and `bicep build-params` on `main.bicepparam`: no errors, no warnings.
- `deploy.sh` and `teardown.sh`: `bash -n` and ShellCheck 0.11.0 at `-S style`: clean.
- `deploy.ps1` and `teardown.ps1`: ASCII-only (Windows PowerShell 5.1 safe) and parsed clean by PowerShell 7.6.9's parser. A first stub run caught a Set-StrictMode crash in the option check (fixed). A full stub run of `deploy.ps1` could not finish on the build machine, so the PowerShell flow past that point has not been executed yet. `.github/workflows/infra.yml` parses both scripts with Windows PowerShell 5.1 and PowerShell 7 and runs PSScriptAnalyzer on every change.
- `deploy.sh` end to end against stand-in `az`, `gh`, `npx`, `curl` and `dig` commands: all steps in order, with the custom domain bound; the deployment token reached `gh` only through stdin and the upload only through `SWA_CLI_DEPLOYMENT_TOKEN`, and appeared in no output or command line. Also checked: the "proxied in Cloudflare / no CNAME yet" path, conflicting and missing option values, and `teardown.sh` with and without the typed confirmation.
- `.github/workflows/deploy-swa.yml`: valid YAML; action inputs checked against `Azure/static-web-apps-deploy`'s `action.yml`.
- `staticwebapp.config.json`: valid against the schemastore.org schema.
- Static Web Apps CLI 2.1.0: `swa deploy ./site --env production --swa-config-location ./site` with a dummy token: picked up the config file, chose production, did not prompt, and exited 1 when the service rejected the token (so the script's error path works). Note: `--dry-run` in 2.1.0 still contacts the service and exits 0, so the scripts don't use it.
- The built site (31 pages) served locally with the config's headers and 404 rule applied, opened in headless Chromium: 0 CSP violations, 0 console errors, fonts load, the theme toggle and its inline bootstrap work, search loads its index, a missing page returns the book's 404 page with status 404.
- Not tested: anything against real Azure (resource creation, token read, the upload, the custom-domain binding) and the GitHub Actions run. The first real run is yours.
