# Nostalgia - Project Context for Claude

## Project Overview

**Nostalgia** is a web application that bridges vintage audio equipment (vinyl players, tape decks, radios) with modern Google Cast speakers. It captures analog audio from a mixer connected to a Raspberry Pi and streams it wirelessly to Chromecast/Sonos/Google Home devices.

## Technology Stack

### Backend
- **Python 3.11+** with FastAPI (async-first web framework)
- **pychromecast** for Google Cast device discovery and control
- **FFmpeg** for audio capture (ALSA) and MP3 encoding
- **WebSockets** for real-time VU meter data streaming
- **pytest** for testing

### Frontend
- **React 19** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling (dark theme, green accent #17cf54)
- **Vitest** + React Testing Library for tests

### Deployment
- **Nginx** reverse proxy (routes API, WebSocket, and stream to backend)
- **Systemd** service management on Raspberry Pi
- **deploy.sh** for automated SSH-based deployment

## Architecture

```
[Vintage Audio Source] → [USB Audio Interface (Sonos Line-In Adapter)]
    ↓
[Raspberry Pi 4 - Server]
    ├── FastAPI Backend (Port 8000)
    │   ├── Cast Manager (pychromecast)
    │   ├── Audio Broadcaster (FFmpeg pipeline)
    │   └── VU Meter (WebSocket)
    ├── Nginx (Port 80)
    └── Audio Capture (ALSA → FFmpeg → MP3)
         ↓
    [Tablet UI - Nexus 7] ←→ [Google Cast Devices]
```

## Project Structure

```
nostalgia/
├── frontend/                    # React + TypeScript app
│   ├── src/
│   │   ├── App.tsx             # Main app (device polling)
│   │   ├── api.ts              # REST + WebSocket client
│   │   ├── types/index.ts      # TypeScript interfaces
│   │   └── components/
│   │       ├── Header.tsx      # App header with banner
│   │       ├── NowPlaying.tsx  # VU meter + live indicator
│   │       ├── DeviceList.tsx  # Cast device list
│   │       ├── DeviceItem.tsx  # Device toggle + volume
│   │       └── StopButton.tsx  # Stop all casting
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/                     # Python FastAPI server
│   ├── main.py                 # FastAPI app + endpoints
│   ├── cast_manager.py         # Cast device management
│   ├── broadcaster.py          # FFmpeg audio pipeline
│   ├── vu_meter.py             # VU meter calculations
│   ├── nostalgia.service       # Systemd unit file
│   ├── nostalgia.nginx         # Nginx config
│   └── tests/                  # pytest tests
│
├── deploy.sh                   # Deployment script
├── README.md                   # Quick start guide
├── DESIGN.md                   # Technical design doc
└── PRD.md                      # Product requirements
```

## Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/devices` | List discovered Cast devices |
| POST | `/api/cast/start` | Start casting to a device |
| POST | `/api/cast/stop` | Stop casting from a device |
| POST | `/api/cast/volume` | Set device volume (0.0-1.0) |
| GET | `/stream.mp3` | Audio stream (HTTP/MP3) |
| WS | `/ws` | VU meter data stream |

## How It Works

1. **Startup:** Systemd launches backend → Cast discovery + audio capture begin
2. **Audio Pipeline:** ALSA capture → FFmpeg (PCM) → VU meter → FFmpeg (MP3) → `/stream.mp3`
3. **Frontend:** Polls `/api/devices` every 5s, connects to `/ws` for real-time VU data
4. **Casting:** User toggles device → POST `/api/cast/start` → device streams `/stream.mp3`

## Development Commands

### Frontend
```bash
cd frontend
npm install
npm run dev          # Development server
npm run build        # Production build
npm run test         # Run tests
npm run coverage     # Test coverage (80% required)
```

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload    # Development server
pytest                       # Run tests
```

### Deployment
```bash
./deploy.sh          # Build frontend + deploy to Pi via SSH
```

## Important Notes

- Audio device is configured in `broadcaster.py` (default: `plug:dsnoop:1`)
- VU meter threshold for "Live" indicator: -75dB (`NowPlaying.tsx`)
- Device polling interval: 5 seconds (`App.tsx`)
- Test coverage requirement: 80% (frontend)
