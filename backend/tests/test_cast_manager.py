import pytest
from unittest.mock import MagicMock, patch
from cast_manager import CastManager

@pytest.fixture
def manager():
    return CastManager()

def test_get_devices_empty(manager):
    assert manager.get_devices() == []

@patch('cast_manager.pychromecast.discovery.discover_chromecasts')
@patch('cast_manager.pychromecast.get_chromecasts')
def test_discovery_callback(mock_get, mock_discover, manager):
    # Mock a found device
    mock_cast = MagicMock()
    mock_cast.uuid = "uuid-1"
    mock_cast.name = "Test Cast"
    mock_cast.model_name = "Chromecast"
    mock_cast.cast_type = "audio"
    mock_cast.status = MagicMock()
    mock_cast.status.volume_level = 0.5
    
    # Mock media status
    mock_mc_status = MagicMock()
    mock_mc_status.content_id = "http://server/stream.mp3"
    mock_mc_status.player_state = "PLAYING"
    mock_cast.media_controller.status = mock_mc_status

    # Simulate discovery callback
    manager._on_cast_discovered(mock_cast)
    
    devices = manager.get_devices()
    assert len(devices) == 1
    assert devices[0]["id"] == "uuid-1"
    assert devices[0]["name"] == "Test Cast"
    assert devices[0]["volume"] == 0.5
    assert devices[0]["is_active"] == True

def test_play_media_success(manager):
    mock_cast = MagicMock()
    manager.casts["uuid-1"] = mock_cast
    assert manager.play_media("uuid-1", "http://url") == True
    mock_cast.media_controller.play_media.assert_called_once()

def test_stop_media_success(manager):
    mock_cast = MagicMock()
    manager.casts["uuid-1"] = mock_cast
    assert manager.stop_media("uuid-1") == True
    mock_cast.media_controller.stop.assert_called_once()

def test_set_volume_success(manager):
    mock_cast = MagicMock()
    manager.casts["uuid-1"] = mock_cast
    assert manager.set_volume("uuid-1", 0.7) == True
    mock_cast.set_volume.assert_called_with(0.7)

def test_play_media_no_device(manager):
    assert manager.play_media("non-existent", "http://url") == False

def test_set_volume_no_device(manager):
    assert manager.set_volume("non-existent", 0.5) == False