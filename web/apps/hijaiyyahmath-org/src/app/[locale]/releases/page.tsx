import ReleaseMatrixTable from "@/components/ReleaseMatrixTable";
import { getReleaseMatrix } from "@/lib/loadContent";

export default function Page() {
    const rm = getReleaseMatrix();

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold mb-4">Release Identity Matrix</h1>
                <div className="prose dark:prose-invert max-w-none space-y-3">
                    <p className="text-gray-700 dark:text-gray-300">
                        The <strong>Release Identity Matrix</strong> is the canonical registry of all cryptographically-locked module versions in Matematika Hijaiyyah. Each entry records the precise release tag, git commit hash, and integrity hash for deterministic reproducibility and audit-grade verification.
                    </p>
                    
                    <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-4 space-y-2">
                        <div>
                            <span className="font-semibold text-black dark:text-white">Single Source of Truth:</span>
                            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1 font-mono bg-white dark:bg-gray-800 p-2 rounded">src/content/release_matrix.json</div>
                        </div>
                        <div>
                            <span className="font-semibold text-black dark:text-white text-sm">What This Page Shows</span>
                            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1 mt-1 ml-4">
                                <li>• <strong>Layer:</strong> Stack tier (Core Engine, Normative Oracle, etc.)</li>
                                <li>• <strong>Module:</strong> Named component (hisa-vm, hgss-hc18dc, etc.)</li>
                                <li>• <strong>Release ID:</strong> Version identifier with status suffix</li>
                                <li>• <strong>Status:</strong> Lock state (PROD_LOCKED, FROZEN, etc.)</li>
                                <li>• <strong>Details:</strong> Expandable section with metadata, verification commands, and downloads</li>
                            </ul>
                        </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-400 border-l-4 border-gray-300 dark:border-gray-700 pl-3">
                        Each module includes cryptographic hash locks, normative verification commands, and download links for offline audit-grade deployment.
                    </p>
                </div>
            </div>

            <ReleaseMatrixTable
                stackVersion={rm.stack.stack_version}
                modules={rm.modules as any}
            />
        </div>
    );
}
