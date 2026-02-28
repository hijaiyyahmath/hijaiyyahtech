"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckItem, checkFrozenSchemaBasics, allOk } from "@/lib/schemaChecks";

type VerifyResponse = {
    ok: boolean;
    computed_event_sha256?: string;
    matches_event_field?: boolean;
    error?: string;
};

export default function EvidenceVerifier() {
    const [eventObj, setEventObj] = useState<any>(null);
    const [rawText, setRawText] = useState<string>("");
    const [clientChecks, setClientChecks] = useState<CheckItem[]>([]);
    const [server, setServer] = useState<VerifyResponse | null>(null);
    const [expected, setExpected] = useState<string>("");

    // load expected sha (public)
    async function loadExpected() {
        const r = await fetch("/downloads/hgss/evidence.expected.json", { cache: "no-store" });
        const j = await r.json();
        setExpected(j.expected_event_sha256 || "");
    }

    async function loadSample() {
        const r = await fetch("/downloads/hgss/evidence.json", { cache: "no-store" });
        const txt = await r.text();
        setRawText(txt);
        const obj = JSON.parse(txt);
        setEventObj(obj);
    }

    function onUpload(file: File) {
        const reader = new FileReader();
        reader.onload = () => {
            const txt = String(reader.result || "");
            setRawText(txt);
            const obj = JSON.parse(txt);
            setEventObj(obj);
        };
        reader.readAsText(file);
    }

    async function verifyServer(obj: any) {
        setServer(null);
        const r = await fetch("/api/verify-evidence", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ event: obj })
        });
        const j = await r.json();
        setServer(j);
    }

    useEffect(() => {
        loadExpected().catch(() => { });
    }, []);

    useEffect(() => {
        if (!eventObj) return;
        const checks = checkFrozenSchemaBasics(eventObj);
        setClientChecks(checks);
        // only call server if client basic checks passed (reduces noise)
        if (allOk(checks)) {
            verifyServer(eventObj).catch(() => setServer({ ok: false, error: "SERVER_VERIFY_FAILED" }));
        } else {
            setServer(null);
        }
    }, [eventObj]);

    const expectedMatch = useMemo(() => {
        if (!server?.computed_event_sha256 || !expected) return null;
        return server.computed_event_sha256 === expected;
    }, [server, expected]);

    return (
        <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border bg-white p-4 dark:bg-gray-950 dark:border-gray-800">
                <h2 className="text-lg font-semibold">Input</h2>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Load the official sample (public) or upload your own evidence JSON.
                </p>

                <div className="mt-4 flex flex-wrap gap-2">
                    <button
                        className="rounded-md bg-black px-3 py-2 text-sm text-white dark:bg-white dark:text-black"
                        onClick={loadSample}
                    >
                        Load Sample (HGSS evidence.json)
                    </button>
                    <a
                        className="rounded-md border px-3 py-2 text-sm dark:border-gray-800 dark:text-gray-300"
                        href="/downloads/hgss/evidence.json"
                        download
                    >
                        Download Sample
                    </a>
                    <a
                        className="rounded-md border px-3 py-2 text-sm dark:border-gray-800 dark:text-gray-300"
                        href="/downloads/hgss/evidence.sha256.txt"
                        target="_blank"
                    >
                        Sample SHA-256
                    </a>
                </div>

                <div className="mt-4">
                    <label className="block text-sm font-medium dark:text-gray-200">Upload evidence.json</label>
                    <input
                        className="mt-2 block w-full text-sm dark:text-gray-300"
                        type="file"
                        accept=".json,application/json"
                        onChange={(e) => {
                            const f = e.target.files?.[0];
                            if (f) onUpload(f);
                        }}
                    />
                </div>

                <div className="mt-4">
                    <label className="block text-sm font-medium dark:text-gray-200">Raw JSON</label>
                    <textarea
                        className="mt-2 h-64 w-full rounded-md border p-2 font-mono text-xs dark:bg-gray-900 dark:border-gray-800 dark:text-gray-200"
                        value={rawText}
                        onChange={(e) => {
                            setRawText(e.target.value);
                            try {
                                setEventObj(JSON.parse(e.target.value));
                            } catch {
                                setEventObj(null);
                            }
                        }}
                        placeholder="Paste evidence JSON here…"
                    />
                </div>

                <p className="mt-3 text-xs text-gray-500 dark:text-gray-500">
                    Note: Canonical CBOR digest is computed server-side only (ephemeral, no storage), to match RFC 8949 canonicalization.
                </p>
            </div>

            <div className="rounded-xl border bg-white p-4 dark:bg-gray-950 dark:border-gray-800">
                <h2 className="text-lg font-semibold dark:text-gray-100">Verification Results</h2>

                <div className="mt-4">
                    <h3 className="text-sm font-semibold dark:text-gray-200">Client-side Frozen Schema Checks</h3>
                    <ul className="mt-2 space-y-1 text-sm">
                        {clientChecks.map((c) => (
                            <li key={c.key} className="flex items-start gap-2">
                                <span className={c.ok ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}>
                                    {c.ok ? "PASS" : "FAIL"}
                                </span>
                                <span className="font-mono dark:text-gray-200">{c.key}</span>
                                {c.detail ? <span className="text-gray-500 dark:text-gray-400">— {c.detail}</span> : null}
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="mt-6">
                    <h3 className="text-sm font-semibold dark:text-gray-200">Server-side Canonical CBOR Digest</h3>
                    {!server ? (
                        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                            Awaiting valid schema input…
                        </p>
                    ) : server.ok ? (
                        <div className="mt-2 space-y-2 text-sm">
                            <div>
                                <div className="text-gray-600 dark:text-gray-400">Computed event_sha256</div>
                                <div className="break-all font-mono dark:text-gray-200">{server.computed_event_sha256}</div>
                            </div>
                            <div>
                                <div className="text-gray-600 dark:text-gray-400">Matches event.event_sha256 field</div>
                                <div className={server.matches_event_field ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}>
                                    {server.matches_event_field ? "PASS" : "FAIL"}
                                </div>
                            </div>
                            <div>
                                <div className="text-gray-600 dark:text-gray-400">Matches expected_event_sha256 (testvector)</div>
                                {expectedMatch === null ? (
                                    <div className="text-gray-500 dark:text-gray-500">N/A</div>
                                ) : (
                                    <div className={expectedMatch ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}>
                                        {expectedMatch ? "PASS" : "FAIL"}
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <p className="mt-2 text-sm text-red-700 dark:text-red-400">
                            Server verify failed: {server.error}
                        </p>
                    )}
                </div>

                <div className="mt-6 rounded-md bg-gray-50 p-3 text-sm dark:bg-gray-900">
                    <div className="font-semibold dark:text-gray-100">What this proves</div>
                    <ul className="mt-1 list-disc pl-5 text-gray-700 dark:text-gray-300">
                        <li>Schema frozen keys/locks are satisfied (client-side).</li>
                        <li>Canonical CBOR digest matches RFC 8949 (server-side).</li>
                        <li>event_sha256 is reproducible and interoperable.</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
