# Hijaiyyah-AI HGSS VM v1.0

AI-driven agent for Hijaiyah Guarded Signature Scheme (HGSS) evidence generation and validation.

## Features
- **Baseline Mode**: Direct generation evaluation.
- **Guarded Mode**: Automated repair loop with recursive validation.
- **Validation Layers**:
    - Schema Frozen (Version/Commit locks)
    - CBOR Canonical Hashing
    - Ground Truth Oracle (HGSS Verifier)
- **A/B Testing**: Comprehensive metrics reporting.

## Getting Started
1. Clone the repository.
2. Setup environment:
   ```bash
   cp .env.example .env
   # Edit .env with your LLM API Key
   ```
3. Vendor the HGSS dependency:
   Ensure `HGSS-HCVM-v1.HC18DC` is available in `deps/hgss-hc18dc/`.
4. Run check:
   ```bash
   python tools/env_check.py
   ```
5. Run A/B test:
   ```bash
   python tools/run_ab_test.py --dataset datasets/tasks/hgss_evidence_cases.jsonl
   ```

## Repository Structure
- `spec/`: Normative specifications.
- `src/`: Core agent and evaluation logic.
- `tools/`: CLI utilities.
- `datasets/`: Task cases for benchmarking.
