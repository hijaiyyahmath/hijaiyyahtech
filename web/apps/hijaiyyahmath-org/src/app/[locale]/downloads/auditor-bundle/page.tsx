import { redirect } from "next/navigation";
import { loadAuditorBundles } from "@/lib/auditorReleases";

export const dynamic = "force-dynamic";

export default async function AuditorBundleRedirect() {
    const bundles = await loadAuditorBundles();
    if (bundles.length > 0) {
        redirect(bundles[0].tar_url);
    }
    redirect("/en/downloads");
}
