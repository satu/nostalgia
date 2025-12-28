import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock WebSocket
class MockWebSocket {
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onmessage: ((event: any) => void) | null = null;
  onerror: (() => void) | null = null;
  readyState = 1;

  constructor(url: string) {
    setTimeout(() => this.onopen?.(), 0);
  }

  send(data: string) {}
  close() {
    this.onclose?.();
  }
}

vi.stubGlobal('WebSocket', MockWebSocket);

// Mock Audio
vi.stubGlobal('Audio', class {
  play = vi.fn().mockResolvedValue(undefined);
  pause = vi.fn();
  src = "";
});
