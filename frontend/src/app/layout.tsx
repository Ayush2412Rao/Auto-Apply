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
        {/* Full-screen JARVIS Holographic Interface Background Texture */}
        <div 
          className="fixed inset-0 pointer-events-none -z-30 bg-cover bg-center bg-no-repeat opacity-[0.22] mix-blend-screen filter contrast-125 brightness-110"
          style={{ 
            backgroundImage: "url('/images/jarvis_hud_bg.jpg')",
            maskImage: "radial-gradient(circle at center, black 65%, transparent 95%)",
            WebkitMaskImage: "radial-gradient(circle at center, black 65%, transparent 95%)"
          }}
        />
        
        {/* Cybernetic Scan Grid */}
        <div className="fixed inset-0 pointer-events-none -z-20 cyber-grid opacity-50" />

        {/* Ambient sci-fi reactor lighting blooms */}
        <div className="fixed top-[-10%] left-1/4 w-[650px] h-[650px] bg-[#007BA7]/15 rounded-full blur-[140px] pointer-events-none -z-10 animate-pulse-glow" />
        <div className="fixed bottom-[-10%] right-10 w-[650px] h-[650px] bg-[#FF2D95]/12 rounded-full blur-[160px] pointer-events-none -z-10" />
        <div className="fixed top-1/3 right-1/4 w-[450px] h-[450px] bg-[#007BA7]/10 rounded-full blur-[130px] pointer-events-none -z-10" />
        
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
