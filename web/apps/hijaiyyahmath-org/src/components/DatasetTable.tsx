"use client";

// src/components/DatasetTable.tsx
import { useMemo, useState } from "react";

type DatasetItem = {
    name: string;
    description: string;
    sha256: string;
};

type Props = {
    datasets: DatasetItem[];
};

export default function DatasetTable({ datasets }: Props) {
    const [query, setQuery] = useState("");

    const rowsAll = useMemo(() => datasets ?? [], [datasets]);

    const rowsFiltered = useMemo(() => {
        const q = query.trim().toLowerCase();
        if (!q) return rowsAll;
        return rowsAll.filter((d) => {
            const hay = `${d.name} ${d.description} ${d.sha256}`.toLowerCase();
            return hay.includes(q);
        });
    }, [rowsAll, query]);

    async function copy(text: string) {
        await navigator.clipboard.writeText(text);
    }

    return (
        <div className="rounded-xl border bg-white dark:bg-gray-950 dark:border-gray-800">
            <div className="flex flex-col gap-3 border-b px-4 py-3 dark:border-gray-800 md:flex-row md:items-center md:justify-between">
                <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Datasets (Normative Seals)</div>
                    <div className="font-semibold">Hash-locked source-of-truth files</div>
                </div>

                <div className="flex flex-col gap-2 md:items-end">
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                        Showing <span className="font-mono">{rowsFiltered.length}</span> of{" "}
                        <span className="font-mono">{rowsAll.length}</span>
                    </div>

                    <div className="flex w-full items-center gap-2 md:w-[420px]">
                        <input
                            className="w-full rounded-md border px-3 py-2 text-sm dark:bg-gray-900 dark:border-gray-800"
                            placeholder="Filter datasets (name, description, sha256)…"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                        />
                        <button
                            className="rounded-md border px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-900 dark:border-gray-800"
                            onClick={() => setQuery("")}
                            disabled={!query}
                            title="Clear filter"
                        >
                            Clear
                        </button>
                    </div>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 text-xs text-gray-600 dark:bg-gray-900 dark:text-gray-300">
                        <tr>
                            <th className="px-4 py-3">Dataset</th>
                            <th className="px-4 py-3">Description</th>
                            <th className="px-4 py-3">SHA-256</th>
                            <th className="px-4 py-3">Action</th>
                        </tr>
                    </thead>

                    <tbody>
                        {rowsFiltered.map((d, i) => (
                            <tr key={i} className="border-t dark:border-gray-800">
                                <td className="px-4 py-3 font-mono whitespace-nowrap">{d.name}</td>
                                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{d.description}</td>
                                <td className="px-4 py-3 font-mono text-xs break-all">{d.sha256}</td>
                                <td className="px-4 py-3">
                                    <button
                                        className="rounded-md border px-2 py-1 text-xs hover:bg-gray-50 dark:hover:bg-gray-900 dark:border-gray-800"
                                        onClick={() => copy(d.sha256)}
                                    >
                                        Copy SHA
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="border-t px-4 py-3 text-xs text-gray-600 dark:text-gray-400 dark:border-gray-800">
                Note: Dataset seals are normative. Any modification requires a new release lock.
            </div>
        </div>
    );
}
