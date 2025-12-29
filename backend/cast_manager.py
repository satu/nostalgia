import pychromecast
from pychromecast.controllers.multizone import MultizoneController
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
            
            if chromecast.cast_type == 'group':
                logger.info(f"Initializing MultizoneController for group {chromecast.name}")
                mz = MultizoneController(chromecast.uuid)
                chromecast.register_handler(mz)
                chromecast.mz = mz # Attach to object
                
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
                    if mc_status.content_id.endswith("/stream.mp3"):
                        if mc_status.player_state == "IDLE":
                            # If IDLE, check reason. If cancelled/finished/error, it's inactive.
                            # If reason is None (loading) or INTERRUPTED, we consider it active (or transient)
                            if mc_status.idle_reason in ["CANCELLED", "FINISHED", "ERROR"]:
                                is_active = False
                            else:
                                is_active = True
                        else:
                            # PLAYING, BUFFERING, PAUSED
                            is_active = True
                    
                    # Debug logging for active transitions or specific devices
                    if cc.name == "Sea room display" or is_active:
                        logger.info(f"Device {cc.name}: State={mc_status.player_state}, Content={mc_status.content_id}, IdleReason={mc_status.idle_reason}, Active={is_active}")

                volume = cc.status.volume_level if cc.status else 0
                
                # Get group members if available
                members = []
                if hasattr(cc, 'mz'):
                    members = cc.mz.members

                device_list.append({
                    "id": str(cc.uuid),
                    "name": cc.name,
                    "model": cc.model_name,
                    "type": cc.cast_type,
                    "volume": volume,
                    "is_active": is_active,
                    "members": members
                })
            except Exception as e:
                logger.error(f"Error reading status for {cc.name}: {e}")
                
        return device_list

    def get_device(self, device_id: str) -> Optional[pychromecast.Chromecast]:
        return self.casts.get(device_id)

    def play_media(self, device_id: str, media_url: str, content_type: str = "audio/mpeg", title: str = None, thumb: str = None):
        cast = self.get_device(device_id)
        if cast:
            try:
                # Use a short timeout for connection check
                cast.wait(timeout=2.0)
                mc = cast.media_controller
                mc.play_media(media_url, content_type, title=title, thumb=thumb)
                # Do NOT block until active. Let the status polling handle the state update.
                # mc.block_until_active() 
                logger.info(f"Sent play command to {cast.name}")
                return True
            except Exception as e:
                logger.error(f"Failed to play media on {cast.name}: {e}")
        return False

    def stop_media(self, device_id: str):
        cast = self.get_device(device_id)
        if cast:
            try:
                cast.wait(timeout=2.0)
                cast.media_controller.stop()
                logger.info(f"Sent stop command to {cast.name}")
                return True
            except Exception as e:
                logger.error(f"Failed to stop media on {cast.name}: {e}")
        return False

    def set_volume(self, device_id: str, volume: float):
        cast = self.get_device(device_id)
        if cast:
            try:
                cast.wait(timeout=1.0)
                cast.set_volume(volume)
                logger.info(f"Set volume on {cast.name} to {volume}")
                return True
            except Exception as e:
                logger.error(f"Failed to set volume on {cast.name}: {e}")
        return False

# Global instance
cast_manager = CastManager()
