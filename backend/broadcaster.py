import asyncio
import subprocess
import shlex
import logging
import re
from typing import Set, Optional
from vu_meter import vu_meter

logger = logging.getLogger(__name__)

# Device name to search for in ALSA capture devices
AUDIO_DEVICE_NAME = "Sonos"


def detect_audio_device() -> Optional[str]:
    """
    Auto-detect the ALSA card ID for the audio input device.
    Parses 'arecord -l' output to find a device matching AUDIO_DEVICE_NAME.
    Returns the ALSA device string (e.g., 'plug:dsnoop:2') or None if not found.
    """
    try:
        result = subprocess.run(
            ["arecord", "-l"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Parse output like:
        # card 2: Adapter [Sonos USB-C Line-in Adapter], device 0: USB Audio [USB Audio]
        for line in result.stdout.splitlines():
            if AUDIO_DEVICE_NAME.lower() in line.lower():
                match = re.match(r"card (\d+):", line)
                if match:
                    card_id = match.group(1)
                    device = f"plug:dsnoop:{card_id}"
                    logger.info(f"Auto-detected audio device: {device} ({line.strip()})")
                    return device

        logger.warning(f"Could not find audio device matching '{AUDIO_DEVICE_NAME}' in arecord -l output")
        return None

    except subprocess.TimeoutExpired:
        logger.error("Timeout running arecord -l")
        return None
    except FileNotFoundError:
        logger.error("arecord command not found")
        return None
    except Exception as e:
        logger.error(f"Error detecting audio device: {e}")
        return None


class AudioBroadcaster:
    def __init__(self):
        self.clients: Set[asyncio.Queue] = set()
        self.capture_process = None
        self.encode_process = None
        self.is_running = False
        self._processing_task = None
        self._broadcast_task = None
        self._audio_device: Optional[str] = None

    async def start(self):
        if self.is_running:
            return

        logger.info("Starting AudioBroadcaster Pipeline...")

        # Auto-detect audio device if not already set
        if not self._audio_device:
            self._audio_device = detect_audio_device()

        if not self._audio_device:
            logger.error("No audio device detected, using fallback 'plug:dsnoop:2'")
            self._audio_device = "plug:dsnoop:2"

        # 1. Capture Process: ALSA -> PCM (S16LE, 44.1kHz, Stereo)
        # Using ffmpeg for capture as it handles format conversion reliably
        capture_cmd = f"ffmpeg -f alsa -i {self._audio_device} -ac 2 -ar 44100 -f s16le pipe:1"
        
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

    async def restart(self):
        """Restart the audio pipeline, re-detecting the audio device."""
        logger.info("Restarting AudioBroadcaster Pipeline...")
        await self.stop()
        # Clear the cached device so it re-detects on start
        self._audio_device = None
        await self.start()
        logger.info("AudioBroadcaster Pipeline restarted.")

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
