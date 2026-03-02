import Link from "next/link";
import styles from "./downloads.module.css";
import { bundleAnchorId, loadAuditorBundles } from "@/lib/auditorReleases";

export const dynamic = "force-static";

export default async function DownloadsPage({ params }: { params: { locale: string } }) {
    const bundles = await loadAuditorBundles();

    return (
        <main className={styles.container}>
            <h1 className={styles.h1}>Auditor Downloads</h1>
            <p className={styles.lead}>
                Download the full offline auditor bundle (<code>.tar.gz + venv</code>) or use the Docker image pinned by digest.
                All releases are integrity-locked with SHA-256 and designed for deterministic audit execution.
            </p>

            {bundles.map((b) => {
                const anchor = bundleAnchorId(b);
                const isLatest = b === bundles[0];
                const tarUrl = isLatest ? `/${params.locale}/downloads/auditor-bundle` : b.tar_url;
                const shaUrl = isLatest ? `/${params.locale}/downloads/sha256sums` : b.sha256sums_url;

                return (
                    <section key={b.bundle_id} className={styles.card}>
                        <h2 className={styles.cardTitle}>{b.bundle_id}</h2>
                        <ul className={styles.meta}>
                            <li><b>Date:</b> {b.date}</li>
                            <li><b>HL-18:</b> {b.hl18_release_id}</li>
                            <li><b>HISA-VM:</b> {b.hisa_vm_release_id}</li>
                        </ul>

                        <div className={styles.actions}>
                            <a className={styles.button} href={tarUrl}>Download .tar.gz</a>
                            <a className={styles.buttonSecondary} href={shaUrl}>SHA256SUMS.txt</a>
                            <Link className={styles.buttonSecondary} href={`/${params.locale}/docs/auditor-quickstart#${anchor}`}>
                                Quickstart
                            </Link>
                        </div>

                        <h3 className={styles.sectionTitle}>Tarball SHA-256</h3>
                        <pre className={styles.code}>{`sha256  ${b.tar_sha256}`}</pre>

                        <h3 className={styles.sectionTitle}>Docker (Digest pinned)</h3>
                        <pre className={styles.code}>{`docker pull ${b.docker_image}@${b.docker_digest}`}</pre>

                        <p className={styles.small}>
                            Release page:{" "}
                            <a href={b.github_release_url} target="_blank" rel="noreferrer">
                                GitHub Releases
                            </a>
                        </p>

                        <p className={styles.small}>
                            Quickstart anchor: <code>#{anchor}</code>
                        </p>
                    </section>
                );
            })}
        </main>
    );
}
