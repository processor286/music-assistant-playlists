"""Config flow for Music Assistant Playlists integration."""
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

from .const import (
    CONF_PL_ENTITY_ID,
    CONF_PL_MEDIA_ID,
    CONF_PL_NAME,
    CONF_PL_OWNER,
    CONF_PLAYLISTS,
    DOMAIN,
)

_TEXT = TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT))
_ENTITY_MA = EntitySelector(EntitySelectorConfig(domain="media_player"))


def _user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    d = defaults or {}
    return vol.Schema(
        {
            vol.Required("user_name", default=d.get("user_name", "")): _TEXT,
            vol.Optional("playlist_1_name", default=d.get("playlist_1_name", "")): _TEXT,
            vol.Optional("playlist_1_media_id", default=d.get("playlist_1_media_id", "")): _TEXT,
            vol.Optional("playlist_1_entity_id", default=d.get("playlist_1_entity_id", "")): _ENTITY_MA,
            vol.Optional("playlist_2_name", default=d.get("playlist_2_name", "")): _TEXT,
            vol.Optional("playlist_2_media_id", default=d.get("playlist_2_media_id", "")): _TEXT,
            vol.Optional("playlist_2_entity_id", default=d.get("playlist_2_entity_id", "")): _ENTITY_MA,
            vol.Optional("playlist_3_name", default=d.get("playlist_3_name", "")): _TEXT,
            vol.Optional("playlist_3_media_id", default=d.get("playlist_3_media_id", "")): _TEXT,
            vol.Optional("playlist_3_entity_id", default=d.get("playlist_3_entity_id", "")): _ENTITY_MA,
        }
    )


def _playlists_from_form(form: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract non-empty playlist rows from a user form submission."""
    user_name = form.get("user_name", "").strip()
    playlists = []
    for n in (1, 2, 3):
        name = form.get(f"playlist_{n}_name", "").strip()
        media_id = form.get(f"playlist_{n}_media_id", "").strip()
        entity_id = form.get(f"playlist_{n}_entity_id", "").strip()
        if name and media_id and entity_id:
            playlists.append(
                {
                    CONF_PL_NAME: name,
                    CONF_PL_OWNER: user_name,
                    CONF_PL_MEDIA_ID: media_id,
                    CONF_PL_ENTITY_ID: entity_id,
                }
            )
    return playlists


def _form_from_playlists(owner: str, playlists: list[dict]) -> dict[str, Any]:
    """Rebuild form defaults from stored playlist dicts for a given owner."""
    own = [p for p in playlists if p.get(CONF_PL_OWNER) == owner]
    d: dict[str, Any] = {"user_name": owner}
    for i, p in enumerate(own[:3], start=1):
        d[f"playlist_{i}_name"] = p.get(CONF_PL_NAME, "")
        d[f"playlist_{i}_media_id"] = p.get(CONF_PL_MEDIA_ID, "")
        d[f"playlist_{i}_entity_id"] = p.get(CONF_PL_ENTITY_ID, "")
    return d


# ---------------------------------------------------------------------------
# ConfigFlow
# ---------------------------------------------------------------------------

class MusicAssistantPlaylistsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Initial setup — collect 3 users and their playlists."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        self._all_playlists: list[dict[str, Any]] = []

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        return await self.async_step_user_1()

    async def async_step_user_1(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._all_playlists.extend(_playlists_from_form(user_input))
            return await self.async_step_user_2()
        return self.async_show_form(step_id="user_1", data_schema=_user_schema())

    async def async_step_user_2(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._all_playlists.extend(_playlists_from_form(user_input))
            return await self.async_step_user_3()
        return self.async_show_form(step_id="user_2", data_schema=_user_schema())

    async def async_step_user_3(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._all_playlists.extend(_playlists_from_form(user_input))
            return self.async_create_entry(
                title="Music Assistant Playlists",
                data={CONF_PLAYLISTS: self._all_playlists},
            )
        return self.async_show_form(step_id="user_3", data_schema=_user_schema())

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return MusicAssistantPlaylistsOptionsFlow(config_entry)


# ---------------------------------------------------------------------------
# OptionsFlow
# ---------------------------------------------------------------------------

class MusicAssistantPlaylistsOptionsFlow(OptionsFlow):
    """Reconfiguration via Settings → Integrations → Configure."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry
        self._all_playlists: list[dict[str, Any]] = []

    def _current_data(self) -> dict[str, Any]:
        return self._entry.options if self._entry.options else self._entry.data

    def _owners(self) -> list[str]:
        seen: list[str] = []
        for p in self._current_data().get(CONF_PLAYLISTS, []):
            owner = p.get(CONF_PL_OWNER, "")
            if owner and owner not in seen:
                seen.append(owner)
        # Pad to 3 slots
        while len(seen) < 3:
            seen.append("")
        return seen

    async def async_step_init(self, user_input: dict | None = None) -> ConfigFlowResult:
        return await self.async_step_user_1()

    async def async_step_user_1(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._all_playlists.extend(_playlists_from_form(user_input))
            return await self.async_step_user_2()
        owners = self._owners()
        existing_playlists = self._current_data().get(CONF_PLAYLISTS, [])
        defaults = _form_from_playlists(owners[0], existing_playlists) if owners[0] else {}
        return self.async_show_form(
            step_id="user_1", data_schema=_user_schema(defaults)
        )

    async def async_step_user_2(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._all_playlists.extend(_playlists_from_form(user_input))
            return await self.async_step_user_3()
        owners = self._owners()
        existing_playlists = self._current_data().get(CONF_PLAYLISTS, [])
        defaults = _form_from_playlists(owners[1], existing_playlists) if owners[1] else {}
        return self.async_show_form(
            step_id="user_2", data_schema=_user_schema(defaults)
        )

    async def async_step_user_3(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._all_playlists.extend(_playlists_from_form(user_input))
            return self.async_create_entry(data={CONF_PLAYLISTS: self._all_playlists})
        owners = self._owners()
        existing_playlists = self._current_data().get(CONF_PLAYLISTS, [])
        defaults = _form_from_playlists(owners[2], existing_playlists) if owners[2] else {}
        return self.async_show_form(
            step_id="user_3", data_schema=_user_schema(defaults)
        )
