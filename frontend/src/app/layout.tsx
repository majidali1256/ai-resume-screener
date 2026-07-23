import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MATCH.AI — AI Resume Screener & Feedback System",
  description: "Deterministic AI resume screening, match scoring (0-100), missing keywords detection, and rewrite suggestions powered by Google Gemini Flash and FastAPI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <body className="min-h-full flex flex-col bg-slate-950 text-slate-100">{children}</body>
    </html>
  );
}
