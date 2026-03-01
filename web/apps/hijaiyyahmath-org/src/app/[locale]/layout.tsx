import "@/app/globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export function generateStaticParams() {
    return [{ locale: "en" }];
}

export default function LocaleLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
            <body className="bg-gray-50 font-sans text-gray-900">
                <Header />
                <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
                <Footer />
            </body>
        </html>
    );
}
