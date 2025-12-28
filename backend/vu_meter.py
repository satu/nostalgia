import asyncio
import subprocess
import shlex
import logging
import audioop
import math
from typing import Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class VUMeter:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.process = None
        self.is_running = False
        self._task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        if not self.is_running:
            await self.start()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        if not self.active_connections:
            # Optional: Stop to save CPU if no one watching
            # await self.stop()
            pass

    async def start(self):
        if self.is_running:
            return

        logger.info("Starting VUMeter capture...")
        # Capture mono 16-bit 8000Hz PCM - lightweight
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
        # 8000Hz * 2 bytes * 2 channels = 32000 bytes/sec
        # We want updates ~30fps = ~33ms
        # 32000 * 0.033 ~= 1024 bytes (power of 2 is nice)
        chunk_size = 1024 
        
        while self.is_running and self.process:
            data = await loop.run_in_executor(None, self.process.stdout.read, chunk_size)
            
            if not data:
                break

            # Calculate RMS for Left and Right channels
            try:
                # audioop.rms calculates root mean square
                # But data is interleaved L R L R
                # We need to de-interleave to get L and R separately
                # Or just send average mono for MVP visual
                
                # De-interleaving in Python might be slow.
                # Let's try simple stereo RMS first.
                
                # S16_LE = 2 bytes width
                rms_stereo = audioop.rms(data, 2)
                
                # Convert to dB? Or just raw 0-32768
                # dB = 20 * log10(rms / 32768)
                # Avoid log(0)
                db = 20 * math.log10(rms_stereo / 32768) if rms_stereo > 0 else -96.0
                
                # Send to clients
                # Format: {"l": 0-100, "r": 0-100, "db": -20}
                # Since we have mono RMS effectively here (audioop treats stream as one), 
                # we'll send same to L/R for now unless we separate.
                
                # To separate L/R in python efficiently without numpy:
                # Iterate? Too slow.
                # Let's just stick to "Stereo Average" for the UI bars for now to keep it lightweight.
                
                # Map dB to percentage 0-100 for UI
                # Noise floor ~ -60dB, Max 0dB
                percentage = max(0, min(100, (db + 60) / 60 * 100))
                
                message = {
                    "l": percentage,
                    "r": percentage,
                    "db": round(db, 1)
                }
                
                # Broadcast
                for connection in list(self.active_connections):
                    await connection.send_json(message)
                    
            except Exception as e:
                # logger.error(f"Meter error: {e}")
                pass

# Global instance
vu_meter = VUMeter()
