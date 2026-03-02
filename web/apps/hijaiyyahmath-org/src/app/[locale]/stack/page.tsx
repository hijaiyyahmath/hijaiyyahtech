import Tabs from "@/components/Tabs";
import { getReleaseMatrix } from "@/lib/loadContent";
import CodeBlock from "@/components/CodeBlock";

function StackDiagram() {
    const diagram = `
HL-18 (Mathematics / v18)
      ↓
HijaiyyahLang (Language)
      ↓
HISA (ISA Contract)
      ↓
HC-HCPU (Silicon | Photonic | Qubit)
      ↓
Codex-AI (Audit-aware harness)
      ↓
HGSS/HC18DC (Optional security wrapper)
`;
    return <CodeBlock code={diagram.trim()} />;
}

export default function Page() {
    const rm = getReleaseMatrix();
    const mods = rm.modules as any[];

    const tabItems = [
        {
            id: "core",
            label: "Core (HL-18)",
            content: (
                <div className="space-y-3 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian I: Matematika Hijaiyyah Core (HL-18)</div>
                    <p className="text-gray-700 dark:text-gray-300">
                        The <strong>Hijaiyyah Language v18 (HL-18)</strong> is the foundational codex engine implementing deterministic word-to-vector mapping with full audit-grade guarantees. It provides the ground truth implementation for all downstream layers.
                    </p>

                    <div className="rounded border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-3 space-y-2">
                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Origin Protocol & Discrete Geometry</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Geometric Foundation:</strong> Discrete geometry (8-neighborhood, mod-4 adjacency rules, barycentric coordinates) derives word-vector encodings.</li>
                                <li><strong>v18 Integer Output:</strong> Every input word maps deterministically to an 18-dimensional integer vector via locked geometric rules (no randomness, no approximation).</li>
                                <li><strong>Audit Gate Principles:</strong> All operations obey fail-closed constraints: if any geometry rule is violated, execution halts with audit event (no silent failure).</li>
                                <li><strong>Reproducibility:</strong> Identical inputs always produce identical outputs; bit-level reproduction is guaranteed.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">CSGI & MainPath Skeleton</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Canonical Skeleton Graph Interface (CSGI):</strong> Represents word structure as an undirected graph Γ(w) with 18 vertices (one per v18 dimension) and edges encoding adjacency.</li>
                                <li><strong>MainPath Algorithm:</strong> Deterministic traversal of CSGI using 8-neighborhood rules and closed-hint heuristic. Produces canonical skeleton representation.</li>
                                <li><strong>Graph Invariants:</strong> Cycle detection, planarity checks, and degree constraints form audit layers. Violation → TRAP.</li>
                                <li><strong>Witness Hole Awareness:</strong> Normaliz metric detects structural "holes" in the lattice; these are documented and integral to the codex identity.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Formula Derivation & Audit Gates</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>AN/AK/AQ Formulas:</strong> Three canonical derivation chains computing word geometry invariants (area, keyword density, quaternary structure).</li>
                                <li><strong>ρ (Rho) Calculation:</strong> Modular reduction operator mapping geometry to signed byte range; deterministic and invertible.</li>
                                <li><strong>Mod-4 Rule:</strong> Every v18-word element must satisfy (element mod 4) in {'{0,1,2,3}'}; violations trigger TRAP immediately.</li>
                                <li><strong>Audit Trail:</strong> All formula steps are logged in deterministic order; reproducible independently via transcript verification.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">VC-1 Jim (ج) Vortex Anchor</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Primary Vortex:</strong> The letter ج (Jim) is the foundational anchor in Hijaiyyah geometry; its v18-vector is locked in all downstream codex computations.</li>
                                <li><strong>Binding Mechanism:</strong> All AI/ML features derive interpretability from Jim's geometric structure; predictions trace back to Jim's position in the manifold.</li>
                                <li><strong>Stability Guarantee:</strong> VC-1 Jim never changes across releases; it is locked in the canonical specification file.</li>
                                <li><strong>Interpretability Lever:</strong> Classifiers exposing Jim-derived features are inherently explainable (not black-box).</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Release & Verification</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Release Tag:</strong> <code>HL-18-v1.0+local.1</code> identifies the canonical codex engine version.</li>
                                <li><strong>Normaliz Metrics:</strong> Hilbert basis size 38, rank 14, integrally_closed=false. These constants are locked and audited in every release.</li>
                                <li><strong>CLI Verification:</strong> <code>hl18 verify-release</code> command checks bit-integrity and geometric constrains on release artifacts.</li>
                                <li><strong>Audit-Grade Contract:</strong> Fail-closed on any formula mismatch, full transcript logging, and deterministic halt semantics.</li>
                            </ul>
                        </div>
                    </div>

                    <p className="text-xs text-gray-600 dark:text-gray-400 border-l-2 border-gray-300 dark:border-gray-700 pl-2 mt-2">
                        <strong>Foundation Principle:</strong> HL-18 is the <em>ground truth</em> for the entire stack. All downstream layers (HL, HISA-VM, HCPU, Codex-AI, HGSS) depend on and validate against HL-18's deterministic output. Any modification to HL-18 requires a new release tag and cascading re-verification.
                    </p>
                </div>
            )
        },
        {
            id: "lang",
            label: "Language (HL)",
            content: (
                <div className="space-y-3 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian II: HijaiyyahLang (HL-18)</div>
                    <p className="text-gray-700 dark:text-gray-300">
                        <strong>HijaiyyahLang (HL)</strong> is the programming language layer implementing word sequences as deterministic monoid aggregations. It abstracts away low-level geometry and provides a high-level API for codex computation.
                    </p>

                    <div className="rounded border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-3 space-y-2">
                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Syntax & Semantics</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Input:</strong> Unicode text sequences (Hijaiyyah script or transliteration) representing word streams.</li>
                                <li><strong>Parsing:</strong> Deterministic tokenizer and grammar rules validate input; malformed input triggers parse error (fail-closed).</li>
                                <li><strong>Monoid Aggregation:</strong> Words are combined using associative binary ops (concatenation, blending) into composite vectors without losing structure.</li>
                                <li><strong>Output:</strong> Stream of v18-dimensional integer vectors, one per word (or aggregated composite if specified).</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Core Library & Normaliz</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Release:</strong> <code>HL-18-v1.0+local.1</code> (synchronized with HL-18 core codex version).</li>
                                <li><strong>Normaliz Integration:</strong> Hilbert basis (HB) is precomputed with 38 elements, lattice rank 14, witness hole at integrally_closed=false.</li>
                                <li><strong>Metric Invariants:</strong> Distance functions, gram matrices, and volume bounds are locked in release specification; re-verification uses these constants.</li>
                                <li><strong>Library Functions:</strong> word_to_vector, aggregate_stream, verify_sequence, export_cbor, etc.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Compilation & Execution</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Ahead-of-Time (AoT) Compilation:</strong> HL source files compile to HISA bytecode (linkable binaries suitable for HCPU/HISA-VM).</li>
                                <li><strong>Just-in-Time (JiT) Interpretation:</strong> Streaming mode allows incremental word processing without full pre-compilation.</li>
                                <li><strong>Audit Trail:</strong> Both modes emit deterministic trace logs (instruction sequence, vector values, constraint checks).</li>
                                <li><strong>Memory Model:</strong> Stack-based allocation with frame pointers; no heap randomization (deterministic layout).</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">CLI & Verification Tools</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong><code>hl18</code> Command:</strong> Main entry point for parsing, compiling, and executing HL programs.</li>
                                <li><strong><code>verify-hl18-release</code>:</strong> Checks release integrity (manifest hashes, version locks, Normaliz metric constants).</li>
                                <li><strong><code>export-vectors</code>:</strong> Batch processing utility to export word sequences to v18 vectors in JSON/CBOR format.</li>
                                <li><strong><code>benchmark-codex</code>:</strong> Performance testing tool with auditable timing and constraint violation detection.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Standards & Interoperability</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>CBOR Export:</strong> Compiled v18 vectors can be exported as RFC 8949 canonical CBOR for third-party processing.</li>
                                <li><strong>JSON-LD Context:</strong> Optional semantic annotation using standard ontology (metadata, version, timestamp).</li>
                                <li><strong>Test Vectors:</strong> Official test suites with golden outputs; every HL implementation must pass 100% of tests (regression suite).</li>
                                <li><strong>Binding Verification:</strong> Cross-check HL outputs against HL-18 ground truth; deterministic equivalence is proven per release.</li>
                            </ul>
                        </div>
                    </div>

                    <p className="text-xs text-gray-600 dark:text-gray-400 border-l-2 border-gray-300 dark:border-gray-700 pl-2 mt-2">
                        <strong>Design Intent:</strong> HijaiyyahLang is a practical abstraction layer. Users write HL programs instead of raw HISA bytecode. The compiler ensures all geometric rules are enforced at compile time, making runtime violations impossible (fail-closed-by-design).
                    </p>
                </div>
            )
        },
        {
            id: "isa",
            label: "ISA/VM (HISA)",
            content: (
                <div className="space-y-3 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian III: HISA / Virtual Machines</div>
                    <p className="text-gray-700 dark:text-gray-300">
                        The <strong>Hijaiyyah Instruction Set Architecture (HISA)</strong> is the deterministic contract layer defining bit-exact instruction encoding, execution semantics, and audit guarantees. It bridges high-level HL programs and low-level HCPU hardware.
                    </p>

                    <div className="rounded border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-3 space-y-2">
                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Instruction Encoding & Contract</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Instruction Format:</strong> Fixed 32-bit encoding: [opcode (6 bits) | Rd (4 bits) | Ra (4 bits) | Rb (4 bits) | subop (5 bits) | imm8 (8 bits)].</li>
                                <li><strong>Opcode Space:</strong> 64 primary operations (arithmetic, memory, geometry, control flow); subop extends this for variants.</li>
                                <li><strong>Register Constraints:</strong> Rd ≠ Ra (no read-after-write hazards). This forces structured computation and prevents hidden data flow.</li>
                                <li><strong>Deterministic Encoding:</strong> No alternative representations; canonical form is enforced by parser and verifier.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Instruction Set & Semantics</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>VEC (Vector) Ops:</strong> VADD, VSUB, VMUL, VMOD4, VGEOM (18-lane operations on V-registers).</li>
                                <li><strong>SCALAR Ops:</strong> ADD, SUB, MUL, MOD, CMP (64-bit integer operations on R-registers).</li>
                                <li><strong>MEMORY Ops:</strong> LOAD, STORE (with 256-byte alignment invariants). No unaligned access.</li>
                                <li><strong>CONTROL Ops:</strong> JMP, JCOND, CALL, RET, HALT (deterministic branching, no speculative execution).</li>
                                <li><strong>GEOMETRY Ops:</strong> CSGI_QUERY, MAINPATH, AN_DERIV, AK_DERIV, AQ_DERIV (direct codex computation).</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Fail-Closed TRAP Taxonomy</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>TRAP Types:</strong> 16 distinct fail conditions (GEOMETRY_VIOLATION, CONSTRAINT_BREACH, UNDEFINED_OP, MEMORY_FAULT, etc.).</li>
                                <li><strong>Halt Semantics:</strong> Any TRAP immediately halts execution and emits audit event. No recovery, no masking.</li>
                                <li><strong>Status Register:</strong> TRAP flag and trap code are recorded for inspection (read-only to user code).</li>
                                <li><strong>Audit Trace:</strong> Instruction sequence up to TRAP is logged deterministically; reproducible failure diagnosis.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">CORE-1 Adjacency Rules</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Definition:</strong> CORE-1 specifies valid register sequences and data dependency patterns across instructions.</li>
                                <li><strong>Constraint:</strong> No instruction may read a register modified by the immediately preceding instruction (1-cycle read-after-write forbidden).</li>
                                <li><strong>Verification:</strong> Static analyzer checks all compiled HISA bytecode for CORE-1 violations before execution (fail-closed at load time).</li>
                                <li><strong>Pipeline Consideration:</strong> Ensures deterministic behavior even under pipelined hardware (no timing-dependent bugs).</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">HISA-VM (Reference Virtual Machine)</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Purpose:</strong> Cycle-accurate interpreter of HISA instructions; used for offline audit and trace verification.</li>
                                <li><strong>State Machine:</strong> Fetch → Decode → Execute → Write-back (4-stage pipeline, fully deterministic, no speculation).</li>
                                <li><strong>Audit Features:</strong> Instruction-by-instruction logging, register snapshots, memory trace, constraint checks.</li>
                                <li><strong>Binary Equivalence:</strong> Produces identical results to HCPU hardware implementations (Silicon/Photonic/Quantum).</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">HCVM (Crypto Virtual Machine)</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Purpose:</strong> Extended VM for HGSS pipeline execution, adding cryptographic primitives and evidence generation.</li>
                                <li><strong>Extensions:</strong> CBOR encoding/decoding ops, SHA-256 hashing, HMAC computation, nonce management.</li>
                                <li><strong>Entropy Locked:</strong> Execution entropy is strictly controlled; every random decision is logged and reproducible.</li>
                                <li><strong>Evidence Trail:</strong> HCVM records all intermediate states and produces evidence.json artifact at program termination.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Compiler & LLVM/MLIR Integration</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>LLVM Target:</strong> HISA is implemented as an LLVM backend; high-level LLVM IR can be lowered to HISA bytecode.</li>
                                <li><strong>Vector Lowering:</strong> LLVM &lt;18 × i32&gt; vector types map directly to HISA V-registers (no scalarization needed).</li>
                                <li><strong>MLIR Dialect:</strong> Custom MLIR dialect represents HISA operations at intermediate representation level; enables optimization passes.</li>
                                <li><strong>Verification Hook:</strong> All compiled HISA code passes static analysis (CORE-1, geometry constraints) before code generation.</li>
                            </ul>
                        </div>
                    </div>

                    <p className="text-xs text-gray-600 dark:text-gray-400 border-l-2 border-gray-300 dark:border-gray-700 pl-2 mt-2">
                        <strong>Design Philosophy:</strong> HISA is the <em>narrow waist</em> of the stack. Everything above (HijaiyyahLang, Codex-AI) compiles down to HISA. Everything below (HCPU, HCVM) implements HISA. Modifications to HISA require formal specification updates and comprehensive re-verification across all layers.
                    </p>
                </div>
            )
        },
        {
            id: "compute",
            label: "Compute (HCPU)",
            content: (
                <div className="space-y-3 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian IV: HC-HCPU (Silicon / Photonic / Qubit)</div>
                    <p className="text-gray-700 dark:text-gray-300">
                        The <strong>Hijaiyyah Core Processing Unit (HCPU)</strong> is a family of deterministic compute architectures designed to execute the HISA contract faithfully. Three reference implementations are provided: Silicon (practical baseline), Photonic (next-gen acceleration), and Quantum (reversible research).
                    </p>

                    <div className="rounded border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-3 space-y-2">
                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Architecture & Register File</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>18-Lane Vector Units (V0..V15):</strong> Each V-register holds 18× u32 words matching v18 codex word size. All vector operations are deterministic and fail-closed on geometry constraint violations.</li>
                                <li><strong>Scalar Registers (R0..R7):</strong> 64-bit integer registers for loop counters, addresses, and control flow. Operations are HISA-audited.</li>
                                <li><strong>Program Counter & Status:</strong> Instruction fetch respects alignment rules. Status flags (ZERO, TRAP, HALT) are observable for audit tracing.</li>
                                <li><strong>Memory Contract:</strong> Byte-addressable with 256-byte alignment boundaries (matching codex frame boundaries). Cache coherency is deterministic.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Silicon Implementation (HC-HCPU-Si)</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Datapath:</strong> 18-lane SIMD microarchitecture with per-cycle arithmetic diversity (mod-4 geometry checks, AN/AK/AQ derivations).</li>
                                <li><strong>Clock Synchronization:</strong> Deterministic all-lanes-synchronized execution; no speculative paths to avoid audit trail ambiguity.</li>
                                <li><strong>Fail-Closed TRAP Logic:</strong> Any geometry violation (constraint failure) triggers TRAP; halt and audit event logging (not recovery).</li>
                                <li><strong>Throughput:</strong> ~2 v18-word operations per cycle per V-lane, aggregate 36 words/cycle (theoretical peak).</li>
                                <li><strong>Verification Hook:</strong> Cycle-accurate reference model (in C/Verilog) allows offline audit reproduction.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Photonic Implementation (HC-HCPU-Ph)</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>WDM Channels:</strong> 18 independent wavelengths carrying parallel v18-word computation. Each wavelength carries a distinct logic stream.</li>
                                <li><strong>Optical Gates:</strong> Deterministic logic implemented via phase-tuned Mach-Zehnder interferometers and photonic switches.</li>
                                <li><strong>Synchronization:</strong> Common optical clock ensures all wavelengths remain phase-aligned (deterministic global synchronization guaranteed).</li>
                                <li><strong>Audit Trail:</strong> Inline phase-locked photodiodes sample every wavelength for real-time trace verification.</li>
                                <li><strong>Latency & Throughput:</strong> Potential 10× speedup vs silicon from optical parallelism; determinism maintained end-to-end.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Quantum Implementation (HC-HCPU-Qu)</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Reversible Subset:</strong> Subset of HISA amenable to reversible quantum circuits (NOT, CNOT, Toffoli chains).</li>
                                <li><strong>Ancilla State Encoding:</strong> Temporary working qubits used for uncompute steps; no net entropy increase.</li>
                                <li><strong>Measurement & Collapse:</strong> Final v18-word read forces quantum-to-classical collapse; result is deterministic (no randomness in output, only in hidden ancilla states).</li>
                                <li><strong>Audit:</strong> Quantum traces are reproducible but verification requires controlled re-execution (experimental research, not production).</li>
                                <li><strong>Advantage:</strong> Potential exponential speedup for certain geometry queries; reversible nature ensures no ambient entropy leakage.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Release & Verification</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>HCPU Reference RTL:</strong> Verilog/SystemVerilog specifications for all three implementations, locked in release manifests.</li>
                                <li><strong>Verification Methodologies:</strong> Silicon via formal model checking and cycle-accurate trace comparison. Photonic via optical simulation (Lumerical/VPIphotonics). Quantum via Qiskit verification circuits.</li>
                                <li><strong>Binding to HL-18:</strong> All three implementations guarantee bit-identical v18 outputs (formal correctness); interchange is deterministic.</li>
                                <li><strong>Audit Contract:</strong> Fail-closed TRAP on any geometry violation, full event logging, deterministic halt (no recovery paths).</li>
                            </ul>
                        </div>
                    </div>

                    <p className="text-xs text-gray-600 dark:text-gray-400 border-l-2 border-gray-300 dark:border-gray-700 pl-2 mt-2">
                        <strong>Design Principle:</strong> All three HCPU variants (Silicon, Photonic, Quantum) are <em>substitutable</em> at the HISA contract boundary. Choosing Silicon is default (proven, mature). Photonic and Quantum are research-grade accelerators that maintain the same deterministic, audit-grade guarantees.
                    </p>
                </div>
            )
        },
        {
            id: "ai",
            label: "AI (Codex-AI)",
            content: (
                <div className="space-y-3 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian V: Codex-AI Universal Harness + HGSS-HCVM</div>
                    <p className="text-gray-700 dark:text-gray-300">
                        The <strong>Codex-AI layer</strong> is an industrial AI harness that bridges geometric-deterministic codex computation with practical machine learning. It provides both baseline and guarded execution modes with audit-grade evidence generation.
                    </p>

                    <div className="rounded border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-3 space-y-2">
                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Core Architecture</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Vision → CSGI → v18 Pipeline:</strong> Input streams (images, text) decode to Canonical Skeleton Graph Interface (CSGI), then map to v18 integer vectors via HL-18 codex engine.</li>
                                <li><strong>Deterministic Audit Gates:</strong> All vector operations lock to mod-4 geometric rules, CORE-1 adjacency verification, and AN/AK/AQ formula derivation (fail-closed on violation).</li>
                                <li><strong>Interpretable Classifiers:</strong> Output layers expose codex manifold decisions (not black-box neural nets); every prediction traces back to frozen geometric locks.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Execution Modes</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Baseline Mode:</strong> Direct codex computation (fast, deterministic, but minimal adaptation).</li>
                                <li><strong>Guarded Mode (Recommended):</strong> Wraps baseline with HGSS oracle loops, repair logic, and consensus verification. Slower but audit-grade with full evidence trail.</li>
                                <li><strong>A/B Testing:</strong> Run baseline vs guarded in parallel, measure pass@1 vs pass@k metrics, capture divergence forensics.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Release & Versions</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Release:</strong> <code>HCPU-AI-v1.0+local.1</code> (currently in test/demo phase)</li>
                                <li><strong>HGSS-HCVM Binding:</strong> Codex-AI runs under HGSS-HCVM-v1.HC18DC for evidence-grade security wrapper and frozen attestation.</li>
                                <li><strong>Dependency Chain:</strong> Requires HL-18-v1.0+local.1 (codex engine), HISA-VM-v1.0 (execution), and locked release manifests.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Evaluation & Forensics</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Pass@1 / Pass@k:</strong> Deterministic single-shot accuracy vs multi-attempt consensus scoring.</li>
                                <li><strong>HGSS Artifacts:</strong> Every execution generates <code>evidence.json</code> with frozen schema locks, SHA-256 reproducibility, and canonical CBOR digest.</li>
                                <li><strong>Audit Trail:</strong> Client-side frozen checks + server-side CBOR verification ensure no silent failures (fail-closed on any schema breach).</li>
                                <li><strong>Interoperability:</strong> All results are RFC 8949 canonical and suitable for third-party verification and compliance workflows.</li>
                            </ul>
                        </div>
                    </div>

                    <p className="text-xs text-gray-600 dark:text-gray-400 border-l-2 border-gray-300 dark:border-gray-700 pl-2 mt-2">
                        <strong>Note:</strong> Codex-AI is <em>not</em> a probabilistic deep learning model. It is deterministic geometry-based computation that happens to be packaged as an AI harness. All decisions are auditable, reproducible, and locked to integer operations.
                    </p>
                </div>
            )
        },
        {
            id: "security",
            label: "Security (HGSS)",
            content: (
                <div className="space-y-3 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian VI: HGSS / HC18DC (Guarded Signature Scheme)</div>
                    <p className="text-gray-700 dark:text-gray-300">
                        The <strong>Hijaiyyah Guarded Signature Scheme (HGSS)</strong> is an evidence-grade cryptographic wrapper and oracle harness that provides non-repudiation, audit trails, and deterministic repair for the deterministic codex computation.
                    </p>

                    <div className="rounded border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-3 space-y-2">
                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">HC18DC (Hijaiyyah Codex 18-Dimensional Canonical)</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Output Target:</strong> All HGSS computations produce HC18DC artifacts: deterministic, locked, and canonical.</li>
                                <li><strong>18 Dimensions:</strong> Output space is isomorphic to v18 codex geometry, ensuring full traceability back to HL-18 origin.</li>
                                <li><strong>Canonical Representation:</strong> RFC 8949 CBOR encoding enforces single serialization form (no alternative encodings possible).</li>
                                <li><strong>Immutability Lock:</strong> Once computed, HC18DC artifacts are frozen and cannot be modified without invalidating all downstream signatures.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Frozen Schema & Audit Rules</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Frozen JSON/CBOR Schema:</strong> Client-side schema validation checks all required fields, types, and format constraints before any cryptographic operation.</li>
                                <li><strong>Field Derivations:</strong> Metadata fields (timestamp, version, schema_version) are deterministically derived and immutable.</li>
                                <li><strong>Hash Chains:</strong> Every artifact participates in SHA-256 hash chains; breaking any link invalidates all downstream proofs.</li>
                                <li><strong>Fail-Closed Semantics:</strong> Any schema violation (missing field, wrong type, constraint breach) triggers TRAP and audit logging (no recovery).</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Canonical CBOR Digest & Verification</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>RFC 8949 Encoding:</strong> All artifacts are serialized using canonical CBOR (deterministic encoding rules ensure single valid representation).</li>
                                <li><strong>Digest Computation:</strong> event_sha256 is the SHA-256 hash of the canonical CBOR payload (excluding the signature itself).</li>
                                <li><strong>Reproducible Verification:</strong> Any independent verifier can re-encode the same data and confirm the digest matches (no ambiguity).</li>
                                <li><strong>Interoperability:</strong> Third-party tools can verify HGSS artifacts without proprietary code; CBOR is a standard data format.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Guarded Execution & Oracle Loops</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Baseline Computation:</strong> Plain deterministic codex calculation (fast, minimal overhead).</li>
                                <li><strong>Guarded Mode:</strong> Wraps baseline with oracle loops that verify results at checkpoints, detect divergences, and trigger repair if needed.</li>
                                <li><strong>Repair Logic:</strong> If divergence detected, HGSS applies consensus voting (multiple independent runs), re-derives affected vectors, and logs the anomaly.</li>
                                <li><strong>Evidence Generation:</strong> Every guarded execution produces evidence.json with full trace (inputs, intermediate states, outputs, repair decisions).</li>
                                <li><strong>Non-Repudiation:</strong> Oracle signature binds evidence to computational identity; proof is cryptographically sound.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Binding & Key Derivation</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>AAD (Additional Authenticated Data):</strong> Binds context (module version, release tag, executor identity) to every computation.</li>
                                <li><strong>KDF (Key Derivation Function):</strong> HMAC-based, derives per-execution cryptographic keys from master seed and nonce.</li>
                                <li><strong>Nonce Governance:</strong> Range-leased nonces ensure no key reusage across independent executions.</li>
                                <li><strong>Entropy Source:</strong> CSPRNG (cryptographically secure random generator) is used for nonce generation; entropy pool is system-audited.</li>
                            </ul>
                        </div>

                        <div>
                            <span className="font-semibold text-gray-800 dark:text-gray-100">Release & Distribution</span>
                            <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300 mt-1 space-y-1">
                                <li><strong>Release Tag:</strong> <code>HGSS-HCVM-v1.HC18DC</code> identifies the canon guarded scheme implementation and output target.</li>
                                <li><strong>Binding to Codex-AI:</strong> Codex-AI harness runs under HGSS for guarded execution; all predictions are wrapped in HC18DC artifacts.</li>
                                <li><strong>Distribution Format:</strong> AuditorBundle packages HGSS runtime, specifications, sample evidence, and verification tools as a unified release.</li>
                                <li><strong>Cryptographic Attestation:</strong> Release manifest is signed by auditor authority; tamper detection is automatic.</li>
                            </ul>
                        </div>
                    </div>

                    <p className="text-xs text-gray-600 dark:text-gray-400 border-l-2 border-gray-300 dark:border-gray-700 pl-2 mt-2">
                        <strong>Design Principle:</strong> HGSS is an <em>optional but recommended</em> security wrapper. You can run baseline (deterministic, fast) or guarded (deterministic + evidence + repair + non-repudiation). Both modes are valid; guarded is recommended for audit-grade deployments.
                    </p>
                </div>
            )
        }
    ];

    return (
        <div className="space-y-4">
            <h1 className="text-2xl font-bold">Technology Stack</h1>
            <p className="text-gray-700 dark:text-gray-300">
                The stack is modular. Releases are enumerated in the Release Identity Matrix and can be verified via commands.
            </p>

            <StackDiagram />

            <Tabs items={tabItems} defaultId="core" />

            <div className="rounded-xl border bg-white p-4 dark:bg-gray-900 dark:border-gray-800">
                <div className="text-sm font-semibold">Modules (from Release Identity Matrix)</div>
                <ul className="mt-2 list-disc pl-5 text-sm text-gray-700 dark:text-gray-300">
                    {mods.map((m, i) => (
                        <li key={i}>
                            <span className="font-semibold">{m.layer}:</span> {m.name} —{" "}
                            <span className="font-mono">{m.release_id}</span>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
