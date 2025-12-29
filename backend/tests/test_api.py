import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add backend to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Nostalgia API is running"}

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('main.cast_manager')
def test_get_devices(mock_cm):
    mock_cm.get_devices.return_value = [{"id": "1", "name": "Speaker"}]
    response = client.get("/api/devices")
    assert response.status_code == 200
    assert response.json() == [{"id": "1", "name": "Speaker"}]

@patch('main.cast_manager')
def test_start_cast(mock_cm):
    mock_cm.play_media.return_value = True
    response = client.post("/api/cast/start", json={"device_id": "1"})
    assert response.status_code == 200
    assert response.json()["status"] == "started"
    # Verify title and thumb are passed
    args, kwargs = mock_cm.play_media.call_args
    assert kwargs["title"] == "Nostalgia"
    assert "banner.jpg" in kwargs["thumb"]

@patch('main.cast_manager')
def test_start_cast_fail(mock_cm):
    mock_cm.play_media.return_value = False
    response = client.post("/api/cast/start", json={"device_id": "bad"})
    assert response.status_code == 404

@patch('main.cast_manager')
def test_stop_cast(mock_cm):
    mock_cm.stop_media.return_value = True
    response = client.post("/api/cast/stop", json={"device_id": "1"})
    assert response.status_code == 200
    assert response.json()["status"] == "stopped"

@patch('main.cast_manager')
def test_set_volume(mock_cm):
    mock_cm.set_volume.return_value = True
    response = client.post("/api/cast/volume", json={"device_id": "1", "volume": 0.5})
    assert response.status_code == 200
    assert response.json()["status"] == "volume_set"

@patch('main.broadcaster')
def test_stream_audio(mock_bc):
    mock_bc.stream_generator.return_value = iter([b'audio_chunk'])
    response = client.get("/stream.mp3")
    assert response.status_code == 200
    assert response.content == b'audio_chunk'
