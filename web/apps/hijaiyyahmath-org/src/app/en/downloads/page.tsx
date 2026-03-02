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

      <section style={{ marginTop: 24, borderLeft: "4px solid #111", paddingLeft: 16 }}>
        <h2 style={{ margin: "0 0 16px 0", fontSize: 20 }}>Offline Auditor Bundle — How to Run (Full Software)</h2>

        <p style={{ margin: "0 0 16px 0", color: "#333", lineHeight: 1.6 }}>
          The file <b>HijaiyyahStack-AuditorBundle-… .tar.gz</b> is an <b>offline "full running software" package</b>.
          <br />
          It is not a single executable application. Instead, you <b>extract</b> it, then run the <b>one-command audit wrapper</b> included inside the bundle.
          <br />
          <br />
          This produces deterministic PASS/TRAP outputs and saves forensic artifacts for external review.
        </p>

        <div style={{ margin: "20px 0" }}>
          <h3 style={{ margin: "0 0 10px 0", fontSize: 16 }}>1) Download the Bundle</h3>
          <p style={{ margin: "0 0 8px 0", color: "#555" }}>
            Click <b>"Download .tar.gz"</b> at the top of this page.
            <br />
            Your browser will download a file similar to:
          </p>
          <ul style={{ margin: "8px 0 8px 20px", color: "#555" }}>
            <li><code>HijaiyyahStack-AuditorBundle-v1.0_2026-03-01.tar.gz</code></li>
          </ul>
          <p style={{ margin: "8px 0 0 0", color: "#999", fontSize: 13 }}>
            (Downloads are binary transfers; some browsers briefly show a blank tab during the transfer. This is normal.)
          </p>
        </div>

        <div style={{ margin: "20px 0" }}>
          <h3 style={{ margin: "0 0 10px 0", fontSize: 16 }}>2) (Recommended) Verify SHA‑256 Before Extracting</h3>
          <p style={{ margin: "0 0 10px 0", color: "#555" }}>
            Download <b>SHA256SUMS.txt</b> and verify the tarball hash:
          </p>

          <p style={{ margin: "10px 0 8px 0", fontWeight: 600, fontSize: 14 }}>Linux / macOS</p>
          {codeBlock(`sha256sum HijaiyyahStack-AuditorBundle-v1.0_2026-03-01.tar.gz
# Compare the output with the matching line in SHA256SUMS.txt`)}

          <p style={{ margin: "14px 0 8px 0", fontWeight: 600, fontSize: 14 }}>Windows (PowerShell)</p>
          {codeBlock(`Get-FileHash .\\HijaiyyahStack-AuditorBundle-v1.0_2026-03-01.tar.gz -Algorithm SHA256
# Compare with SHA256SUMS.txt`)}
        </div>

        <div style={{ margin: "20px 0" }}>
          <h3 style={{ margin: "0 0 10px 0", fontSize: 16 }}>3) Extract the Bundle</h3>

          <p style={{ margin: "10px 0 8px 0", fontWeight: 600, fontSize: 14 }}>Linux / macOS</p>
          {codeBlock(`tar -xzf HijaiyyahStack-AuditorBundle-v1.0_2026-03-01.tar.gz
cd AuditorBundle`)}

          <p style={{ margin: "14px 0 8px 0", fontWeight: 600, fontSize: 14 }}>Windows</p>
          <p style={{ margin: "0 0 8px 0", color: "#555" }}>
            Use one of the following options:
          </p>
          <p style={{ margin: "8px 0 0 0" }}>
            <b>Option A (recommended): 7‑Zip</b>
            <br />
            <span style={{ color: "#555" }}>
              Right‑click the .tar.gz → 7‑Zip → Extract Here / Extract to AuditorBundle\
              <br />
              Then open the extracted folder AuditorBundle\
            </span>
          </p>
          <p style={{ margin: "10px 0 8px 0" }}>
            <b>Option B: Windows Terminal / PowerShell</b>
          </p>
          {codeBlock(`tar -xzf HijaiyyahStack-AuditorBundle-v1.0_2026-03-01.tar.gz
cd AuditorBundle`)}

          <p style={{ margin: "14px 0 8px 0", color: "#555" }}>
            After extraction, you should see folders like:
          </p>
          {codeBlock(`scripts/
hl18/
hisa-vm/
release/
specs/`)}
        </div>

        <div style={{ margin: "20px 0" }}>
          <h3 style={{ margin: "0 0 10px 0", fontSize: 16 }}>4) Run the One‑Command Audit Wrapper (Recommended)</h3>
          <p style={{ margin: "0 0 10px 0", color: "#555" }}>
            The bundle includes a one-command "one‑stop audit" script.
          </p>

          <p style={{ margin: "10px 0 8px 0", fontWeight: 600, fontSize: 14 }}>Linux / macOS (script: scripts/audit.sh)</p>
          {codeBlock(`chmod +x scripts/audit.sh
./scripts/audit.sh`)}

          <p style={{ margin: "14px 0 8px 0", fontWeight: 600, fontSize: 14 }}>Windows (script: scripts/audit.ps1)</p>
          {codeBlock(`powershell -ExecutionPolicy Bypass -File .\\scripts\\audit.ps1`)}

          <p style={{ margin: "14px 0 8px 0", fontWeight: 600, fontSize: 14 }}>What the wrapper does:</p>
          <ul style={{ margin: "8px 0 0 0", paddingLeft: 20, color: "#555" }}>
            <li>Creates a local Python virtual environment (.venv/)</li>
            <li>Installs locked dependencies from requirements.lock.txt</li>
            <li>Installs the HL‑18 module (and required VM tooling)</li>
            <li>Runs the normative conformance verification:
              <ul style={{ margin: "6px 0 0 0" }}>
                <li>Integrity verification</li>
                <li>PASS case (expected HALT_SUCCESS)</li>
                <li>CORE‑1 negative case (expected TRAP(5) CORE1_REQUIRED)</li>
              </ul>
            </li>
            <li>Runs operational demos (letter + word audit) and saves forensic artifacts</li>
          </ul>
        </div>

        <div style={{ margin: "20px 0" }}>
          <h3 style={{ margin: "0 0 10px 0", fontSize: 16 }}>5) Where to Find the Results (Forensic Artifacts)</h3>
          <p style={{ margin: "0 0 10px 0", color: "#555" }}>
            After the wrapper completes, review the logs and artifacts:
          </p>

          <p style={{ margin: "10px 0 8px 0" }}>
            <b>Primary log</b>
          </p>
          {codeBlock(`artifacts/audit_wrapper.log`)}

          <p style={{ margin: "14px 0 8px 0" }}>
            <b>Conformance evidence</b>
          </p>
          {codeBlock(`artifacts/verify_all/`)}

          <p style={{ margin: "14px 0 8px 0" }}>
            <b>Operational demo evidence</b>
          </p>
          {codeBlock(`artifacts/runs/`)}

          <p style={{ margin: "14px 0 0 0", color: "#555", fontSize: 13 }}>
            If your bundle is configured to store artifacts under en/, the locations will be:
            <br />
            <code>en/artifacts/audit_wrapper.log</code>, <code>en/artifacts/verify_all/</code>, <code>en/artifacts/runs/</code>
          </p>
        </div>

        <div style={{ margin: "20px 0" }}>
          <h3 style={{ margin: "0 0 10px 0", fontSize: 16 }}>6) Expected Normative Outcomes</h3>
          <p style={{ margin: "0 0 10px 0", color: "#555" }}>
            A correct run <b>MUST</b> produce:
          </p>
          <ul style={{ margin: "8px 0 0 0", paddingLeft: 20, color: "#555" }}>
            <li>Integrity: <b>PASS</b></li>
            <li>PASS conformance: Status: <b>HALT_SUCCESS</b> (ERR=0)</li>
            <li>CORE‑1 negative conformance: <b>TRAP(5) CORE1_REQUIRED</b> (ERR=5)</li>
          </ul>
          <p style={{ margin: "10px 0 0 0", color: "#555" }}>
            If any step fails, the wrapper stops immediately (fail‑closed) and the logs explain the reason.
          </p>
        </div>
      </section>
    </main>
  );
}
