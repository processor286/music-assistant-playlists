# Spotify Playlists — Voice Control for Home Assistant

A [HACS](https://hacs.xyz) custom integration that lets up to three people start their favourite Spotify playlists on any HomePod by voice, via Home Assistant.

---

## What it does

- Configure **three people**, each with **three named Spotify playlists**
- Configure up to **three HomePod targets** (any `media_player` entity)
- Trigger playback by voice via **HA Assist** or **Siri Shortcuts**
- Trigger playback from automations via the `spotify_playlists.play` service
- Reconfigure everything from the HA UI — no YAML required

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Home Assistant 2024.4+ | For `OptionsFlowWithReload` support |
| HACS | For easy installation |
| Spotify integration | The [official HA Spotify integration](https://www.home-assistant.io/integrations/spotify/) must be set up so your HomePods appear as `media_player` entities |
| HomePod media player entities | Via the Spotify integration or AirPlay/HomeKit Controller |

---

## Installation

### Option A — HACS (recommended)

1. Open HACS → Integrations → ⋮ → Custom Repositories
2. Add this repository URL as an **Integration**
3. Install **Spotify Playlists**
4. Restart Home Assistant

### Option B — Manual

```bash
cp -r custom_components/spotify_playlists \
       /config/custom_components/spotify_playlists
```

Restart Home Assistant.

---

## Setup

1. Go to **Settings → Integrations → + Add Integration**
2. Search for **Spotify Playlists**
3. Work through the four setup screens:

| Screen | What to enter |
|---|---|
| **Person 1** | Name (used in voice commands) + 3 playlist names + Spotify URIs |
| **Person 2** | Same |
| **Person 3** | Same |
| **HomePod Targets** | Up to 3 HomePod names + their `media_player` entity IDs |

To find a playlist's Spotify URI: open Spotify → right-click a playlist → Share → **Copy Spotify URI**. It looks like `spotify:playlist:37i9dQZF1DX0XUsuxWHRQd`.

To reconfigure later: **Settings → Integrations → Spotify Playlists → Configure**.

---

## Voice Commands

The integration registers a **Home Assistant Assist** intent (`SpotifyPlaylistPlay`). You also need to add a sentence definition file.

### Step 1 — Copy the sentences file

Copy `custom_sentences/en/spotify_playlists.yaml` from this repo into your HA config directory:

```
/config/custom_sentences/en/spotify_playlists.yaml
```

Create the `custom_sentences/en/` directory if it doesn't exist.

### Step 2 — Restart Home Assistant

### Step 3 — Speak

From any Assist-enabled device:

| What you say | What happens |
|---|---|
| `Play Gary's Workout playlist on the Kitchen HomePod` | Plays Gary's "Workout" playlist on the kitchen HomePod |
| `Play Gary's second playlist on the Living Room` | Plays Gary's second configured playlist in the living room |
| `Start Alice's Chill playlist` | Plays Alice's "Chill" playlist on the first (default) HomePod |
| `Play Bob's first playlist on the Bedroom HomePod` | Plays Bob's first playlist in the bedroom |

Names are matched **case-insensitively with fuzzy matching**, so minor mispronunciations are handled.

---

## Strict voice matching (optional)

For more reliable voice recognition, edit `spotify_playlists.yaml` to add a `lists:` section with your exact configured names. HA Assist will then only accept utterances that match your names precisely:

```yaml
language: "en"
intents:
  SpotifyPlaylistPlay:
    data:
      - sentences:
          - "(play|start|put on) {user}'s {playlist} [playlist] on [the] {target} [HomePod]"
          - "(play|start|put on) {user}'s {playlist} [playlist]"
lists:
  user:
    values:
      - "Gary"
      - "Alice"
      - "Bob"
  playlist:
    values:
      - "Workout"
      - "Chill"
      - "Morning"
      - "Focus"
      # ... add all your playlist names here
  target:
    values:
      - "Kitchen"
      - "Living Room"
      - "Bedroom"
```

---

## Voice on HomePods — Two Approaches

HomePods use **Siri** as their native voice assistant, not HA Assist. Choose one of:

### Approach A: HA Assist satellite near the HomePod

Use a small always-on device (e.g. an ESPHome voice satellite or a Raspberry Pi with a microphone) running HA Assist next to the HomePod. Speak to the satellite; it routes to HA Assist; playback starts on the HomePod.

### Approach B: Siri Shortcuts → HA Webhook (recommended for HomePods)

1. In HA, create an automation triggered by **Webhook** (Settings → Automations → + → Trigger: Webhook)
2. Set the action to call `spotify_playlists.play` with the desired user/playlist/target
3. On iOS/macOS, create a **Siri Shortcut**:
   - Action: **Get Contents of URL**
   - URL: `https://<your-ha-url>/api/webhook/<webhook-id>`
   - Method: POST
   - Body type: JSON — e.g. `{"user": "Gary", "playlist": "Workout", "target": "Kitchen"}`
4. Give the shortcut a phrase: **"Play Gary's workout"**
5. Say it on any Apple device including HomePod: **"Hey Siri, play Gary's workout"**

You can create one shortcut per person/playlist/room combination.

---

## `spotify_playlists.play` Service

Use this service in automations and scripts:

```yaml
service: spotify_playlists.play
data:
  user: "Gary"
  playlist: "Workout"   # name or "first" / "second" / "third"
  target: "Kitchen"
```

---

## Automation Example

Play a morning playlist on a schedule:

```yaml
alias: Gary's Morning Music
trigger:
  - platform: time
    at: "07:30:00"
condition:
  - condition: time
    weekday: [mon, tue, wed, thu, fri]
action:
  - service: spotify_playlists.play
    data:
      user: "Gary"
      playlist: "Morning"
      target: "Kitchen"
```

---

## Troubleshooting

**Voice command not recognised**
- Confirm `custom_sentences/en/spotify_playlists.yaml` is in your HA config directory
- Restart HA after adding the file
- Try the strict `lists:` approach (see above)

**Playlist doesn't play**
- Confirm the media player entity ID is correct (Developer Tools → States, filter `media_player`)
- Confirm the Spotify URI is correct — test with `media_player.play_media` directly
- Check HA logs: Settings → System → Logs, filter by `spotify_playlists`

**Name not matched**
- Names are fuzzy-matched; try to use the exact name you configured
- Check spelling — e.g. "workout" vs "Workout" is fine (case-insensitive), but "workot" might not match

---

## License

MIT License — see LICENSE file.
