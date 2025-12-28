import React from 'react';

interface StopButtonProps {
  onStopAll: () => void;
}

export const StopButton: React.FC<StopButtonProps> = ({ onStopAll }) => {
  return (
    <div className="p-4 bg-background-light dark:bg-background-dark sticky bottom-0 z-10 border-t border-slate-200 dark:border-slate-800">
      <button 
        onClick={onStopAll}
        className="flex w-full cursor-pointer items-center justify-center rounded-xl h-12 bg-slate-200 dark:bg-[#29382e] hover:bg-red-500/10 hover:text-red-500 dark:hover:bg-red-900/20 dark:hover:text-red-400 text-slate-600 dark:text-slate-300 gap-2 text-base font-bold leading-normal tracking-[0.015em] transition-all duration-200 group"
      >
        <span className="material-symbols-outlined group-hover:fill-current">stop_circle</span>
        <span className="">Stop All Casting</span>
      </button>
    </div>
  );
};
