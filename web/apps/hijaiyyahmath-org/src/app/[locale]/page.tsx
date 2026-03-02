import Link from "next/link";
import ReleaseBadge from "@/components/ReleaseBadge";
import CodeBlock from "@/components/CodeBlock";
import HijaiyyahLetterRow from "@/components/HijaiyyahLetterRow";

export default function Page({ params }: { params: { locale: string } }) {
    const quick = `# Quick verification (Windows PowerShell)
cd c:\\hijaiyyah-codex

python scripts/env_check.py
python scripts/run_tests_all.py
python scripts/run_demos_all.py

# Web sample
curl http://localhost:3000/hijaiyyahtech/downloads/hgss/evidence.json`;

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
                        <Link className="rounded-md bg-black px-3 py-2 text-sm text-white dark:bg-white dark:text-black" href={`/${params.locale}/stack`}>
                            View Technology Stack
                        </Link>
                        <Link className="rounded-md border px-3 py-2 text-sm dark:border-gray-800" href={`/${params.locale}/tools/evidence-verifier`}>
                            Evidence Verifier Tool
                        </Link>
                        <Link className="rounded-md border px-3 py-2 text-sm dark:border-gray-800" href={`/${params.locale}/releases`}>
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
                            term: "HL-18 (HijaiyyahLang)",
                            def: "Word-to-Vector (v18) audit engine and ground-truth implementation for the Hijaiyyah codex.",
                            audit: ["Release: HL-18-v1.0+local.1", "Normaliz Metric Validation", "Injective Mapping Audit"]
                        },
                        {
                            term: "H-ISA (Hijaiyyah-Instruction Architecture)",
                            def: "Audit-centric Instruction Set Architecture for deterministic execution via HISA-VM.",
                            audit: ["ISA Table Conformance", "Bit-exact IW Encoding", "Fail-closed TRAP Taxonomy"]
                        },
                        {
                            term: "HCPU (Hijaiyyah Core Processing Unit)",
                            def: "Deterministic compute module (Silicon/Photonic/Qubit) for H-ISA execution.",
                            audit: ["18-lane Silicon Datapath", "Photonic WDM Verification", "Reversible Qubit Subset"]
                        },
                        {
                            term: "HCVM (Hijaiyyah Crypto Virtual Machine)",
                            def: "Normative Virtual Machine for audit trail execution and evidence-grade integrity.",
                            audit: ["Release: HISA-VM-v1.0+local.1", "Entropy-locked execution", "Deterministic TRAP logging"]
                        },
                        {
                            term: "HGSS (Hijaiyyah Guarded Signature Scheme)",
                            def: "Industrial AI harness with guarded repair loops and evidence generation.",
                            audit: ["Release: HCPU-AI-v1.0+local.1", "Audit-grade deterministic VM", "Frozen Schema Validation"]
                        },
                        {
                            term: "HC18DC (Hijaiyyah Codex 18-Dimensional Canonical) CSGI",
                            def: "The normative geometric artifact and Canonical Skeleton Graph Interface (CSGI) implementation lock.",
                            audit: ["Canonical CBOR Digest", "Skeletal Graph Γ(h) Lock", "Traceable Audit Artifact"]
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
                    <a className="text-blue-700 underline" href="/hijaiyyahtech/downloads/hgss/evidence.json" target="_blank">/hijaiyyahtech/downloads/hgss/evidence.json</a>
                </div>
            </div>
        </div>
    );
}
