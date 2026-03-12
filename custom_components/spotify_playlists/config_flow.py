"""Config flow for Spotify Playlists integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import DOMAIN


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

_TEXT = TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT))
_ENTITY_MP = EntitySelector(EntitySelectorConfig(domain="media_player"))


def _user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    d = defaults or {}
    return vol.Schema(
        {
            vol.Required("name", default=d.get("name", "")): _TEXT,
            vol.Required("spotify_entity", default=d.get("spotify_entity", "")): _ENTITY_MP,
            vol.Optional("playlist_1_name", default=d.get("playlist_1_name", "")): _TEXT,
            vol.Optional("playlist_1_uri", default=d.get("playlist_1_uri", "")): _TEXT,
            vol.Optional("playlist_2_name", default=d.get("playlist_2_name", "")): _TEXT,
            vol.Optional("playlist_2_uri", default=d.get("playlist_2_uri", "")): _TEXT,
            vol.Optional("playlist_3_name", default=d.get("playlist_3_name", "")): _TEXT,
            vol.Optional("playlist_3_uri", default=d.get("playlist_3_uri", "")): _TEXT,
        }
    )


def _targets_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    d = defaults or {}
    return vol.Schema(
        {
            vol.Required("target_1_name", default=d.get("target_1_name", "")): _TEXT,
            vol.Required("target_1_source", default=d.get("target_1_source", "")): _TEXT,
            vol.Optional("target_2_name", default=d.get("target_2_name", "")): _TEXT,
            vol.Optional("target_2_source", default=d.get("target_2_source", "")): _TEXT,
            vol.Optional("target_3_name", default=d.get("target_3_name", "")): _TEXT,
            vol.Optional("target_3_source", default=d.get("target_3_source", "")): _TEXT,
        }
    )


# ---------------------------------------------------------------------------
# Data assembly helpers
# ---------------------------------------------------------------------------

def _user_dict_from_form(form: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": form["name"].strip(),
        "spotify_entity_id": form["spotify_entity"].strip(),
        "playlist_1_name": form["playlist_1_name"].strip(),
        "playlist_1_uri": form["playlist_1_uri"].strip(),
        "playlist_2_name": form["playlist_2_name"].strip(),
        "playlist_2_uri": form["playlist_2_uri"].strip(),
        "playlist_3_name": form["playlist_3_name"].strip(),
        "playlist_3_uri": form["playlist_3_uri"].strip(),
    }


def _user_dict_to_form(user: dict[str, Any]) -> dict[str, Any]:
    """Flatten a stored user dict back to form field names."""
    d = dict(user)
    # stored as spotify_entity_id, form field is spotify_entity
    d["spotify_entity"] = d.pop("spotify_entity_id", "")
    return d


def _assemble_entry_data(
    user_1: dict, user_2: dict, user_3: dict, targets_form: dict
) -> dict[str, Any]:
    targets = []
    for n in (1, 2, 3):
        name = targets_form.get(f"target_{n}_name", "").strip()
        source = targets_form.get(f"target_{n}_source", "").strip()
        if name and source:
            targets.append({"name": name, "source_name": source})

    return {
        "users": [
            _user_dict_from_form(user_1),
            _user_dict_from_form(user_2),
            _user_dict_from_form(user_3),
        ],
        "targets": targets,
    }


def _targets_form_from_data(data: dict[str, Any]) -> dict[str, Any]:
    """Flatten stored targets list back to form field names."""
    targets = data.get("targets", [{}, {}, {}])
    flat: dict[str, Any] = {}
    for i, t in enumerate(targets[:3], start=1):
        flat[f"target_{i}_name"] = t.get("name", "")
        flat[f"target_{i}_source"] = t.get("source_name", "")
    return flat


# ---------------------------------------------------------------------------
# ConfigFlow
# ---------------------------------------------------------------------------

class SpotifyPlaylistsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial setup config flow."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        self._user_1: dict = {}
        self._user_2: dict = {}
        self._user_3: dict = {}

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        return await self.async_step_user_1()

    async def async_step_user_1(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._user_1 = user_input
            return await self.async_step_user_2()
        return self.async_show_form(step_id="user_1", data_schema=_user_schema())

    async def async_step_user_2(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._user_2 = user_input
            return await self.async_step_user_3()
        return self.async_show_form(step_id="user_2", data_schema=_user_schema())

    async def async_step_user_3(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._user_3 = user_input
            return await self.async_step_targets()
        return self.async_show_form(step_id="user_3", data_schema=_user_schema())

    async def async_step_targets(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            entry_data = _assemble_entry_data(
                self._user_1, self._user_2, self._user_3, user_input
            )
            return self.async_create_entry(title="Spotify Playlists", data=entry_data)
        return self.async_show_form(step_id="targets", data_schema=_targets_schema())

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return SpotifyPlaylistsOptionsFlow(config_entry)


# ---------------------------------------------------------------------------
# OptionsFlow
# ---------------------------------------------------------------------------

class SpotifyPlaylistsOptionsFlow(OptionsFlow):
    """Handle reconfiguration via Settings → Integrations → Configure."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry
        self._user_1: dict = {}
        self._user_2: dict = {}
        self._user_3: dict = {}

    def _current_data(self) -> dict[str, Any]:
        # options take precedence over initial data (set after first reconfigure)
        return self._entry.options if self._entry.options else self._entry.data

    async def async_step_init(self, user_input: dict | None = None) -> ConfigFlowResult:
        return await self.async_step_user_1()

    async def async_step_user_1(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._user_1 = user_input
            return await self.async_step_user_2()
        existing = self._current_data().get("users", [{}, {}, {}])
        return self.async_show_form(
            step_id="user_1",
            data_schema=_user_schema(_user_dict_to_form(existing[0]) if existing else {}),
        )

    async def async_step_user_2(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._user_2 = user_input
            return await self.async_step_user_3()
        existing = self._current_data().get("users", [{}, {}, {}])
        return self.async_show_form(
            step_id="user_2",
            data_schema=_user_schema(_user_dict_to_form(existing[1]) if len(existing) > 1 else {}),
        )

    async def async_step_user_3(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._user_3 = user_input
            return await self.async_step_targets()
        existing = self._current_data().get("users", [{}, {}, {}])
        return self.async_show_form(
            step_id="user_3",
            data_schema=_user_schema(_user_dict_to_form(existing[2]) if len(existing) > 2 else {}),
        )

    async def async_step_targets(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            new_data = _assemble_entry_data(
                self._user_1, self._user_2, self._user_3, user_input
            )
            # Store back as options; async_setup_entry prefers options over data
            return self.async_create_entry(data=new_data)
        existing_flat = _targets_form_from_data(self._current_data())
        return self.async_show_form(
            step_id="targets",
            data_schema=_targets_schema(existing_flat),
        )
