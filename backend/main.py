from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
import subprocess
import shlex
import logging
import socket

from cast_manager import cast_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start Cast Discovery
    cast_manager.start_discovery()
    yield
    # Shutdown logic if needed

app = FastAPI(title="Nostalgia API", lifespan=lifespan)

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class CastRequest(BaseModel):
    device_id: str

class VolumeRequest(BaseModel):
    device_id: str
    volume: float

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.get("/")
async def root():
    return {"message": "Nostalgia API is running"}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/api/devices")
async def get_devices():
    """List all discovered Cast devices."""
    return cast_manager.get_devices()

@app.post("/api/cast/start")
async def start_cast(req: CastRequest):
    ip = get_local_ip()
    url = f"http://{ip}:8000/stream.mp3"
    success = cast_manager.play_media(req.device_id, url)
    if success:
        return {"status": "started", "device_id": req.device_id, "url": url}
    raise HTTPException(status_code=404, detail="Device not found or failed to start")

@app.post("/api/cast/stop")
async def stop_cast(req: CastRequest):
    success = cast_manager.stop_media(req.device_id)
    if success:
         return {"status": "stopped", "device_id": req.device_id}
    raise HTTPException(status_code=404, detail="Device not found or failed to stop")

@app.post("/api/cast/volume")
async def set_volume(req: VolumeRequest):
    success = cast_manager.set_volume(req.device_id, req.volume)
    if success:
        return {"status": "volume_set", "device_id": req.device_id, "volume": req.volume}
    raise HTTPException(status_code=404, detail="Device not found or failed to set volume")

@app.get("/stream.mp3")
async def stream_audio():
    # ffmpeg command to capture from ALSA and encode to MP3
    # -f alsa: input format
    # -i hw:1,0: input device (Card 1, Device 0 - Sonos Adapter)
    # -acodec libmp3lame: audio codec
    # -ab 192k: bitrate
    # -f mp3: output format
    # pipe:1: output to stdout
    cmd = "ffmpeg -f alsa -i hw:1,0 -acodec libmp3lame -ab 192k -f mp3 pipe:1"
    
    # Run ffmpeg as a subprocess
    process = subprocess.Popen(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL 
    )

    def iterfile():
        try:
            while True:
                data = process.stdout.read(4096)
                if not data:
                    break
                yield data
        finally:
            process.terminate()

    return StreamingResponse(iterfile(), media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)