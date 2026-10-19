import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'Auto-Apply | Agentic AI Job Application Platform',
  description: 'Production-ready personal AI job discovery and application platform powered by LangGraph, ChromaDB, Gemini, and Apify.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased selection:bg-indigo-500/30 selection:text-indigo-200">
        <div className="flex">
          <Sidebar />
          <main className="ml-64 flex-1 p-8 min-h-screen">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
