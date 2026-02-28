"use client";

import { useEffect, useState } from "react";

const KEY = "hm_theme";

export default function ThemeToggle() {
    const [dark, setDark] = useState(false);

    useEffect(() => {
        const saved = localStorage.getItem(KEY);
        const isDark = saved === "dark";
        setDark(isDark);
        document.documentElement.classList.toggle("dark", isDark);
    }, []);

    function toggle() {
        const next = !dark;
        setDark(next);
        document.documentElement.classList.toggle("dark", next);
        localStorage.setItem(KEY, next ? "dark" : "light");
    }

    return (
        <button
            onClick={toggle}
            className="rounded-md border px-2 py-1 text-xs hover:bg-gray-50 dark:hover:bg-gray-800 dark:border-gray-800"
            aria-label="Toggle dark mode"
            title="Toggle theme"
        >
            {dark ? "Dark" : "Light"}
        </button>
    );
}
