import React, { useEffect, useState, useRef } from 'react';
import { getWebSocketUrl } from '../api';

export const NowPlaying: React.FC = () => {
  const [levels, setLevels] = useState({ l: 0, r: 0, db: -96 });
  const [isSignalActive, setIsSignalActive] = useState(false);
  const [isPlayingLocal, setIsPlayingLocal] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Update signal active state based on levels with a 5s hold time to prevent flickering during quiet passages
    if (levels.db > -75) {
      setIsSignalActive(true);
    } else if (isSignalActive) {
      const timeout = setTimeout(() => setIsSignalActive(false), 5000);
      return () => clearTimeout(timeout);
    }
  }, [levels.db, isSignalActive]);

  const toggleLocalPlayback = () => {
    if (!audioRef.current) {
      // Use relative path for stream, assumes /stream.mp3 is proxied
      audioRef.current = new Audio('/stream.mp3');
      audioRef.current.onended = () => setIsPlayingLocal(false);
      audioRef.current.onerror = () => setIsPlayingLocal(false);
    }

    if (isPlayingLocal) {
      audioRef.current.pause();
      // Reset source to stop buffering
      audioRef.current.src = ""; 
      audioRef.current = null;
      setIsPlayingLocal(false);
    } else {
      // Re-create to ensure fresh stream
      audioRef.current = new Audio('/stream.mp3');
      audioRef.current.play().catch(e => console.error("Playback failed", e));
      setIsPlayingLocal(true);
    }
  };

  useEffect(() => {
    const connect = () => {
      const socket = new WebSocket(getWebSocketUrl());
      
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // data format: { l: 0-100, r: 0-100, db: -xx }
          setLevels(data);
        } catch (e) {
          console.error(e);
        }
      };

      socket.onclose = () => {
        // Reconnect after 1s
        setTimeout(connect, 1000);
      };

      ws.current = socket;
    };

    connect();

    return () => {
      ws.current?.close();
    };
  }, []);

  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-col items-stretch justify-start rounded-xl overflow-hidden shadow-lg bg-surface-light dark:bg-surface-dark border border-slate-200 dark:border-slate-800">
        {/* Image */}
        <div 
          className="w-full h-48 bg-[center_85%] bg-no-repeat bg-cover relative group" 
          style={{ backgroundImage: 'url("/banner.jpg")' }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-surface-dark/90 to-transparent"></div>
          <div className="absolute bottom-4 left-4 right-4 flex justify-between items-end">
            <div>
              {/* Removed Phono label as requested */}
            </div>
            <div className={`flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-1 rounded-full border transition-colors duration-300 ${isSignalActive ? 'border-primary/50' : 'border-white/10'}`}>
              <div className={`w-2 h-2 rounded-full transition-all duration-300 ${isSignalActive ? 'bg-primary animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-slate-500'}`}></div>
              <span className="text-xs font-medium text-white transition-opacity duration-300">{isSignalActive ? 'Live' : 'Silent'}</span>
            </div>
          </div>
        </div>

        {/* Info & VU Meter */}
        <div className="flex flex-col gap-4 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm font-medium">
              <span className="material-symbols-outlined text-[18px]">input</span>
              <span>Line-In (RCA)</span>
            </div>
            
            <div className="flex items-center gap-3">
              <button 
                onClick={toggleLocalPlayback}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider transition-all ${
                  isPlayingLocal 
                    ? 'bg-primary text-white shadow-md shadow-primary/30 ring-1 ring-primary/50' 
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
                }`}
              >
                <span className="material-symbols-outlined text-[14px]">
                  {isPlayingLocal ? 'volume_up' : 'headphones'}
                </span>
                {isPlayingLocal ? 'Listening' : 'Listen'}
              </button>
              <span className="text-xs font-mono text-slate-400 dark:text-slate-500 hidden sm:inline-block">44.1kHz</span>
            </div>
          </div>

          {/* VU Meter Component */}
          <div className="flex flex-col gap-2">
            <div className="flex gap-6 justify-between items-center">
              <p className="text-slate-900 dark:text-white text-xs font-bold uppercase tracking-wider">Input Level (VU)</p>
              <p className="text-primary text-xs font-mono">{levels.db} dB</p>
            </div>
            {/* Left Channel */}
            <div className="h-1.5 w-full rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden flex items-center">
              <div className="h-full rounded-full bg-primary transition-all duration-75" style={{ width: `${levels.l}%` }}></div>
            </div>
            {/* Right Channel */}
            <div className="h-1.5 w-full rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden flex items-center">
              <div className="h-full rounded-full bg-primary transition-all duration-75" style={{ width: `${levels.r}%` }}></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
