import { loadAuditorBundles } from "@/lib/auditorReleases";

export default async function Sha256SumsRedirect() {
    const bundles = await loadAuditorBundles();
    const targetUrl = bundles.length > 0 ? bundles[0].sha256sums_url : "/en/downloads";

    return (
        <html>
            <head>
                <meta http-equiv="refresh" content={`0; url=${targetUrl}`} />
                <title>Redirecting...</title>
            </head>
            <body style={{ backgroundColor: "black", color: "white", display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
                <p>Redirecting to SHA256SUMS...</p>
                <script dangerouslySetInnerHTML={{ __html: `window.location.href = "${targetUrl}";` }} />
            </body>
        </html>
    );
}
