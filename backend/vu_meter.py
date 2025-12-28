import asyncio
import subprocess
import shlex
import logging
import math
import struct
from typing import Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class VUMeter:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.process = None
        self.is_running = False
        self._task = None

    def calculate_rms(self, data):
        """Calculate RMS for S16_LE PCM data manually."""
        # Each sample is 2 bytes
        count = len(data) // 2
        if count == 0:
            return 0
        # Unpack Little Endian Signed Short
        try:
            samples = struct.unpack(f"<{count}h", data)
            sum_sq = sum(float(s) * s for s in samples)
            return math.sqrt(sum_sq / count)
        except Exception:
            return 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        if not self.is_running:
            await self.start()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def start(self):
        # No internal capture process needed
        self.is_running = True
        logger.info("VUMeter started (passive mode).")

    async def stop(self):
        self.is_running = False
        logger.info("VUMeter stopped.")

    async def process_pcm(self, data):
        """Process incoming PCM data chunk."""
        if not self.is_running or not self.active_connections:
            return

        try:
            rms_stereo = self.calculate_rms(data)
            
            # Max value for 16-bit is 32768
            db = 20 * math.log10(rms_stereo / 32768.0) if rms_stereo > 0 else -96.0
            
            # Map dB to percentage 0-100
            percentage = max(0, min(100, (db + 60) / 60 * 100))
            
            message = {
                "l": percentage,
                "r": percentage,
                "db": round(db, 1)
            }
            
            # Broadcast
            for connection in list(self.active_connections):
                try:
                    await connection.send_json(message)
                except Exception:
                    self.active_connections.remove(connection)
                
        except Exception:
            pass

    # async def _meter_loop(self): ... REMOVED

# Global instance
vu_meter = VUMeter()
