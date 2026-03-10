"""Shared helpers for Spotify Playlists integration."""
from __future__ import annotations

import difflib

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    CONF_TARGETS,
    CONF_USERS,
    MEDIA_CONTENT_TYPE_MUSIC,
    MEDIA_PLAYER_DOMAIN,
    SERVICE_PLAY_MEDIA,
)


def _best_match(query: str, candidates: list[str], cutoff: float = 0.6) -> str | None:
    """Return the best fuzzy match for query in candidates, or None."""
    q = query.lower()
    for c in candidates:
        if c.lower() == q:
            return c
    matches = difflib.get_close_matches(q, [c.lower() for c in candidates], n=1, cutoff=cutoff)
    if matches:
        return next(c for c in candidates if c.lower() == matches[0])
    return None


def resolve_playlist(data: dict, user_name: str, playlist_name: str) -> tuple[str, str]:
    """
    Find the Spotify URI for a user's playlist.

    Returns (resolved_user_name, playlist_uri).
    Raises HomeAssistantError if not found.
    """
    users = data.get(CONF_USERS, [])
    user_names = [u["name"] for u in users]
    matched_name = _best_match(user_name, user_names)
    if not matched_name:
        raise HomeAssistantError(
            f"No configured user matches '{user_name}'. "
            f"Configured users: {', '.join(user_names)}"
        )

    user = next(u for u in users if u["name"] == matched_name)

    # Support ordinal words as playlist references
    ordinals = {
        "first": 1, "1st": 1, "one": 1,
        "second": 2, "2nd": 2, "two": 2,
        "third": 3, "3rd": 3, "three": 3,
    }

    pl_name_lower = playlist_name.lower().strip()
    if pl_name_lower in ordinals:
        n = ordinals[pl_name_lower]
        uri = user.get(f"playlist_{n}_uri", "")
        name = user.get(f"playlist_{n}_name", f"playlist {n}")
        if uri:
            return matched_name, uri
        raise HomeAssistantError(
            f"{matched_name} does not have a playlist {n} configured."
        )

    pl_names = [user[f"playlist_{n}_name"] for n in (1, 2, 3) if user.get(f"playlist_{n}_name")]
    matched_pl = _best_match(playlist_name, pl_names)
    if not matched_pl:
        raise HomeAssistantError(
            f"No playlist matching '{playlist_name}' found for {matched_name}. "
            f"Playlists: {', '.join(pl_names)}"
        )

    for n in (1, 2, 3):
        if user.get(f"playlist_{n}_name") == matched_pl:
            return matched_name, user[f"playlist_{n}_uri"]

    raise HomeAssistantError(f"Could not resolve playlist URI for '{matched_pl}'.")


def resolve_target(data: dict, target_name: str) -> tuple[str, str]:
    """
    Find the entity_id for a HomePod target.

    Returns (resolved_target_name, entity_id).
    Raises HomeAssistantError if not found.
    """
    targets = data.get(CONF_TARGETS, [])
    if not targets:
        raise HomeAssistantError("No HomePod targets are configured.")

    target_names = [t["name"] for t in targets]
    matched = _best_match(target_name, target_names, cutoff=0.5)
    if not matched:
        raise HomeAssistantError(
            f"No target matching '{target_name}'. "
            f"Configured targets: {', '.join(target_names)}"
        )

    target = next(t for t in targets if t["name"] == matched)
    return matched, target["entity_id"]


async def async_trigger_playback(
    hass: HomeAssistant,
    data: dict,
    user_name: str,
    playlist_name: str,
    target_name: str,
) -> tuple[str, str, str]:
    """
    Resolve names and call media_player.play_media.

    Returns (resolved_user, resolved_playlist, resolved_target) for response speech.
    """
    resolved_user, playlist_uri = resolve_playlist(data, user_name, playlist_name)

    # Resolve playlist display name for response
    users = data.get(CONF_USERS, [])
    user = next(u for u in users if u["name"] == resolved_user)
    pl_display = playlist_name
    for n in (1, 2, 3):
        if user.get(f"playlist_{n}_uri") == playlist_uri:
            pl_display = user[f"playlist_{n}_name"]
            break

    resolved_target, entity_id = resolve_target(data, target_name)

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_PLAY_MEDIA,
        {
            "entity_id": entity_id,
            ATTR_MEDIA_CONTENT_ID: playlist_uri,
            ATTR_MEDIA_CONTENT_TYPE: MEDIA_CONTENT_TYPE_MUSIC,
        },
    )

    return resolved_user, pl_display, resolved_target
