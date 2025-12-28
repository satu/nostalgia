from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import subprocess
import shlex
import logging

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
