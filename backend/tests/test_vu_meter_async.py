import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from vu_meter import VUMeter

@pytest.mark.asyncio
async def test_vu_meter_connections():
    meter = VUMeter()
    mock_ws = AsyncMock()
    
    await meter.connect(mock_ws)
    assert mock_ws in meter.active_connections
    mock_ws.accept.assert_called_once()
    
    meter.disconnect(mock_ws)
    assert mock_ws not in meter.active_connections