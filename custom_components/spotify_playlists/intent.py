"""HA Assist intent handler for Spotify Playlists."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.helpers import config_validation as cv, intent
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, INTENT_PLAY_PLAYLIST
from .helpers import async_trigger_playback


class SpotifyPlaylistIntentHandler(intent.IntentHandler):
    """Handle 'play <user>'s <playlist> on <target>' Assist voice commands."""

    intent_type = INTENT_PLAY_PLAYLIST
    description = "Play a configured Spotify playlist on a HomePod"

    slot_schema = {
        vol.Required("user"): cv.string,
        vol.Required("playlist"): cv.string,
        vol.Optional("target"): cv.string,
    }

    def __init__(self, data: dict) -> None:
        self._data = data

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        hass = intent_obj.hass
        slots = self.async_validate_slots(intent_obj.slots)

        user_name = slots["user"]["value"]
        playlist_name = slots["playlist"]["value"]
        target_name = slots.get("target", {}).get("value") or ""

        # Default to first configured target if none specified
        if not target_name:
            targets = self._data.get("targets", [])
            if targets:
                target_name = targets[0]["name"]
            else:
                response = intent_obj.create_response()
                response.async_set_speech("No HomePod targets are configured.")
                return response

        try:
            resolved_user, resolved_playlist, resolved_target = await async_trigger_playback(
                hass, self._data, user_name, playlist_name, target_name
            )
        except HomeAssistantError as err:
            raise intent.IntentHandleError(str(err)) from err

        response = intent_obj.create_response()
        response.async_set_speech(
            f"Playing {resolved_user}'s {resolved_playlist} playlist "
            f"on the {resolved_target}."
        )
        return response
