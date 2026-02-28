const HEX64 = /^[0-9a-f]{64}$/;
const HEX24 = /^[0-9a-f]{24}$/;

export type CheckItem = { key: string; ok: boolean; detail?: string };

export function checkFrozenSchemaBasics(event: any): CheckItem[] {
    const items: CheckItem[] = [];

    const requiredTop = [
        "event_type", "hgss_version", "git_hash", "git_tag", "timestamp_utc",
        "node_id_hex", "key_id_hex", "txid_hex", "mh28_sha256", "csgi28_sha256",
        "lease", "lease_sig", "nonce", "aggregates", "commitment", "mac",
        "ciphertext", "trace", "hsm", "status", "event_sha256"
    ];

    const expectVersion = "HGSS-HCVM-v1.HC18DC";
    const expectHash = "e392c68";
    const expectEventType = "HGSS_HC18DC_TX";

    // map/object
    items.push({
        key: "top_level_is_object",
        ok: typeof event === "object" && event !== null && !Array.isArray(event),
        detail: "Top-level MUST be a JSON object."
    });

    for (const k of requiredTop) {
        items.push({
            key: `required:${k}`,
            ok: event && Object.prototype.hasOwnProperty.call(event, k),
            detail: `MUST contain key: ${k}`
        });
    }

    // stop early if missing keys
    const missing = items.filter(x => x.key.startsWith("required:") && !x.ok);
    if (missing.length) return items;

    // locks
    items.push({
        key: "lock:event_type",
        ok: event.event_type === expectEventType,
        detail: `MUST be ${expectEventType}`
    });
    items.push({
        key: "lock:hgss_version",
        ok: event.hgss_version === expectVersion,
        detail: `MUST be ${expectVersion}`
    });
    items.push({
        key: "lock:git_hash",
        ok: event.git_hash === expectHash,
        detail: `MUST be ${expectHash}`
    });
    items.push({
        key: "lock:git_tag",
        ok: event.git_tag === expectVersion,
        detail: `MUST be ${expectVersion}`
    });

    // fixed hex lengths
    const hex64Keys = ["node_id_hex", "key_id_hex", "txid_hex", "mh28_sha256", "csgi28_sha256", "event_sha256"];
    for (const k of hex64Keys) {
        items.push({
            key: `hex64:${k}`,
            ok: typeof event[k] === "string" && HEX64.test(event[k]),
            detail: "MUST be 64 lowercase hex chars"
        });
    }

    // nonce96_hex
    items.push({
        key: "hex24:nonce.nonce96_hex",
        ok: typeof event.nonce?.nonce96_hex === "string" && HEX24.test(event.nonce.nonce96_hex),
        detail: "MUST be 24 lowercase hex chars (12 bytes)"
    });

    // minimal type checks (maps)
    for (const k of ["lease", "lease_sig", "nonce", "aggregates", "commitment", "mac", "ciphertext", "trace", "hsm", "status"]) {
        items.push({
            key: `type:${k}_is_object`,
            ok: typeof event[k] === "object" && event[k] !== null && !Array.isArray(event[k]),
            detail: `${k} MUST be an object/map`
        });
    }

    return items;
}

export function allOk(items: CheckItem[]): boolean {
    return items.every(x => x.ok);
}
