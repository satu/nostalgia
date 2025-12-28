# Design Document: Nostalgia

## 1. System Architecture
Nostalgia follows a client-server architecture where the Raspberry Pi acts as the central hub (Server) and the Nexus 7 tablet acts as the controller (Client).

### 1.1 High-Level Component Diagram
```
[ Mixer ] --(3.5mm)--> [ USB Audio Interface ]
                             |
                      [ Raspberry Pi ]
                             |
        +--------------------+---------------------+
        |                    |                     |
 [ Web Server ]      [ Audio Streamer ]    [ Cast Controller ]
 (FastAPI/Uvicorn)    (FFmpeg/Icecast)      (PyChromecast)
        |                    |                     |
        |             [ Local Network ]            |
        |                    |                     |
 [ Tablet App ]       [ Cast Devices ]      <------+
 (React Frontend)     (Google Home/CC)
```

## 2. Tech Stack
- **Backend**: Python 3.11+
    - **Web Framework**: FastAPI (high performance, easy async support).
    - **Cast Integration**: `pychromecast`.
    - **Audio Processing**: `ffmpeg` for capturing from ALSA/PulseAudio and streaming as an HTTP chunked response or OGG/MP3 stream.
    - **Discovery**: `zeroconf` (via pychromecast).
- **Frontend**: React (TypeScript)
    - **Styling**: Tailwind CSS + Material UI (for a polished look on the Nexus 7).
    - **State Management**: React Query (for device discovery polling).
- **Deployment**:
    - **Service Manager**: `systemd` to ensure the app starts on boot and restarts on failure.
    - **Reverse Proxy**: Nginx (optional, depending on complexity).

## 3. Subsystems

### 3.1 Audio Capture & Streaming
The backend will use `ffmpeg` to capture audio from the USB interface (e.g., `hw:1,0`). 
- **Format**: PCM/WAV (low latency) or MP3 (better compatibility).
- **Mechanism**: An HTTP endpoint `/stream.mp3` will spawn an ffmpeg process that pipes its output directly to the HTTP response.

### 3.2 Cast Controller
Responsible for:
- Scanning the network for `Cast` devices.
- Maintaining status of connected devices.
- Commanding a device/group to play the `/stream.mp3` URL.
- Synchronizing volume and play/stop commands.

### 3.3 Frontend (Tablet UI)
Optimized for 1280x800 resolution (Nexus 7).
- **Kiosk Mode**: Web app will be added to the home screen or opened in a dedicated kiosk browser.
- **Main View**:
    - Toggle switch for "Master Power" (start/stop streaming).
    - Grid/List of discovered speakers with multi-select capability.
    - Status banner showing what is currently being played.

## 4. API Definition (Internal)

### 4.1 REST Endpoints
- `GET /api/devices`: Returns a list of discovered Cast devices/groups.
- `POST /api/cast/start`: Starts casting to a list of device IDs.
    - Body: `{ "device_ids": ["id1", "id2"], "volume": 50 }`
- `POST /api/cast/stop`: Stops all active casting sessions.
- `GET /stream.mp3`: The actual audio stream.

## 5. Deployment Details
The application will be deployed to `/home/dariofreni/nostalgia` on the Raspberry Pi.
A `systemd` unit file `nostalgia.service` will be created to manage the process.

## 6. Security Considerations
- The app is restricted to the local network. 
- No authentication is required for the initial MVP, as it's a physical device-integrated system.
