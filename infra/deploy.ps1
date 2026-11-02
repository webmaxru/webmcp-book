<#
.SYNOPSIS
  One command to put the web edition of "Tools, Not Clicks" on Azure Static Web Apps (Free).

.DESCRIPTION
  Creates (or updates) the resource group rg-webmcp-book and the Static Web App
  swa-webmcp-book on the FREE plan (infra/main.bicep), builds the site with
  `python tools/build.py site`, uploads dist/site to production with the Static Web Apps
  CLI, stores the app's deployment token as the GitHub Actions secret
  AZURE_STATIC_WEB_APPS_API_TOKEN (when gh is logged in) and checks the live URL.
  Optionally binds a custom domain (its CNAME must exist first) and adds a budget alert.

  Safe to re-run: existing resources are updated in place, the token stays the same,
  the site is re-uploaded. The deployment token is never printed, never put on a command
  line and never written to a file.

  Works in Windows PowerShell 5.1 and PowerShell 7+ (Windows, macOS, Linux).
  macOS/Linux bash twin: infra/deploy.sh.

.EXAMPLE
  pwsh ./infra/deploy.ps1
.EXAMPLE
  pwsh ./infra/deploy.ps1 -CustomDomain webmcp.salnikov.no
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\infra\deploy.ps1 -UploadOnly
#>
[CmdletBinding()]
param(
  [string]$ResourceGroup = 'rg-webmcp-book',
  [string]$SwaName = 'swa-webmcp-book',
  [ValidateSet('westeurope', 'eastus2', 'centralus', 'westus2', 'eastasia')]
  [string]$Location = 'westeurope',
  [string]$Repo = 'webmaxru/webmcp-book',
  [string]$Subscription = '',
  [string]$CustomDomain = '',
  [string]$BudgetEmail = '',
  [ValidateRange(1, 100000)]
  [int]$BudgetAmount = 1,
  [string]$BudgetName = 'budget-webmcp-book',
  [switch]$SkipGitHub,
  [switch]$BuildOnly,
  [switch]$InfraOnly,
  [switch]$UploadOnly,
  [switch]$NoBuild,
  [switch]$Yes
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$SwaCliVersion = '2.1.0'   # @azure/static-web-apps-cli, pinned
$SecretName = 'AZURE_STATIC_WEB_APPS_API_TOKEN'
$InfraDir = $PSScriptRoot
$Root = Split-Path -Parent $InfraDir
$SiteDir = Join-Path (Join-Path $Root 'dist') 'site'
$stamp = (Get-Date).ToString('yyyyMMdd-HHmmss')
$IsWin = ($env:OS -eq 'Windows_NT')

function Write-Step([string]$Text) { Write-Host ''; Write-Host ("== {0}" -f $Text) -ForegroundColor Cyan }
function Write-Ok([string]$Text) { Write-Host ("    OK   {0}" -f $Text) -ForegroundColor Green }
function Write-Info([string]$Text) { Write-Host ("    ..   {0}" -f $Text) -ForegroundColor Gray }
function Write-Warn2([string]$Text) { Write-Host ("    WARN {0}" -f $Text) -ForegroundColor Yellow }
function Exit-WithHint([string]$Text, [string]$Hint) {
  Write-Host ''
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
function Invoke-Az {
  param([string[]]$Arguments, [string]$What, [switch]$AllowFail)
  $r = Invoke-Native -Exe 'az' -Arguments ($Arguments + @('--only-show-errors'))
  if ($r.Code -ne 0 -and -not $AllowFail) { Exit-WithHint ("{0} failed: {1}" -f $What, $r.Err) 'Fix the cause above, then re-run (safe to re-run).' }
  return $r
}
function Test-Url([string]$Url, [int]$Expected) {
  $code = 0
  for ($i = 0; $i -lt 6; $i++) {
    try {
      $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 20 -MaximumRedirection 0 -ErrorAction Stop
      $code = [int]$resp.StatusCode
    } catch {
      $code = 0
      if ($_.Exception.PSObject.Properties['Response'] -and $_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
    }
    if ($code -eq $Expected) { Write-Ok ("{0} -> {1}" -f $Url, $code); return $true }
    Start-Sleep -Seconds 10
  }
  Write-Warn2 ("{0} -> {1} (expected {2})" -f $Url, $code, $Expected)
  return $false
}
function Get-CnameTarget([string]$Name) {
  try {
    $rec = Resolve-DnsName -Name $Name -Type CNAME -Server 1.1.1.1 -DnsOnly -ErrorAction Stop | Where-Object { $_.QueryType -eq 'CNAME' } | Select-Object -First 1
    if ($rec) { return ([string]$rec.NameHost).TrimEnd('.') }
    return ''
  } catch {
    if (Get-Command nslookup -ErrorAction SilentlyContinue) {
      $out = (& nslookup -type=CNAME $Name 1.1.1.1 2>$null) -join "`n"
      $m = [regex]::Match($out, 'canonical name\s*=\s*(\S+)')
      if ($m.Success) { return $m.Groups[1].Value.TrimEnd('.') }
    }
    return ''
  }
}

if (@(@($BuildOnly, $InfraOnly, $UploadOnly) | Where-Object { $_ }).Count -gt 1) {
  Exit-WithHint 'Use only one of -BuildOnly, -InfraOnly, -UploadOnly.' ''
}
$CustomDomain = ($CustomDomain.ToLowerInvariant() -replace '^https?://', '' -replace '/.*$', '').TrimEnd('.')

$doAzure = $true; $doInfra = $true; $doBuild = $true; $doUpload = $true
if ($BuildOnly) { $doAzure = $false; $doInfra = $false; $doUpload = $false }
if ($InfraOnly) { $doBuild = $false; $doUpload = $false }
if ($UploadOnly) { $doInfra = $false }
if ($NoBuild) { $doBuild = $false }

Write-Host 'Tools, Not Clicks: web edition -> Azure Static Web Apps (Free)' -ForegroundColor White

# ---------------------------------------------------------------------------------------
Write-Step 'Checking tools'
if ($doAzure) {
  if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Exit-WithHint 'Azure CLI (az) is not installed.' 'winget install -e --id Microsoft.AzureCLI (macOS: brew install azure-cli), then az login'
  }
  $azv = Invoke-Native -Exe 'az' -Arguments @('version', '--query', '"azure-cli"', '-o', 'tsv')
  Write-Ok ("Azure CLI {0}" -f $azv.Out)
  if ($doInfra) {
    $bv = Invoke-Native -Exe 'az' -Arguments @('bicep', 'version', '--only-show-errors')
    if ($bv.Code -ne 0) { Write-Info 'installing Bicep'; Invoke-Az -Arguments @('bicep', 'install') -What 'Installing Bicep' | Out-Null }
    Write-Ok 'Bicep'
  }
}
$py = $null
if ($doBuild) {
  foreach ($cand in @('python3', 'python', 'py')) {
    if (Get-Command $cand -ErrorAction SilentlyContinue) {
      $v = Invoke-Native -Exe $cand -Arguments @('-c', 'import sys; print(1 if sys.version_info >= (3, 11) else 0)')
      if ($v.Code -eq 0 -and $v.Out -eq '1') { $py = $cand; break }
    }
  }
  if (-not $py) { Exit-WithHint 'Python 3.11+ is needed for the build.' 'winget install -e --id Python.Python.3.12 (macOS: brew install python@3.12)' }
  if (-not (Test-Path (Join-Path (Join-Path $Root 'tools') 'build.py'))) { Exit-WithHint "tools/build.py not found under $Root." 'Run this script from a full clone of the book repo.' }
  $pv = Invoke-Native -Exe $py -Arguments @('-V')
  Write-Ok $pv.Out
}
if ($doUpload) {
  if (-not (Get-Command npx -ErrorAction SilentlyContinue)) { Exit-WithHint 'Node.js (npx) is not installed; the upload uses the Static Web Apps CLI.' 'winget install -e --id OpenJS.NodeJS.LTS' }
  $nv = Invoke-Native -Exe 'node' -Arguments @('-p', 'process.versions.node.split(".")[0]')
  if ($nv.Code -ne 0 -or [int]$nv.Out -lt 18) { Exit-WithHint 'Node 18+ is needed for the Static Web Apps CLI.' 'winget install -e --id OpenJS.NodeJS.LTS' }
  Write-Ok ("Node {0}, Static Web Apps CLI {1} via npx" -f $nv.Out, $SwaCliVersion)
}
$useGh = $false
if ($doAzure -and -not $SkipGitHub) {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Write-Warn2 'gh not found: the GitHub secret step will be printed for you' }
  else {
    $gs = Invoke-Native -Exe 'gh' -Arguments @('auth', 'status', '--hostname', 'github.com')
    if ($gs.Code -ne 0) { Write-Warn2 'gh is not logged in (gh auth login): the GitHub secret step will be printed' }
    else { $useGh = $true; Write-Ok 'GitHub CLI logged in' }
  }
}

# ---------------------------------------------------------------------------------------
$subId = ''
if ($doAzure) {
  Write-Step 'Azure login and subscription'
  if ($Subscription) { Invoke-Az -Arguments @('account', 'set', '--subscription', $Subscription) -What 'Switching subscription' | Out-Null }
  $acct = Invoke-Native -Exe 'az' -Arguments @('account', 'show', '-o', 'json', '--only-show-errors')
  if ($acct.Code -ne 0) { Exit-WithHint 'You are not logged in to Azure.' 'Run: az login' }
  $a = $acct.Out | ConvertFrom-Json
  $subId = $a.id
  Write-Ok ("Subscription: {0} ({1})" -f $a.name, $subId)
  $dom = if ($CustomDomain) { $CustomDomain } else { 'none' }
  $bud = if ($BudgetEmail) { $BudgetEmail } else { 'none' }
  Write-Info ("Resource group {0} | Static Web App {1} ({2}, Free) | domain: {3} | budget: {4}" -f $ResourceGroup, $SwaName, $Location, $dom, $bud)
  if (-not $Yes) {
    $answer = Read-Host '    Continue with this subscription? [y/N]'
    if ($answer -notmatch '^(y|yes)$') { Write-Host 'Stopped. Nothing changed.' -ForegroundColor Yellow; exit 0 }
  }
}

$hostName = ''
if ($doInfra) {
  Write-Step "Resource group $ResourceGroup"
  $ex = Invoke-Az -Arguments @('group', 'exists', '--name', $ResourceGroup) -What 'Checking the resource group'
  if ($ex.Out -eq 'true') { Write-Ok 'exists (left as is)' }
  else {
    Invoke-Az -Arguments @('group', 'create', '--name', $ResourceGroup, '--location', $Location, '--tags', 'project=webmcp-book', 'managedBy=bicep', '-o', 'none') -What 'Creating the resource group' | Out-Null
    Write-Ok ("created in {0}" -f $Location)
  }

  Write-Step "Static Web App $SwaName (Free plan)"
  Write-Info 'deploying infra/main.bicep (about a minute)'
  $d = Invoke-Az -Arguments @('deployment', 'group', 'create', '--resource-group', $ResourceGroup, '--name', "webmcp-book-$stamp",
    '--template-file', (Join-Path $InfraDir 'main.bicep'), '--parameters', "swaName=$SwaName", "location=$Location",
    '--query', 'properties.outputs.defaultHostname.value', '-o', 'tsv') -What 'Deploying main.bicep'
  $hostName = $d.Out
  Write-Ok ("ready: https://{0}" -f $hostName)

  if ($BudgetEmail) {
    Write-Step 'Monthly budget alert'
    $budgetUrl = "/subscriptions/$subId/resourceGroups/$ResourceGroup/providers/Microsoft.Consumption/budgets/$($BudgetName)?api-version=2023-11-01"
    $existing = Invoke-Native -Exe 'az' -Arguments @('rest', '--method', 'get', '--url', $budgetUrl, '--query', 'properties.timePeriod.startDate', '-o', 'tsv', '--only-show-errors')
    if ($existing.Code -eq 0 -and $existing.Out.Length -ge 10) { $startDate = $existing.Out.Substring(0, 10) }
    else { $startDate = (Get-Date).ToUniversalTime().ToString('yyyy-MM-01') }
    $b = Invoke-Native -Exe 'az' -Arguments @('deployment', 'group', 'create', '--resource-group', $ResourceGroup, '--name', "webmcp-book-budget-$stamp",
      '--template-file', (Join-Path $InfraDir 'budget.bicep'), '--parameters', "budgetName=$BudgetName", "amount=$BudgetAmount",
      "contactEmail=$BudgetEmail", "startDate=$startDate", '-o', 'none', '--only-show-errors')
    if ($b.Code -eq 0) { Write-Ok ("budget {0}: {1}/month (billing currency), alerts at 80% actual and 100% forecast to {2}" -f $BudgetName, $BudgetAmount, $BudgetEmail) }
    else { Write-Warn2 ("budget not created (the site is fine): {0}" -f $b.Err) }
  }
} elseif ($doAzure) {
  Write-Step "Static Web App $SwaName"
  $s = Invoke-Native -Exe 'az' -Arguments @('staticwebapp', 'show', '--name', $SwaName, '--resource-group', $ResourceGroup, '--query', 'defaultHostname', '-o', 'tsv', '--only-show-errors')
  if ($s.Code -ne 0 -or -not $s.Out) { Exit-WithHint "Static Web App $SwaName not found in $ResourceGroup." 'Run deploy.ps1 without -UploadOnly once.' }
  $hostName = $s.Out
  Write-Ok ("found: https://{0}" -f $hostName)
}

# ---------------------------------------------------------------------------------------
if ($doBuild) {
  Write-Step 'Building the site (tools/build.py site)'
  $venv = Join-Path $Root '.venv'
  $venvPy = if ($IsWin) { Join-Path (Join-Path $venv 'Scripts') 'python.exe' } else { Join-Path (Join-Path $venv 'bin') 'python' }
  if (-not (Test-Path $venvPy)) {
    $mk = Invoke-Native -Exe $py -Arguments @('-m', 'venv', $venv)
    if ($mk.Code -ne 0) { Exit-WithHint ("Could not create {0}: {1}" -f $venv, $mk.Err) '' }
  }
  $req = Join-Path (Join-Path $Root 'tools') 'requirements.txt'
  $reqSite = Join-Path (Join-Path $Root 'tools') 'requirements-site.txt'
  if (Test-Path $reqSite) { $req = $reqSite }
  Invoke-Native -Exe $venvPy -Arguments @('-m', 'pip', 'install', '--quiet', '--upgrade', 'pip') | Out-Null
  if (Test-Path $req) {
    $pi = Invoke-Native -Exe $venvPy -Arguments @('-m', 'pip', 'install', '--quiet', '-r', $req)
    if ($pi.Code -ne 0) { Exit-WithHint ("pip install failed: {0}" -f $pi.Err) '' }
  }
  Push-Location $Root
  try { & $venvPy 'tools/build.py' 'site'; $bc = $LASTEXITCODE } finally { Pop-Location }
  if ($bc -ne 0) { Exit-WithHint 'The site build failed (see above).' 'Fix it, then re-run with -UploadOnly.' }
}

if ($doUpload -or $BuildOnly) {
  if (-not (Test-Path (Join-Path $SiteDir 'index.html'))) { Exit-WithHint 'dist/site/index.html is missing.' 'Build first: python tools/build.py site' }
  $cfg = Join-Path $Root 'staticwebapp.config.json'
  if ((Test-Path $cfg) -and -not (Test-Path (Join-Path $SiteDir 'staticwebapp.config.json'))) { Copy-Item $cfg $SiteDir }
  $files = @(Get-ChildItem -Path $SiteDir -Recurse -File)
  $bytes = ($files | Measure-Object -Property Length -Sum).Sum
  Write-Ok ("dist/site: {0} files, {1:N1} MB (Free plan limits: 250 MB per environment, 15,000 files)" -f $files.Count, ($bytes / 1MB))
  if ($bytes -ge 250MB) { Exit-WithHint 'dist/site is larger than the Free plan allows (250 MB).' 'Shrink images or move to the Standard plan.' }
  $checkPy = $py
  if (-not $checkPy) { foreach ($cand in @('python3', 'python', 'py')) { if (Get-Command $cand -ErrorAction SilentlyContinue) { $checkPy = $cand; break } } }
  if ($checkPy) {
    & $checkPy (Join-Path $InfraDir 'check_site.py') $SiteDir
    if ($LASTEXITCODE -ne 0) { Exit-WithHint 'The pre-upload check failed (see above): the live site would break or the headers would block something.' 'python infra/check_site.py dist/site --update-csp fixes inline-script hashes; other findings need a change in theme/ or staticwebapp.config.json.' }
  } else { Write-Warn2 'Python not found: skipped infra/check_site.py' }
}
if ($BuildOnly) {
  Write-Host ''
  Write-Host 'Built. Preview locally: python -m http.server -d dist/site 8080  (then http://localhost:8080)' -ForegroundColor Green
  exit 0
}

# ---------------------------------------------------------------------------------------
# The deployment token: read into memory only. Never printed, never on a command line.
$token = $null
if ($doAzure) {
  $tk = Invoke-Az -Arguments @('staticwebapp', 'secrets', 'list', '--name', $SwaName, '--resource-group', $ResourceGroup, '--query', 'properties.apiKey', '-o', 'tsv') -What 'Reading the deployment token'
  $token = $tk.Out
  $tk = $null
  if (-not $token) { Exit-WithHint 'The deployment token came back empty.' "Portal: $SwaName > Overview > Manage deployment token, then re-run." }
}

try {
  if ($doUpload) {
    Write-Step 'Uploading dist/site to production'
    # The CLI reads the token from SWA_CLI_DEPLOYMENT_TOKEN, so it never appears in the process list.
    $env:SWA_CLI_DEPLOYMENT_TOKEN = $token
    Push-Location $Root
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
      & npx --yes "@azure/static-web-apps-cli@$SwaCliVersion" deploy ./dist/site --env production --swa-config-location ./dist/site
      $uc = $LASTEXITCODE
    } finally {
      $ErrorActionPreference = $prev
      Pop-Location
      Remove-Item Env:SWA_CLI_DEPLOYMENT_TOKEN -ErrorAction SilentlyContinue
    }
    if ($uc -ne 0) { Exit-WithHint 'The upload failed (see above).' 'Re-run with -UploadOnly -NoBuild to retry the upload.' }
    Write-Ok 'uploaded'
  }

  if ($doAzure) {
    Write-Step ("GitHub: {0} on {1}" -f $SecretName, $Repo)
    $manual = $true
    if ($useGh) {
      $prev = $ErrorActionPreference
      $ErrorActionPreference = 'Continue'
      try { $setOut = $token | & gh secret set $SecretName --repo $Repo 2>&1; $setCode = $LASTEXITCODE } finally { $ErrorActionPreference = $prev }
      if ($setCode -eq 0) { Write-Ok 'secret set; pushes to main and releases now deploy through .github/workflows/deploy-swa.yml'; $manual = $false }
      else { Write-Warn2 ("gh could not set the secret (admin rights on {0} needed): {1}" -f $Repo, (($setOut | ForEach-Object { "$_" }) -join ' ')) }
    }
    if ($manual) {
      Write-Warn2 'Set it by hand so GitHub can deploy (the token goes to your clipboard, not the screen):'
      Write-Host ("      1. az staticwebapp secrets list -n {0} -g {1} --query properties.apiKey -o tsv | Set-Clipboard" -f $SwaName, $ResourceGroup) -ForegroundColor Yellow
      Write-Host ("      2. https://github.com/{0}/settings/secrets/actions > New repository secret" -f $Repo) -ForegroundColor Yellow
      Write-Host ("         Name: {0}   Secret: paste > Add secret" -f $SecretName) -ForegroundColor Yellow
    }
  }
} finally {
  $token = $null
  Remove-Variable -Name token -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------------------------------
if ($doUpload) {
  Write-Step 'Checking the live site'
  if (-not (Test-Url ("https://{0}/" -f $hostName) 200)) { Write-Warn2 'A fresh upload can take a minute to reach every edge; open the URL again shortly.' }
  Test-Url ("https://{0}/this-page-does-not-exist-{1}" -f $hostName, $stamp) 404 | Out-Null
}

# ---------------------------------------------------------------------------------------
$domainReady = $false
if ($CustomDomain -and $doAzure) {
  Write-Step "Custom domain $CustomDomain"
  $cur = Invoke-Native -Exe 'az' -Arguments @('staticwebapp', 'hostname', 'show', '--name', $SwaName, '--resource-group', $ResourceGroup, '--hostname', $CustomDomain, '--query', 'status', '-o', 'tsv', '--only-show-errors')
  if ($cur.Code -eq 0 -and $cur.Out -eq 'Ready') { $domainReady = $true; Write-Ok 'already bound and Ready' }
  else {
    $target = Get-CnameTarget $CustomDomain
    if ($target -ne $hostName) {
      if ($target) { Write-Warn2 ("{0} points to {1}, not to {2}." -f $CustomDomain, $target, $hostName) }
      else { Write-Warn2 ("{0} has no CNAME to {1} yet (if the record exists in Cloudflare, it must be DNS only, grey cloud)." -f $CustomDomain, $hostName) }
      $label = $CustomDomain.Split('.')[0]
      Write-Host '      Create this record at your DNS provider (salnikov.no is on Cloudflare), DNS only:' -ForegroundColor Yellow
      Write-Host ("        Type CNAME   Name {0}   Target {1}   TTL Auto (or 300 while testing)" -f $label, $hostName) -ForegroundColor Yellow
      Write-Host ("      Then re-run: pwsh ./infra/deploy.ps1 -UploadOnly -NoBuild -CustomDomain {0}   (details: CUSTOM-DOMAIN.md)" -f $CustomDomain) -ForegroundColor Yellow
    } else {
      Write-Ok ("CNAME {0} -> {1} found" -f $CustomDomain, $hostName)
      Invoke-Az -Arguments @('staticwebapp', 'hostname', 'set', '--name', $SwaName, '--resource-group', $ResourceGroup, '--hostname', $CustomDomain, '--validation-method', 'cname-delegation', '--no-wait', '-o', 'none') -What 'Adding the custom domain' | Out-Null
      Write-Info 'validation started; waiting up to 10 minutes for Azure to validate and issue the certificate'
      $status = ''
      for ($i = 0; $i -lt 40; $i++) {
        $st = Invoke-Native -Exe 'az' -Arguments @('staticwebapp', 'hostname', 'show', '--name', $SwaName, '--resource-group', $ResourceGroup, '--hostname', $CustomDomain, '--query', 'status', '-o', 'tsv', '--only-show-errors')
        $status = $st.Out
        if ($status -eq 'Ready' -or $status -eq 'Failed') { break }
        Start-Sleep -Seconds 15
      }
      if ($status -eq 'Ready') {
        $domainReady = $true
        Write-Ok 'bound, certificate issued'
        Test-Url ("https://{0}/" -f $CustomDomain) 200 | Out-Null
      } elseif ($status -eq 'Failed') {
        $em = Invoke-Native -Exe 'az' -Arguments @('staticwebapp', 'hostname', 'show', '--name', $SwaName, '--resource-group', $ResourceGroup, '--hostname', $CustomDomain, '--query', 'errorMessage', '-o', 'tsv', '--only-show-errors')
        Write-Warn2 ("validation failed: {0}" -f $em.Out)
        Write-Warn2 ("See CUSTOM-DOMAIN.md > Troubleshooting, then: az staticwebapp hostname delete -n {0} -g {1} --hostname {2} --yes, and re-run." -f $SwaName, $ResourceGroup, $CustomDomain)
      } else {
        $shown = if ($status) { $status } else { 'validating' }
        Write-Info ("still {0}; Azure keeps going in the background. Check: az staticwebapp hostname list -n {1} -g {2} -o table" -f $shown, $SwaName, $ResourceGroup)
      }
    }
  }
}

Write-Host ''
if ($domainReady) { Write-Host ("Done. Web edition: https://{0}  (also https://{1})" -f $CustomDomain, $hostName) -ForegroundColor Green }
else { Write-Host ("Done. Web edition: https://{0}" -f $hostName) -ForegroundColor Green }
Write-Host 'Cost: Static Web Apps Free plan = 0. Remove everything: pwsh ./infra/teardown.ps1' -ForegroundColor Gray
