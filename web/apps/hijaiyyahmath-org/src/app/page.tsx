export const dynamic = "force-static";

const BASE = "/hijaiyyahmath.org";
const TARGET = `${BASE}/en/`;

export default function RootPage() {
    return (
        <main style={{ padding: 24, fontFamily: "system-ui, sans-serif" }}>
            <h1 style={{ margin: "0 0 8px 0" }}>Redirecting…</h1>
            <p style={{ margin: 0 }}>
                If you are not redirected automatically, open:{" "}
                <a href={TARGET}>{TARGET}</a>
            </p>
        </main>
    );
}
