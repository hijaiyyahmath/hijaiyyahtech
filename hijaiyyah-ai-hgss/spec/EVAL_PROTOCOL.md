# Evaluation Protocol — Hijaiyyah-AI

## 1. Metrics

- **Pass@1 (Baseline)**: The percentage of tasks that pass validation on the first attempt without repair.
- **Pass@1 (Guarded)**: Equivalent to Baseline (first attempt).
- **Pass@k (Guarded)**: The percentage of tasks that pass validation within `k` repair attempts (default k=4).
- **Efficiency**: Average number of repair steps required for success.
- **Latency**: End-to-end time for generation (including repair loops).

## 2. Dataset
Evaluation MUST use the standard industrial batch file: `datasets/tasks/hgss_evidence_cases.jsonl`.

## 3. Reporting
Reports MUST include:
- A/B comparison of Pass rates.
- Histogram of error categories encountered.
- Final validation status for every case.
