import Link from "next/link";
import { loadAuditorBundles } from "@/lib/auditorReleases";

export const dynamic = "force-static";

// CANONICAL RULE (locked):
// All internal navigation must be under: /hijaiyyahtech/en/...
const BASE = "/hijaiyyahtech";
const EN = `${BASE}/en`;

function codeBlock(s: string) {
  return (
    <pre
      style={{
        background: "#f6f6f6",
        border: "1px solid #eee",
        borderRadius: 10,
        padding: 12,
        overflowX: "auto",
        fontSize: 13,
        lineHeight: 1.45,
        margin: 0,
        fontFamily:
          'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
      }}
    >
      {s}
    </pre>
  );
}

export default async function DownloadsPage() {
  const bundles = await loadAuditorBundles();
  const latest = bundles[0];

  return (
    <main style={{ maxWidth: 980, margin: "0 auto", padding: "28px 16px", fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: 30, margin: "0 0 10px 0" }}>Auditor Downloads</h1>
      <p style={{ margin: "0 0 18px 0", color: "#333", lineHeight: 1.6 }}>
        All internal pages are canonical under <code>{EN}/…</code>. Downloads are initiated via internal redirect pages:
        <code> {EN}/downloads/go/…</code> to keep the user flow consistent.
      </p>

      <section style={{ border: "1px solid #e7e7e7", borderRadius: 12, padding: 16, background: "#fff" }}>
        <h2 style={{ margin: "0 0 10px 0", fontSize: 18 }}>Latest Release</h2>

        {!latest ? (
          <p style={{ margin: 0 }}>No bundles configured in public/releases/auditor_bundles.json</p>
        ) : (
          <>
            <ul style={{ margin: "0 0 14px 0", paddingLeft: 18 }}>
              <li>
                <b>Bundle ID:</b> {latest.bundle_id}
              </li>
              <li>
                <b>Date:</b> {latest.date}
              </li>
              <li>
                <b>HL‑18:</b> {latest.hl18_release_id}
              </li>
              <li>
                <b>HISA‑VM:</b> {latest.hisa_vm_release_id}
              </li>
            </ul>

            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 14 }}>
              {/* IMPORTANT: open in a new tab to avoid "blank/black tab" confusion during binary download */}
              <a
                href={`${EN}/downloads/go/auditor-bundle/`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "inline-block",
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid #111",
                  background: "#111",
                  color: "#fff",
                  textDecoration: "none",
                  fontWeight: 700,
                }}
              >
                Download .tar.gz
              </a>

              <a
                href={`${EN}/downloads/go/sha256sums/`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "inline-block",
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid #ddd",
                  background: "#fff",
                  color: "#111",
                  textDecoration: "none",
                  fontWeight: 700,
                }}
              >
                SHA256SUMS.txt
              </a>

              <Link
                href={`${EN}/docs/auditor-quickstart/`}
                style={{
                  display: "inline-block",
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid #ddd",
                  background: "#fff",
                  color: "#111",
                  textDecoration: "none",
                  fontWeight: 700,
                }}
              >
                Quickstart
              </Link>

              <a
                href={latest.github_release_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "inline-block",
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid #ddd",
                  background: "#fff",
                  color: "#111",
                  textDecoration: "none",
                  fontWeight: 700,
                }}
              >
                GitHub Release
              </a>
            </div>

            <h3 style={{ margin: "14px 0 8px 0", fontSize: 14 }}>Tarball SHA‑256</h3>
            {codeBlock(`sha256  ${latest.tar_sha256}`)}

            <p style={{ margin: "10px 0 0 0", color: "#555", fontSize: 13 }}>
              Note: downloads are binary transfers; some browsers show a blank/black tab while downloading. This is normal.
              The download buttons open in a new tab so the Downloads page remains visible.
            </p>
          </>
        )}
      </section>

      {bundles.length > 1 ? (
        <section style={{ marginTop: 16, border: "1px solid #e7e7e7", borderRadius: 12, padding: 16, background: "#fff" }}>
          <h2 style={{ margin: "0 0 10px 0", fontSize: 18 }}>Other Releases</h2>
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {bundles.slice(1).map((b) => (
              <li key={b.bundle_id}>
                <b>{b.bundle_id}</b> — <a href={b.github_release_url} target="_blank" rel="noreferrer">release</a>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </main>
  );
}
