import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from broadcaster import AudioBroadcaster

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
    assert bc.process == mock_process
    
    await bc.stop()
    assert bc.is_running == False
    assert bc.process == None
    mock_process.terminate.assert_called_once()