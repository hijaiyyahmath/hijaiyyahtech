import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";
import SearchDialog from "@/components/SearchDialog";

const nav = [
    { href: "/en", label: "Home" },
    { href: "/en/stack", label: "Technology Stack" },
    { href: "/en/releases", label: "Releases" },
    { href: "/en/datasets", label: "Datasets" },
    { href: "/en/tools/evidence-verifier", label: "Tools" },
    { href: "/en/downloads", label: "Auditor Bundle" },
    { href: "/en/docs/auditor-quickstart", label: "Quickstart" }
];

export default function Header() {
    return (
        <header className="border-b bg-white dark:bg-gray-950 dark:border-gray-800">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
                <div className="font-semibold">
                    <Link href="/en">HijaiyyahMath.org</Link>
                </div>

                <nav className="hidden gap-4 text-sm md:flex">
                    {nav.map((n) => (
                        <Link key={n.href} href={n.href} className="text-gray-700 hover:text-black dark:text-gray-200 dark:hover:text-white">
                            {n.label}
                        </Link>
                    ))}
                </nav>

                <div className="flex items-center gap-2">
                    <SearchDialog />
                    <ThemeToggle />
                </div>
            </div>
        </header>
    );
}
