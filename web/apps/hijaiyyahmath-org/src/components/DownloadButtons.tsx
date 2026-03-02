"use client";

// src/components/DownloadButtons.tsx
export default function DownloadButtons() {
    const links = [
        "/hijaiyyahtech/downloads/hgss/evidence.json",
        "/hijaiyyahtech/downloads/hgss/evidence.expected.json",
        "/hijaiyyahtech/downloads/hgss/evidence.sha256.txt"
    ];

    async function copyLinks() {
        await navigator.clipboard.writeText(links.join("\n"));
    }

    function downloadAll() {
        for (const u of links) {
            const a = document.createElement("a");
            a.href = u;
            a.download = "";
            document.body.appendChild(a);
            a.click();
            a.remove();
        }
    }

    return (
        <div className="flex flex-wrap gap-2">
            <button
                className="rounded-md bg-black px-3 py-2 text-sm text-white dark:bg-white dark:text-black"
                onClick={downloadAll}
            >
                Download All HGSS Samples
            </button>
            <button
                className="rounded-md border px-3 py-2 text-sm dark:border-gray-800"
                onClick={copyLinks}
            >
                Copy Download Links
            </button>
        </div>
    );
}
