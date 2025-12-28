import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { NowPlaying } from './NowPlaying';

// Mock the API
vi.mock('../api', () => ({
  getWebSocketUrl: vi.fn(() => 'ws://localhost/ws'),
  api: {}
}));

describe('NowPlaying', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders signal status', () => {
    render(<NowPlaying />);
    expect(screen.getByText('Silent')).toBeInTheDocument();
  });

  it('toggles local playback when listen button is clicked', () => {
    render(<NowPlaying />);
    const listenButton = screen.getByRole('button', { name: /listen/i });
    
    // Initial state
    expect(listenButton).toHaveTextContent('Listen');
    
    // Click to play
    fireEvent.click(listenButton);
    expect(listenButton).toHaveTextContent('Listening');
    
    // Click to stop
    fireEvent.click(listenButton);
    expect(listenButton).toHaveTextContent('Listen');
  });

  it('updates VU meter and signal status on websocket message', async () => {
    let capturedSocket: any;
    
    // Mock WebSocket to capture instance
    const MockSocket = class {
      onopen: (() => void) | null = null;
      onmessage: ((event: any) => void) | null = null;
      onclose: (() => void) | null = null;
      constructor() { capturedSocket = this; setTimeout(() => this.onopen?.(), 0); }
      close() {}
    };
    vi.stubGlobal('WebSocket', MockSocket);

    render(<NowPlaying />);
    
    await waitFor(() => expect(capturedSocket).toBeDefined());

    // Send quiet signal
    act(() => {
        capturedSocket.onmessage({ data: JSON.stringify({ l: 0, r: 0, db: -90 }) });
    });
    expect(screen.getByText('-90 dB')).toBeInTheDocument();
    expect(screen.getByText('Silent')).toBeInTheDocument();

    // Send loud signal
    act(() => {
        capturedSocket.onmessage({ data: JSON.stringify({ l: 50, r: 50, db: -10 }) });
    });
    expect(screen.getByText('-10 dB')).toBeInTheDocument();
    expect(screen.getByText('Live')).toBeInTheDocument();
  });
});
