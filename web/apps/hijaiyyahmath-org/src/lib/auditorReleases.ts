import { promises as fs } from "fs";
import path from "path";

export type AuditorBundle = {
    bundle_id: string;
    date: string;
    hl18_release_id: string;
    hisa_vm_release_id: string;
    tar_url: string;
    tar_sha256: string;
    sha256sums_url: string;
    docker_image: string;
    docker_digest: string;
};

export async function loadAuditorBundles(): Promise<AuditorBundle[]> {
    const p = path.join(process.cwd(), "public", "releases", "auditor_bundles.json");
    const raw = await fs.readFile(p, "utf-8");
    const data = JSON.parse(raw);
    if (!Array.isArray(data)) throw new Error("auditor_bundles.json must be an array");
    return data as AuditorBundle[];
}

export function bundleAnchorId(b: AuditorBundle): string {
    // stable anchor for quickstart sections
    return `${b.bundle_id}`.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}
