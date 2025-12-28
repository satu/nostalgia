# Product Requirement Document: Nostalgia

## 1. Executive Summary
**Nostalgia** is a web application running on a Raspberry Pi designed to modernize vintage audio equipment by enabling it to stream audio to Google Cast (Chromecast/Google Home) devices. The system captures audio from a mixer (connected to the vintage gear) via a USB audio adapter on the Raspberry Pi and casts this audio to selected speakers on the local network. A dedicated tablet (Nexus 7) acts as the always-on controller for the system.

## 2. Problem Statement
Vintage audio equipment provides high-quality or sentimental audio experiences but lacks modern connectivity. Users want to listen to their vinyls, tapes, or radio on their modern multi-room speaker systems (Sonos/Google Home) without running long cables.

## 3. Solution Overview
- **Hardware Setup**:
    - **Source**: Vintage Audio Equipment connected to a Mixer.
    - **Capture**: Raspberry Pi with a USB Audio Input (Sonos line-in adapter or similar) receiving audio from the Mixer's 3.5mm output.
    - **Controller**: Nexus 7 tablet running a web browser in kiosk mode, always pointing to the Nostalgia web app.
    - **Output**: Google Cast-enabled speakers (Google Home, Chromecast Audio, etc.).
- **Software**: A web application hosted on the Raspberry Pi that manages audio capture, device discovery, and streaming.

## 4. Key Features

### 4.1 Audio Streaming (Core)
- **Capture**: reliable low-latency audio capture from the default input device on the Raspberry Pi.
- **Transcoding**: Real-time encoding of audio (e.g., to MP3/WAV/FLAC) suitable for casting.
- **Streaming**: Serve the captured audio stream over HTTP/local network for Cast devices to consume.

### 4.2 Device Discovery & Control
- **Discovery**: Automatically discover all Google Cast devices and groups on the local network (mDNS/Cast protocol).
- **Selection**: User can select one or multiple devices/groups to start casting to.
- **Grouping/Sync**:
    - Support connecting to existing Cast Groups.
    - *Nice-to-have*: Ad-hoc grouping – selecting multiple individual speakers and having them play synchronously (similar to Google Home app).
- **Volume Control**: Basic volume control for the stream (optional, might rely on individual speaker volume).

### 4.3 User Interface (Frontend)
- **Target Device**: Optimized for Nexus 7 (7-inch touch screen).
- **Design**:
    - Simple, "Now Playing" style interface.
    - List of available speakers/groups.
    - Status indicator (Idle, Casting to [Device Name]).
    - "Stop Casting" button.
- **Experience**: The app should feel native. Auto-refresh device list.

### 4.4 System & Deployment
- **Auto-Start**: The web service must start automatically on boot (Systemd/Tmux).
- **Stability**: Service should automatically recover from crashes.
- **Local Network Only**: No external internet access required for operation (except for the Cast devices themselves if they need to fetch the stream).

## 5. Technical Requirements
- **Platform**: Raspberry Pi (Linux).
- **Language/Stack**: Python (likely) or Node.js for backend; HTML/CSS/JS for frontend.
    - *Rationale*: Python has excellent libraries for `pychromecast` and audio handling (`ffmpeg` wrappers).
- **Audio Input**: 3.5mm Line-In (USB Adapter).
- **Network**: Local LAN (WiFi/Ethernet).

## 6. Future Considerations / Out of Scope (MVP)
- Two-way communication (controlling the vintage gear) is out of scope.
- Spotify/AirPlay support (focus is strictly casting *from* line-in).
