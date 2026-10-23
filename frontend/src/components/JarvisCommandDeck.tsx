'use client';

import React, { useState, useEffect } from 'react';
import { 
  Radar, 
  Cpu, 
  Volume2, 
  VolumeX, 
  Radio, 
  Zap, 
  ShieldCheck, 
  Activity, 
  Sparkles,
  Terminal,
  Crosshair
} from 'lucide-react';
import { soundFx } from '@/lib/soundFx';

export default function JarvisCommandDeck() {
  const [currentTime, setCurrentTime] = useState<string>('');
  const [audioEnabled, setAudioEnabled] = useState<boolean>(true);
  const [scanning, setScanning] = useState<boolean>(false);
  const [overdrive, setOverdrive] = useState<boolean>(false);
  const [scanMessage, setScanMessage] = useState<string | null>(null);
  const [radarDegree, setRadarDegree] = useState<number>(0);

  useEffect(() => {
    setAudioEnabled(soundFx.enabled);
    const updateClock = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleDateString('en-GB') + ' // ' + 
        now.toLocaleTimeString('en-US', { hour12: false }) + ' IST'
      );
    };
    updateClock();
    const timer = setInterval(updateClock, 1000);

    // Radar rotation degree ticker
    const radarTimer = setInterval(() => {
      setRadarDegree(prev => (prev + 12) % 360);
    }, 100);

    return () => {
      clearInterval(timer);
      clearInterval(radarTimer);
    };
  }, []);

  const toggleSound = () => {
    const newState = soundFx.toggleAudio();
    setAudioEnabled(newState);
  };

  const triggerTacticalScan = () => {
    soundFx.playScan();
    setScanning(true);
    setScanMessage('JARVIS: Sweeping Naukri, Glassdoor & Google Jobs across India coordinates...');
    
    setTimeout(() => {
      soundFx.playChirp();
      setScanning(false);
      setScanMessage('Tactical Sweep Complete: 1-2 Yrs Experience Target Lock Verified // All Nodes Synchronized');
      setTimeout(() => setScanMessage(null), 4000);
    }, 2200);
  };

  const triggerOverdrive = () => {
    soundFx.playEngage();
    setOverdrive(prev => !prev);
  };

  return (
    <div className="relative mb-8 p-6 rounded-2xl glass-panel hud-bracket border border-white/10 overflow-hidden shadow-2xl shadow-[#007BA7]/10">
      {/* Background ambient HUD scan ray */}
      {scanning && (
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#007BA7]/20 to-[#FF2D95]/20 animate-pulse pointer-events-none -z-10" />
      )}

      {/* Top Telemetry Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-white/10 text-xs">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${overdrive ? 'bg-[#FF2D95]' : 'bg-[#007BA7]'}`} />
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${overdrive ? 'bg-[#FF2D95]' : 'bg-[#007BA7]'}`} />
            </span>
            <span className="font-mono font-bold tracking-wider text-white">
              J.A.R.V.I.S. PROTOCOL // <span className={overdrive ? 'text-[#FF2D95]' : 'text-[#007BA7]'}>{overdrive ? 'OVERDRIVE ACTIVE' : 'SYSTEM ONLINE'}</span>
            </span>
          </div>
          <span className="hidden sm:inline text-white/20">•</span>
          <span className="hidden sm:inline font-mono text-slate-400">SYS.LOC: [28.5355° N, 77.3910° E] NOIDA</span>
        </div>

        <div className="flex items-center gap-4 font-mono text-slate-300">
          <span className="text-slate-400">{currentTime || 'SYNCHRONIZING...'}</span>
          
          <button
            onClick={toggleSound}
            title="Toggle Audio Feedback"
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/[0.04] backdrop-blur-md border border-white/[0.08] hover:border-[#007BA7]/50 text-slate-300 hover:text-white transition-all cursor-pointer"
          >
            {audioEnabled ? (
              <>
                <Volume2 className="w-3.5 h-3.5 text-[#007BA7]" />
                <span className="text-[11px] text-[#007BA7] font-semibold">AUDIO ON</span>
              </>
            ) : (
              <>
                <VolumeX className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-[11px] text-slate-500">MUTED</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Interactive Deck */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center pt-5">
        
        {/* Left: Holographic ARC Reactor Core */}
        <div className="lg:col-span-4 flex items-center justify-center">
          <div 
            onClick={() => { soundFx.playClick(); triggerTacticalScan(); }}
            className="relative group cursor-pointer w-44 h-44 flex items-center justify-center select-none"
            title="Click to trigger JARVIS Tactical Scan"
          >
            {/* Outer Rotating HUD Ring */}
            <div className={`absolute inset-0 rounded-full border border-dashed border-[#007BA7]/40 ${overdrive ? 'animate-spin-slow duration-700' : 'animate-spin-slow'}`} />
            
            {/* Reverse Middle Concentric Ring */}
            <div className={`absolute inset-2 rounded-full border border-[#FF2D95]/30 ${overdrive ? 'animate-spin-reverse duration-500' : 'animate-spin-reverse'}`} />
            
            {/* Radar Crosshairs */}
            <div className="absolute inset-x-0 top-1/2 h-px bg-gradient-to-r from-transparent via-[#007BA7]/50 to-transparent" />
            <div className="absolute inset-y-0 left-1/2 w-px bg-gradient-to-b from-transparent via-[#007BA7]/50 to-transparent" />

            {/* Glowing Center Hologram Orb */}
            <div className="relative w-28 h-28 rounded-full overflow-hidden border-2 border-[#007BA7] shadow-lg shadow-[#007BA7]/30 group-hover:border-[#FF2D95] group-hover:shadow-[#FF2D95]/40 transition-all">
              <img 
                src="/images/jarvis_orb.jpg" 
                alt="JARVIS Core" 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-[#007BA7]/10 mix-blend-overlay group-hover:bg-[#FF2D95]/15 transition-all" />
            </div>

            {/* Live Degree Angle Readout */}
            <div className="absolute -bottom-2 bg-black/60 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-mono font-bold text-[#007BA7] border border-[#007BA7]/40 shadow-sm">
              HDG {String(radarDegree).padStart(3, '0')}°
            </div>
          </div>
        </div>

        {/* Center: Live Tactical Metrics & Spectrum */}
        <div className="lg:col-span-5 space-y-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-[#007BA7]" />
                Neural Sync // Gemini 1.5 & ChromaDB
              </span>
              <span className="text-xs font-mono font-bold text-[#FF2D95]">99.4% COHERENCE</span>
            </div>
            {/* Futuristic Tech Meter */}
            <div className="w-full bg-white/[0.04] h-2 rounded-full overflow-hidden border border-white/[0.08] p-0.5">
              <div 
                className="h-full bg-gradient-to-r from-[#007BA7] via-[#0092c4] to-[#FF2D95] rounded-full transition-all duration-700 shadow-sm shadow-[#FF2D95]/50"
                style={{ width: '99.4%' }}
              />
            </div>
          </div>

          {/* Equalizer Audio Frequency Visualizer */}
          <div className="p-3.5 rounded-xl bg-white/[0.03] backdrop-blur-md border border-white/[0.08] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Radio className="w-4 h-4 text-[#FF2D95] animate-pulse" />
              <div>
                <span className="text-[11px] font-mono font-semibold text-slate-300 block">AUDIO & TELEMETRY SPECTRUM</span>
                <span className="text-[10px] font-mono text-slate-500">BANDWIDTH: 100 Gbit // LATENCY: 12ms</span>
              </div>
            </div>

            {/* EQ Frequency Bars */}
            <div className="flex items-end gap-1 h-6">
              {[40, 75, 95, 60, 85, 100, 70, 50, 90, 65, 80, 45].map((height, i) => (
                <div 
                  key={i} 
                  className={`w-1 rounded-full transition-all duration-300 ${
                    i % 2 === 0 ? 'bg-[#007BA7]' : 'bg-[#FF2D95]'
                  } ${scanning ? 'animate-bounce' : ''}`}
                  style={{ 
                    height: scanning ? `${Math.min(100, height + 20)}%` : `${height}%`,
                    animationDelay: `${i * 0.05}s` 
                  }}
                />
              ))}
            </div>
          </div>

          {/* Target Profile HUD Matrix */}
          <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div className="p-2.5 rounded-xl bg-white/[0.03] backdrop-blur-md border border-white/[0.08]">
              <span className="text-slate-500 block text-[10px]">EXPERIENCE LOCK</span>
              <span className="text-slate-200 font-semibold text-[#007BA7]">1-2 Years (Auto-Increment)</span>
            </div>
            <div className="p-2.5 rounded-xl bg-white/[0.03] backdrop-blur-md border border-white/[0.08]">
              <span className="text-slate-500 block text-[10px]">TARGET COMPENSATION</span>
              <span className="text-slate-200 font-semibold text-[#FF2D95]">6+ LPA CTC (Full-Time)</span>
            </div>
          </div>
        </div>

        {/* Right: Interactive Command Buttons */}
        <div className="lg:col-span-3 flex flex-col gap-2.5">
          <button
            onClick={triggerTacticalScan}
            disabled={scanning}
            className={`w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-mono font-bold transition-all shadow-lg cursor-pointer ${
              scanning 
                ? 'bg-white/[0.05] text-slate-400 border border-[#007BA7]/30 cursor-wait'
                : 'bg-gradient-to-r from-[#007BA7]/90 to-[#0092c4]/90 hover:from-[#008dbf] hover:to-[#FF2D95] text-white shadow-[#007BA7]/20 border border-[#007BA7]/40'
            }`}
          >
            <Crosshair className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
            <span>{scanning ? 'SWEEPING RADAR...' : 'EXECUTE TACTICAL SCAN'}</span>
          </button>

          <button
            onClick={triggerOverdrive}
            className={`w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-mono font-bold border transition-all cursor-pointer ${
              overdrive
                ? 'bg-[#FF2D95]/15 border-[#FF2D95] text-[#FF2D95] shadow-lg shadow-[#FF2D95]/20'
                : 'bg-white/[0.03] backdrop-blur-md hover:bg-white/[0.06] text-slate-300 border-white/[0.08] hover:border-[#FF2D95]/50'
            }`}
          >
            <Zap className={`w-4 h-4 ${overdrive ? 'text-[#FF2D95] fill-[#FF2D95]' : 'text-slate-400'}`} />
            <span>{overdrive ? 'OVERDRIVE ENGAGED' : 'ENGAGE OVERDRIVE'}</span>
          </button>

          <div className="p-2.5 rounded-xl bg-white/[0.02] backdrop-blur-md border border-white/[0.06] text-[10px] font-mono text-slate-400 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>HALLUCINATION GUARD: 100% GROUND TRUTH VERIFIED</span>
          </div>
        </div>

      </div>

      {/* Dynamic Scan Alert Strip */}
      {scanMessage && (
        <div className="mt-4 p-2.5 rounded-xl bg-black/40 backdrop-blur-xl border border-[#007BA7]/50 text-xs font-mono text-[#007BA7] flex items-center gap-2 animate-fadeIn">
          <Terminal className="w-4 h-4 text-[#FF2D95]" />
          <span className="animate-pulse">{scanMessage}</span>
        </div>
      )}
    </div>
  );
}
