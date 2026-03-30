# Music Assistant Playlists

Home Assistant custom integration that exposes per-playlist **trigger switches** to HomeKit, allowing you to start shuffled Music Assistant playlists via "Hey Siri" from a HomePod.

## How it works

For each configured playlist the integration creates a `switch` entity. When the switch is turned on:

1. `music_assistant.play_media` is called on the configured MA player (replaces current queue)
2. `media_player.shuffle_set` enables shuffle on that player
3. The switch automatically resets to OFF after 3 seconds

Expose the switches to HomeKit (via the HomeKit Bridge integration) and assign them to HA areas matching your HomePod rooms.

## Hey Siri usage

| Command | What happens |
|---|---|
| `Hey Siri, turn on Treadmill` | Plays "Treadmill" playlist on its configured MA player |
| `Hey Siri, turn on Treadmill in the Living Room` | Same, but Siri targets the Living Room HomePod's local switch |

For stop/skip, expose your MA `media_player.*` entities to HomeKit directly — HomeKit treats them as speakers and Siri can pause/skip them by room name.

## Installation

1. Copy `custom_components/music_assistant_playlists/` into your HA `custom_components/` folder
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration** and search for **Music Assistant Playlists**

## Configuration

The setup wizard has 3 steps (one per user). For each user enter:

- **User name** — used to group playlists; not exposed to HomeKit
- **Playlist N — display name** — becomes the HomeKit switch name, e.g. `Treadmill`
- **Playlist N — MA playlist name or URI** — the playlist name as it appears in Music Assistant (or a full URI like `spotify://playlist/…`)
- **Playlist N — MA player** — the `media_player.mass_*` entity to play on

Leave a playlist row blank to skip it.

## Reconfiguration

**Settings → Integrations → Music Assistant Playlists → Configure** to update any values. The integration reloads automatically and recreates all switch entities.

## Room-based Siri targeting

To support `"Hey Siri, turn on Treadmill in the Living Room"`:

1. In HA, assign each switch entity to the matching area (e.g. assign `switch.treadmill` to the *Living Room* area)
2. In the HomeKit Bridge config, include the switch entities
3. HomeKit will place the switches in the corresponding HomeKit rooms, matching your HomePod locations
4. If a playlist should be available in multiple rooms, create duplicate entries in the config (same playlist name, different MA player entity) — HA and HomeKit will show them in separate rooms

## Stop & skip via Siri

Expose your MA media player entities (e.g. `media_player.mass_living_room`) through HomeKit Bridge. Then:

- `"Hey Siri, pause Living Room"` — pauses playback
- `"Hey Siri, next track in the Living Room"` — skips
- `"Hey Siri, stop Living Room"` — stops
