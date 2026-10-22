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
      <body className="min-h-screen bg-[#0A0A0A] text-slate-100 antialiased selection:bg-[#FF2D95]/30 selection:text-[#FF2D95] relative overflow-x-hidden">
        {/* Subtle ambient lighting effects */}
        <div className="fixed top-0 left-1/4 w-96 h-96 bg-[#007BA7]/10 rounded-full blur-3xl pointer-events-none -z-10"></div>
        <div className="fixed bottom-0 right-10 w-96 h-96 bg-[#FF2D95]/10 rounded-full blur-3xl pointer-events-none -z-10"></div>
        
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
