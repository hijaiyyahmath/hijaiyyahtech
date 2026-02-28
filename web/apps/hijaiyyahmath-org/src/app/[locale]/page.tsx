import Link from "next/link";
import ReleaseBadge from "@/components/ReleaseBadge";
import CodeBlock from "@/components/CodeBlock";
import HijaiyyahLetterRow from "@/components/HijaiyyahLetterRow";

export default function Page() {
    const quick = `# Quick verification (Windows PowerShell)
cd c:\\hijaiyah-codex

python scripts/env_check.py
python scripts/run_tests_all.py
python scripts/run_demos_all.py

# Web sample
curl http://localhost:3000/downloads/hgss/evidence.json`;

    return (
        <div className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-2">
                <div className="space-y-3">
                    <h1 className="text-3xl font-bold">
                        Matematika Hijaiyyah Technology Stack v1.0
                    </h1>
                    <p className="text-gray-700 dark:text-gray-300">
                        A deterministic, audit-aware technology stack built from Hijaiyyah geometric codex (v18),
                        spanning language, ISA, compute (silicon/photonic/qubit), AI harness, and optional security module (HGSS/HC18DC).
                    </p>

                    <div className="flex flex-wrap gap-2">
                        <Link className="rounded-md bg-black px-3 py-2 text-sm text-white dark:bg-white dark:text-black" href="/en/stack">
                            View Technology Stack
                        </Link>
                        <Link className="rounded-md border px-3 py-2 text-sm dark:border-gray-800" href="/en/tools/evidence-verifier">
                            Evidence Verifier Tool
                        </Link>
                        <Link className="rounded-md border px-3 py-2 text-sm dark:border-gray-800" href="/en/releases">
                            Release Matrix
                        </Link>
                    </div>
                </div>

                <ReleaseBadge />
            </div>

            <HijaiyyahLetterRow />

            <div>
                <h2 className="text-xl font-semibold">Quick Commands</h2>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Copy-paste commands to verify the monorepo and run key demos.
                </p>
                <div className="mt-3">
                    <CodeBlock code={quick} />
                </div>
            </div>

            <div>
                <h2 className="text-xl font-semibold">Stack Definitions</h2>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Core terminology used across the Matematika Hijaiyyah ecosystem.
                </p>
                <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {[
                        {
                            term: "HL-18 (HijaiyahLang)",
                            def: "Word-to-Vector (v18) audit engine and ground-truth implementation for the Hijaiyyah codex.",
                            audit: ["Release: HL-18-v1.0+local.1", "Normaliz Metric Validation", "Injective Mapping Audit"]
                        },
                        {
                            term: "HISA",
                            def: "Hijaiyyah Instruction Set Architecture: Audit-centric ISA for deterministic execution via HISA-VM.",
                            audit: ["ISA Table Conformance", "Bit-exact IW Encoding", "Fail-closed TRAP Taxonomy"]
                        },
                        {
                            term: "HCPU-AI",
                            def: "Reference execution engine for stack compliance, integrating AI loops with HISA-VM delegation.",
                            audit: ["Release: HCPU-AI-v1.0+local.1", "Regs: 18xV(u32), 8xR(u64)", "Modes: CORE/FEEDBACK/OWNER"]
                        },
                        {
                            term: "HGSS-HCVM",
                            def: "Deterministic crypto pipeline (HCVM) executing the security wrapper (HGSS) for evidence generation.",
                            audit: ["Audit-grade deterministic VM", "Evidence-grade security wrapper", "Frozen Schema Validation"]
                        },
                        {
                            term: "HC18DC",
                            def: "Hijaiyyah Codex 18-Dimensional Canonical: The normative geometric artifact produced by the HGSS pipeline.",
                            audit: ["Canonical CBOR Digest", "Deterministic Target Output", "Traceable Audit Artifact"]
                        },
                        {
                            term: "HC-HCPU",
                            def: "Physical implementation targets for HISA: Silicon microarchitecture, Photonic accelerators, or Qubit subsets.",
                            audit: ["18-lane Silicon Datapath", "Photonic WDM Verification", "Reversible Qubit Subset"]
                        },
                    ].map((item, i) => (
                        <div key={i} className="rounded-xl border bg-white p-4 dark:bg-gray-900 dark:border-gray-800 flex flex-col">
                            <div className="font-semibold text-black dark:text-white border-b pb-2 mb-2 dark:border-gray-800">{item.term}</div>
                            <div className="text-sm text-gray-700 dark:text-gray-300 flex-grow">{item.def}</div>
                            <div className="mt-3 pt-3 border-t dark:border-gray-800">
                                <span className="text-[10px] uppercase tracking-wider font-bold text-gray-400 dark:text-gray-500">Audit Stages</span>
                                <ul className="mt-1 space-y-1 text-[11px] font-mono text-gray-600 dark:text-gray-400">
                                    {item.audit.map((step, si) => (
                                        <li key={si}>• {step}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="rounded-xl border bg-white p-4 dark:bg-gray-900 dark:border-gray-800">
                <div className="text-sm font-semibold">Public Sample</div>
                <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">
                    Readers can download the official HGSS sample and verify it using the web tool.
                </p>
                <div className="mt-2 text-sm">
                    <a className="text-blue-700 underline" href="/downloads/hgss/evidence.json" target="_blank">/downloads/hgss/evidence.json</a>
                </div>
            </div>
        </div>
    );
}
