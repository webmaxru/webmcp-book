#!/usr/bin/env bash
# One command to put the web edition of "Tools, Not Clicks" on Azure Static Web Apps (Free).
# macOS / Linux / WSL. Windows: infra/deploy.ps1 does the same.
#
#   ./infra/deploy.sh                                  # infra + build + upload + GitHub secret
#   ./infra/deploy.sh --custom-domain webmcp.salnikov.no   # ...and bind the domain (CNAME first!)
#
# Safe to re-run: the resource group and the app are created once and updated in place,
# the deployment token stays the same, the site is re-uploaded.
#
# Options (defaults in brackets):
#   --resource-group NAME  [rg-webmcp-book]     --swa-name NAME    [swa-webmcp-book]
#   --location REGION      [westeurope]         --repo OWNER/NAME  [vibeprogrammer/webmcp-book]
#   --subscription ID      switch the Azure subscription first
#   --custom-domain HOST   bind HOST (its CNAME must already point at the app, CUSTOM-DOMAIN.md)
#   --budget-email EMAIL   add a monthly budget alert   --budget-amount N [1]
#   --skip-github          don't set the GitHub secret (print the manual step instead)
#   --build-only           only build dist/site locally; nothing in Azure
#   --infra-only           Azure resources + GitHub secret; no build, no upload
#   --upload-only          the app must exist: build + upload only (no Bicep deployment)
#   --no-build             upload dist/site as it is (skip the Python build)
#   --yes, -y              don't ask before changing Azure
#   -h, --help
set -euo pipefail

RG=rg-webmcp-book; SWA=swa-webmcp-book; LOCATION=westeurope; REPO=vibeprogrammer/webmcp-book
SUBSCRIPTION=""; CUSTOM_DOMAIN=""; BUDGET_EMAIL=""; BUDGET_AMOUNT=1; BUDGET_NAME=budget-webmcp-book
YES=0; SKIP_GH=0; BUILD_ONLY=0; INFRA_ONLY=0; UPLOAD_ONLY=0; NO_BUILD=0
SWA_CLI_VERSION=2.1.0              # @azure/static-web-apps-cli, pinned
SECRET_NAME=AZURE_STATIC_WEB_APPS_API_TOKEN

need_arg() { [ $# -ge 2 ] && [ -n "$2" ] || { echo "Option $1 needs a value" >&2; exit 2; }; }
while [ $# -gt 0 ]; do
  case "$1" in
    --resource-group) need_arg "$@"; RG=$2; shift 2;;
    --swa-name) need_arg "$@"; SWA=$2; shift 2;;
    --location) need_arg "$@"; LOCATION=$2; shift 2;;
    --repo) need_arg "$@"; REPO=$2; shift 2;;
    --subscription) need_arg "$@"; SUBSCRIPTION=$2; shift 2;;
    --custom-domain) need_arg "$@"; CUSTOM_DOMAIN=$2; shift 2;;
    --budget-email) need_arg "$@"; BUDGET_EMAIL=$2; shift 2;;
    --budget-amount) need_arg "$@"; BUDGET_AMOUNT=$2; shift 2;;
    --skip-github) SKIP_GH=1; shift;;
    --build-only) BUILD_ONLY=1; shift;;
    --infra-only) INFRA_ONLY=1; shift;;
    --upload-only) UPLOAD_ONLY=1; shift;;
    --no-build) NO_BUILD=1; shift;;
    --yes|-y) YES=1; shift;;
    -h|--help) sed -n '2,26p' "$0"; exit 0;;
    *) echo "Unknown option: $1 (see --help)" >&2; exit 2;;
  esac
done
if [ $((BUILD_ONLY + INFRA_ONLY + UPLOAD_ONLY)) -gt 1 ]; then
  echo "Use only one of --build-only, --infra-only, --upload-only" >&2; exit 2
fi
CUSTOM_DOMAIN=$(printf '%s' "$CUSTOM_DOMAIN" | tr '[:upper:]' '[:lower:]' | sed 's#^https\?://##; s#/.*$##; s#\.$##')

