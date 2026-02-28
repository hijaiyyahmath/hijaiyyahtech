import Tabs from "@/components/Tabs";
import { getReleaseMatrix } from "@/lib/loadContent";
import CodeBlock from "@/components/CodeBlock";

function StackDiagram() {
    const diagram = `
HL-18 (Mathematics / v18)
      ↓
HijaiyahLang (Language)
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
                <div className="space-y-2 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian I: Matematika Hijaiyyah Core</div>
                    <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300">
                        <li><strong>Origin Protocol:</strong> Discrete geometry → v18 codex → Audit.</li>
                        <li><strong>CSGI & MainPath:</strong> Deterministic skeleton graph (8-neighborhood) & closed_hint.</li>
                        <li><strong>Audit Gates:</strong> Formula derivations (AN/AK/AQ, U/ρ, mod-4 rule) with TRAP on mismatch.</li>
                        <li><strong>VC-1 Jim (ج):</strong> Primary vortex anchor for binding and interpretable AI features.</li>
                    </ul>
                </div>
            )
        },
        {
            id: "lang",
            label: "Language (HL)",
            content: (
                <div className="space-y-2 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian II: HijaiyahLang HL-18</div>
                    <p className="text-gray-700 dark:text-gray-300">
                        A release-grade language core implementing word sequences as monoid aggregations.
                    </p>
                    <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300">
                        <li><strong>Release Tree:</strong> <code>HL-18-v1.0+local.1</code> with SHA-256 integrity locks.</li>
                        <li><strong>Normaliz Metrics:</strong> HB size 38, rank 14, integrally_closed=false (witness hole aware).</li>
                        <li><strong>CLI Entrypoints:</strong> <code>hl18</code> and <code>verify-hl18-release</code>.</li>
                    </ul>
                </div>
            )
        },
        {
            id: "isa",
            label: "ISA/VM (HISA)",
            content: (
                <div className="space-y-2 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian III: HISA + Virtual Machines</div>
                    <p className="text-gray-700 dark:text-gray-300">
                        Bit-exact instruction contract [opcode|Rd|Ra|Rb|subop|imm8] for deterministic auditing.
                    </p>
                    <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300">
                        <li><strong>HISA v1.0:</strong> Fail-closed TRAP taxonomy and CORE-1 adjacency rules.</li>
                        <li><strong>HISA-VM:</strong> Deterministic register machine for codex audit (AN/AK/AQ, rho, mod-4).</li>
                        <li><strong>HCVM:</strong> Crypto Virtual Machine for HGSS pipeline execution.</li>
                        <li><strong>LLVM/MLIR:</strong> Pattern for <code>&lt;18 x i32&gt;</code> V-register lowering.</li>
                    </ul>
                </div>
            )
        },
        {
            id: "compute",
            label: "Compute (HCPU)",
            content: (
                <div className="space-y-2 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian IV: HC-HCPU (Silicon / Photonic / Qubit)</div>
                    <p className="text-gray-700 dark:text-gray-300">
                        Reference hardware architectures derived from the HISA contract.
                    </p>
                    <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300">
                        <li><strong>Silicon:</strong> 18-lane microarchitecture, V0..V15 (18x u32) + scalar R0..R7.</li>
                        <li><strong>Photonic:</strong> WDM channel mapping for 18-lane acceleration, verified by audit.</li>
                        <li><strong>Qubit:</strong> Reversible subset research with ancilla/uncompute state encoding.</li>
                    </ul>
                </div>
            )
        },
        {
            id: "ai",
            label: "AI (Codex-AI)",
            content: (
                <div className="space-y-2 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian V: Codex-AI Universal + HGSS VM</div>
                    <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300">
                        <li><strong>Hybrid Model:</strong> Vision → CSGI → v18 → Audit → Interpretable Classifier.</li>
                        <li><strong>Harness:</strong> Baseline vs Guarded (A/B Test) with repair loops and HGSS oracles.</li>
                        <li><strong>Metrics:</strong> pass@1 vs pass@k evaluation with forensic artifact generation.</li>
                    </ul>
                </div>
            )
        },
        {
            id: "security",
            label: "Security (HGSS)",
            content: (
                <div className="space-y-2 text-sm">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">Bagian VI: HGSS / HC18DC</div>
                    <p className="text-gray-700 dark:text-gray-300">
                        Evidence-grade crypto wrapper for non-disputable multi-dimensional artifacts.
                    </p>
                    <ul className="list-disc pl-5 text-gray-700 dark:text-gray-300">
                        <li><strong>HC18DC:</strong> Hijaiyyah Codex 18-Dimensional Canonical output target.</li>
                        <li><strong>Audit Schema:</strong> Frozen rules, Canonical CBOR, and event_sha256 locks.</li>
                        <li><strong>Binding:</strong> AAD/KDF binding and strict nonce governance range leasing.</li>
                    </ul>
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
