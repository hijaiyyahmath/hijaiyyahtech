import { getReleaseMatrix } from "@/lib/loadContent";

export default function ReleaseBadge() {
    const rm = getReleaseMatrix();
    const hgss = (rm.modules as any[]).find((m) => (m.release_id || "").includes("HGSS-HCVM"));

    return (
        <div className="rounded-xl border bg-white p-4 dark:bg-gray-900 dark:border-gray-800">
            <div className="text-xs text-gray-600 dark:text-gray-400">Release Badge</div>
            <div className="mt-1 text-sm font-semibold">{rm.stack.stack_version}</div>
            {hgss ? (
                <div className="mt-2 space-y-1 text-xs">
                    <div>
                        <span className="text-gray-600 dark:text-gray-400">HGSS:</span>{" "}
                        <span className="font-mono">{hgss.release_id}</span>
                    </div>
                    {hgss.git_hash ? (
                        <div>
                            <span className="text-gray-600 dark:text-gray-400">commit:</span>{" "}
                            <span className="font-mono">{hgss.git_hash}</span>
                        </div>
                    ) : null}
                    <div className="pt-1">
                        <a className="text-blue-700 underline" href="/downloads/hgss/evidence.json" target="_blank">
                            Download public evidence.json
                        </a>
                    </div>
                </div>
            ) : (
                <div className="mt-2 text-xs text-gray-500">HGSS module not listed in matrix.</div>
            )}
        </div>
    );
}
