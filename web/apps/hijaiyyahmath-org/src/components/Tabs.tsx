"use client";

import { useState } from "react";

export type TabItem = {
    id: string;
    label: string;
    content: React.ReactNode;
};

export default function Tabs({ items, defaultId }: { items: TabItem[]; defaultId?: string }) {
    const [active, setActive] = useState(defaultId ?? items[0]?.id);

    return (
        <div className="rounded-xl border bg-white dark:bg-gray-900 dark:border-gray-800">
            <div className="flex flex-wrap gap-2 border-b p-3 dark:border-gray-800">
                {items.map((t) => (
                    <button
                        key={t.id}
                        onClick={() => setActive(t.id)}
                        className={[
                            "rounded-md px-3 py-2 text-sm border",
                            active === t.id
                                ? "bg-black text-white border-black dark:bg-white dark:text-black dark:border-white"
                                : "bg-white text-gray-700 border-gray-200 hover:bg-gray-50 dark:bg-gray-900 dark:text-gray-200 dark:border-gray-800 dark:hover:bg-gray-800"
                        ].join(" ")}
                    >
                        {t.label}
                    </button>
                ))}
            </div>

            <div className="p-4">
                {items.find((t) => t.id === active)?.content}
            </div>
        </div>
    );
}
