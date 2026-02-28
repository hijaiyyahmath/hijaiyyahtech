import { NextResponse } from "next/server";
import crypto from "crypto";
import * as cbor from "cbor";
import { z } from "zod";

const ReqSchema = z.object({
    event: z.record(z.any())
});

function sha256Hex(buf: Buffer): string {
    return crypto.createHash("sha256").update(buf).digest("hex");
}

function canonicalCbor(obj: any): Buffer {
    // RFC 8949 canonical encoding
    return cbor.encodeCanonical(obj);
}

export async function POST(req: Request) {
    const body = await req.json().catch(() => null);
    const parsed = ReqSchema.safeParse(body);
    if (!parsed.success) {
        return NextResponse.json(
            { ok: false, error: "INVALID_REQUEST_BODY" },
            { status: 400 }
        );
    }

    const event = parsed.data.event;

    // Exclude event_sha256 for hashing to avoid self-reference
    const eventNoHash: any = { ...event };
    delete eventNoHash["event_sha256"];

    const cborBytes = canonicalCbor(eventNoHash);
    const computedEventSha256 = sha256Hex(cborBytes);

    const got = typeof event["event_sha256"] === "string" ? event["event_sha256"] : "";
    const matchesField = got === computedEventSha256;

    return NextResponse.json({
        ok: true,
        computed_event_sha256: computedEventSha256,
        matches_event_field: matchesField,
        canonical_cbor_sha256_basis: "SHA-256(CBOR_canonical(event_without_event_sha256))"
    });
}
