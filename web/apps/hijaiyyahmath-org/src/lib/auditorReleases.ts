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
    docker_digest: string | null;
    github_release_url: string;
};

export async function loadAuditorBundles(): Promise<AuditorBundle[]> {
    const p = path.join(process.cwd(), "public", "releases", "auditor_bundles.json");
    const raw = await fs.readFile(p, "utf-8");
    const data = JSON.parse(raw);
    if (!Array.isArray(data)) throw new Error("auditor_bundles.json must be an array");

    const bundles = data as AuditorBundle[];

    // Fail-closed: require valid ISO date strings and sort newest-first deterministically.
    for (const b of bundles) {
        const t = Date.parse(b.date);
        if (Number.isNaN(t)) {
            throw new Error(`auditor_bundles.json: invalid date for bundle_id=${b.bundle_id}: ${JSON.stringify(b.date)}`);
        }
    }

    bundles.sort((a, b) => Date.parse(b.date) - Date.parse(a.date));
    return bundles;
}

export function bundleAnchorId(b: AuditorBundle): string {
    // stable anchor for quickstart sections
    return `${b.bundle_id}`.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}
