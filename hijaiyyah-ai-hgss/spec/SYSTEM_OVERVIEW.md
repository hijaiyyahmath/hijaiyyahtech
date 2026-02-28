# System Overview — Hijaiyyah-AI HGSS VM v1.0

Release ID: `HGSS-HCVM-v1.HC18DC`  
Commit: `e392c68`

## 1. Objective
The Hijaiyyah-AI HGSS VM is an intelligent agent layer that sits on top of the HGSS audit-evidence generator. Its goal is to maximize the success rate of generated JSON evidence that meets strict normative standards.

## 2. Modes of Operation

### Mode A: Baseline
The Baseline mode represents a standard direct LLM execution. 
- The system prompt and user prompt are sent to the LLM.
- The output is stored directly as a JSON event.
- Success is measured by the normative validator tools after the fact.

### Mode B: Guarded (Hijaiyyah-AI)
The Guarded mode implements an active **Repair Loop**.
- **Generate**: LLM generates the initial response.
- **Validate**: The agent runs the output through three validation layers:
    1. Schema Frozen
    2. CBOR Event Hash
    3. HGSS Verifier (Ground Truth)
- **Repair**: If validation fails, the agent captures the specific errors, maps them to the **Error Taxonomy**, and provides structured feedback to the LLM for a repair attempt.
- **Repeat**: This process repeats until validation passes or the maximum iteration limit (default: 3) is reached.

## 3. High-Level Architecture
[LLM] <--> [Repair Loop Agent] --> [Validation Suite] --> Ground Truth Oracle (HGSS)
