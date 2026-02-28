// src/components/HijaiyyahLetterRow.tsx
export default function HijaiyyahLetterRow() {
    const letters =
        "ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن و ه ي";

    const items = letters.split(" ");

    return (
        <div className="rounded-xl border bg-white p-4 dark:bg-gray-950 dark:border-gray-800">
            <div className="text-xs text-gray-600 dark:text-gray-400">Normative Hijaiyyah Set (28)</div>

            <div className="mt-3 flex flex-wrap gap-2 font-arabic text-lg leading-none">
                {items.map((ch) => (
                    <span
                        key={ch}
                        className="rounded-full border px-3 py-2 bg-gray-50 dark:bg-gray-900 dark:border-gray-800"
                        title={ch}
                    >
                        {ch}
                    </span>
                ))}
            </div>

            <div className="mt-3 text-xs text-gray-600 dark:text-gray-400">
                Locked ordering used across HL‑18 / HISA / evidence tooling.
            </div>
        </div>
    );
}
