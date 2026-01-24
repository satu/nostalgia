import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from broadcaster import AudioBroadcaster, detect_audio_device

@pytest.mark.asyncio
async def test_audio_broadcaster_client_management():
    bc = AudioBroadcaster()
    mock_request = AsyncMock()
    mock_request.is_disconnected.return_value = False
    
    # Mock start to do nothing
    bc.start = AsyncMock()
    
    gen = bc.stream_generator(mock_request)
    
    # Start generator task
    async def consume():
        async for _ in gen:
            break

    task = asyncio.create_task(consume())
    
    # Give it time to register client
    await asyncio.sleep(0.05)
    assert len(bc.clients) == 1
    
    # Send data to unblock queue.get()
    queue = list(bc.clients)[0]
    await queue.put(b"data")
    
    # Wait for task to finish
    await task
    
    # For async generators, finally block runs on aclose() if partially consumed
    await gen.aclose()
    
    # Client should be removed in finally block
    assert len(bc.clients) == 0

@pytest.mark.asyncio
@patch('broadcaster.subprocess.Popen')
async def test_audio_broadcaster_start_stop(mock_popen):
    bc = AudioBroadcaster()
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    
    await bc.start()
    assert bc.is_running == True
    assert bc.capture_process == mock_process
    assert bc.encode_process == mock_process
    
    await bc.stop()
    assert bc.is_running == False
    assert bc.capture_process == None
    assert bc.encode_process == None
    assert mock_process.terminate.call_count == 2


@patch('broadcaster.subprocess.run')
def test_detect_audio_device_finds_sonos(mock_run):
    """Test that detect_audio_device correctly parses arecord output."""
    mock_run.return_value = MagicMock(
        stdout="""**** List of CAPTURE Hardware Devices ****
card 0 [Headphones     ]: bcm2835_headpho - bcm2835 Headphones
card 2: Adapter [Sonos USB-C Line-in Adapter], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0"""
    )

    device = detect_audio_device()
    assert device == "plug:dsnoop:2"


@patch('broadcaster.subprocess.run')
def test_detect_audio_device_not_found(mock_run):
    """Test that detect_audio_device returns None when device not found."""
    mock_run.return_value = MagicMock(
        stdout="""**** List of CAPTURE Hardware Devices ****
card 0 [Headphones     ]: bcm2835_headpho - bcm2835 Headphones"""
    )

    device = detect_audio_device()
    assert device is None


@pytest.mark.asyncio
@patch('broadcaster.subprocess.Popen')
@patch('broadcaster.detect_audio_device')
async def test_audio_broadcaster_restart(mock_detect, mock_popen):
    """Test that restart stops and starts with fresh device detection."""
    bc = AudioBroadcaster()
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    mock_detect.return_value = "plug:dsnoop:3"

    # Start first time
    await bc.start()
    assert bc.is_running == True
    assert bc._audio_device == "plug:dsnoop:3"

    # Restart should re-detect
    mock_detect.return_value = "plug:dsnoop:4"
    await bc.restart()

    assert bc.is_running == True
    assert bc._audio_device == "plug:dsnoop:4"
    assert mock_detect.call_count == 2