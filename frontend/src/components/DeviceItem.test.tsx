import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DeviceItem from './DeviceItem';

describe('DeviceItem', () => {
  const mockDevice = {
    id: '1',
    name: 'Test Device',
    model: 'Model X',
    type: 'audio' as const,
    volume: 0.5,
    is_active: false
  };

  it('renders device info', () => {
    // When idle
    render(<DeviceItem device={mockDevice} allDevices={[mockDevice]} onToggle={() => {}} onVolumeChange={() => {}} />);
    expect(screen.getByText('Test Device')).toBeInTheDocument();
    expect(screen.getByText('Idle')).toBeInTheDocument();
  });

  it('renders group info when idle', () => {
    const groupDevice = { ...mockDevice, type: 'group' as const };
    render(<DeviceItem device={groupDevice} allDevices={[groupDevice]} onToggle={() => {}} onVolumeChange={() => {}} />);
    expect(screen.getByText(/Group • Model X/i)).toBeInTheDocument();
  });

  it('calls onToggle when checkbox is clicked', () => {
    const onToggle = vi.fn();
    render(<DeviceItem device={mockDevice} allDevices={[mockDevice]} onToggle={onToggle} onVolumeChange={() => {}} />);
    
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);
    
    expect(onToggle).toHaveBeenCalledWith('1', true);
  });

  it('renders group info and members when active', () => {
    const member1 = { id: 'm1', name: 'Member 1', model: 'Nest Mini', type: 'audio' as const, volume: 0.3, is_active: false };
    const groupDevice = { 
        id: 'g1', 
        name: 'Group 1', 
        model: 'Group Model', 
        type: 'group' as const, 
        volume: 0.5, 
        is_active: true,
        members: ['m1']
    };
    
    const onVolumeChange = vi.fn();
    render(
        <DeviceItem 
            device={groupDevice} 
            allDevices={[groupDevice, member1]} 
            onToggle={() => {}} 
            onVolumeChange={onVolumeChange} 
        />
    );
    
    expect(screen.getByText('Member 1')).toBeInTheDocument();
    expect(screen.getByText('30%')).toBeInTheDocument();

    // Change member volume
    const sliders = screen.getAllByRole('slider');
    expect(sliders).toHaveLength(2); // Group volume + Member volume
    
    fireEvent.change(sliders[1], { target: { value: '0.4' } });
    expect(onVolumeChange).toHaveBeenCalledWith('m1', 0.4);
  });

  it('renders different icons based on device type', () => {
    const tvDevice = { ...mockDevice, type: 'cast' as const };
    const { rerender } = render(<DeviceItem device={tvDevice} allDevices={[tvDevice]} onToggle={() => {}} onVolumeChange={() => {}} />);
    expect(screen.getByText('tv')).toBeInTheDocument();

    const audioDevice = { ...mockDevice, type: 'audio' as const };
    rerender(<DeviceItem device={audioDevice} allDevices={[audioDevice]} onToggle={() => {}} onVolumeChange={() => {}} />);
    expect(screen.getByText('speaker')).toBeInTheDocument();
  });
});