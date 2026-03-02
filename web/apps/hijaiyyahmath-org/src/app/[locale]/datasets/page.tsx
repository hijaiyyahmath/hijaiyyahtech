// src/app/[locale]/datasets/page.tsx
import DatasetTable from "@/components/DatasetTable";
import DownloadButtons from "@/components/DownloadButtons";
import { getDatasets } from "@/lib/loadContent";

export default function Page() {
    const d = getDatasets();

    return (
        <div className="space-y-4">
            <h1 className="text-2xl font-bold">Datasets</h1>
            <p className="text-gray-700 dark:text-gray-300">
                Public datasets are hash-locked and treated as normative inputs for the Technology Stack.
            </p>

            <DatasetTable datasets={d.datasets as any} />

            <div className="rounded-xl border bg-white p-4 dark:bg-gray-950 dark:border-gray-800">
                <div className="text-sm font-semibold">HGSS Public Sample</div>
                <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">
                    Download the official sample generated from <span className="font-mono">hgss-hc18dc/artifacts/evidence.json</span>{" "}
                    and verify it using the Evidence Verifier Tool.
                </p>

                <div className="mt-3">
                    <DownloadButtons />
                </div>

                <ul className="mt-3 list-disc pl-5 text-sm">
                    <li><a className="text-blue-700 underline" href="/hijaiyyahtech/downloads/hgss/evidence.json" target="_blank">/hijaiyyahtech/downloads/hgss/evidence.json</a></li>
                    <li><a className="text-blue-700 underline" href="/hijaiyyahtech/downloads/hgss/evidence.expected.json" target="_blank">/hijaiyyahtech/downloads/hgss/evidence.expected.json</a></li>
                    <li><a className="text-blue-700 underline" href="/hijaiyyahtech/downloads/hgss/evidence.sha256.txt" target="_blank">/hijaiyyahtech/downloads/hgss/evidence.sha256.txt</a></li>
                </ul>
            </div>
        </div>
    );
}
