import ReleaseMatrixTable from "@/components/ReleaseMatrixTable";
import { getReleaseMatrix } from "@/lib/loadContent";

export default function Page() {
    const rm = getReleaseMatrix();

    return (
        <div className="space-y-4">
            <h1 className="text-2xl font-bold">Releases</h1>
            <p className="text-gray-700">
                This page is driven by a single source of truth:{" "}
                <span className="font-mono">src/content/release_matrix.json</span>.
                Each module includes verification commands and hash locks where applicable.
            </p>

            <ReleaseMatrixTable
                stackVersion={rm.stack.stack_version}
                modules={rm.modules as any}
            />
        </div>
    );
}
