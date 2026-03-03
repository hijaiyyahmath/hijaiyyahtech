# HGSS Evidence Agent Suite — Build & Run

.PHONY: all build test install clean help

help:
	@echo "HGSS Evidence Agent Suite v1.0 — Build Targets"
	@echo ""
	@echo "Targets:"
	@echo "  make build        - Build agent service (Rust/Go)"
	@echo "  make test         - Run unit + integration tests"
	@echo "  make verify       - Run hgss_verify_evidence.py strict verifier"
	@echo "  make pkg-windows  - Build Windows MSI installer"
	@echo "  make pkg-linux    - Build Linux deb + rpm packages"
	@echo "  make install      - Install locally (agent + viewer)"
	@echo "  make clean        - Clean build artifacts"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make build"
	@echo "  2. make test"
	@echo "  3. hgss-viewer  (launch UI)"

all: build test

build:
	@echo "[Agent] Building agent service..."
	cd agent && cargo build --release
	@echo "[Viewer] Building viewer UI..."
	cd viewer && cargo build --release
	@echo "✅ Build complete"

test:
	@echo "[Unit Tests] Running tests..."
	cd agent && cargo test --release
	@echo "[Integration] Running end-to-end test..."
	cd agent && cargo test --test integration_test --release
	@echo "✅ Tests passed"

verify:
	@echo "[Verifier] Testing hgss_verify_evidence.py..."
	python tools/hgss_verify_evidence.py \
	  --event agent/tests/fixtures/event.cbor \
	  --trace agent/tests/fixtures/trace.jsonl \
	  --schema hgss-hc18dc/spec/AUDIT_EVIDENCE_SCHEMA.md
	@echo "✅ Verification passed"

pkg-windows:
	@echo "[Packaging] Building Windows MSI..."
	cd agent/packaging/windows && ./build.sh
	@echo "✅ MSI ready: HGSS-Evidence-Agent-Suite-1.0.exe"

pkg-linux:
	@echo "[Packaging] Building Linux packages..."
	cd agent/packaging/linux && ./build.sh
	@echo "✅ Packages ready: .deb + .rpm"

install:
	@echo "[Install] Installing locally..."
	cd agent && cargo install --path .
	cd viewer && cargo install --path .
	@echo "✅ Installed: hgss-agent (service), hgss-viewer (UI), hgssctl (CLI)"

clean:
	@echo "[Clean] Removing build artifacts..."
	cd agent && cargo clean
	cd viewer && cargo clean
	rm -f *.exe *.deb *.rpm
	@echo "✅ Clean complete"

.DEFAULT_GOAL := help
