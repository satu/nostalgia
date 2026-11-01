import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { NowPlaying } from './NowPlaying';

// Mock the API
const mockRestartAudio = vi.fn().mockResolvedValue({ status: 'restarted' });
vi.mock('../api', () => ({
  getWebSocketUrl: vi.fn(() => 'ws://localhost/ws'),
  api: {
    restartAudio: () => mockRestartAudio()
  }
}));

describe('NowPlaying', () => {
  afterEach(() => {
    vi.restoreAllMocks();
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
    vi.useFakeTimers();
    let capturedSocket: any;
    
    const MockSocket = vi.fn().mockImplementation(function(this: any) {
      capturedSocket = this;
      this.close = vi.fn();
    });
    vi.stubGlobal('WebSocket', MockSocket);

    render(<NowPlaying />);
    
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

    // Send quiet signal again, should stay "Live" for 5 seconds
    act(() => {
        capturedSocket.onmessage({ data: JSON.stringify({ l: 0, r: 0, db: -90 }) });
    });
    expect(screen.getByText('Live')).toBeInTheDocument();

    // Fast-forward time to check timeout
    act(() => {
        vi.advanceTimersByTime(5100);
    });
    expect(screen.getByText('Silent')).toBeInTheDocument();

    vi.useRealTimers();
  });

  it('calls restartAudio when reset button is clicked', async () => {
    vi.useFakeTimers();
    const MockSocket = vi.fn().mockImplementation(function(this: any) {
      this.close = vi.fn();
    });
    vi.stubGlobal('WebSocket', MockSocket);

    render(<NowPlaying />);

    const resetButton = screen.getByTitle('Restart audio capture');
    expect(resetButton).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(resetButton);
    });

    expect(mockRestartAudio).toHaveBeenCalled();

    vi.useRealTimers();
  });
});
