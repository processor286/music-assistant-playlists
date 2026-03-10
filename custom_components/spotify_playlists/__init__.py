"""Spotify Playlists — voice-controlled playlist launcher for HomePods."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.intent as ha_intent
from homeassistant.helpers import config_validation as cv
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SERVICE_PLAY
from .helpers import async_trigger_playback
from .intent import SpotifyPlaylistIntentHandler


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the spotify_playlists component (YAML config not supported)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Spotify Playlists from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Options (from reconfiguration) take precedence over initial setup data
    data = entry.options if entry.options else entry.data
    hass.data[DOMAIN][entry.entry_id] = data

    # Register the HA Assist intent handler with current config data
    ha_intent.async_register(hass, SpotifyPlaylistIntentHandler(data))

    # Register the spotify_playlists.play service
    async def handle_play(call: ServiceCall) -> None:
        user_name = call.data["user"]
        playlist_name = call.data["playlist"]
        target_name = call.data["target"]
        try:
            await async_trigger_playback(hass, data, user_name, playlist_name, target_name)
        except HomeAssistantError:
            raise

    hass.services.async_register(
        DOMAIN,
        SERVICE_PLAY,
        handle_play,
        schema=vol.Schema(
            {
                vol.Required("user"): cv.string,
                vol.Required("playlist"): cv.string,
                vol.Required("target"): cv.string,
            }
        ),
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)

    if hass.services.has_service(DOMAIN, SERVICE_PLAY):
        hass.services.async_remove(DOMAIN, SERVICE_PLAY)

    return True
