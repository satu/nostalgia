# Nostalgia Project Context

## Overview
Nostalgia is a digital interface for a vinyl setup. It runs on a Raspberry Pi 4 (`nostalgia`) connected to a USB Audio Interface (Behringer U-Control UCA222).

### Components
1.  **Frontend (React + Vite + Tailwind):**
    *   Runs on a Nexus 7 tablet (via Fully Kiosk Browser).
    *   Visualizes "Now Playing" status, VU meter, and controls Google Cast devices.
    *   Served by Nginx at `/var/www/nostalgia`.
    *   Connects to backend via WebSocket (`/ws`) for VU meter data.

2.  **Backend (Python FastAPI):**
    *   Runs as a systemd service (`nostalgia.service`).
    *   **Broadcaster (`broadcaster.py`):** Captures audio from `plug:dsnoop:1` (shared ALSA device) using FFmpeg and streams it to `/stream.mp3`. Supports multiple clients via a `BroadcastStream` buffer.
    *   **VU Meter (`vu_meter.py`):** Captures audio independently via `arecord` (8000Hz), calculates RMS (manual calculation for Python 3.13 compatibility), and broadcasts DB levels via WebSocket.
    *   **Cast Manager (`cast_manager.py`):** Discovers and controls Google Cast devices (volume, playback).

## Deployment
*   **Host:** `nostalgia` (Raspberry Pi).
*   **User:** `dariofreni` / `root`.
*   **Service:** `sudo systemctl restart nostalgia`.
*   **Logs:** `sudo journalctl -u nostalgia -f`.

### Manual Deployment
```bash
# Frontend
cd frontend
npm run build
ssh nostalgia "sudo chown -R dariofreni:dariofreni /var/www/nostalgia"
rsync -avz dist/ nostalgia:/var/www/nostalgia/
ssh nostalgia "sudo chown -R www-data:www-data /var/www/nostalgia"

# Backend
rsync -avz backend/ nostalgia:~/nostalgia/
ssh nostalgia "sudo systemctl restart nostalgia"
```

## Hardware / Audio Config
*   **Audio Device:** `hw:1,0` (USB Audio Codec).
*   **ALSA Config:** Uses `dsnoop` plugin to allow multiple processes (ffmpeg + vu_meter) to read from the capture device simultaneously.
    *   Input: `plug:dsnoop:1`

## Known Issues / Quirks
*   **Python 3.13:** `audioop` module is removed. VU meter uses manual struct unpacking and math for RMS calculation.
*   **Tablet:** Nexus 7 (2013) running LineageOS + Fully Kiosk. Resolution 1920x1200.
*   **CSS:** `@import` statements must be at the very top of `index.css` to load Material Symbols correctly.

## Future Tasks
*   Increase test coverage (>80%).
*   Polish Dashboard UI (Rolling averages).
