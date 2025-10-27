import logging
from protocol import ControlCommand, Packet, PacketType

logger = logging.getLogger(__name__)

class ControlCommands:
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
    
    def _send_command(self, command_json: str):
        try:
            payload = command_json.encode('utf-8')
            packet = Packet(PacketType.CONTROL_COMMAND, payload)
            self.connection_manager.send_data(packet.to_bytes())
            logger.debug(f"Sent command: {command_json}")
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
    
    def set_resolution(self, width: int, height: int):
        command = ControlCommand.set_resolution(width, height)
        self._send_command(command)
    
    def set_fps(self, fps: int):
        command = ControlCommand.set_fps(fps)
        self._send_command(command)
    
    def switch_camera(self, camera: str = "back"):
        command = ControlCommand.switch_camera(camera)
        self._send_command(command)
    
    def set_flash(self, enabled: bool):
        command = ControlCommand.set_flash(enabled)
        self._send_command(command)
    
    def set_focus(self, mode: str, distance: float = 0.0):
        command = ControlCommand.set_focus(mode, distance)
        self._send_command(command)
    
    def set_brightness(self, value: float):
        command = ControlCommand.set_brightness(value)
        self._send_command(command)