INFRA_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$INFRA_DIR/.." && pwd)"
SITE_DIR="$ROOT/dist/site"
STAMP=$(date +%Y%m%d-%H%M%S)
TOKEN=""
DOMAIN_READY=0
trap 'TOKEN=""; unset TOKEN' EXIT

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then c() { printf '\033[%sm%s\033[0m\n' "$1" "$2"; }
else c() { printf '%s\n' "$2"; }; fi
step() { echo; c 36 "== $1"; }
ok()   { c 32 "   OK   $1"; }
info() { c 90 "   ..   $1"; }
warn() { c 33 "   WARN $1"; }
die()  { echo; c 31 "ERROR: $1"; [ -n "${2:-}" ] && c 33 "Next:  $2"; exit 1; }

DO_AZURE=1; DO_INFRA=1; DO_BUILD=1; DO_UPLOAD=1
[ $BUILD_ONLY = 1 ] && { DO_AZURE=0; DO_INFRA=0; DO_UPLOAD=0; }
[ $INFRA_ONLY = 1 ] && { DO_BUILD=0; DO_UPLOAD=0; }
[ $UPLOAD_ONLY = 1 ] && DO_INFRA=0
[ $NO_BUILD = 1 ] && DO_BUILD=0

c 1 "Tools, Not Clicks: web edition -> Azure Static Web Apps (Free)"

# --------------------------------------------------------------------------------------
step "Checking tools"
if [ $DO_AZURE = 1 ]; then
  command -v az >/dev/null || die "Azure CLI (az) is not installed." \
    "macOS: brew install azure-cli | Linux: https://learn.microsoft.com/cli/azure/install-azure-cli | then az login"
  ok "Azure CLI $(az version --query '"azure-cli"' -o tsv 2>/dev/null || echo '?')"
  if [ $DO_INFRA = 1 ]; then
    az bicep version --only-show-errors >/dev/null 2>&1 || { info "installing Bicep"; az bicep install --only-show-errors; }
    ok "Bicep"
  fi
fi
if [ $DO_BUILD = 1 ]; then
  command -v python3 >/dev/null || die "python3 is not installed." "Install Python 3.11+ (brew install python@3.12)"
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' \
    || die "Python 3.11+ is needed (found $(python3 -V 2>&1))." "brew install python@3.12, or use pyenv"
  [ -f "$ROOT/tools/build.py" ] || die "tools/build.py not found under $ROOT." "Run this script from a full clone of the book repo."
  ok "$(python3 -V)"
fi
if [ $DO_UPLOAD = 1 ]; then
  command -v npx >/dev/null || die "Node.js (npx) is not installed; the upload uses the Static Web Apps CLI." "Install Node 20+ (brew install node@20)"
  NODE_MAJOR=$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)
  [ "$NODE_MAJOR" -ge 18 ] || die "Node 18+ is needed for the Static Web Apps CLI (found $(node -v 2>/dev/null || echo none))." "Install Node 20+"
  ok "Node $(node -v), Static Web Apps CLI $SWA_CLI_VERSION via npx"
  command -v curl >/dev/null || die "curl is not installed."
fi
USE_GH=0
if [ $DO_AZURE = 1 ] && [ $SKIP_GH = 0 ]; then
  if ! command -v gh >/dev/null; then warn "gh not found: the GitHub secret step will be printed for you"
  elif ! gh auth status --hostname github.com >/dev/null 2>&1; then warn "gh is not logged in (gh auth login): the GitHub secret step will be printed"
  else USE_GH=1; ok "GitHub CLI logged in"; fi
fi

# --------------------------------------------------------------------------------------
if [ $DO_AZURE = 1 ]; then
  step "Azure login and subscription"
  if [ -n "$SUBSCRIPTION" ]; then
    az account set --subscription "$SUBSCRIPTION" --only-show-errors || die "Could not switch to subscription $SUBSCRIPTION." "az account list -o table"
  fi
  SUB_ID=$(az account show --query id -o tsv --only-show-errors 2>/dev/null) || die "You are not logged in to Azure." "az login"
  ok "Subscription: $(az account show --query name -o tsv --only-show-errors) ($SUB_ID)"
  info "Resource group $RG | Static Web App $SWA ($LOCATION, Free) | domain: ${CUSTOM_DOMAIN:-none} | budget: ${BUDGET_EMAIL:-none}"
  if [ $YES = 0 ]; then
    read -r -p "   Continue with this subscription? [y/N] " a
    case "$a" in y|Y|yes|YES) ;; *) echo "Stopped. Nothing changed."; exit 0;; esac
  fi
