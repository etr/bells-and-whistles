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
- `gender`: still used when `tts_provider` is `polly`; omitted from config when provider is `elevenlabs` (configure command only writes it for Polly)

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
- The generator reads this file at generation time; phrases are NOT hardcoded in Python
- Users can edit this file to customize phrases before running `generate_sounds.py`
- This file is version-controlled

## New Melodies

### Cyberpunk (10 melodies)

Synth-heavy, dark electronic: low bass drones, glitchy arpeggios, neon-noir stings, detuned tones. Defined as `(freq_hz, duration_ms)` tuples in `generate_sounds.py` under `THEMES['cyberpunk']`.

### D&D (10 melodies)

Fantasy/adventure: lute-like arpeggios, horn fanfares, harp glissandos, medieval modal phrases (open fifths, Dorian/Mixolydian intervals). Defined under `THEMES['dnd']`.

Both themes follow existing conventions: 10 melodies each, ≤2 seconds, sine-wave generation. Full note sequences will be defined in the implementation (not in this spec) — melody composition is a creative task done during coding.

## generate_sounds.py Changes

- Read `speech_phrases.json` for all phrase data instead of inline `SPEECH_PHRASES` dict
- New `generate_speech_elevenlabs(api_key, voice_id, theme_filter, ...)` function:
  - Calls ElevenLabs REST API `POST /v1/text-to-speech/{voice_id}` using `urllib.request` (stdlib only — no `requests` dependency)
  - Receives MP3 response body; convert to WAV using `ffmpeg` CLI (`subprocess.run(['ffmpeg', '-i', tmp.mp3, '-ar', '16000', '-ac', '1', '-f', 'wav', out.wav])`)
  - If `ffmpeg` is not installed, print a clear error and skip speech generation (not a hard crash)
  - On API errors (invalid key, bad voice_id, rate limit), log the error and skip that phrase — do not abort the entire run
  - Output path: `sounds/speech/elevenlabs/{voice_id}/{theme}/stop_0.wav`, `notification_3.wav`, etc.
  - Output format: 16-bit mono WAV at 16000 Hz (matching Polly output)
  - Numbered files for random selection at runtime
- Existing `generate_speech()` (Polly) updated to read from `speech_phrases.json` and output numbered files per theme
- New CLI flags: `--tts-provider`, `--api-key`, `--voice-id`, `--theme` (extended to include cyberpunk/dnd)
- Add `THEMES['cyberpunk']` and `THEMES['dnd']` melody definitions (10 each, full note sequences in code)

**Note:** `speech_phrases.json` is read only at generation time. At runtime, the shell script plays pre-generated WAV files — it never reads the JSON file.

## notify-sound.sh Changes

- Read `tts_provider`, `elevenlabs_voice_id` from config (default provider: `polly`)
- Speech file lookup changes:
  - Resolve speech base dir:
    - Polly: `sounds/speech/{gender}/`
    - ElevenLabs: `sounds/speech/elevenlabs/{voice_id}/`
  - Determine speech theme dir: try `{base}/{theme}/` first; if it doesn't exist, fall back to `{base}/default/`
  - If neither dir exists, skip speech entirely (silent — matches current behavior of playing melody only)
- Random phrase selection: glob `stop_*.wav` or `notification_*.wav` in the resolved dir, count matches, pick one with `$RANDOM % count`
- Window-specific variants: try `stop_window_{WIN}_*.wav` first, fall back to `stop_*.wav`
- Config parsing updated to also extract `tts_provider` and `elevenlabs_voice_id` (add to the existing python3 one-liner)

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
