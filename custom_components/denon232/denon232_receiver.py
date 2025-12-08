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
        self._available = False
        self.ser = None
        self.lock = threading.Lock()
        
        # Try to connect, but don't fail if we can't (development mode support)
        try:
            self.ser = serial.Serial(
                serial_port,
                baudrate=9600,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=timeout,
                write_timeout=write_timeout,
            )
            self._available = True
            _LOGGER.info("Connected to Denon receiver at %s", serial_port)
        except (serial.SerialException, OSError) as err:
            _LOGGER.warning(
                "Could not connect to serial port %s: %s. "
                "Running in development/offline mode.",
                serial_port,
                err,
            )
            self._available = False

    @property
    def available(self) -> bool:
        """Return True if the receiver connection is available."""
        return self._available

    def serial_command(
        self, cmd: str, response: bool = False, all_lines: bool = False
    ) -> str | list[str] | None:
        """Send a command to the receiver and optionally read response."""
        if not self._available or self.ser is None:
            _LOGGER.debug("Command %s skipped - receiver not available", cmd)
            if response:
                return [] if all_lines else ""
            return None
            
        _LOGGER.debug("Command: %s", cmd)
        
        try:
            if not self.ser.is_open:
                self.ser.open()
        except (serial.SerialException, OSError) as err:
            _LOGGER.error("Failed to open serial port: %s", err)
            self._available = False
            if response:
                return [] if all_lines else ""
            return None

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
        except (serial.SerialException, OSError) as err:
            _LOGGER.error("Serial communication error: %s", err)
            self._available = False
            if response:
                return [] if all_lines else ""
            return None
        finally:
            self.lock.release()

    def close(self) -> None:
        """Close the serial connection."""
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
                _LOGGER.debug("Serial connection closed for %s", self._serial_port)
        except (serial.SerialException, OSError) as err:
            _LOGGER.error("Error closing serial connection: %s", err)
