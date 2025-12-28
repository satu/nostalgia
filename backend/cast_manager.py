import pychromecast
import threading
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CastManager:
    def __init__(self):
        self.casts: Dict[str, pychromecast.Chromecast] = {}
        self.browser = None

    def start_discovery(self):
        logger.info("Starting Cast discovery...")
        # non-blocking discovery
        pychromecast.get_chromecasts(blocking=False, callback=self._on_cast_discovered)

    def _on_cast_discovered(self, chromecast: pychromecast.Chromecast):
        logger.info(f"Discovered cast device: {chromecast.name} ({chromecast.uuid})")
        # We need to connect to the device to get status/control it
        try:
            chromecast.wait()
            self.casts[str(chromecast.uuid)] = chromecast
        except Exception as e:
            logger.error(f"Failed to connect to {chromecast.name}: {e}")

    def get_devices(self) -> List[Dict]:
        device_list = []
        for uuid, cc in self.casts.items():
            # Basic status check
            try:
                status = cc.status
                volume = cc.status.volume_level if cc.status else 0
                is_active = False # You might determine this if it's playing OUR stream
                
                # Check if it's playing our app or stream? 
                # For now just return basic info
                device_list.append({
                    "id": str(cc.uuid),
                    "name": cc.device.friendly_name,
                    "model": cc.model_name,
                    "type": cc.cast_type,
                    "volume": volume,
                    "is_active": is_active # Placeholder
                })
            except Exception as e:
                logger.error(f"Error reading status for {cc.name}: {e}")
                
        return device_list

    def get_device(self, device_id: str) -> Optional[pychromecast.Chromecast]:
        return self.casts.get(device_id)

# Global instance
cast_manager = CastManager()
