import type { Metadata } from "next";
import { Inter, Amiri } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });
const amiri = Amiri({
  weight: ["400", "700"],
  subsets: ["arabic"],
  variable: "--font-arabic"
});

export const metadata: Metadata = {
  title: "HadithGPT - AI-Powered Hadith Search",
  description: "Search and explore authentic Hadiths with AI-powered semantic search across Sahih Bukhari, Sahih Muslim, and more.",
  keywords: ["hadith", "islam", "search", "bukhari", "muslim", "quran", "sunnah"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} ${amiri.variable}`}>{children}</body>
    </html>
  );
}
