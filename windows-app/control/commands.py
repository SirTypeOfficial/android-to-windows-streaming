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
    
    def set_zoom(self, ratio: float):
        command = ControlCommand.set_zoom(ratio)
        self._send_command(command)
    
    def set_manual_mode(self, enabled: bool):
        command = ControlCommand.set_manual_mode(enabled)
        self._send_command(command)
    
    def set_manual_iso(self, iso: int):
        command = ControlCommand.set_manual_iso(iso)
        self._send_command(command)
    
    def set_manual_shutter(self, nanos: int):
        command = ControlCommand.set_manual_shutter(nanos)
        self._send_command(command)
    
    def set_manual_focus(self, distance: float):
        command = ControlCommand.set_manual_focus(distance)
        self._send_command(command)
    
    def set_white_balance(self, mode: str, kelvin: int = 5500):
        command = ControlCommand.set_white_balance(mode, kelvin)
        self._send_command(command)
    
    def set_tap_focus(self, x: float, y: float, screen_width: int, screen_height: int):
        command = ControlCommand.set_tap_focus(x, y, screen_width, screen_height)
        self._send_command(command)
    
    def get_camera_capabilities(self):
        command = ControlCommand.get_camera_capabilities()
        self._send_command(command)

