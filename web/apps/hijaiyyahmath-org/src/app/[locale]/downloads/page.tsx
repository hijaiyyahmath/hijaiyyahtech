import { redirect } from "next/navigation";

export const dynamic = "force-static";

export default async function DownloadsPage({ params }: { params: { locale: string } }) {
    // Redirect to canonical /en/downloads path (fixed structure without [locale] param)
    redirect("/hijaiyyahtech/en/downloads/");
}
