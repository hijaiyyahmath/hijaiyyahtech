export default function CodeBlock({ code }: { code: string }) {
    return (
        <pre className="overflow-x-auto rounded-xl border bg-gray-50 p-4 text-xs dark:bg-gray-950 dark:border-gray-800">
            <code className="font-mono">{code}</code>
        </pre>
    );
}
