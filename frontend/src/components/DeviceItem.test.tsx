import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DeviceItem from './DeviceItem';

describe('DeviceItem', () => {
  const mockDevice = {
    id: '1',
    name: 'Test Device',
    model: 'Model X',
    type: 'audio',
    volume: 0.5,
    is_active: false
  };

  it('renders device info', () => {
    // When idle
    render(<DeviceItem device={mockDevice} onToggle={() => {}} onVolumeChange={() => {}} />);
    expect(screen.getByText('Test Device')).toBeInTheDocument();
    expect(screen.getByText('Idle')).toBeInTheDocument();
  });

  it('renders group info when idle', () => {
    const groupDevice = { ...mockDevice, type: 'group' };
    render(<DeviceItem device={groupDevice} onToggle={() => {}} onVolumeChange={() => {}} />);
    expect(screen.getByText(/Group • Model X/i)).toBeInTheDocument();
  });

  it('calls onToggle when checkbox is clicked', () => {
    const onToggle = vi.fn();
    render(<DeviceItem device={mockDevice} onToggle={onToggle} onVolumeChange={() => {}} />);
    
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);
    
    expect(onToggle).toHaveBeenCalledWith('1', true);
  });

  it('renders slider and calls onVolumeChange when active', () => {
    const activeDevice = { ...mockDevice, is_active: true };
    const onVolumeChange = vi.fn();
    render(<DeviceItem device={activeDevice} onToggle={() => {}} onVolumeChange={onVolumeChange} />);
    
    expect(screen.getByText(/Active • Casting/i)).toBeInTheDocument();
    
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '0.8' } });
    
    expect(onVolumeChange).toHaveBeenCalledWith('1', 0.8);
  });
});