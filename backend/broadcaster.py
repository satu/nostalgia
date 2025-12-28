import asyncio
import subprocess
import shlex
import logging
from typing import Set
from vu_meter import vu_meter

logger = logging.getLogger(__name__)

class AudioBroadcaster:
    def __init__(self):
        self.clients: Set[asyncio.Queue] = set()
        self.capture_process = None
        self.encode_process = None
        self.is_running = False
        self._processing_task = None
        self._broadcast_task = None

    async def start(self):
        if self.is_running:
            return

        logger.info("Starting AudioBroadcaster Pipeline...")
        
        # 1. Capture Process: ALSA -> PCM (S16LE, 44.1kHz, Stereo)
        # Using ffmpeg for capture as it handles format conversion reliably
        capture_cmd = "ffmpeg -f alsa -i plug:dsnoop:1 -ac 2 -ar 44100 -f s16le pipe:1"
        
        # 2. Encode Process: PCM -> MP3
        # Read from pipe:0 (stdin)
        encode_cmd = "ffmpeg -f s16le -ar 44100 -ac 2 -i pipe:0 -acodec libmp3lame -ab 192k -f mp3 pipe:1"

        try:
            self.capture_process = subprocess.Popen(
                shlex.split(capture_cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            
            self.encode_process = subprocess.Popen(
                shlex.split(encode_cmd),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            
            self.is_running = True
            self._processing_task = asyncio.create_task(self._pipeline_loop())
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())
            
        except Exception as e:
            logger.error(f"Failed to start pipeline: {e}")
            await self.stop()

    async def stop(self):
        self.is_running = False
        
        if self.capture_process:
            self.capture_process.terminate()
            self.capture_process = None
            
        if self.encode_process:
            self.encode_process.terminate()
            self.encode_process = None
            
        if self._processing_task:
            self._processing_task.cancel()
            try: await self._processing_task
            except: pass
            
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try: await self._broadcast_task
            except: pass
            
        logger.info("AudioBroadcaster stopped.")

    async def _pipeline_loop(self):
        """Reads PCM, updates VU Meter, writes to Encoder."""
        loop = asyncio.get_event_loop()
        chunk_size = 4096 # ~23ms of audio at 44.1kHz
        
        while self.is_running and self.capture_process and self.encode_process:
            try:
                # Read PCM from capture
                pcm_data = await loop.run_in_executor(None, self.capture_process.stdout.read, chunk_size)
                
                if not pcm_data:
                    break
                
                # Update VU Meter
                await vu_meter.process_pcm(pcm_data)
                
                # Write to Encoder
                try:
                    await loop.run_in_executor(None, self.encode_process.stdin.write, pcm_data)
                    await loop.run_in_executor(None, self.encode_process.stdin.flush)
                except (BrokenPipeError, OSError):
                    break
                
            except Exception as e:
                logger.error(f"Pipeline error: {e}")
                break

    async def _broadcast_loop(self):
        """Reads MP3 from Encoder, broadcasts to clients."""
        loop = asyncio.get_event_loop()
        chunk_size = 4096
        
        while self.is_running and self.encode_process:
            try:
                mp3_data = await loop.run_in_executor(None, self.encode_process.stdout.read, chunk_size)
                
                if not mp3_data:
                    break

                # Broadcast
                for queue in list(self.clients):
                    if not queue.full():
                        queue.put_nowait(mp3_data)
                        
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                break

    async def stream_generator(self, request):
        queue = asyncio.Queue(maxsize=100)
        self.clients.add(queue)
        
        if not self.is_running:
            await self.start()

        try:
            while True:
                data = await queue.get()
                yield data
                if await request.is_disconnected():
                    break
        finally:
            self.clients.remove(queue)

# Global instance
broadcaster = AudioBroadcaster()