fi

if [ $DO_INFRA = 1 ]; then
  step "Resource group $RG"
  if [ "$(az group exists -n "$RG" --only-show-errors)" = true ]; then ok "exists (left as is)"
  else
    az group create -n "$RG" -l "$LOCATION" --tags project=webmcp-book managedBy=bicep -o none --only-show-errors \
      || die "Could not create resource group $RG." "You need Contributor (or Owner) on the subscription, or create the group first and get Contributor on it."
    ok "created in $LOCATION"
  fi

  step "Static Web App $SWA (Free plan)"
  info "deploying infra/main.bicep (about a minute)"
  # The custom domain is bound further down with the Azure CLI, after its CNAME is checked,
  # so a missing DNS record can't fail the deployment itself.
  HOST=$(az deployment group create -g "$RG" -n "webmcp-book-$STAMP" -f "$INFRA_DIR/main.bicep" --only-show-errors \
           -p swaName="$SWA" location="$LOCATION" \
           --query properties.outputs.defaultHostname.value -o tsv) \
    || die "Deploying main.bicep failed (see above)." "Contributor on $RG is needed; --location must be westeurope, eastus2, centralus, westus2 or eastasia; an app name already used in another group fails too. Safe to re-run."
  ok "ready: https://$HOST"

  if [ -n "$BUDGET_EMAIL" ]; then
    step "Monthly budget alert"
    URL="/subscriptions/$SUB_ID/resourceGroups/$RG/providers/Microsoft.Consumption/budgets/$BUDGET_NAME?api-version=2023-11-01"
    START=$(az rest --method get --url "$URL" --query properties.timePeriod.startDate -o tsv --only-show-errors 2>/dev/null | cut -c1-10 || true)
    START=${START:-$(date -u +%Y-%m-01)}
    if az deployment group create -g "$RG" -n "webmcp-book-budget-$STAMP" -f "$INFRA_DIR/budget.bicep" -o none --only-show-errors \
         -p budgetName="$BUDGET_NAME" amount="$BUDGET_AMOUNT" contactEmail="$BUDGET_EMAIL" startDate="$START"; then
      ok "budget $BUDGET_NAME: $BUDGET_AMOUNT/month (billing currency), alerts at 80% actual and 100% forecast to $BUDGET_EMAIL"
    else
      warn "budget not created (the site is fine). Portal: Cost Management > Budgets > + Add, scope $RG"
    fi
  fi
elif [ $DO_AZURE = 1 ]; then
  step "Static Web App $SWA"
  HOST=$(az staticwebapp show -n "$SWA" -g "$RG" --query defaultHostname -o tsv --only-show-errors 2>/dev/null) \
    || die "Static Web App $SWA not found in $RG." "Run ./infra/deploy.sh without --upload-only once."
  ok "found: https://$HOST"
fi

if [ $DO_AZURE = 1 ]; then
  # Read once into a variable. Never printed, never on a command line, never in a file.
  TOKEN=$(az staticwebapp secrets list -n "$SWA" -g "$RG" --query properties.apiKey -o tsv --only-show-errors) \
    || die "Could not read the deployment token of $SWA." "You need Contributor on $RG."
  [ -n "$TOKEN" ] || die "The deployment token came back empty." "Portal: $SWA > Overview > Manage deployment token, then re-run."
fi

# --------------------------------------------------------------------------------------
if [ $DO_BUILD = 1 ]; then
  step "Building the site (python3 tools/build.py site)"
  VENV="$ROOT/.venv"
  REQ="$ROOT/tools/requirements.txt"
  [ -f "$ROOT/tools/requirements-site.txt" ] && REQ="$ROOT/tools/requirements-site.txt"
  if [ ! -x "$VENV/bin/python" ]; then python3 -m venv "$VENV" || die "Could not create $VENV." "Debian/Ubuntu: sudo apt install python3-venv"; fi
  "$VENV/bin/python" -m pip install --quiet --upgrade pip >/dev/null
  if [ -f "$REQ" ]; then
    "$VENV/bin/python" -m pip install --quiet -r "$REQ" || die "pip install -r ${REQ#"$ROOT"/} failed (see above)."
  fi
  (cd "$ROOT" && "$VENV/bin/python" tools/build.py site) || die "The site build failed (see above)." "Fix it, then re-run with --upload-only."
