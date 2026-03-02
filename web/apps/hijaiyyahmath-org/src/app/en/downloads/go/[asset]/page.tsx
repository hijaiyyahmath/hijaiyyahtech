import { loadAuditorBundles } from "@/lib/auditorReleases";

export const dynamic = "force-static";

const BASE = "/hijaiyyahtech";
const EN = `${BASE}/en`;

// Static export requires fixed params for a dynamic segment.
export function generateStaticParams() {
  return [{ asset: "auditor-bundle" }, { asset: "sha256sums" }];
}

type Props = {
  params: { asset: string };
};

export default async function DownloadRedirectPage({ params }: Props) {
  const bundles = await loadAuditorBundles();
  const latest = bundles[0];

  let target = "";
  if (latest) {
    if (params.asset === "auditor-bundle") target = latest.tar_url;
    if (params.asset === "sha256sums") target = latest.sha256sums_url;
  }

  if (!target) {
    return (
      <main style={{ padding: 24, fontFamily: "system-ui, sans-serif" }}>
        <h1 style={{ margin: "0 0 8px 0" }}>Download not configured</h1>
        <p style={{ margin: 0 }}>
          Missing release entry in <code>public/releases/auditor_bundles.json</code> or unknown asset type.
        </p>
        <p style={{ margin: "10px 0 0 0" }}>
          Back: <a href={`${EN}/downloads/`}>{EN}/downloads/</a>
        </p>
      </main>
    );
  }

  return (
    <main style={{ padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ margin: "0 0 8px 0" }}>Redirecting to GitHub Release…</h1>
      {/* Export-safe redirect (no router runtime required) */}
      <meta httpEquiv="refresh" content={`0; url=${target}`} />

      <p style={{ margin: "0 0 10px 0" }}>
        Your download should start automatically. You may close this tab after the download begins.
      </p>

      <p style={{ margin: 0 }}>
        If it does not start, open:
        <br />
        <a href={target} rel="noreferrer">
          {target}
        </a>
      </p>
    </main>
  );
}
