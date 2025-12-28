import React from 'react';

export const NowPlaying: React.FC = () => {
  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-col items-stretch justify-start rounded-xl overflow-hidden shadow-lg bg-surface-light dark:bg-surface-dark border border-slate-200 dark:border-slate-800">
        {/* Image */}
        <div 
          className="w-full h-48 bg-center bg-no-repeat bg-cover relative group" 
          style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDgDAuf_R_jhvp8YD8egR-kPcqKZ3-tO8ZrSwzAX5Xezh0UZBQRucgmCbGQ6NwPq3mD-o5hoZRB19dXGVtI3Fser28VD1dTxb8oWUP2XZmfOdeT9kWp3xd0ngW9L_RSmByYyHO6GdRUWuNE3_hjme4Ani4aXYicGwp8HcDkxU7ymG_-hECsfb02U-i_Wu27vFZVZN-uG1WfKxZGN1qpU4FZLL9xKSwwZk8U4u-d7qvU5yQRqkGJGphmZFGnjp9kgyHNou2fvy6ELQg")' }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-surface-dark/90 to-transparent"></div>
          <div className="absolute bottom-4 left-4 right-4 flex justify-between items-end">
            <div>
              <p className="text-primary text-xs font-bold uppercase tracking-wider mb-1">Source Input</p>
              <h3 className="text-white text-2xl font-bold leading-tight">Phono</h3>
            </div>
            <div className="flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
              <span className="text-xs font-medium text-white">Live</span>
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
            <span className="text-xs font-mono text-slate-400 dark:text-slate-500">44.1kHz / 16bit</span>
          </div>

          {/* VU Meter Component - Static for now */}
          <div className="flex flex-col gap-2">
            <div className="flex gap-6 justify-between items-center">
              <p className="text-slate-900 dark:text-white text-xs font-bold uppercase tracking-wider">Input Level (VU)</p>
              <p className="text-primary text-xs font-mono">-3 dB</p>
            </div>
            {/* Left Channel */}
            <div className="h-1.5 w-full rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden flex items-center">
              <div className="h-full rounded-full bg-primary transition-all duration-75" style={{ width: '72%' }}></div>
            </div>
            {/* Right Channel */}
            <div className="h-1.5 w-full rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden flex items-center">
              <div className="h-full rounded-full bg-primary transition-all duration-75" style={{ width: '68%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
