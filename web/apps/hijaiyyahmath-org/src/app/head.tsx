const BASE = "/hijaiyyahmath.org";
const TARGET = `${BASE}/en/`;

export default function Head() {
    return (
        <>
            <meta httpEquiv="refresh" content={`0; url=${TARGET}`} />
            <meta name="robots" content="noindex" />
            <link rel="canonical" href={TARGET} />
            <title>Redirecting…</title>
        </>
    );
}
