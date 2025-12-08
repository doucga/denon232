"""Media player platform for Denon AVR RS-232 integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_NAME, CONF_SERIAL_PORT, DOMAIN, NORMAL_INPUTS, ZONE2_INPUTS
from .denon232_receiver import Denon232Receiver

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Denon media player from a config entry."""
    receiver: Denon232Receiver = hass.data[DOMAIN][entry.entry_id]
    name = entry.data[CONF_NAME]
    serial_port = entry.data[CONF_SERIAL_PORT]

    entities = [
        DenonMainZone(receiver, name, serial_port, entry.entry_id),
        DenonZone2(receiver, name, serial_port, entry.entry_id),
    ]

    async_add_entities(entities, True)


class DenonBase(MediaPlayerEntity):
    """Base class for Denon media player entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        receiver: Denon232Receiver,
        name: str,
        serial_port: str,
        entry_id: str,
        zone: str,
    ) -> None:
        """Initialize the Denon media player."""
        self._receiver = receiver
        self._base_name = name
        self._serial_port = serial_port
        self._entry_id = entry_id
        self._zone = zone
        
        # State attributes
        self._power_state: str | None = None
        self._volume: float = 0
        self._volume_max: int = 65
        self._muted: bool = False
        self._source: str | None = None
        self._source_list = NORMAL_INPUTS.copy()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._receiver.available

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Denon receiver."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._serial_port)},
            name=self._base_name,
            manufacturer="Denon",
            model="AVR RS-232",
        )

    @property
    def source_list(self) -> list[str]:
        """Return the list of available input sources."""
        return sorted(list(self._source_list.keys()))


class DenonMainZone(DenonBase):
    """Representation of the Denon Main Zone."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(
        self,
        receiver: Denon232Receiver,
        name: str,
        serial_port: str,
        entry_id: str,
    ) -> None:
        """Initialize the Main Zone."""
        super().__init__(receiver, name, serial_port, entry_id, "main")
        self._attr_unique_id = f"{serial_port}_main"
        self._attr_name = "Main Zone"

    async def async_update(self) -> None:
        """Get the latest details from the device."""
        hass = self.hass

        # Get power state
        self._power_state = await hass.async_add_executor_job(
            self._receiver.serial_command, "PW?", True
        )

        # Get volume and max volume
        volume_lines = await hass.async_add_executor_job(
            self._receiver.serial_command, "MV?", True, True
        )
        if volume_lines:
            for line in volume_lines:
                if line.startswith("MVMAX "):
                    # Only grab two digit max
                    self._volume_max = int(line[6:8])
                    _LOGGER.debug("MVMAX Value: %s", self._volume_max)
                elif line.startswith("MV"):
                    # Volume can be 2 or 3 chars (e.g., MV50 or MV505 for half-dB)
                    vol_str = line[2:]
                    if len(vol_str) == 3:
                        # Half-dB value like "505" means 50.5
                        self._volume = int(vol_str[:2]) + 0.5
                    else:
                        self._volume = int(vol_str[:2])
                    if self._volume == 99:
                        self._volume = 0
                    _LOGGER.debug("MV Value: %s", self._volume)

        # Get mute state
        mute_response = await hass.async_add_executor_job(
            self._receiver.serial_command, "MU?", True
        )
        self._muted = mute_response == "MUON"

        # Get source
        source_response = await hass.async_add_executor_job(
            self._receiver.serial_command, "SI?", True
        )
        if source_response and source_response.startswith("SI"):
            self._source = source_response[2:]

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        if self._power_state == "PWSTANDBY":
            return MediaPlayerState.OFF
        return MediaPlayerState.ON

    @property
    def volume_level(self) -> float:
        """Volume level of the media player (0..1)."""
        return self._volume / self._volume_max if self._volume_max else 0

    @property
    def is_volume_muted(self) -> bool:
        """Return boolean if volume is currently muted."""
        return self._muted

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        for pretty_name, name in self._source_list.items():
            if self._source == name:
                return pretty_name
        return self._source

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, "PWON"
        )

    async def async_turn_off(self) -> None:
        """Turn off media player."""
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, "PWSTANDBY"
        )

    async def async_volume_up(self) -> None:
        """Volume up media player."""
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, "MVUP"
        )

    async def async_volume_down(self) -> None:
        """Volume down media player."""
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, "MVDOWN"
        )

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        volume_int = round(volume * self._volume_max)
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, f"MV{volume_int:02d}"
        )

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        mute_cmd = "MUON" if mute else "MUOFF"
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, mute_cmd
        )

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        source_cmd = self._source_list.get(source, source)
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, f"SI{source_cmd}"
        )


