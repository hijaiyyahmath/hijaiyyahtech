#!/usr/bin/env bash
set -e

# One-command audit verification for Linux/macOS)
# Path: scripts/audit.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Hijaiyyah Auditor Bundle: Environment Setup ==="

# 1) Create venv
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# 2) Activate venv
source .venv/bin/activate

# 3) Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.lock.txt
pip install -e hl18 -e hisa-vm

# Verify installation
echo "Checking package availability..."
python -c "import hijaiyyahlang; import hisavm; print('OK: packages found')"

# 4) Run Verification
echo "=== Phase 1: Conformance Verification ==="
export PYTHONPATH="$PWD/hisa-vm/src:$PWD/hl18/src:$PYTHONPATH"
python scripts/verify_all.py | tee artifacts/audit_wrapper.log

# 5) Run Demo
if [[ "$*" != *"--skip-demo"* ]]; then
    echo "=== Phase 2: Operational Demo ==="
    python scripts/run_full_demo.py | tee -a artifacts/audit_wrapper.log
fi

echo "=== Audit Complete ==="
echo "Logs: artifacts/audit_wrapper.log"
echo "Artifacts: artifacts/verify_all/ and artifacts/runs/"
