"use client";

import { useMemo, useState, useEffect } from "react";

type Module = {
    layer: string;
    name: string;
    release_id: string;
    status: string;
    git_hash?: string;
    spec?: string;
    tag?: string;
    verify_commands?: string[];
    public_downloads?: string[];
    artifacts?: { path: string; sha256: string }[];
    depends_on?: string;
};

type Props = {
    stackVersion: string;
    modules: Module[];
};

function badgeClass(status: string) {
    const s = status.toLowerCase();
    if (s.includes("frozen")) return "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-200 dark:border-blue-900";
    if (s.includes("locked")) return "bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-200 dark:border-green-900";
    if (s.includes("forensic")) return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950 dark:text-amber-200 dark:border-amber-900";
    if (s.includes("release")) return "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950 dark:text-purple-200 dark:border-purple-900";
    return "bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-900 dark:text-gray-200 dark:border-gray-800";
}

export default function ReleaseMatrixTable({ stackVersion, modules }: Props) {
    const [open, setOpen] = useState<string | null>(null);
    const [query, setQuery] = useState("");
    const [statusFilter, setStatusFilter] = useState<string>("ALL");

    const rowsAll = useMemo(() => modules ?? [], [modules]);

    const statuses = useMemo(() => {
        const set = new Set<string>();
        for (const m of rowsAll) set.add(m.status);
        return ["ALL", ...Array.from(set).sort((a, b) => a.localeCompare(b))];
    }, [rowsAll]);

    const rowsFiltered = useMemo(() => {
        const q = query.trim().toLowerCase();

        return rowsAll.filter((m) => {
            if (statusFilter !== "ALL" && m.status !== statusFilter) return false;

            if (!q) return true;
            const hay = [
                m.layer, m.name, m.release_id, m.status,
                m.git_hash ?? "", m.tag ?? "", m.spec ?? "", m.depends_on ?? ""
            ].join(" ").toLowerCase();
            return hay.includes(q);
        });
    }, [rowsAll, query, statusFilter]);

    useEffect(() => {
        setOpen(null);
    }, [query, statusFilter]);

    async function copy(text: string) {
        await navigator.clipboard.writeText(text);
    }

    function resetFilters() {
        setQuery("");
        setStatusFilter("ALL");
    }

    return (
        <div className="rounded-xl border bg-white dark:bg-gray-950 dark:border-gray-800">
            <div className="flex flex-col gap-3 border-b px-4 py-3 dark:border-gray-800 md:flex-row md:items-center md:justify-between">
                <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Release Identity Matrix</div>
                    <div className="font-semibold">{stackVersion}</div>
                    <div className="mt-1 text-xs text-gray-500">
                        Source: <span className="font-mono">src/content/release_matrix.json</span>
                    </div>
                </div>

                <div className="flex flex-col gap-2 md:items-end">
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                        Showing <span className="font-mono">{rowsFiltered.length}</span> of{" "}
                        <span className="font-mono">{rowsAll.length}</span>
                    </div>

                    <div className="flex w-full flex-col gap-2 md:w-[560px] md:flex-row md:items-center">
                        <input
                            className="w-full rounded-md border px-3 py-2 text-sm dark:bg-gray-900 dark:border-gray-800"
                            placeholder="Search (layer, module, release_id, status, hash)…"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                        />

                        <select
                            className="rounded-md border px-3 py-2 text-sm dark:bg-gray-900 dark:border-gray-800"
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            title="Filter by status"
                        >
                            {statuses.map((s) => (
                                <option key={s} value={s}>
                                    {s === "ALL" ? "All status" : s}
                                </option>
                            ))}
                        </select>

                        <button
                            className="rounded-md border px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-900 dark:border-gray-800"
                            onClick={resetFilters}
                            disabled={!query && statusFilter === "ALL"}
                            title="Reset filters"
                        >
                            Reset
                        </button>
                    </div>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 text-xs text-gray-600 dark:bg-gray-900 dark:text-gray-300">
                        <tr>
                            <th className="px-4 py-3">Layer</th>
                            <th className="px-4 py-3">Module</th>
                            <th className="px-4 py-3">Release ID</th>
                            <th className="px-4 py-3">Status</th>
                            <th className="px-4 py-3">Details</th>
                        </tr>
                    </thead>

                    <tbody>
                        {rowsFiltered.map((m, idx) => {
                            const key = `${m.layer}:${m.release_id}:${idx}`;
                            const isOpen = open === key;

                            return (
                                <>
                                    <tr key={key} className="border-t dark:border-gray-800">
                                        <td className="px-4 py-3 whitespace-nowrap">{m.layer}</td>
                                        <td className="px-4 py-3">{m.name}</td>
                                        <td className="px-4 py-3 font-mono whitespace-nowrap">{m.release_id}</td>
                                        <td className="px-4 py-3">
                                            <span className={`inline-flex items-center rounded-md border px-2 py-1 text-xs ${badgeClass(m.status)}`}>
                                                {m.status}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <button
                                                className="rounded-md border px-2 py-1 text-xs hover:bg-gray-50 dark:hover:bg-gray-900 dark:border-gray-800"
                                                onClick={() => setOpen(isOpen ? null : key)}
                                            >
                                                {isOpen ? "Hide" : "View"}
                                            </button>
                                        </td>
                                    </tr>

                                    {isOpen ? (
                                        <tr className="border-t bg-white dark:bg-gray-950 dark:border-gray-800">
                                            <td colSpan={5} className="px-4 py-4">
                                                <div className="grid gap-4 lg:grid-cols-2">
                                                    <div className="space-y-2">
                                                        <div className="text-xs font-semibold text-gray-600 dark:text-gray-400">Locked Metadata</div>
                                                        <div className="text-sm">
                                                            {m.tag ? (
                                                                <div>
                                                                    <span className="text-gray-600 dark:text-gray-400">tag:</span>{" "}
                                                                    <span className="font-mono">{m.tag}</span>
                                                                </div>
                                                            ) : null}
                                                            {m.git_hash ? (
                                                                <div>
                                                                    <span className="text-gray-600 dark:text-gray-400">git_hash:</span>{" "}
                                                                    <span className="font-mono">{m.git_hash}</span>
                                                                </div>
                                                            ) : null}
                                                            {m.spec ? (
                                                                <div>
                                                                    <span className="text-gray-600 dark:text-gray-400">spec:</span>{" "}
                                                                    <span className="font-mono">{m.spec}</span>
                                                                </div>
                                                            ) : null}
                                                            {m.depends_on ? (
                                                                <div>
                                                                    <span className="text-gray-600 dark:text-gray-400">depends_on:</span>{" "}
                                                                    <span className="font-mono">{m.depends_on}</span>
                                                                </div>
                                                            ) : null}
                                                        </div>

                                                        {m.artifacts?.length ? (
                                                            <>
                                                                <div className="pt-2 text-xs font-semibold text-gray-600 dark:text-gray-400">Artifacts / Hash Locks</div>
                                                                <ul className="space-y-1 text-xs">
                                                                    {m.artifacts.map((a, i) => (
                                                                        <li key={i} className="flex items-start justify-between gap-3 rounded-md border bg-gray-50 p-2 dark:bg-gray-900 dark:border-gray-800">
                                                                            <div className="min-w-0">
                                                                                <div className="font-mono break-all">{a.path}</div>
                                                                                <div className="font-mono break-all text-gray-600 dark:text-gray-400">{a.sha256}</div>
                                                                            </div>
                                                                            <button
                                                                                className="shrink-0 rounded-md border px-2 py-1 hover:bg-white dark:hover:bg-gray-950 dark:border-gray-800"
                                                                                onClick={() => copy(a.sha256)}
                                                                            >
                                                                                Copy SHA
                                                                            </button>
                                                                        </li>
                                                                    ))}
                                                                </ul>
                                                            </>
                                                        ) : null}
                                                    </div>

                                                    <div className="space-y-2">
                                                        <div className="flex items-center justify-between">
                                                            <div className="text-xs font-semibold text-gray-600 dark:text-gray-400">Verification Commands</div>
                                                            {m.verify_commands?.length ? (
                                                                <button
                                                                    className="rounded-md border px-2 py-1 text-xs hover:bg-gray-50 dark:hover:bg-gray-900 dark:border-gray-800"
                                                                    onClick={() => copy(m.verify_commands!.join("\n"))}
                                                                    title="Copy all verification commands"
                                                                >
                                                                    Copy All
                                                                </button>
                                                            ) : null}
                                                        </div>

                                                        {m.verify_commands?.length ? (
                                                            <div className="space-y-2">
                                                                {m.verify_commands.map((cmd, i) => (
                                                                    <div key={i} className="rounded-md border bg-gray-50 p-2 dark:bg-gray-900 dark:border-gray-800">
                                                                        <div className="flex items-center justify-between gap-2">
                                                                            <div className="min-w-0 font-mono text-xs break-all">{cmd}</div>
                                                                            <button
                                                                                className="shrink-0 rounded-md border bg-white px-2 py-1 text-xs hover:bg-gray-50 dark:bg-gray-950 dark:hover:bg-gray-900 dark:border-gray-800"
                                                                                onClick={() => copy(cmd)}
                                                                            >
                                                                                Copy
                                                                            </button>
                                                                        </div>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        ) : (
                                                            <div className="text-sm text-gray-500">No commands provided for this module.</div>
                                                        )}

                                                        {m.public_downloads?.length ? (
                                                            <>
                                                                <div className="pt-3 text-xs font-semibold text-gray-600 dark:text-gray-400">Public Downloads</div>
                                                                <ul className="space-y-1 text-sm">
                                                                    {m.public_downloads.map((u, i) => (
                                                                        <li key={i}>
                                                                            <a className="text-blue-700 underline" href={u} target="_blank">
                                                                                {u}
                                                                            </a>
                                                                        </li>
                                                                    ))}
                                                                </ul>
                                                            </>
                                                        ) : null}
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    ) : null}
                                </>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
