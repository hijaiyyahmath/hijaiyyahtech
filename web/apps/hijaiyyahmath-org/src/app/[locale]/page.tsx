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
curl https://hijaiyyahmath.github.io/hijaiyyahtech/en/artifacts/evidence.json`;

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold mb-4">
                    Matematika Hijaiyyah Technology Stack v1.0
                </h1>
                
                <div className="prose dark:prose-invert max-w-none space-y-4 mb-6">
                    <p className="text-gray-700 dark:text-gray-300 text-base leading-relaxed">
                        Matematika Hijaiyyah Technology Stack v1.0 is a deterministic, audit‑grade computing framework built on a discrete geometric encoding of the canonical 28 Hijaiyyah letters. It defines a dataset‑sealed mathematical domain (H₂₈) and maps each letter to a canonical 18‑dimensional integer vector (v18) via HL‑18 (HijaiyahLang 18‑Dimensional). All computations are integer‑only and governed by explicit, checkable invariants.
                    </p>
                    
                    <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-6 space-y-4">
                        <div>
                            <h3 className="font-bold text-black dark:text-white mb-3">Stack Structure (Locked Terms)</h3>
                            <div className="space-y-3 text-sm">
                                <div>
                                    <div className="font-semibold text-black dark:text-white">HL‑18 (HijaiyahLang 18‑Dimensional)</div>
                                    <p className="text-gray-600 dark:text-gray-400 mt-1">Word‑to‑Vector engine (v18), canonical codex implementation, and mathematical audit layer.</p>
                                    <p className="text-gray-500 dark:text-gray-500 mt-1 font-mono text-xs">Repo: hijaiyahlang-hl18/ | Verifier: <code className="bg-gray-100 dark:bg-gray-800 px-1 rounded">verify-hl18-release --spec specs/HL18_release_integrity_local.yaml --check-manifest</code></p>
                                </div>
                                <div>
                                    <div className="font-semibold text-black dark:text-white">HISA (Hijaiyyah Instruction Set Architecture)</div>
                                    <p className="text-gray-600 dark:text-gray-400 mt-1">Audit‑centric instruction architecture for executing codex operations.</p>
                                    <p className="text-gray-500 dark:text-gray-500 mt-1 font-mono text-xs">Normative reference: cmm18c/spec/ISA_TABLE.md and hisa-vm/</p>
                                </div>
                                <div>
                                    <div className="font-semibold text-black dark:text-white">HISA‑VM</div>
                                    <p className="text-gray-600 dark:text-gray-400 mt-1">Deterministic virtual machine for executing HISA programs and enforcing invariant gates (fail‑closed).</p>
                                </div>
                                <div>
                                    <div className="font-semibold text-black dark:text-white">HGSS‑HCVM‑v1.HC18DC</div>
                                    <p className="text-gray-600 dark:text-gray-400 mt-1">Evidence‑grade security wrapper where HCVM runs the HGSS pipeline to produce the canonical HC18DC artifact.</p>
                                    <p className="text-gray-500 dark:text-gray-500 mt-1 font-mono text-xs">Normative reference: hgss-hc18dc/spec/HCVM_ISA.md</p>
                                </div>
                            </div>
                        </div>
                        
                        <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                            <h3 className="font-bold text-black dark:text-white mb-2">Deterministic Composition (Words / Text)</h3>
                            <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">Words are constructed as additive compositions of letter vectors:</p>
                            <div className="bg-white dark:bg-gray-800 rounded p-3 font-mono text-sm text-center text-gray-800 dark:text-gray-300">
                                Cod(w) = ∑v18
                            </div>
                            <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">ensuring deterministic and auditable aggregation.</p>
                        </div>
                    </div>
                    
                    <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-6">
                        <h3 className="font-bold text-black dark:text-white mb-3">What the Stack Enforces (Audit Contract)</h3>
                        <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                            <li className="flex items-start"><span className="mr-2 font-bold text-black dark:text-white">•</span>Dataset‑sealed execution (SHA‑256 + MANIFEST release integrity)</li>
                            <li className="flex items-start"><span className="mr-2 font-bold text-black dark:text-white">•</span>Integer‑only computation</li>
                            <li className="flex items-start"><span className="mr-2 font-bold text-black dark:text-white">•</span>CORE‑1 adjacency rule: SETFLAG → AUDIT</li>
                            <li className="flex items-start"><span className="mr-2 font-bold text-black dark:text-white">•</span>mod‑4 geometric gate</li>
                            <li className="flex items-start"><span className="mr-2 font-bold text-black dark:text-white">•</span>Fail‑closed behavior: invariant violations trigger TRAP/HALT</li>
                        </ul>
                    </div>
                    
                    <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-6">
                        <h3 className="font-bold text-black dark:text-white mb-3">What This Website Provides</h3>
                        <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                            <li className="flex items-start"><span className="mr-2 font-bold text-black dark:text-white">•</span>Release matrix and version locks</li>
                            <li className="flex items-start"><span className="mr-2 font-bold text-black dark:text-white">•</span>Auditor Bundle downloads (offline‑ready)</li>
                            <li className="flex items-start"><span className="mr-2 font-bold text-black dark:text-white">•</span>Deterministic verification guidance</li>
                            <li className="flex items-start"><span className="mr-2 font-bold text-black dark:text-white">•</span>Evidence and artifact validation</li>
                        </ul>
                    </div>
                    
                    <div className="italic text-sm text-gray-600 dark:text-gray-400 border-l-4 border-gray-300 dark:border-gray-700 pl-4">
                        Matematika Hijaiyyah is not a probabilistic model and not a symbolic interpretation system. It is a structured, deterministic, geometry‑based framework designed for reproducible audit‑grade computation.
                    </div>
                </div>

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
                    <a className="text-blue-700 underline" href="/hijaiyyahtech/en/artifacts/evidence.json" download target="_blank">Download evidence.json</a>
                </div>
            </div>
        </div>
    );
}
