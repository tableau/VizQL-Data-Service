# driver.ps1 - dev driver for the VizQL Data Service Python SDK.
#
# Runs from python_sdk/ (or any cwd; script resolves paths from its own location).
# .sh scripts are delegated to Git Bash; Python / pip / lint tools run inline.
#
# Usage:
#   powershell -NoProfile -File .claude/skills/run-vizql-data-service-py/driver.ps1 <subcommand>
# (Windows PowerShell 5.1; pwsh 7 not required.)
#
# Subcommands:
#   setup            Install package in editable mode with [dev] extras.
#   check-version    Verify pyproject.toml <-> OpenAPI schema major.minor match.
#   gen              Regenerate src/api/openapi_generated.py from the schema.
#   build            Clean, build sdist + wheel into dist/.
#   format           Apply black + isort (writes changes).
#   lint             Run black --check, isort --check-only, flake8, mypy.
#   test             Run pytest against tests/.
#   examples-help    Print examples.py CLI help (no server needed).
#   examples         Run examples.py; extra args are forwarded (e.g. -s <url> --async).
#                    If no -s/--server is given, defaults to -s http://localhost.
#                    If no auth flag (-u/-p/-n/-t/-j) is given, defaults to
#                    -u testadmin -p 123.
#   all              gen -> check-version -> build -> lint -> test  (matches CI).
#   help             Show this help.

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('setup','check-version','gen','build','format','lint','test','examples-help','examples','all','help')]
    [string] $Subcommand = 'help',

    # Remaining args forwarded to the subcommand (used by 'examples').
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Rest
)

$ErrorActionPreference = 'Stop'

# Resolve repo root (python_sdk/) from this script's location.
# $PSScriptRoot is reliable even when a param() block runs before the body.
$SkillRoot = $PSScriptRoot
if (-not $SkillRoot) { $SkillRoot = Split-Path -Parent $PSCommandPath }
$RepoRoot  = Resolve-Path (Join-Path $SkillRoot '..\..\..')
Set-Location $RepoRoot

function Get-BashPath {
    $bash = Get-Command bash -ErrorAction SilentlyContinue
    if ($bash) { return $bash.Source }
    $candidates = @(
        'C:\Program Files\Git\bin\bash.exe',
        'C:\Program Files\Git\usr\bin\bash.exe'
    )
    foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
    throw "Git Bash not found. Install Git for Windows or add bash.exe to PATH."
}

function Invoke-Bash([string] $ScriptRelPath) {
    $bash = Get-BashPath
    Write-Host "[driver] bash $ScriptRelPath" -ForegroundColor Cyan
    & $bash $ScriptRelPath
    if ($LASTEXITCODE -ne 0) { throw "bash $ScriptRelPath failed with exit $LASTEXITCODE" }
}

function Invoke-Step([string] $Label, [scriptblock] $Body) {
    Write-Host "[driver] $Label" -ForegroundColor Cyan
    & $Body
    if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit $LASTEXITCODE" }
}

function Cmd-Setup {
    Invoke-Step "python -m pip install --upgrade pip" { python -m pip install --upgrade pip }
    Invoke-Step "pip install -e .[dev]" { pip install -e ".[dev]" }
}

function Cmd-CheckVersion { Invoke-Bash 'scripts/check_version.sh' }

function Cmd-Gen { Invoke-Bash 'scripts/generate_stub.sh' }

function Cmd-Build { Invoke-Bash 'scripts/build.sh' }

function Cmd-Format {
    Invoke-Step "black ." { black . }
    Invoke-Step "isort ." { isort . }
}

function Cmd-Lint {
    Invoke-Step "black --check" { black . --check }
    Invoke-Step "isort --check-only" { isort . --check-only }
    Invoke-Step "flake8" { flake8 . }
    Invoke-Step "mypy" { mypy . }
}

function Cmd-Test { Invoke-Step "pytest" { pytest tests -q --disable-warnings } }

function Cmd-ExamplesHelp { Invoke-Step "examples.py --help" { python src/examples/examples.py --help } }

function Cmd-Examples([string[]] $Passthrough) {
    if (-not $Passthrough) { $Passthrough = @() }

    # Match on the flag *name* only, so both space-form (`-u alice`) and
    # equals-form (`--user=alice`) are detected. Without this split,
    # `--user=alice` slips past and the driver silently overrides it with
    # the injected default credentials.
    $authFlags   = @('-u','--user','-p','--password','-n','--pat-name','-t','--pat-secret','-j','--jwt-token')
    $serverFlags = @('-s','--server')

    $hasAuth   = $false
    $hasServer = $false
    foreach ($tok in $Passthrough) {
        $name = ($tok -split '=', 2)[0]
        if (-not $hasAuth   -and $authFlags   -contains $name) { $hasAuth   = $true }
        if (-not $hasServer -and $serverFlags -contains $name) { $hasServer = $true }
    }

    $finalArgs = @('src/examples/examples.py') + $Passthrough
    if (-not $hasServer) {
        Write-Host "[driver] no -s/--server supplied - defaulting to -s http://localhost" -ForegroundColor Yellow
        $finalArgs += @('-s','http://localhost')
    }
    if (-not $hasAuth) {
        Write-Host "[driver] no auth flag supplied - defaulting to -u testadmin -p 123" -ForegroundColor Yellow
        $finalArgs += @('-u','testadmin','-p','123')
    }

    Invoke-Step "examples.py $($Passthrough -join ' ')" { python @finalArgs }
}

function Cmd-All {
    Cmd-Gen
    Cmd-CheckVersion
    Cmd-Build
    Cmd-Lint
    Cmd-Test
}

function Cmd-Help {
    $self = Join-Path $SkillRoot 'driver.ps1'
    Get-Content $self | Select-String -Pattern '^#' | ForEach-Object { $_.Line -replace '^# ?','' } | Select-Object -First 24
}

switch ($Subcommand) {
    'setup'         { Cmd-Setup }
    'check-version' { Cmd-CheckVersion }
    'gen'           { Cmd-Gen }
    'build'         { Cmd-Build }
    'format'        { Cmd-Format }
    'lint'          { Cmd-Lint }
    'test'          { Cmd-Test }
    'examples-help' { Cmd-ExamplesHelp }
    'examples'      { Cmd-Examples $Rest }
    'all'           { Cmd-All }
    'help'          { Cmd-Help }
}
