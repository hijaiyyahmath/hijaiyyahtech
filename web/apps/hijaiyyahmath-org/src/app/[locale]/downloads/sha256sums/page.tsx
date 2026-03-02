import { redirect } from "next/navigation";
import { loadAuditorBundles } from "@/lib/auditorReleases";

export const dynamic = "force-dynamic";

export default async function Sha256SumsRedirect() {
    const bundles = await loadAuditorBundles();
    if (bundles.length > 0) {
        redirect(bundles[0].sha256sums_url);
    }
    redirect("/en/downloads");
}
