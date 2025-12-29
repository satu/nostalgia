import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import App from './App';
import { api } from './api';

// Mock the API
vi.mock('./api', () => ({
  getWebSocketUrl: vi.fn(() => 'ws://localhost/ws'),
  api: {
    getDevices: vi.fn(),
    startCast: vi.fn(),
    stopCast: vi.fn(),
    setVolume: vi.fn(),
  }
}));

describe('App Component', () => {
  it('renders loading state initially', async () => {
    (api.getDevices as any).mockResolvedValue([]);
    render(<App />);
    expect(screen.getByText(/loading devices.../i)).toBeInTheDocument();
  });

  it('renders devices after loading', async () => {
    (api.getDevices as any).mockResolvedValue([
      { id: '1', name: 'Kitchen Speaker', model: 'Nest Audio', type: 'audio', volume: 0.5, is_active: false }
    ]);
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('Kitchen Speaker')).toBeInTheDocument();
    });
  });

  it('renders error message on failure', async () => {
    (api.getDevices as any).mockRejectedValue(new Error('API Error'));
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/failed to load devices/i)).toBeInTheDocument();
    });
  });

  it('handles device toggle', async () => {
    const devices = [{ id: '1', name: 'D1', model: 'M', type: 'audio', volume: 0.5, is_active: false }];
    (api.getDevices as any).mockResolvedValue(devices);
    (api.startCast as any).mockResolvedValue({ status: 'started' });
    
    render(<App />);
    
    const checkbox = await screen.findByRole('checkbox');
    await act(async () => {
      fireEvent.click(checkbox);
    });
    
    expect(api.startCast).toHaveBeenCalledWith('1');
  });

  it('reverts device toggle on failure', async () => {
    const devices = [{ id: '1', name: 'D1', model: 'M', type: 'audio', volume: 0.5, is_active: false }];
    (api.getDevices as any).mockResolvedValue(devices);
    (api.startCast as any).mockRejectedValue(new Error('Fail'));
    
    render(<App />);
    
    const checkbox = await screen.findByRole('checkbox');
    await act(async () => {
      fireEvent.click(checkbox);
    });
    
    await waitFor(() => {
       expect(api.startCast).toHaveBeenCalledWith('1');
    });
  });

  it('handles volume change', async () => {
    const devices = [{ id: '1', name: 'D1', model: 'M', type: 'audio', volume: 0.5, is_active: true }];
    (api.getDevices as any).mockResolvedValue(devices);
    (api.setVolume as any).mockResolvedValue({});
    
    render(<App />);
    
    const slider = await screen.findByRole('slider');
    await act(async () => {
      fireEvent.change(slider, { target: { value: '0.8' } });
    });
    
    expect(api.setVolume).toHaveBeenCalledWith('1', 0.8);
  });

  it('handles stop all', async () => {
    const devices = [
      { id: '1', name: 'D1', model: 'M', type: 'audio', volume: 0.5, is_active: true },
      { id: '2', name: 'D2', model: 'M', type: 'audio', volume: 0.5, is_active: true }
    ];
    (api.getDevices as any).mockResolvedValue(devices);
    (api.stopCast as any).mockResolvedValue({});
    
    render(<App />);
    
    // Wait for devices to be rendered
    await screen.findByText('D1');
    await screen.findByText('D2');
    
    const stopAllBtn = await screen.findByText(/stop all/i);
    await act(async () => {
      fireEvent.click(stopAllBtn);
    });
    
    await waitFor(() => {
      expect(api.stopCast).toHaveBeenCalledTimes(2);
    });
  });

  it('sorts devices: active first, then alphabetical', async () => {
    const devices = [
      { id: '3', name: 'C', model: 'M', type: 'audio', volume: 0.5, is_active: false },
      { id: '1', name: 'B', model: 'M', type: 'audio', volume: 0.5, is_active: true },
      { id: '2', name: 'A', model: 'M', type: 'audio', volume: 0.5, is_active: false },
    ];
    (api.getDevices as any).mockResolvedValue(devices);
    
    render(<App />);
    
    await waitFor(() => {
      const elements = screen.getAllByText(/^[A-C]$/);
      expect(elements[0]).toHaveTextContent('B'); // Active
      expect(elements[1]).toHaveTextContent('A'); // Inactive, sorted alpha
      expect(elements[2]).toHaveTextContent('C'); // Inactive, sorted alpha
    });
  });
});
