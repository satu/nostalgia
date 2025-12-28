import asyncio
import subprocess
import shlex
import logging
from typing import Set

logger = logging.getLogger(__name__)

class AudioBroadcaster:
    def __init__(self):
        self.clients: Set[asyncio.Queue] = set()
        self.process = None
        self.is_running = False
        self._task = None

    async def start(self):
        if self.is_running:
            return

        logger.info("Starting AudioBroadcaster...")
        # Use plughw:1,0 for better compatibility if hw:1,0 is picky
        cmd = "ffmpeg -f alsa -i hw:1,0 -acodec libmp3lame -ab 192k -f mp3 pipe:1"
        
        try:
            self.process = subprocess.Popen(
                shlex.split(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE # Capture stderr for debugging
            )
            self.is_running = True
            self._task = asyncio.create_task(self._broadcast_loop())
        except Exception as e:
            logger.error(f"Failed to start FFmpeg: {e}")
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
        logger.info("AudioBroadcaster stopped.")

    async def _broadcast_loop(self):
        loop = asyncio.get_event_loop()
        buffer_size = 4096
        
        while self.is_running and self.process:
            # Run blocking read in executor
            data = await loop.run_in_executor(None, self.process.stdout.read, buffer_size)
            
            if not data:
                # Check for errors
                return_code = self.process.poll()
                if return_code is not None:
                    stderr = await loop.run_in_executor(None, self.process.stderr.read)
                    if stderr:
                        logger.error(f"FFmpeg error: {stderr.decode('utf-8', errors='ignore')}")
                    break
                continue

            # Broadcast to all connected clients
            # Iterate over a copy because clients might disconnect during iteration
            for queue in list(self.clients):
                try:
                    # Put data in queue, non-blocking if possible or with timeout
                    # If queue is full, we might drop frames or block. 
                    # For audio streaming, dropping is better than lagging infinitely.
                    if not queue.full():
                        queue.put_nowait(data)
                except Exception as e:
                    logger.warning(f"Error sending to client: {e}")

    async def stream_generator(self, request):
        queue = asyncio.Queue(maxsize=100) # Buffer of ~400KB
        self.clients.add(queue)
        
        # Ensure broadcaster is running
        if not self.is_running:
            await self.start()

        try:
            while True:
                # Wait for data
                data = await queue.get()
                yield data
                
                # Detect client disconnect via request state (FastAPI specific)
                if await request.is_disconnected():
                    break
        except Exception as e:
             # logger.debug(f"Client disconnected: {e}")
             pass
        finally:
            self.clients.remove(queue)
            # Optional: Stop broadcaster if no clients left? 
            # For now, keep it running to keep device "hot" and ready, or to avoid startup lag.
            if not self.clients:
                 logger.info("No more clients, keeping stream alive for now...")

# Global instance
broadcaster = AudioBroadcaster()
