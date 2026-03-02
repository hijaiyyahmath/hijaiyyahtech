# Hijaiyyah Auditor Wrapper (Windows)
# Path: scripts/audit.ps1

# One-command audit verification for Windows PowerShell
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Definition)
Set-Location $RootDir

# 1) Create venv
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

# 2) Activate venv
$VenvPath = Join-Path $RootDir ".venv\Scripts\Activate.ps1"
. $VenvPath

# 3) Install dependencies
Write-Host "Installing dependencies..."
python -m pip install -r requirements.lock.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pip install -e hisa-vm
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pip install -e hl18
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Verify installation
Write-Host "Checking package availability..."
python -c "import hijaiyyahlang; import hisavm; Write-Host 'OK: packages found'"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# 4) Run Verification
Write-Host "=== Phase 1: Conformance Verification ===" -ForegroundColor Green
$env:PYTHONPATH = "$PWD\hisa-vm\src;$PWD\hl18\src;$env:PYTHONPATH"
python scripts/verify_all.py | Tee-Object -FilePath artifacts/audit_wrapper.log
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# 5) Run Demo
Write-Host "=== Phase 2: Operational Demo ===" -ForegroundColor Green
python scripts/run_full_demo.py | Tee-Object -FilePath artifacts/audit_wrapper.log -Append
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== Audit Complete ===" -ForegroundColor Cyan
Write-Host "Logs: artifacts/audit_wrapper.log"
Write-Host "Artifacts: artifacts/verify_all/ and artifacts/runs/"
