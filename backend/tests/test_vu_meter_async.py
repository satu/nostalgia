import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from vu_meter import VUMeter

@pytest.mark.asyncio
@patch('vu_meter.subprocess.Popen')
async def test_vu_meter_start_stop(mock_popen):
    meter = VUMeter()
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    
    await meter.start()
    assert meter.is_running == True
    assert meter.process == mock_process
    
    await meter.stop()
    assert meter.is_running == False
    assert meter.process == None
    mock_process.terminate.assert_called_once()

@pytest.mark.asyncio
async def test_vu_meter_connections():
    meter = VUMeter()
    mock_ws = AsyncMock()
    
    await meter.connect(mock_ws)
    assert mock_ws in meter.active_connections
    mock_ws.accept.assert_called_once()
    
    meter.disconnect(mock_ws)
    assert mock_ws not in meter.active_connections
