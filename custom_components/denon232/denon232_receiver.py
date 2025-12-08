"""
Denon RS232 interface to control the receiver.

Based off:
https://github.com/home-assistant/home-assistant/blob/dev/homeassistant/components/media_player/denon.py#L228
https://github.com/joopert/nad_receiver/blob/master/nad_receiver/__init__.py 

Not all receivers have all functions.
Functions can be found on in the xls file within this repository
"""

import logging
import threading

import serial

DEFAULT_TIMEOUT = 1
DEFAULT_WRITE_TIMEOUT = 1

_LOGGER = logging.getLogger(__name__)


class Denon232Receiver:
    """Denon232 receiver."""

    def __init__(
        self,
        serial_port: str,
        timeout: float = DEFAULT_TIMEOUT,
        write_timeout: float = DEFAULT_WRITE_TIMEOUT,
    ):
        """Create RS232 connection."""
        self._serial_port = serial_port
        self._timeout = timeout
        self._write_timeout = write_timeout
        self.ser = serial.Serial(
            serial_port,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=timeout,
            write_timeout=write_timeout,
        )
        self.lock = threading.Lock()

    def serial_command(
        self, cmd: str, response: bool = False, all_lines: bool = False
    ) -> str | list[str] | None:
        """Send a command to the receiver and optionally read response."""
        _LOGGER.debug("Command: %s", cmd)
        
        if not self.ser.is_open:
            self.ser.open()

        try:
            self.lock.acquire()

            # Denon uses the suffix \r, so add those to the above cmd.
            final_command = f"{cmd}\r".encode("utf-8")
            # Write data to serial port
            self.ser.write(final_command)
            
            # Read data from serial port
            if response:
                lines = []
                while True:
                    line = self.ser.read_until(b"\r")
                    if not line:
                        break
                    decoded_line = line.decode().strip()
                    lines.append(decoded_line)
                    _LOGGER.debug("Received: %s", decoded_line)
                
                if all_lines:
                    return lines
                return lines[0] if lines else ""
            
            return None
        finally:
            self.lock.release()

    def close(self) -> None:
        """Close the serial connection."""
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
                _LOGGER.debug("Serial connection closed for %s", self._serial_port)
        except serial.SerialException as err:
            _LOGGER.error("Error closing serial connection: %s", err)