fi

if [ $DO_UPLOAD = 1 ] || [ $BUILD_ONLY = 1 ]; then
  [ -f "$SITE_DIR/index.html" ] || die "dist/site/index.html is missing." "Build first: python3 tools/build.py site"
  if [ -f "$ROOT/staticwebapp.config.json" ] && [ ! -f "$SITE_DIR/staticwebapp.config.json" ]; then
    cp "$ROOT/staticwebapp.config.json" "$SITE_DIR/"
  fi
  FILES=$(find "$SITE_DIR" -type f | wc -l | tr -d ' ')
  SIZE=$(du -sk "$SITE_DIR" | cut -f1)
  ok "dist/site: $FILES files, $((SIZE / 1024)) MB (Free plan limits: 250 MB per environment, 15,000 files)"
  [ "$SIZE" -lt 250000 ] || die "dist/site is larger than the Free plan's 250 MB." "Shrink images or move to the Standard plan."
  if command -v python3 >/dev/null; then
    python3 "$INFRA_DIR/check_site.py" "$SITE_DIR" \
      || die "The pre-upload check failed (see above): the live site would break or the headers would block something." \
             "python3 infra/check_site.py dist/site --update-csp fixes inline-script hashes; other findings need a change in theme/ or staticwebapp.config.json."
  else
    warn "python3 not found: skipped infra/check_site.py"
  fi
fi
if [ $BUILD_ONLY = 1 ]; then
  echo; c 32 "Built. Preview locally: python3 -m http.server -d dist/site 8080  (then http://localhost:8080)"
  exit 0
fi

# --------------------------------------------------------------------------------------
if [ $DO_UPLOAD = 1 ]; then
  step "Uploading dist/site to production"
  # The token travels in the environment variable the CLI reads, not on the command line.
  (cd "$ROOT" && SWA_CLI_DEPLOYMENT_TOKEN="$TOKEN" npx --yes "@azure/static-web-apps-cli@$SWA_CLI_VERSION" \
      deploy ./dist/site --env production --swa-config-location ./dist/site) \
    || die "The upload failed (see above)." "Re-run with --upload-only --no-build to retry the upload."
  ok "uploaded"
fi

# --------------------------------------------------------------------------------------
if [ $DO_AZURE = 1 ]; then
  step "GitHub: $SECRET_NAME on $REPO"
  if [ $USE_GH = 1 ] && printf '%s' "$TOKEN" | gh secret set "$SECRET_NAME" --repo "$REPO" >/dev/null; then
    ok "secret set; pushes to main and releases now deploy through .github/workflows/deploy-swa.yml"
  else
    [ $USE_GH = 1 ] && warn "gh could not set the secret (you need admin rights on $REPO)."
    warn "Set it by hand so GitHub can deploy (the token goes to your clipboard, not the screen):"
    echo "     1. az staticwebapp secrets list -n $SWA -g $RG --query properties.apiKey -o tsv | pbcopy   (Linux: xclip -sel clip)"
    echo "     2. https://github.com/$REPO/settings/secrets/actions > New repository secret"
    echo "        Name: $SECRET_NAME   Secret: paste > Add secret"
  fi
fi
TOKEN=""

# --------------------------------------------------------------------------------------
check_url() { # $1 = url, $2 = expected status
  local code=""
  for _ in 1 2 3 4 5 6; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "$1" || true)
    [ "$code" = "$2" ] && { ok "$1 -> $code"; return 0; }
    sleep 10
  done
  warn "$1 -> ${code:-no answer} (expected $2)"; return 1
}
if [ $DO_UPLOAD = 1 ]; then
  step "Checking the live site"
  check_url "https://$HOST/" 200 || warn "A fresh upload can take a minute to reach every edge; open the URL again shortly."
  check_url "https://$HOST/this-page-does-not-exist-$STAMP" 404 || true
fi

