from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
import logging
import socket

from cast_manager import cast_manager
from broadcaster import broadcaster
from vu_meter import vu_meter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start Cast Discovery and ensure broadcaster state
    cast_manager.start_discovery()
    # Auto-start broadcaster for always-on recording (VU Meter)
    await broadcaster.start() 
    
    # Start VU Meter (Passive)
    await vu_meter.start()
    
    yield
    # Shutdown logic
    await broadcaster.stop()
    await vu_meter.stop()

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
    banner_url = f"http://{ip}/banner.jpg"
    success = cast_manager.play_media(
        req.device_id, 
        url, 
        title="Nostalgia", 
        thumb=banner_url
    )
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


@app.post("/api/audio/restart")
async def restart_audio():
    """Restart the audio capture pipeline, re-detecting the audio device."""
    try:
        await broadcaster.restart()
        return {"status": "restarted"}
    except Exception as e:
        logger.error(f"Failed to restart audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart audio: {e}")


@app.get("/stream.mp3")
async def stream_audio(request: Request):
    return StreamingResponse(broadcaster.stream_generator(request), media_type="audio/mpeg")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await vu_meter.connect(websocket)
    try:
        while True:
            # Keep connection open, wait for client close
            await websocket.receive_text()
    except Exception:
        vu_meter.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
