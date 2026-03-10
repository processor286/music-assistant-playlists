"""Constants for the Spotify Playlists integration."""

DOMAIN = "spotify_playlists"

# Config entry keys
CONF_USERS = "users"
CONF_TARGETS = "targets"

# Per-user keys (used as f-string templates)
CONF_USER_NAME = "name"
CONF_PL_NAME_TPL = "playlist_{n}_name"
CONF_PL_URI_TPL = "playlist_{n}_uri"

# Per-target keys
CONF_TARGET_NAME = "name"
CONF_TARGET_ENTITY = "entity_id"

# Intent and service names
INTENT_PLAY_PLAYLIST = "SpotifyPlaylistPlay"
SERVICE_PLAY = "play"

# media_player service constants
MEDIA_PLAYER_DOMAIN = "media_player"
SERVICE_PLAY_MEDIA = "play_media"
ATTR_MEDIA_CONTENT_ID = "media_content_id"
ATTR_MEDIA_CONTENT_TYPE = "media_content_type"
MEDIA_CONTENT_TYPE_MUSIC = "music"
