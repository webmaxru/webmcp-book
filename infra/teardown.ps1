<#
.SYNOPSIS
  Removes what infra/deploy.ps1 created: the resource group rg-webmcp-book with the
  Static Web App, its custom domain binding and the optional budget.

.DESCRIPTION
  Lists what is in the resource group and asks you to type its name before deleting it.
  Optionally removes the GitHub secret AZURE_STATIC_WEB_APPS_API_TOKEN so the deploy
  workflow goes back to skipping. The DNS record of a custom domain lives at your DNS
  provider and is NOT touched: delete the CNAME yourself afterwards.

  Works in Windows PowerShell 5.1 and PowerShell 7+.

.EXAMPLE
  pwsh ./infra/teardown.ps1
.EXAMPLE
  pwsh ./infra/teardown.ps1 -RemoveGitHubSecret -Yes
#>
[CmdletBinding()]
param(
  [string]$ResourceGroup = 'rg-webmcp-book',
  [string]$Repo = 'webmaxru/webmcp-book',
  [string]$Subscription = '',
  [switch]$RemoveGitHubSecret,
  [switch]$Yes
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$SecretName = 'AZURE_STATIC_WEB_APPS_API_TOKEN'

function Write-Ok([string]$Text) { Write-Host ("    OK   {0}" -f $Text) -ForegroundColor Green }
function Write-Info([string]$Text) { Write-Host ("    ..   {0}" -f $Text) -ForegroundColor Gray }
function Write-Warn2([string]$Text) { Write-Host ("    WARN {0}" -f $Text) -ForegroundColor Yellow }
function Exit-WithHint([string]$Text, [string]$Hint) {
  Write-Host ("ERROR: {0}" -f $Text) -ForegroundColor Red
  if ($Hint) { Write-Host ("Next:  {0}" -f $Hint) -ForegroundColor Yellow }
  exit 1
}
function Invoke-Native {
  param([Parameter(Mandatory = $true)][string]$Exe, [string[]]$Arguments = @())
  $prev = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  try { $all = & $Exe @Arguments 2>&1; $code = $LASTEXITCODE } finally { $ErrorActionPreference = $prev }
  $outLines = @(); $errLines = @()
  foreach ($line in @($all)) {
    if ($line -is [System.Management.Automation.ErrorRecord]) { $errLines += $line.ToString() } else { $outLines += [string]$line }
  }
  return [pscustomobject]@{ Code = $code; Out = (($outLines -join "`n").Trim()); Err = (($errLines -join "`n").Trim()) }
}

if (-not (Get-Command az -ErrorAction SilentlyContinue)) { Exit-WithHint 'Azure CLI (az) is not installed.' 'winget install -e --id Microsoft.AzureCLI' }
if ($Subscription) {
  $s = Invoke-Native -Exe 'az' -Arguments @('account', 'set', '--subscription', $Subscription, '--only-show-errors')
  if ($s.Code -ne 0) { Exit-WithHint $s.Err 'Check the subscription id: az account list -o table' }
}
$acct = Invoke-Native -Exe 'az' -Arguments @('account', 'show', '--query', 'name', '-o', 'tsv', '--only-show-errors')
if ($acct.Code -ne 0) { Exit-WithHint 'You are not logged in to Azure.' 'Run: az login' }

Write-Host 'Tools, Not Clicks: teardown' -ForegroundColor White
Write-Info ("Subscription: {0}" -f $acct.Out)
$ex = Invoke-Native -Exe 'az' -Arguments @('group', 'exists', '--name', $ResourceGroup, '--only-show-errors')
if ($ex.Out -ne 'true') {
  Write-Ok ("resource group {0} does not exist (nothing to delete)" -f $ResourceGroup)
} else {
  $list = Invoke-Native -Exe 'az' -Arguments @('resource', 'list', '--resource-group', $ResourceGroup, '-o', 'json', '--only-show-errors')
  $items = @()
  if ($list.Code -eq 0 -and $list.Out) { $items = @($list.Out | ConvertFrom-Json) }
  Write-Info ("Resource group {0} contains:" -f $ResourceGroup)
  foreach ($it in $items) { Write-Host ("          {0}  {1}" -f $it.type, $it.name) }
  $other = @($items | Where-Object { $_.type -ne 'Microsoft.Web/staticSites' }).Count
  if ($other -gt 0) { Write-Warn2 ("{0} resource(s) besides the Static Web App will be deleted too." -f $other) }
  if (-not $Yes) {
    $answer = Read-Host ("    Type the resource group name ({0}) to delete it with everything in it" -f $ResourceGroup)
    if ($answer -ne $ResourceGroup) { Write-Host 'Stopped. Nothing was deleted.' -ForegroundColor Yellow; exit 0 }
  }
  $del = Invoke-Native -Exe 'az' -Arguments @('group', 'delete', '--name', $ResourceGroup, '--yes', '--only-show-errors')
  if ($del.Code -ne 0) { Exit-WithHint ("Deleting {0} failed: {1}" -f $ResourceGroup, $del.Err) 'You need Contributor/Owner on it.' }
  Write-Ok ("resource group {0} deleted (the site is gone; its deployment token is void)" -f $ResourceGroup)
}

if ($RemoveGitHubSecret) {
  if (Get-Command gh -ErrorAction SilentlyContinue) {
    $gs = Invoke-Native -Exe 'gh' -Arguments @('secret', 'delete', $SecretName, '--repo', $Repo)
    if ($gs.Code -eq 0) { Write-Ok ("GitHub secret {0} removed (the deploy workflow skips again)" -f $SecretName) }
    else { Write-Warn2 ("Could not remove the GitHub secret: {0}" -f $gs.Err) }
  } else {
    Write-Warn2 ("gh not found: remove {0} at https://github.com/{1}/settings/secrets/actions" -f $SecretName, $Repo)
  }
} else {
  Write-Info ("GitHub secret {0} left on {1} (use -RemoveGitHubSecret to remove it)" -f $SecretName, $Repo)
}
Write-Info 'If you bound a custom domain, delete its CNAME at your DNS provider too.'
