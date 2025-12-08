"""Config flow for Denon AVR RS-232 integration."""
from __future__ import annotations

import logging
import os
from typing import Any

import serial
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_NAME, CONF_SERIAL_PORT, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


def validate_serial_port(port: str) -> bool:
    """Validate that the serial port exists and can be opened."""
    try:
        # Check if port exists
        if not os.path.exists(port):
            return False
        # Try to open the port briefly
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        ser.close()
        return True
    except (serial.SerialException, OSError):
        return False


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    port = data[CONF_SERIAL_PORT]
    
    # Run validation in executor since it's blocking
    is_valid = await hass.async_add_executor_job(validate_serial_port, port)
    
    if not is_valid:
        raise CannotConnect(f"Cannot connect to serial port: {port}")
    
    return {"title": data.get(CONF_NAME, DEFAULT_NAME)}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Denon AVR RS-232."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if this serial port is already configured
            self._async_abort_entries_match({CONF_SERIAL_PORT: user_input[CONF_SERIAL_PORT]})
            
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        # Show the form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_SERIAL_PORT, default="/dev/ttyUSB0"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""

