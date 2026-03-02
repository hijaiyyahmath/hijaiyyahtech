import EvidenceVerifier from "@/components/EvidenceVerifier";

export default function Page() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold mb-4">HGSS Evidence Verifier</h1>
                
                <div className="prose dark:prose-invert max-w-none space-y-4">
                    <p className="text-gray-700 dark:text-gray-300 text-base leading-relaxed">
                        The <strong>HGSS Evidence Verifier</strong> is a deterministic audit tool for validating <code>evidence.json</code> artifacts produced by the Hijaiyyah Guarded Signature Scheme (HGSS) pipeline. It performs two-stage verification: client-side schema integrity checks and server-side canonical CBOR digest validation.
                    </p>
                    
                    <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-4 space-y-3">
                        <div>
                            <span className="font-semibold text-black dark:text-white">Release Lock:</span>
                            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1 font-mono bg-white dark:bg-gray-800 p-2 rounded">HGSS-HCVM-v1.HC18DC @ Git commit e392c68</div>
                        </div>
                        <div>
                            <span className="font-semibold text-black dark:text-white text-sm">Verification Modes</span>
                            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1 mt-1 ml-4">
                                <li>• <strong>Client-side:</strong> Frozen schema key locks, structure validation (immediate, no network)</li>
                                <li>• <strong>Server-side:</strong> Canonical CBOR hashing (RFC 8949), event_sha256 recomputation (ephemeral, no storage)</li>
                                <li>• <strong>Interoperability:</strong> Match against test vectors and audit-grade reproducibility</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-4">
                        <h3 className="font-bold text-black dark:text-white mb-2">What is evidence.json?</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            The <code>evidence.json</code> file is the official audit artifact produced by the HGSS-HCVM pipeline. It contains:
                        </p>
                        <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1 mt-2 ml-4">
                            <li>• Frozen schema metadata (immutable structure locks)</li>
                            <li>• event_sha256 field (pre-computed SHA-256 of the event object)</li>
                            <li>• Canonical CBOR digest (deterministic binary encoding)</li>
                            <li>• Release identity (HGSS-HCVM version and git hash)</li>
                            <li>• Audit trail metadata (timestamps, normative outcomes)</li>
                        </ul>
                    </div>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-400 border-l-4 border-gray-300 dark:border-gray-700 pl-3">
                        Use this tool to verify that your local copy of evidence.json matches the canonical frozen locks and produces the same deterministic CBOR digest as the official release. All computations are audit-grade and reproducible.
                    </p>
                </div>
            </div>

            <EvidenceVerifier />
        </div>
    );
}
