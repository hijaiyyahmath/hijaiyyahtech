# Hijaiyah-Codex Monorepo Makefile
# Standardized entrypoint for environment, tests, and demos.

PYTHON = python

.PHONY: help env test demo all clean

help:
	@echo "Hijaiyah-Codex Monorepo Management"
	@echo "-----------------------------------"
	@echo "Targets:"
	@echo "  env   : Check environment, modules, and normative locks"
	@echo "  test  : Run unit tests across all sub-modules"
	@echo "  demo  : Run minimal smoke demos for core components"
	@echo "  all   : Execute env, test, and demo sequentially"
	@echo "  clean : Clear logs, reports, and forensic artifacts"

env:
	$(PYTHON) scripts/env_check.py

test:
	$(PYTHON) scripts/run_tests_all.py

demo:
	$(PYTHON) scripts/run_demos_all.py

all:
	$(PYTHON) scripts/run_all.py

clean:
	@echo "[*] Cleaning reports and artifacts..."
	@if exist reports rmdir /s /q reports
	@if exist artifacts rmdir /s /q artifacts
	@mkdir reports
	@mkdir artifacts
	@echo "[OK] Workspace cleaned."