# --------------------------------------------------------------------------------------
cname_of() { # prints the CNAME target of $1 (no trailing dot), empty when there is none
  if command -v dig >/dev/null; then dig +short CNAME "$1" @1.1.1.1 2>/dev/null | head -1 | sed 's/\.$//'
  elif command -v nslookup >/dev/null; then nslookup -type=CNAME "$1" 1.1.1.1 2>/dev/null | awk '/canonical name/ {print $NF}' | head -1 | sed 's/\.$//'
  elif command -v host >/dev/null; then host -t CNAME "$1" 1.1.1.1 2>/dev/null | awk '/alias for/ {print $NF}' | head -1 | sed 's/\.$//'
  fi
}
if [ -n "$CUSTOM_DOMAIN" ] && [ $DO_AZURE = 1 ]; then
  step "Custom domain $CUSTOM_DOMAIN"
  CURRENT=$(az staticwebapp hostname show -n "$SWA" -g "$RG" --hostname "$CUSTOM_DOMAIN" --query status -o tsv --only-show-errors 2>/dev/null || true)
  if [ "$CURRENT" = "Ready" ]; then
    DOMAIN_READY=1; ok "already bound and Ready"
  else
    TARGET=$(cname_of "$CUSTOM_DOMAIN")
    if [ "$TARGET" != "$HOST" ]; then
      if [ -z "$TARGET" ] && command -v dig >/dev/null && [ -n "$(dig +short A "$CUSTOM_DOMAIN" @1.1.1.1 2>/dev/null)" ]; then
        warn "$CUSTOM_DOMAIN answers with A records but no CNAME. In Cloudflare that means the record is proxied (orange cloud)."
        warn "Switch it to DNS only (grey cloud) so Azure can validate it, then re-run."
      else
        warn "$CUSTOM_DOMAIN has no CNAME to $HOST yet${TARGET:+ (it points to $TARGET)}."
      fi
      echo "     Create this record at your DNS provider (salnikov.no is on Cloudflare), DNS only:"
      echo "       Type CNAME   Name ${CUSTOM_DOMAIN%%.*}   Target $HOST   TTL Auto (or 300 while testing)"
      echo "     Then re-run: ./infra/deploy.sh --upload-only --no-build --custom-domain $CUSTOM_DOMAIN   (details: CUSTOM-DOMAIN.md)"
    else
      ok "CNAME $CUSTOM_DOMAIN -> $HOST found"
      az staticwebapp hostname set -n "$SWA" -g "$RG" --hostname "$CUSTOM_DOMAIN" --validation-method cname-delegation --no-wait -o none --only-show-errors \
        || die "Azure refused the domain (see above)." "CUSTOM-DOMAIN.md, section Troubleshooting"
      info "validation started; waiting up to 10 minutes for Azure to validate and issue the certificate"
      STATUS=""
      for _ in $(seq 1 40); do
        STATUS=$(az staticwebapp hostname show -n "$SWA" -g "$RG" --hostname "$CUSTOM_DOMAIN" --query status -o tsv --only-show-errors 2>/dev/null || true)
        case "$STATUS" in Ready|Failed) break;; esac
        sleep 15
      done
      case "$STATUS" in
        Ready) DOMAIN_READY=1; ok "bound, certificate issued"; check_url "https://$CUSTOM_DOMAIN/" 200 || warn "The certificate can take a few more minutes to reach every edge.";;
        Failed) warn "validation failed: $(az staticwebapp hostname show -n "$SWA" -g "$RG" --hostname "$CUSTOM_DOMAIN" --query errorMessage -o tsv --only-show-errors 2>/dev/null)"
                warn "See CUSTOM-DOMAIN.md > Troubleshooting, delete it (az staticwebapp hostname delete -n $SWA -g $RG --hostname $CUSTOM_DOMAIN --yes) and re-run.";;
        *) info "still ${STATUS:-validating}; Azure keeps going in the background. Check: az staticwebapp hostname list -n $SWA -g $RG -o table";;
      esac
    fi
  fi
fi

echo
if [ $DOMAIN_READY = 1 ]; then c 32 "Done. Web edition: https://$CUSTOM_DOMAIN  (also https://$HOST)"
else c 32 "Done. Web edition: https://$HOST"; fi
c 90 "Cost: Static Web Apps Free plan = 0. Remove everything: ./infra/teardown.sh"
