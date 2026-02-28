import EvidenceVerifier from "@/components/EvidenceVerifier";

export default function Page() {
    return (
        <div className="space-y-4">
            <h1 className="text-2xl font-bold">HGSS Evidence Verifier</h1>
            <p className="text-gray-700 dark:text-gray-300">
                Verify <span className="font-mono">evidence.json</span> against frozen locks and canonical CBOR hashing
                (HGSS-HCVM-v1.HC18DC @ e392c68).
            </p>
            <EvidenceVerifier />
        </div>
    );
}
