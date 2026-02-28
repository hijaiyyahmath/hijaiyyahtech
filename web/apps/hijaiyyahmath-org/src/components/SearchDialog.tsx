"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { getReleaseMatrix } from "@/lib/loadContent";

type Item = { label: string; href: string; meta?: string };

export default function SearchDialog() {
    const rm = getReleaseMatrix();
    const [open, setOpen] = useState(false);
    const [q, setQ] = useState("");

    const items: Item[] = useMemo(() => {
        const base: Item[] = [
            { label: "Home", href: "/en" },
            { label: "Technology Stack", href: "/en/stack" },
            { label: "Releases", href: "/en/releases" },
            { label: "Datasets", href: "/en/datasets" },
            { label: "Evidence Verifier", href: "/en/tools/evidence-verifier" }
        ];

        const mods: Item[] = (rm.modules ?? []).map((m: any) => ({
            label: m.name,
            href: "/en/releases",
            meta: `${m.layer} • ${m.release_id}`
        }));

        return [...base, ...mods];
    }, [rm.modules]);

    const filtered = useMemo(() => {
        const s = q.trim().toLowerCase();
        if (!s) return items.slice(0, 12);
        return items
            .filter((it) => (it.label + " " + (it.meta ?? "")).toLowerCase().includes(s))
            .slice(0, 20);
    }, [q, items]);

    useEffect(() => {
        function onKey(e: KeyboardEvent) {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
                e.preventDefault();
                setOpen(true);
                setQ("");
            }
            if (e.key === "Escape") setOpen(false);
        }
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, []);

    if (!open) {
        return (
            <button
                className="rounded-md border px-2 py-1 text-xs hover:bg-gray-50 dark:hover:bg-gray-800 dark:border-gray-800"
                onClick={() => { setOpen(true); setQ(""); }}
                title="Search (Ctrl+K)"
            >
                Search
            </button>
        );
    }

    return (
        <div className="fixed inset-0 z-50 bg-black/40 p-4" onClick={() => setOpen(false)}>
            <div
                className="mx-auto max-w-2xl rounded-xl border bg-white p-4 shadow-lg dark:bg-gray-900 dark:border-gray-800"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="text-sm font-semibold">Search</div>
                <input
                    className="mt-2 w-full rounded-md border p-2 text-sm dark:bg-gray-950 dark:border-gray-800"
                    placeholder="Type to search modules and pages…"
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                    autoFocus
                />

                <div className="mt-3 divide-y rounded-md border dark:border-gray-800 dark:divide-gray-800">
                    {filtered.map((it, i) => (
                        <Link
                            key={i}
                            href={it.href}
                            onClick={() => setOpen(false)}
                            className="block px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-800"
                        >
                            <div className="text-sm">{it.label}</div>
                            {it.meta ? <div className="text-xs text-gray-500">{it.meta}</div> : null}
                        </Link>
                    ))}
                </div>

                <div className="mt-3 text-xs text-gray-500">
                    Tip: Press <span className="font-mono">Esc</span> to close.
                </div>
            </div>
        </div>
    );
}