class DenonZone2(DenonBase):
    """Representation of the Denon Zone 2."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(
        self,
        receiver: Denon232Receiver,
        name: str,
        serial_port: str,
        entry_id: str,
    ) -> None:
        """Initialize Zone 2."""
        super().__init__(receiver, name, serial_port, entry_id, "zone2")
        self._attr_unique_id = f"{serial_port}_zone2"
        self._attr_name = "Zone 2"
        # Zone 2 has limited source options (no TV, HDP per protocol)
        self._source_list = ZONE2_INPUTS.copy()

    async def async_update(self) -> None:
        """Get the latest details from the device."""
        hass = self.hass

        # Get Zone 2 status (returns Z2ON, Z2OFF, or Z2<SOURCE>)
        z2_response = await hass.async_add_executor_job(
            self._receiver.serial_command, "Z2?", True, True
        )
        if z2_response:
            for line in z2_response:
                if line == "Z2ON":
                    self._power_state = "Z2ON"
                elif line == "Z2OFF":
                    self._power_state = "Z2OFF"
                elif line.startswith("Z2") and len(line) > 2:
                    # Check if it's a volume response (2 digits) or source
                    suffix = line[2:]
                    if suffix.isdigit() and len(suffix) <= 3:
                        # Volume value
                        if len(suffix) == 3:
                            self._volume = int(suffix[:2]) + 0.5
                        else:
                            self._volume = int(suffix)
                        if self._volume == 99:
                            self._volume = 0
                        _LOGGER.debug("Z2 Volume: %s", self._volume)
                    elif suffix not in ("ON", "OFF"):
                        # Source value
                        self._source = suffix
                        _LOGGER.debug("Z2 Source: %s", self._source)

        # Get Zone 2 mute state
        mute_response = await hass.async_add_executor_job(
            self._receiver.serial_command, "Z2MU?", True
        )
        self._muted = mute_response == "Z2MUON"

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        if self._power_state == "Z2ON":
            return MediaPlayerState.ON
        return MediaPlayerState.OFF

    @property
    def volume_level(self) -> float:
        """Volume level of Zone 2 (0..1)."""
        return self._volume / self._volume_max if self._volume_max else 0

    @property
    def is_volume_muted(self) -> bool:
        """Return boolean if volume is currently muted."""
        return self._muted

    @property
    def source(self) -> str | None:
        """Return the current input source for Zone 2."""
        for pretty_name, name in self._source_list.items():
            if self._source == name:
                return pretty_name
        return self._source

    async def async_turn_on(self) -> None:
        """Turn Zone 2 on."""
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, "Z2ON"
        )

    async def async_turn_off(self) -> None:
        """Turn Zone 2 off."""
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, "Z2OFF"
        )

    async def async_volume_up(self) -> None:
        """Volume up Zone 2."""
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, "Z2UP"
        )

    async def async_volume_down(self) -> None:
        """Volume down Zone 2."""
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, "Z2DOWN"
        )

    async def async_set_volume_level(self, volume: float) -> None:
        """Set Zone 2 volume level, range 0..1."""
        volume_int = round(volume * self._volume_max)
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, f"Z2{volume_int:02d}"
        )

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) Zone 2."""
        mute_cmd = "Z2MUON" if mute else "Z2MUOFF"
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, mute_cmd
        )

    async def async_select_source(self, source: str) -> None:
        """Select input source for Zone 2."""
        source_cmd = self._source_list.get(source, source)
        await self.hass.async_add_executor_job(
            self._receiver.serial_command, f"Z2{source_cmd}"
        )
