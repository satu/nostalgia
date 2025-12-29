import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DeviceList } from './DeviceList';
import type { Device } from '../types';

const mockDevices: Device[] = [
  { id: '1', name: 'Z Device', model: 'Model A', type: 'cast', volume: 0.5, is_active: false },
  { id: '2', name: 'A Device', model: 'Model B', type: 'cast', volume: 0.5, is_active: true },
  { id: '3', name: 'M Device', model: 'Model C', type: 'cast', volume: 0.5, is_active: false },
  { id: '4', name: 'B Device', model: 'Model D', type: 'cast', volume: 0.5, is_active: true },
];

describe('DeviceList', () => {
  it('renders devices in sorted order (active first, then by name)', () => {
    const onToggle = vi.fn();
    const onVolumeChange = vi.fn();

    render(
      <DeviceList 
        devices={mockDevices} 
        onToggle={onToggle} 
        onVolumeChange={onVolumeChange} 
      />
    );

    const deviceNames = screen.getAllByText(/Device/).map(el => el.textContent);
    
    // Expected order:
    // 1. A Device (active)
    // 2. B Device (active)
    // 3. M Device (idle)
    // 4. Z Device (idle)
    
    expect(deviceNames[0]).toBe('A Device');
    expect(deviceNames[1]).toBe('B Device');
    expect(deviceNames[2]).toBe('M Device');
    expect(deviceNames[3]).toBe('Z Device');
  });
});
