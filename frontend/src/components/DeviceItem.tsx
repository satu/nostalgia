import React, { useState, useEffect, useRef } from 'react';
import type { Device } from '../types';

interface DeviceItemProps {
  device: Device;
  allDevices: Device[];
  onToggle: (id: string, active: boolean) => void;
  onVolumeChange: (id: string, volume: number) => void;
}

const DeviceItem: React.FC<DeviceItemProps> = ({ device, allDevices, onToggle, onVolumeChange }) => {
  const isGroup = device.type === 'group';
  const icon = isGroup ? 'speaker_group' : (device.type === 'audio' ? 'speaker' : 'tv'); // basic mapping

  const memberDevices = device.members 
    ? device.members.map(mid => allDevices.find(d => d.id === mid)).filter(Boolean) as Device[]
    : [];

  // Optimistic UI state to prevent flickering
  const [pendingActive, setPendingActive] = useState<boolean | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync with prop updates
  useEffect(() => {
    if (pendingActive !== null && device.is_active === pendingActive) {
      // Backend confirmed our state
      // Add a grace period to prevent flickering if the state is unstable (e.g. disconnects)
      const confirmTimeout = setTimeout(() => {
        setPendingActive(null);
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }
      }, 5000);
      
      return () => clearTimeout(confirmTimeout);
    }
  }, [device.is_active, pendingActive]);

  const handleToggle = (checked: boolean) => {
    setPendingActive(checked);
    onToggle(device.id, checked);

    // Safety timeout: if backend doesn't update in 20s, revert to prop
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      setPendingActive(null);
    }, 20000);
  };

  const displayActive = pendingActive !== null ? pendingActive : device.is_active;

  return (
    <div className={`flex flex-col gap-3 p-4 rounded-xl border transition-all ${displayActive ? 'bg-surface-light dark:bg-surface-dark border-primary/30 shadow-[0_0_15px_-3px_rgba(23,207,84,0.15)]' : 'bg-surface-light dark:bg-surface-dark border-transparent hover:border-slate-200 dark:hover:border-slate-700'}`}>
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 flex-1">
          <div className={`flex items-center justify-center rounded-lg shrink-0 w-12 h-12 ${displayActive ? 'bg-primary/20 text-primary' : 'bg-slate-100 dark:bg-[#29382e] text-slate-500 dark:text-slate-400'}`}>
            <span className="material-symbols-outlined text-[24px]">{icon}</span>
          </div>
          <div className="flex flex-col justify-center">
            <p className="text-slate-900 dark:text-white text-base font-bold leading-normal line-clamp-1">{device.name}</p>
            <p className={`${displayActive ? 'text-primary font-medium' : 'text-slate-500 dark:text-slate-400 font-normal'} text-sm leading-normal line-clamp-1`}>
              {displayActive ? 'Active • Casting' : (isGroup ? `Group • ${device.model}` : 'Idle')}
            </p>
          </div>
        </div>
        <div className="shrink-0">
          <label className="relative flex h-[31px] w-[51px] cursor-pointer items-center rounded-full border-none bg-slate-200 dark:bg-[#29382e] p-0.5 has-[:checked]:justify-end has-[:checked]:bg-primary transition-colors">
            <div className={`h-[27px] w-[27px] rounded-full bg-white shadow-sm ${pendingActive !== null ? 'animate-pulse' : ''}`}></div>
            <input 
              type="checkbox" 
              className="invisible absolute" 
              checked={displayActive} 
              onChange={(e) => handleToggle(e.target.checked)}
            />
          </label>
        </div>
      </div>

      {/* Volume Slider for Active Device */}
      {displayActive && (
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

      {/* Member Volumes for Active Group */}
      {displayActive && isGroup && memberDevices.length > 0 && (
        <div className="flex flex-col gap-4 mt-2 pt-4 border-t border-slate-100 dark:border-slate-800 animate-in fade-in duration-500">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">Group Members</p>
          {memberDevices.map(member => (
            <div key={member.id} className="flex flex-col gap-2 pl-2 border-l-2 border-primary/20">
               <div className="flex justify-between items-center px-1">
                  <span className="text-sm font-medium text-slate-600 dark:text-slate-300">{member.name}</span>
                  <span className="text-xs text-slate-400">{Math.round(member.volume * 100)}%</span>
               </div>
               <div className="flex items-center gap-3">
                  <div className="relative w-full h-4 flex items-center">
                    <div className="absolute w-full h-1 bg-slate-100 dark:bg-[#1e2a22] rounded-full"></div>
                    <div className="absolute h-1 bg-primary/60 rounded-full" style={{ width: `${member.volume * 100}%` }}></div>
                    <input 
                      type="range" 
                      min="0" 
                      max="1" 
                      step="0.01"
                      value={member.volume} 
                      onChange={(e) => onVolumeChange(member.id, parseFloat(e.target.value))}
                      className="absolute w-full opacity-0 cursor-pointer h-4 z-10" 
                    />
                    {/* Custom Thumb Representation */}
                    <div 
                      className="absolute h-3 w-3 bg-white rounded-full shadow-sm pointer-events-none transition-all duration-75" 
                      style={{ left: `${member.volume * 100}%`, transform: 'translateX(-50%)' }}
                    ></div>
                  </div>
               </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DeviceItem;