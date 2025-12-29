import React from 'react';
import type { Device } from '../types';
import DeviceItem from './DeviceItem';

interface DeviceListProps {
  devices: Device[];
  onToggle: (id: string, active: boolean) => void;
  onVolumeChange: (id: string, volume: number) => void;
}

export const DeviceList: React.FC<DeviceListProps> = ({ devices, onToggle, onVolumeChange }) => {
  const sortedDevices = [...devices].sort((a, b) => {
    if (a.is_active === b.is_active) {
      return a.name.localeCompare(b.name);
    }
    return a.is_active ? -1 : 1;
  });

  return (
    <section className="flex flex-col gap-2 pb-24">
      <h3 className="text-slate-900 dark:text-white tracking-tight text-xl font-bold leading-tight px-1 pb-2">Broadcast To</h3>
      {sortedDevices.map(device => (
        <DeviceItem 
          key={device.id} 
          device={device} 
          allDevices={devices}
          onToggle={onToggle} 
          onVolumeChange={onVolumeChange} 
        />
      ))}
    </section>
  );
};
