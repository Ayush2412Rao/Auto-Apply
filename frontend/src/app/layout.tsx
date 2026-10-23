import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'Auto-Apply | Automated Job Search Platform',
  description: 'Personal automated job discovery and application platform powered by LangGraph, ChromaDB, Gemini, and Apify.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#090A0F] text-slate-100 antialiased selection:bg-[#007BA7]/30 selection:text-[#38bdf8] relative overflow-x-hidden">
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
