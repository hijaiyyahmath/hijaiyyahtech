"use client";

import { useEffect, useState } from "react";

export default function AuditorBundleRedirect() {
    const [status, setStatus] = useState("Redirecting to GitHub Release...");

    useEffect(() => {
        async function doRedirect() {
            try {
                // Try fetching release metadata first
                const res = await fetch("/hijaiyyahtech/releases/auditor_bundles.json", { cache: "no-store" });
                if (res.ok) {
                    const bundles = await res.json();
                    if (bundles && bundles.length > 0) {
                        window.location.href = bundles[0].tar_url;
                        return;
                    }
                }
            } catch (err) {
                console.error("Failed to fetch release metadata:", err);
            }

            // Fallback: direct to the latest known GitHub Release
            const fallbackUrl = "https://github.com/hijaiyyahmath/hijaiyyahtech/releases/download/stack-v1.0/HijaiyyahStack-AuditorBundle-v1.0_2026-03-01.tar.gz";
            window.location.href = fallbackUrl;
        }

        // Small delay to show loading state
        const timer = setTimeout(doRedirect, 500);
        return () => clearTimeout(timer);
    }, []);

    return (
        <div style={{ backgroundColor: "black", color: "white", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", height: "100vh", margin: 0, fontFamily: "sans-serif" }}>
            <div style={{ textAlign: "center" }}>
                <p style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>{status}</p>
                <div className="spinner" />
                <style>
                    {`
                        .spinner { width: 30px; height: 30px; border: 3px solid #333; border-top: 3px solid white; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
                        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                    `}
                </style>
            </div>
        </div>
    );
}
