"""Playlist trigger switches for Music Assistant Playlists."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .const import (
    CONF_PL_ENTITY_ID,
    CONF_PL_MEDIA_ID,
    CONF_PL_NAME,
    CONF_PL_OWNER,
    CONF_PLAYLISTS,
    DOMAIN,
    MA_DOMAIN,
    MA_SERVICE_PLAY_MEDIA,
    SWITCH_AUTO_OFF_DELAY,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PlaylistSwitch(pl) for pl in data.get(CONF_PLAYLISTS, [])
    )


class PlaylistSwitch(SwitchEntity):
    """
    Momentary switch that triggers a Music Assistant playlist.

    Turns ON, starts shuffled playback on the configured MA player,
    then automatically resets to OFF after SWITCH_AUTO_OFF_DELAY seconds.
    Expose to HomeKit and assign to an HA area so Siri can target it by room.
    """

    _attr_icon = "mdi:playlist-play"
    _attr_should_poll = False

    def __init__(self, playlist: dict) -> None:
        self._playlist = playlist
        self._is_on = False
        self._attr_name = playlist[CONF_PL_NAME]
        owner = playlist.get(CONF_PL_OWNER, "")
        slug = slugify(f"{owner}_{playlist[CONF_PL_NAME]}" if owner else playlist[CONF_PL_NAME])
        self._attr_unique_id = f"{DOMAIN}_{slug}"

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        self._is_on = True
        self.async_write_ha_state()

        try:
            await self._trigger_playback()
        except Exception:
            _LOGGER.exception(
                "Failed to start playlist '%s'", self._playlist[CONF_PL_NAME]
            )

        # Schedule auto reset without blocking the turn_on call
        async def _auto_off() -> None:
            await asyncio.sleep(SWITCH_AUTO_OFF_DELAY)
            self._is_on = False
            self.async_write_ha_state()

        self.hass.async_create_task(_auto_off())

    async def async_turn_off(self, **kwargs) -> None:
        self._is_on = False
        self.async_write_ha_state()

    async def _trigger_playback(self) -> None:
        entity_id = self._playlist[CONF_PL_ENTITY_ID]
        media_id = self._playlist[CONF_PL_MEDIA_ID]

        # Start the playlist (replacing any current queue)
        await self.hass.services.async_call(
            MA_DOMAIN,
            MA_SERVICE_PLAY_MEDIA,
            {
                "media_id": media_id,
                "media_type": "playlist",
                "enqueue": "replace",
            },
            target={"entity_id": entity_id},
        )

        # Enable shuffle on the player queue
        await self.hass.services.async_call(
            "media_player",
            "shuffle_set",
            {"shuffle": True},
            target={"entity_id": entity_id},
        )

        _LOGGER.debug(
            "Started playlist '%s' (media_id=%s) on %s",
            self._playlist[CONF_PL_NAME],
            media_id,
            entity_id,
        )
