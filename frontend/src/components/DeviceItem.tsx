import React from 'react';
import type { Device } from '../types';

interface DeviceItemProps {
  device: Device;
  onToggle: (id: string, active: boolean) => void;
  onVolumeChange: (id: string, volume: number) => void;
}

const DeviceItem: React.FC<DeviceItemProps> = ({ device, onToggle, onVolumeChange }) => {
  const isGroup = device.type === 'group';
  const icon = isGroup ? 'speaker_group' : (device.type === 'audio' ? 'speaker' : 'tv'); // basic mapping

  return (
    <div className={`flex flex-col gap-3 p-4 rounded-xl border transition-all ${device.is_active ? 'bg-surface-light dark:bg-surface-dark border-primary/30 shadow-[0_0_15px_-3px_rgba(23,207,84,0.15)]' : 'bg-surface-light dark:bg-surface-dark border-transparent hover:border-slate-200 dark:hover:border-slate-700'}`}>
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 flex-1">
          <div className={`flex items-center justify-center rounded-lg shrink-0 w-12 h-12 ${device.is_active ? 'bg-primary/20 text-primary' : 'bg-slate-100 dark:bg-[#29382e] text-slate-500 dark:text-slate-400'}`}>
            <span className="material-symbols-outlined text-[24px]">{icon}</span>
          </div>
          <div className="flex flex-col justify-center">
            <p className="text-slate-900 dark:text-white text-base font-bold leading-normal line-clamp-1">{device.name}</p>
            <p className={`${device.is_active ? 'text-primary font-medium' : 'text-slate-500 dark:text-slate-400 font-normal'} text-sm leading-normal line-clamp-1`}>
              {device.is_active ? 'Active • Casting' : (isGroup ? `Group • ${device.model}` : 'Idle')}
            </p>
          </div>
        </div>
        <div className="shrink-0">
          <label className="relative flex h-[31px] w-[51px] cursor-pointer items-center rounded-full border-none bg-slate-200 dark:bg-[#29382e] p-0.5 has-[:checked]:justify-end has-[:checked]:bg-primary transition-colors">
            <div className="h-[27px] w-[27px] rounded-full bg-white shadow-sm"></div>
            <input 
              type="checkbox" 
              className="invisible absolute" 
              checked={device.is_active} 
              onChange={(e) => onToggle(device.id, e.target.checked)}
            />
          </label>
        </div>
      </div>

      {/* Volume Slider for Active Device */}
      {device.is_active && (
        <div className="flex items-center gap-3 pt-2 animate-in fade-in slide-in-from-top-2 duration-300">
          <span className="material-symbols-outlined text-slate-400 text-[20px]">volume_mute</span>
          <div className="relative w-full h-6 flex items-center">
            <div className="absolute w-full h-1 bg-slate-200 dark:bg-[#29382e] rounded-full"></div>
            <div className="absolute h-1 bg-primary rounded-full" style={{ width: `${device.volume * 100}%` }}></div>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.01"
              value={device.volume} 
              onChange={(e) => onVolumeChange(device.id, parseFloat(e.target.value))}
              className="absolute w-full opacity-0 cursor-pointer h-6 z-10" 
            />
            {/* Custom Thumb Representation */}
            <div 
              className="absolute h-4 w-4 bg-white rounded-full shadow-md pointer-events-none transition-all duration-75" 
              style={{ left: `${device.volume * 100}%`, transform: 'translateX(-50%)' }}
            ></div>
          </div>
          <span className="material-symbols-outlined text-slate-400 text-[20px]">volume_up</span>
        </div>
      )}
    </div>
  );
};

export default DeviceItem;
