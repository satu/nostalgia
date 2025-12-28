import { Device } from './types';

// Detect if we are in development mode to point to the Pi or localhost
// For now, hardcode the Pi's IP or relative path if served from same origin.
// Since we run Vite locally and backend on Pi, we need the Pi's IP.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://nostalgia:8000/api';

export const api = {
  getDevices: async (): Promise<Device[]> => {
    const response = await fetch(`${API_BASE_URL}/devices`);
    if (!response.ok) throw new Error('Failed to fetch devices');
    return response.json();
  },

  startCast: async (deviceId: string) => {
    const response = await fetch(`${API_BASE_URL}/cast/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_id: deviceId }),
    });
    if (!response.ok) throw new Error('Failed to start casting');
    return response.json();
  },

  stopCast: async (deviceId: string) => {
    const response = await fetch(`${API_BASE_URL}/cast/stop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_id: deviceId }),
    });
    if (!response.ok) throw new Error('Failed to stop casting');
    return response.json();
  },

  setVolume: async (deviceId: string, volume: number) => {
    const response = await fetch(`${API_BASE_URL}/cast/volume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_id: deviceId, volume }),
    });
    if (!response.ok) throw new Error('Failed to set volume');
    return response.json();
  }
};
