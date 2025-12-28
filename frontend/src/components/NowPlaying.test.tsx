import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { NowPlaying } from './NowPlaying';

// Mock the API
vi.mock('../api', () => ({
  getWebSocketUrl: vi.fn(() => 'ws://localhost/ws'),
  api: {}
}));

describe('NowPlaying', () => {
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
});
