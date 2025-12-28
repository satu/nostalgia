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
        if self.is_running:
            return

        logger.info("Starting VUMeter capture...")
        # Capture 8000Hz Stereo PCM
        cmd = "arecord -D plug:dsnoop:1 -f S16_LE -r 8000 -c 2 -t raw"
        
        try:
            self.process = subprocess.Popen(
                shlex.split(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            self.is_running = True
            self._task = asyncio.create_task(self._meter_loop())
        except Exception as e:
            logger.error(f"Failed to start VUMeter: {e}")
            self.is_running = False

    async def stop(self):
        self.is_running = False
        if self.process:
            self.process.terminate()
            self.process = None
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("VUMeter stopped.")

    async def _meter_loop(self):
        loop = asyncio.get_event_loop()
        # 30fps update
        chunk_size = 1024 
        
        while self.is_running and self.process:
            data = await loop.run_in_executor(None, self.process.stdout.read, chunk_size)
            
            if not data:
                break

            if not self.active_connections:
                await asyncio.sleep(0.1)
                continue

            try:
                rms_stereo = self.calculate_rms(data)
                
                # Max value for 16-bit is 32768
                db = 20 * math.log10(rms_stereo / 32768.0) if rms_stereo > 0 else -96.0
                
                # Map dB to percentage 0-100
                percentage = max(0, min(100, (db + 60) / 60 * 100))
                
                # Log occasionally to debug
                # logger.info(f"RMS: {rms_stereo:.2f}, dB: {db:.2f}, %: {percentage:.2f}")

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
                    
            except Exception as e:
                # logger.error(f"Meter loop error: {e}")
                pass

# Global instance
vu_meter = VUMeter()
