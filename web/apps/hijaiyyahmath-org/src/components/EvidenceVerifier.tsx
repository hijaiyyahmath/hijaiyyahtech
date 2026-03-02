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
        const r = await fetch("/hijaiyyahtech/downloads/hgss/evidence.expected.json", { cache: "no-store" });
        const j = await r.json();
        setExpected(j.expected_event_sha256 || "");
    }

    async function loadSample() {
        const r = await fetch("/hijaiyyahtech/downloads/hgss/evidence.json", { cache: "no-store" });
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
                    Load the official sample evidence.json (test vector) or upload your own audit artifact for verification.
                </p>

                <div className="mt-4">
                    <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">📥 Quick Actions</div>
                    <div className="flex flex-wrap gap-2">
                        <button
                            className="rounded-md bg-black px-3 py-2 text-sm text-white hover:bg-gray-800 dark:bg-white dark:text-black dark:hover:bg-gray-200"
                            onClick={loadSample}
                            title="Load official HGSS evidence.json test vector into the verifier"
                        >
                            Load Sample (HGSS evidence.json)
                        </button>
                        <a
                            className="rounded-md border px-3 py-2 text-sm hover:bg-gray-50 dark:border-gray-800 dark:text-gray-300 dark:hover:bg-gray-900"
                            href="/hijaiyyahtech/downloads/hgss/evidence.json"
                            download
                            title="Download the official test vector for offline verification"
                        >
                            Download Sample
                        </a>
                        <a
                            className="rounded-md border px-3 py-2 text-sm hover:bg-gray-50 dark:border-gray-800 dark:text-gray-300 dark:hover:bg-gray-900"
                            href="/hijaiyyahtech/downloads/hgss/evidence.sha256.txt"
                            target="_blank"
                            title="View SHA-256 hash of the official sample for local verification"
                        >
                            Sample SHA-256
                        </a>
                    </div>
                </div>

                <div className="mt-4">
                    <label className="block text-sm font-medium dark:text-gray-200">
                        📄 Upload evidence.json
                        <span className="text-[10px] font-normal text-gray-500 ml-1">(your audit artifact)</span>
                    </label>
                    <input
                        className="mt-2 block w-full text-sm dark:text-gray-300 file:mr-2 file:px-3 file:py-1 file:rounded file:border file:text-xs file:font-medium"
                        type="file"
                        accept=".json,application/json"
                        onChange={(e) => {
                            const f = e.target.files?.[0];
                            if (f) onUpload(f);
                        }}
                        title="Select an evidence.json file from your computer"
                    />
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">Accepted: .json files up to 10 MB</p>
                </div>

                <div className="mt-4">
                    <label className="block text-sm font-medium dark:text-gray-200">
                        📋 Raw JSON
                        <span className="text-[10px] font-normal text-gray-500 ml-1">(paste or edit directly)</span>
                    </label>
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
                        placeholder="Paste evidence JSON here… (or use Load Sample button above)"
                        title="Valid JSON will be parsed automatically"
                    />
                </div>

                <p className="mt-3 text-xs text-gray-600 dark:text-gray-500 border-l-2 border-gray-300 dark:border-gray-700 pl-2">
                    <strong>Note:</strong> Canonical CBOR digest is computed server-side only (ephemeral, no storage). Results are computed safely without persisting any evidence data, following RFC 8949 canonicalization rules.
                </p>
            </div>

            <div className="rounded-xl border bg-white p-4 dark:bg-gray-950 dark:border-gray-800">
                <div>
                    <h2 className="text-lg font-semibold dark:text-gray-100">🔍 Verification Results</h2>
                    <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
                        Two-stage verification: client-side schema locks (immediate) + server-side CBOR digest (RFC 8949 canonical).
                    </p>
                </div>

                <div className="mt-4 pt-4 border-t dark:border-gray-800">
                    <h3 className="text-sm font-semibold dark:text-gray-200 flex items-center gap-2">
                        ✓ Client-side Frozen Schema Checks
                        <span className="text-[10px] font-normal text-gray-500">(instant, no network)</span>
                    </h3>
                    <ul className="mt-2 space-y-1 text-sm">
                        {clientChecks.map((c) => (
                            <li key={c.key} className="flex items-start gap-2">
                                <span className={`font-semibold ${c.ok ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}`}>
                                    {c.ok ? "✓ PASS" : "✗ FAIL"}
                                </span>
                                <span className="font-mono text-xs dark:text-gray-200">{c.key}</span>
                                {c.detail ? <span className="text-gray-500 dark:text-gray-400 text-xs">— {c.detail}</span> : null}
                            </li>
                        ))}
                    </ul>
                    {clientChecks.length === 0 && (
                        <p className="mt-2 text-xs text-gray-500 italic">Waiting for valid JSON input…</p>
                    )}
                </div>

                <div className="mt-6 pt-4 border-t dark:border-gray-800">
                    <h3 className="text-sm font-semibold dark:text-gray-200 flex items-center gap-2">
                        🔐 Server-side Canonical CBOR Digest
                        <span className="text-[10px] font-normal text-gray-500">(RFC 8949, ephemeral)</span>
                    </h3>
                    {!server ? (
                        <p className="mt-2 text-xs text-gray-600 dark:text-gray-400 italic">
                            Awaiting valid schema input… (Load Sample or paste evidence.json above)
                        </p>
                    ) : server.ok ? (
                        <div className="mt-2 space-y-3 text-xs">
                            <div className="rounded border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-2">
                                <div className="text-gray-700 dark:text-gray-300 font-medium">Computed event_sha256 (Canonical CBOR)</div>
                                <div className="break-all font-mono text-[10px] dark:text-gray-200 mt-1">{server.computed_event_sha256}</div>
                            </div>
                            <div className="rounded border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-2">
                                <div className="text-gray-700 dark:text-gray-300 font-medium">Matches event.event_sha256 field</div>
                                <div className={`font-semibold mt-1 ${server.matches_event_field ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}`}>
                                    {server.matches_event_field ? "✓ PASS — SHA-256 recomputation verified" : "✗ FAIL — Mismatch detected"}
                                </div>
                            </div>
                            <div className="rounded border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-2">
                                <div className="text-gray-700 dark:text-gray-300 font-medium">Matches expected_event_sha256 (Test Vector)</div>
                                {expectedMatch === null ? (
                                    <div className="text-gray-500 dark:text-gray-500 mt-1 italic">N/A (no expected value loaded)</div>
                                ) : (
                                    <div className={`font-semibold mt-1 ${expectedMatch ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}`}>
                                        {expectedMatch ? "✓ PASS — Matches official release" : "✗ FAIL — Does not match test vector"}
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <p className="mt-2 text-xs text-red-700 dark:text-red-400 font-medium">
                            ✗ Server verification failed: {server.error}
                        </p>
                    )}
                </div>

                <div className="mt-6 rounded-md bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-900 p-3 text-sm">
                    <div className="font-semibold text-blue-900 dark:text-blue-100">✓ What This Proves</div>
                    <ul className="mt-2 list-disc pl-5 text-blue-800 dark:text-blue-100 space-y-1">
                        <li><strong>Frozen Schema Integrity:</strong> All required keys are present and match locked type signatures (client-side verification, instant).</li>
                        <li><strong>Canonical CBOR Digest:</strong> The evidence object serializes to the same canonical CBOR representation as the official release, following RFC 8949 rules (server-side, ephemeral).</li>
                        <li><strong>SHA-256 Reproducibility:</strong> The event_sha256 field is deterministic and matches the canonical CBOR hash—fully reproducible across any audit platform.</li>
                        <li><strong>Test Vector Compliance:</strong> If official sample is available, your evidence.json matches the known-good HGSS-HCVM-v1.HC18DC release artifact.</li>
                        <li><strong>Audit-grade Interoperability:</strong> Results are deterministic and suitable for certification and compliance workflows.</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
