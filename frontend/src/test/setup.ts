import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock WebSocket
class MockWebSocket {
  onopen: (() => void) | null = null;
  onmessage: ((event: any) => void) | null = null;
  onclose: (() => void) | null = null;

  constructor(_url: string) {
    setTimeout(() => this.onopen?.(), 10);
  }

  send(_data: string) {}

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
