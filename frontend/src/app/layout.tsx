import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'AutoApply // Autonomous Career Intelligence',
  description: 'Next-generation personal AI job discovery and application platform powered by LangGraph, ChromaDB, Gemini, and Apify.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#050508] text-slate-100 antialiased selection:bg-[#FF2D95]/30 selection:text-[#FF2D95] relative overflow-x-hidden">
        <Navbar />
        <main className="pt-20 min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
