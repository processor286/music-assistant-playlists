# Spotify Playlists — Voice Control for Home Assistant

A [HACS](https://hacs.xyz) custom integration that lets up to three people start their favourite Spotify playlists on any HomePod by voice, via Home Assistant.

---

## What it does

- Configure **three people**, each with **three named Spotify playlists**
- Configure up to **three HomePod targets** (any `media_player` entity)
- Trigger playback by voice via **HA Assist** or **Siri on HomePod**
- Trigger playback from the **HA dashboard**, **automations**, or **Developer Tools**
- Reconfigure everything from the HA UI — no YAML required

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Home Assistant 2024.4+ | |
| HACS | For easy installation |
| Spotify integration | The [official HA Spotify integration](https://www.home-assistant.io/integrations/spotify/) must be set up so your HomePods appear as `media_player` entities |

---

## Installation

### Option A — HACS (recommended)

1. Open HACS → Integrations → ⋮ → Custom Repositories
2. Add this repository URL as an **Integration**
3. Install **Spotify Playlists**
4. Restart Home Assistant

### Option B — Manual

Copy the `custom_components/spotify_playlists` folder into your HA config directory:

```
/config/custom_components/spotify_playlists/
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

**Finding a Spotify playlist URI:** open Spotify → right-click a playlist → Share → **Copy Spotify URI**
It looks like: `spotify:playlist:37i9dQZF1DX0XUsuxWHRQd`

**To reconfigure later:** Settings → Integrations → Spotify Playlists → **Configure**

---

## Starting a Playlist

### From the HA web interface (Dashboard)

The quickest way to trigger a playlist from the HA UI without setting up voice:

1. Go to **Settings → Developer Tools → Services**
2. In the Service field select **spotify_playlists.play** (or type it)
3. Switch to **YAML mode** and enter:

```yaml
service: spotify_playlists.play
data:
  user: "Gary"        # person's name as configured
  playlist: "Workout" # playlist name, or "first" / "second" / "third"
  target: "Kitchen"   # HomePod name as configured
```

4. Click **Call Service**

You can also add a **Button card** to your dashboard that calls the service with fixed values — see the Dashboard Button section below.

---

### Dashboard Button card

Add a one-tap play button to any HA dashboard:

1. Edit your dashboard → **+ Add Card** → **Button**
2. Switch to **YAML** and paste:

```yaml
type: button
name: Gary — Workout
icon: mdi:music
tap_action:
  action: perform-action
  perform_action: spotify_playlists.play
  data:
    user: "Gary"
    playlist: "Workout"
    target: "Kitchen"
```

Create one button per person/playlist/room combination and arrange them in a grid card.

---

### Voice via HA Assist

HA Assist is the built-in voice assistant. It works from the HA app, the web UI, and any configured voice satellite device.

**Step 1 — Add the sentences file**

Create the directory and file on your HA instance:

```
/config/custom_sentences/en/spotify_playlists.yaml
```

Paste in this content:

```yaml
language: "en"
intents:
  SpotifyPlaylistPlay:
    data:
      - sentences:
          - "(play|start|put on) {user}'s {playlist} [playlist] on [the] {target} [HomePod]"
          - "(play|start|put on) {playlist} playlist for {user} on [the] {target} [HomePod]"
          - "(play|start|put on) {user}'s {playlist} [playlist]"
          - "(play|start|put on) {playlist} playlist for {user}"
```

**Step 2 — Restart Home Assistant**

**Step 3 — Open Assist and speak**

Click the microphone icon in the top-right corner of HA, or press `a` on your keyboard.

| What you say | What happens |
|---|---|
| `Play Gary's Workout playlist on the Kitchen HomePod` | Plays Gary's Workout on Kitchen HomePod |
| `Play Gary's Workout on the Kitchen` | Same — "HomePod" is optional |
| `Start Alice's Chill playlist` | Plays Alice's Chill on the first (default) HomePod |
| `Play Bob's second playlist on the Bedroom` | Plays Bob's second configured playlist in the Bedroom |
| `Put on Gary's Morning playlist for the Living Room` | Plays Gary's Morning in the Living Room |

Names are matched **case-insensitively with fuzzy matching**, so minor variations work.

**Strict matching (optional):** For more reliable recognition, add a `lists:` block to the sentences file with your exact configured names:

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
      # add all your playlist names here
  target:
    values:
      - "Kitchen"
      - "Living Room"
      - "Bedroom"
```

---

### Voice via Siri on HomePod

HomePods use Siri natively. The simplest approach is a **Siri Shortcut** that calls HA directly.

**Step 1 — Get a Long-Lived Access Token**

In HA: click your **profile picture** (bottom-left) → scroll to **Long-Lived Access Tokens** → **Create Token** → copy it.

**Step 2 — Create a Siri Shortcut**

On your iPhone or iPad, open the **Shortcuts** app:

1. Tap **+** to create a new shortcut
2. Tap **Add Action** → search for **Get Contents of URL**
3. Configure the action:
   - **URL:** `http://YOUR-HA-IP:8123/api/services/spotify_playlists/play`
     (use your actual HA address — local IP or remote URL)
   - **Method:** POST
   - **Headers:** tap Add → Key: `Authorization`, Value: `Bearer YOUR-TOKEN-HERE`
   - **Request Body:** JSON → tap Add → add three fields:
     - `user` = `Gary`
     - `playlist` = `Workout`
     - `target` = `Kitchen`
4. Tap the shortcut name at the top and rename it to something Siri-friendly, e.g. **"Play Gary's workout"**
5. Tap **Done**

**Step 3 — Trigger it**

Say on any Apple device including HomePod:

> **Hey Siri, play Gary's workout**

Make one shortcut per person/playlist/room combination. Suggested naming conventions:

| Shortcut name | Plays |
|---|---|
| `Play Gary's workout` | Gary → Workout → Kitchen |
| `Play Gary's chill music` | Gary → Chill → Living Room |
| `Play Alice's morning playlist` | Alice → Morning → Kitchen |
| `Play bedroom music` | Gary → Evening → Bedroom |

---

### From an Automation

Use the `spotify_playlists.play` service in any automation:

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

The `playlist` field accepts either the configured name or a position: `"first"`, `"second"`, `"third"`.

---

### From a Script

```yaml
alias: Play Chill in Living Room
sequence:
  - service: spotify_playlists.play
    data:
      user: "Alice"
      playlist: "Chill"
      target: "Living Room"
```

---

## Reconfiguring

To change names, playlists, or HomePod assignments at any time:

**Settings → Integrations → Spotify Playlists → Configure**

This walks through the same four screens pre-filled with your current values. Changes take effect immediately on save.

---

## Troubleshooting

**Playlist doesn't play**
- Check the media player entity is correct: Developer Tools → States, filter by `media_player`
- Test the Spotify URI directly: Developer Tools → Services → `media_player.play_media` with `media_content_id: spotify:playlist:...` and `media_content_type: music`
- Check HA logs: Settings → System → Logs, filter by `spotify_playlists`

**Assist voice command not recognised**
- Confirm `/config/custom_sentences/en/spotify_playlists.yaml` exists
- Restart HA after adding or editing the file
- Test in the Assist chat window first before trying voice

**Siri Shortcut not working**
- Test the shortcut by tapping it in the Shortcuts app first — errors appear there
- Make sure the HA URL is reachable from your phone (try it in a browser)
- Double-check the Authorization header value starts with `Bearer ` (with a space)

**Name not matched**
- Use the exact name you configured (case doesn't matter, but spelling does)
- Try using position instead: `"first"`, `"second"`, or `"third"`

---

## License

MIT License — see LICENSE file.
