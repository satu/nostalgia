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
                # Check media status to determine if it's playing our stream
                mc_status = cc.media_controller.status
                is_active = False
                
                if mc_status and mc_status.content_id:
                    # check if playing our stream and in active state
                    if mc_status.content_id.endswith("/stream.mp3") and \
                       mc_status.player_state in ["PLAYING", "BUFFERING"]:
                        is_active = True

                volume = cc.status.volume_level if cc.status else 0
                
                device_list.append({
                    "id": str(cc.uuid),
                    "name": cc.name,
                    "model": cc.model_name,
                    "type": cc.cast_type,
                    "volume": volume,
                    "is_active": is_active
                })
            except Exception as e:
                logger.error(f"Error reading status for {cc.name}: {e}")
                
        return device_list

    def get_device(self, device_id: str) -> Optional[pychromecast.Chromecast]:
        return self.casts.get(device_id)

    def play_media(self, device_id: str, media_url: str, content_type: str = "audio/mpeg"):
        cast = self.get_device(device_id)
        if cast:
            try:
                cast.wait()
                mc = cast.media_controller
                mc.play_media(media_url, content_type)
                mc.block_until_active()
                logger.info(f"Started casting to {cast.name}")
                return True
            except Exception as e:
                logger.error(f"Failed to play media on {cast.name}: {e}")
        return False

    def stop_media(self, device_id: str):
        cast = self.get_device(device_id)
        if cast:
            try:
                cast.wait()
                cast.media_controller.stop()
                logger.info(f"Stopped casting on {cast.name}")
                return True
            except Exception as e:
                logger.error(f"Failed to stop media on {cast.name}: {e}")
        return False

    def set_volume(self, device_id: str, volume: float):
        cast = self.get_device(device_id)
        if cast:
            try:
                cast.wait()
                cast.set_volume(volume)
                logger.info(f"Set volume on {cast.name} to {volume}")
                return True
            except Exception as e:
                logger.error(f"Failed to set volume on {cast.name}: {e}")
        return False

# Global instance
cast_manager = CastManager()
