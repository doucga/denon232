"""The Denon AVR RS-232 integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_SERIAL_PORT, DOMAIN
from .denon232_receiver import Denon232Receiver

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Denon AVR RS-232 from a config entry."""
    serial_port = entry.data[CONF_SERIAL_PORT]
    
    # Create receiver instance in executor (blocking operation)
    receiver = await hass.async_add_executor_job(Denon232Receiver, serial_port)
    
    # Store receiver in hass.data for platforms to access
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = receiver
    
    # Forward setup to media_player platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Close receiver connection and remove from hass.data
        receiver: Denon232Receiver = hass.data[DOMAIN].pop(entry.entry_id)
        await hass.async_add_executor_job(receiver.close)
    
    return unload_ok

