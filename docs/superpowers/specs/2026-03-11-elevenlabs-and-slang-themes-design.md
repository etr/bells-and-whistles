# ElevenLabs TTS + Cyberpunk/D&D Slang Themes

## Goal

Extend bells-and-whistles to support ElevenLabs as a TTS provider (alongside existing AWS Polly), add two new themed sound+speech packs (Cyberpunk 2077 slang, D&D slang), and make speech phrases editable via a standalone JSON file with randomized playback.

## Config Changes

`config.json` gains three optional fields:

```json
{
  "mode": "sound_and_voice",
  "theme": "cyberpunk",
  "tts_provider": "elevenlabs",
  "elevenlabs_api_key": "sk-...",
  "elevenlabs_voice_id": "pNInz6obpgDQGcFmaJgB"
}
```

- `tts_provider`: `"polly"` (default) or `"elevenlabs"`
- `elevenlabs_api_key`: required when provider is `elevenlabs`
- `elevenlabs_voice_id`: required when provider is `elevenlabs`
- `gender`: still used when `tts_provider` is `polly`, ignored for ElevenLabs

## Speech Phrases File

New file `speech_phrases.json` at the repo root. Structure:

```json
{
  "default": {
    "stop": ["Job completed!"],
    "notification": ["Hey! Back to work!"],
    "stop_window": ["Job completed on window {window}!"],
    "notification_window": ["Hey! Back to work! Window {window}!"]
  },
  "cyberpunk": {
    "stop": [
      "Flatline complete, choom!",
      "Preem work. Delta out.",
      "Job's done. Go touch some grass, gonk.",
      "Nova output, choombatta.",
      "Eddies earned. Slot in when ready."
    ],
    "notification": [
      "Hey choom, need your input!",
      "Wake up, samurai — permission needed.",
      "Got a gig for you, merc.",
      "Choom! Eyes on deck!",
      "V, pick up — got a situation."
    ],
    "stop_window": [
      "Flatline complete on window {window}, choom!",
      "Preem work on window {window}. Delta out."
    ],
    "notification_window": [
      "Hey choom! Window {window} needs your input!",
      "Wake up, samurai — window {window} needs you."
    ]
  },
  "dnd": {
    "stop": [
      "Quest complete! Roll for loot.",
      "The party rests. Long rest granted.",
      "Victory! The bard begins composing.",
      "Encounter resolved. XP awarded.",
      "The dungeon master nods approvingly."
    ],
    "notification": [
      "Roll for initiative!",
      "The DM requires your attention!",
      "A wild permission prompt appears!",
      "Halt, adventurer — choice required!",
      "The oracle seeks your guidance!"
    ],
    "stop_window": [
      "Quest complete on window {window}! Roll for loot.",
      "Window {window} encounter resolved. XP awarded."
    ],
    "notification_window": [
      "Roll for initiative! Window {window}!",
      "The DM requires your attention on window {window}!"
    ]
  }
}
```

- `{window}` is a template variable replaced at generation time (one WAV per window index 0-9)
- Themes without a speech entry in this file fall back to `"default"`
- The generator reads this file; phrases are NOT hardcoded in Python

## New Melodies

### Cyberpunk (10 melodies)

Synth-heavy, dark electronic: low bass drones, glitchy arpeggios, neon-noir stings, detuned tones. Defined as `(freq_hz, duration_ms)` tuples in `generate_sounds.py` under `THEMES['cyberpunk']`.

### D&D (10 melodies)

Fantasy/adventure: lute-like arpeggios, horn fanfares, harp glissandos, medieval modal phrases (open fifths, Dorian/Mixolydian intervals). Defined under `THEMES['dnd']`.

Both themes follow existing conventions: 10 melodies each, ≤2 seconds, sine-wave generation.

## generate_sounds.py Changes

- Read `speech_phrases.json` for all phrase data instead of inline `SPEECH_PHRASES` dict
- New `generate_speech_elevenlabs(api_key, voice_id, theme_filter, ...)` function:
  - Calls ElevenLabs REST API `POST /v1/text-to-speech/{voice_id}`
  - Receives MP3, converts to WAV (16-bit mono)
  - Output path: `sounds/speech/elevenlabs/{voice_id}/{theme}/stop_0.wav`, `notification_3.wav`, etc.
  - Numbered files for random selection at runtime
- Existing `generate_speech()` (Polly) updated to read from `speech_phrases.json` and output numbered files per theme
- New CLI flags: `--tts-provider`, `--api-key`, `--voice-id`, `--theme` (extended to include cyberpunk/dnd)
- Add `THEMES['cyberpunk']` and `THEMES['dnd']` melody definitions

## notify-sound.sh Changes

- Read `tts_provider` from config (default: `polly`)
- Speech file lookup changes:
  - Determine speech theme: if current theme has a matching dir under speech path, use it; else use `default`
  - For ElevenLabs: `sounds/speech/elevenlabs/{voice_id}/{speech_theme}/`
  - For Polly: `sounds/speech/{gender}/{speech_theme}/`
- Random phrase selection: count matching `stop_*.wav` or `notification_*.wav` files, pick one with `$RANDOM`
- Window-specific variants: try `stop_window_{WIN}_*.wav` first, fall back to `stop_*.wav`

## configure-bells-and-whistles.md Changes

New question flow:

1. Notification mode (unchanged)
2. **TTS provider**: "Which text-to-speech provider?" → [AWS Polly, ElevenLabs]
3. If Polly: voice gender (unchanged)
4. If ElevenLabs: ask for API key, then voice ID
5. Theme selection: add "Cyberpunk 2077" and "D&D" to the list
6. Write config, clean up old hooks (unchanged)

## README.md Changes

- Add ElevenLabs setup section (API key from elevenlabs.io, finding voice IDs)
- Update config reference with new fields
- Add Cyberpunk and D&D to theme table
- Keep Polly docs but frame as alternative

## CLAUDE.md Changes

- Document `speech_phrases.json` as the phrase source
- Add ElevenLabs generation commands
- Note new themes

## Generated File Layout

```
sounds/
  cyberpunk/           # 10 melody WAVs
  dnd/                 # 10 melody WAVs
  speech/
    male/              # Polly (existing)
      default/         # stop_0.wav, notification_0.wav, etc.
    female/            # Polly (existing)
      default/
    elevenlabs/
      {voice_id}/
        default/       # stop_0.wav, notification_0.wav, etc.
        cyberpunk/     # stop_0.wav .. stop_4.wav, notification_0.wav .. notification_4.wav
        dnd/           # same structure
```

## What Does NOT Change

- Plugin manifest (`.claude-plugin/plugin.json`)
- Hook event registration (`hooks/hooks.json`)
- Platform detection logic in `notify-sound.sh`
- Melody WAV format (16-bit mono 44100 Hz)
- Existing themes and their melodies
