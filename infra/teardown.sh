#!/usr/bin/env bash
# Removes what infra/deploy.sh created: the whole resource group (default rg-webmcp-book),
# which holds the Static Web App, its custom domain binding and the optional budget.
# Windows: infra/teardown.ps1.
#
#   ./infra/teardown.sh [--resource-group rg-webmcp-book] [--subscription ID]
#                       [--remove-github-secret] [--repo vibeprogrammer/webmcp-book] [--yes]
#
# The DNS record for a custom domain lives at your DNS provider and is NOT touched:
# delete the webmcp CNAME yourself afterwards, or it will point at nothing.
set -euo pipefail

RG=rg-webmcp-book; REPO=vibeprogrammer/webmcp-book; SUBSCRIPTION=""; REMOVE_SECRET=0; YES=0
SECRET_NAME=AZURE_STATIC_WEB_APPS_API_TOKEN
need_arg() { [ $# -ge 2 ] && [ -n "$2" ] || { echo "Option $1 needs a value" >&2; exit 2; }; }
while [ $# -gt 0 ]; do
  case "$1" in
    --resource-group) need_arg "$@"; RG=$2; shift 2;;
    --repo) need_arg "$@"; REPO=$2; shift 2;;
    --subscription) need_arg "$@"; SUBSCRIPTION=$2; shift 2;;
    --remove-github-secret) REMOVE_SECRET=1; shift;;
    --yes|-y) YES=1; shift;;
    -h|--help) sed -n '2,10p' "$0"; exit 0;;
    *) echo "Unknown option: $1 (see --help)" >&2; exit 2;;
  esac
done
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then c() { printf '\033[%sm%s\033[0m\n' "$1" "$2"; }
else c() { printf '%s\n' "$2"; }; fi
ok()   { c 32 "   OK   $1"; }
info() { c 90 "   ..   $1"; }
warn() { c 33 "   WARN $1"; }
die()  { echo; c 31 "ERROR: $1"; [ -n "${2:-}" ] && c 33 "Next:  $2"; exit 1; }

command -v az >/dev/null || die "Azure CLI (az) is not installed."
if [ -n "$SUBSCRIPTION" ]; then az account set --subscription "$SUBSCRIPTION" --only-show-errors || die "Could not switch subscription."; fi
SUB_NAME=$(az account show --query name -o tsv --only-show-errors 2>/dev/null) || die "You are not logged in to Azure." "az login"

c 1 "Tools, Not Clicks: teardown"
info "Subscription: $SUB_NAME"
if [ "$(az group exists -n "$RG" --only-show-errors)" != true ]; then
  ok "resource group $RG does not exist (nothing to delete)"
else
  info "Resource group $RG contains:"
  az resource list -g "$RG" --query '[].{type:type, name:name}' -o tsv --only-show-errors | sed 's/^/          /'
  OTHER=$(az resource list -g "$RG" --query "[?type!='Microsoft.Web/staticSites'] | length(@)" -o tsv --only-show-errors)
  [ "${OTHER:-0}" -gt 0 ] && warn "$OTHER resource(s) besides the Static Web App will be deleted too."
  if [ $YES = 0 ]; then
    read -r -p "   Type the resource group name ($RG) to delete it with everything in it: " a
    [ "$a" = "$RG" ] || { echo "Stopped. Nothing was deleted."; exit 0; }
  fi
  az group delete -n "$RG" --yes --only-show-errors || die "Deleting $RG failed (see above)." "You need Contributor/Owner on it."
  ok "resource group $RG deleted (the site is gone; its deployment token is void)"
fi
# A budget is a child of the resource group and goes with it.

if [ $REMOVE_SECRET = 1 ]; then
  if command -v gh >/dev/null && gh secret delete "$SECRET_NAME" --repo "$REPO" >/dev/null 2>&1; then
    ok "GitHub secret $SECRET_NAME removed from $REPO (the deploy workflow skips again)"
  else
    warn "Remove $SECRET_NAME by hand: https://github.com/$REPO/settings/secrets/actions"
  fi
else
  info "GitHub secret $SECRET_NAME left on $REPO (deploys will fail until you re-run deploy.sh or remove it: --remove-github-secret)"
fi
info "If you bound a custom domain, delete its CNAME at your DNS provider too."
