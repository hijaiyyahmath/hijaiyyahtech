import styles from "./quickstart.module.css";
import { bundleAnchorId, loadAuditorBundles } from "@/lib/auditorReleases";

export const dynamic = "force-static";

export default async function AuditorQuickstartPage() {
    const bundles = await loadAuditorBundles();

    return (
        <main className={styles.container}>
            <h1 className={styles.h1}>Auditor Quickstart</h1>
            <p className={styles.p}>
                This page provides copy-paste commands for offline verification (.tar.gz + venv) and reproducible execution (Docker digest pinned).
            </p>

            {bundles.map((b) => {
                const anchor = bundleAnchorId(b);
                return (
                    <section key={b.bundle_id}>
                        <hr className={styles.hr} />
                        <h2 id={anchor} className={styles.h2}>{b.bundle_id}</h2>
                        <p className={styles.small}>
                            HL-18: <b>{b.hl18_release_id}</b> — HISA-VM: <b>{b.hisa_vm_release_id}</b>
                        </p>

                        <h3 className={styles.h2}>A) Offline: .tar.gz + venv</h3>
                        <pre className={styles.code}>{`# 1) Verify tarball hash (compare with /downloads)
sha256sum ${b.tar_url.split("/").pop() ?? "BUNDLE.tar.gz"}

# 2) Extract
tar -xzf ${b.tar_url.split("/").pop() ?? "BUNDLE.tar.gz"}
cd AuditorBundle

# 3) Create venv
python3 -m venv .venv
. .venv/bin/activate

# 4) Install deps (locked) + install HL-18
pip install -r requirements.lock.txt
pip install -e hl18

# 5) Full verification (PASS + CORE-1 TRAP)
python scripts/verify_all.py
`}</pre>

                        <h3 className={styles.h2}>B) Docker (digest pinned)</h3>
                        <pre className={styles.code}>{`docker pull ${b.docker_image}@${b.docker_digest}

docker run --rm -it \\
  -v "$PWD/artifacts:/work/artifacts" \\
  ${b.docker_image}@${b.docker_digest} \\
  python scripts/verify_all.py
`}</pre>
                    </section>
                );
            })}
        </main>
    );
}
