# ElevenLabs TTS + Cyberpunk/D&D Slang Themes Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add ElevenLabs TTS support, Cyberpunk 2077 and D&D themed melodies + speech phrases, and externalize speech phrases to an editable JSON file.

**Architecture:** The plugin has three layers: (1) `generate_sounds.py` generates WAV files at build time, (2) `hooks/notify-sound.sh` plays them at runtime, (3) `commands/configure-bells-and-whistles.md` handles user setup. Changes touch all three layers plus a new `speech_phrases.json` data file.

**Tech Stack:** Python 3 (stdlib only for melodies), ElevenLabs REST API via `urllib.request`, `ffmpeg` for MP3→WAV conversion, Bash for runtime playback.

**Spec:** `docs/superpowers/specs/2026-03-11-elevenlabs-and-slang-themes-design.md`

---

## Chunk 1: Data Layer + New Melodies

### Task 1: Create speech_phrases.json

**Files:**
- Create: `speech_phrases.json`

- [ ] **Step 1: Create the speech phrases JSON file**

Create `speech_phrases.json` at the repo root with all three theme phrase sets (default, cyberpunk, dnd). Each theme has `stop`, `notification`, `stop_window`, and `notification_window` arrays. The `{window}` placeholder is replaced at generation time.

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

- [ ] **Step 2: Commit**

```bash
git add speech_phrases.json
git commit -m "feat: add editable speech phrases JSON for default, cyberpunk, and dnd themes"
```

### Task 2: Add Cyberpunk melody definitions

**Files:**
- Modify: `generate_sounds.py:486` (insert new theme after `'chirps'` closing brace)

- [ ] **Step 1: Add cyberpunk theme to THEMES dict**

Insert after the `'chirps'` theme (line 485, before the closing `}`). 10 melodies, synth-heavy dark electronic vibe — low bass drones, glitchy arpeggios, detuned tones. All ≤2 seconds.

```python
    'cyberpunk': {
        'neon_district': [
            # Low synth bass drone with rising sting
            (110.00, 200), (116.54, 200), (123.47, 200),
            (130.81, 200), (138.59, 300), (0, 50), (277.18, 300),
        ],
        'netrunner_jack': [
            # Rapid ascending digital arpeggio — jacking into the net
            (220.00, 60), (277.18, 60), (329.63, 60), (440.00, 60),
            (554.37, 60), (659.25, 60), (880.00, 60),
            (0, 40), (880.00, 300),
        ],
        'corpo_alert': [
            # Cold, clinical two-tone alarm
            (440.00, 120), (0, 60), (554.37, 120), (0, 60),
            (440.00, 120), (0, 60), (554.37, 120), (0, 60),
            (440.00, 200),
        ],
        'braindance_glitch': [
            # Stuttering glitch pattern — broken playback
            (330.00, 40), (0, 20), (330.00, 40), (0, 20),
            (415.30, 40), (0, 80), (330.00, 40), (0, 20),
            (523.25, 60), (0, 40), (659.25, 300),
        ],
        'arasaka_tower': [
            # Ominous power chord — corporate menace
            (146.83, 300), (0, 50), (146.83, 150), (174.61, 150),
            (146.83, 300), (0, 50), (130.81, 400),
        ],
        'night_city_siren': [
            # Warbling siren sweep — two-tone oscillation
            (440.00, 100), (523.25, 100), (440.00, 100), (523.25, 100),
            (440.00, 100), (523.25, 100), (659.25, 400),
        ],
        'cyberware_boot': [
            # System boot sequence — ascending digital chirps
            (261.63, 50), (0, 30), (329.63, 50), (0, 30),
            (392.00, 50), (0, 30), (523.25, 50), (0, 30),
            (659.25, 50), (0, 30), (783.99, 50), (0, 60),
            (1046.50, 250),
        ],
        'ripperdoc_scan': [
            # Scanning pulse — low sweep with ping
            (130.81, 80), (164.81, 80), (196.00, 80), (246.94, 80),
            (293.66, 80), (0, 100), (1318.51, 60), (0, 40),
            (1318.51, 250),
        ],
        'delamain_chime': [
            # Polite AI assistant tone — clean and precise
            (659.25, 150), (0, 30), (783.99, 150), (0, 30),
            (880.00, 150), (0, 50), (1046.50, 350),
        ],
        'johnny_riff': [
            # Distorted rock riff — Silverhand energy
            (164.81, 120), (0, 40), (196.00, 120), (220.00, 120),
            (196.00, 120), (164.81, 200), (0, 40),
            (146.83, 120), (164.81, 350),
        ],
    },
```

- [ ] **Step 2: Verify melody generation**

```bash
python3 generate_sounds.py --melodies-only --theme cyberpunk
```

Expected: 10 melody WAVs created in `sounds/cyberpunk/`, each ≤2s.

- [ ] **Step 3: Commit**

```bash
git add generate_sounds.py sounds/cyberpunk/
git commit -m "feat: add cyberpunk 2077 melody theme (10 melodies)"
```

### Task 3: Add D&D melody definitions

**Files:**
- Modify: `generate_sounds.py` (insert after cyberpunk theme)

- [ ] **Step 1: Add dnd theme to THEMES dict**

Insert after the `'cyberpunk'` theme. 10 melodies, fantasy/adventure vibe — modal phrases (Dorian, Mixolydian), open fifths, lute arpeggios, horn fanfares. All ≤2 seconds.

```python
    'dnd': {
        'tavern_lute': [
            # Lute arpeggio in D Mixolydian — warm and inviting
            (293.66, 100), (369.99, 100), (440.00, 100), (523.25, 100),
            (440.00, 100), (369.99, 100), (293.66, 100),
            (440.00, 350),
        ],
        'quest_fanfare': [
            # Heroic horn call — open fifths, triumphant
            (293.66, 200), (0, 30), (440.00, 200), (0, 30),
            (587.33, 300), (0, 50), (440.00, 150), (587.33, 350),
        ],
        'critical_hit': [
            # Sharp ascending strike — impact!
            (392.00, 60), (523.25, 60), (659.25, 60),
            (783.99, 60), (1046.50, 80), (0, 40),
            (1046.50, 120), (0, 30), (1046.50, 300),
        ],
        'spell_cast': [
            # Mystical ascending shimmer — arcane energy
            (440.00, 80), (493.88, 80), (554.37, 80),
            (659.25, 80), (783.99, 80), (880.00, 80),
            (1046.50, 80), (1318.51, 350),
        ],
        'dragon_roar': [
            # Low rumbling growl ascending to roar
            (110.00, 150), (123.47, 150), (146.83, 150),
            (174.61, 150), (220.00, 200), (0, 50),
            (293.66, 400),
        ],
        'treasure_chest': [
            # Sparkling discovery — music box wonder
            (783.99, 80), (880.00, 80), (1046.50, 80),
            (880.00, 80), (1046.50, 80), (1318.51, 80),
            (0, 40), (1567.98, 350),
        ],
        'long_rest': [
            # Gentle campfire melody — peaceful Dorian
            (293.66, 200), (329.63, 200), (349.23, 200),
            (392.00, 250), (349.23, 200), (329.63, 200),
            (293.66, 400),
        ],
        'initiative_roll': [
            # Drumroll tension — rapid repeated notes then resolution
            (392.00, 50), (392.00, 50), (392.00, 50), (392.00, 50),
            (392.00, 50), (392.00, 50), (0, 40),
            (523.25, 80), (659.25, 80), (783.99, 350),
        ],
        'bard_flourish': [
            # Quick melodic run — showing off
            (523.25, 60), (587.33, 60), (659.25, 60), (698.46, 60),
            (783.99, 60), (880.00, 60), (783.99, 60),
            (659.25, 60), (783.99, 350),
        ],
        'dungeon_door': [
            # Heavy creaking open — low ominous then reveal
            (146.83, 200), (0, 60), (155.56, 200), (0, 60),
            (164.81, 200), (0, 80), (329.63, 150), (440.00, 300),
        ],
    },
```

- [ ] **Step 2: Verify melody generation**

```bash
python3 generate_sounds.py --melodies-only --theme dnd
```

Expected: 10 melody WAVs created in `sounds/dnd/`, each ≤2s.

- [ ] **Step 3: Commit**

```bash
git add generate_sounds.py sounds/dnd/
git commit -m "feat: add D&D melody theme (10 melodies)"
```

---

## Chunk 2: Generator Refactor — Speech from JSON + ElevenLabs

### Task 4: Refactor generate_sounds.py to read speech phrases from JSON

**Files:**
- Modify: `generate_sounds.py:1-14` (add `json` import)
- Modify: `generate_sounds.py:488-498` (replace inline `SPEECH_PHRASES` with JSON loader)
- Modify: `generate_sounds.py:588-625` (update `generate_speech` to use new phrase structure)
- Modify: `generate_sounds.py:633-655` (update CLI with new flags)

- [ ] **Step 1: Add json import and SPEECH_PHRASES_FILE constant**

At `generate_sounds.py:5`, add `import json` after `import argparse`. At line 14 after `SOUNDS_DIR`, add:

```python
SPEECH_PHRASES_FILE = Path(__file__).parent / 'speech_phrases.json'
```

- [ ] **Step 2: Replace inline SPEECH_PHRASES with JSON loader**

Replace lines 488-503 (the `SPEECH_PHRASES` dict, the for loop, and `POLLY_VOICES`) with:

```python
def load_speech_phrases() -> dict:
    """Load speech phrases from speech_phrases.json."""
    with open(SPEECH_PHRASES_FILE) as f:
        return json.load(f)


def expand_phrases(phrases: dict, theme: str) -> dict[str, str]:
    """Expand a theme's phrases into numbered {name}_{idx} -> text mappings.

    Falls back to 'default' theme if the requested theme has no speech entry.
    Expands {window} templates for window indices 0-9.
    """
    theme_phrases = phrases.get(theme, phrases['default'])
    result: dict[str, str] = {}

    for event_type in ('stop', 'notification'):
        for idx, text in enumerate(theme_phrases.get(event_type, phrases['default'][event_type])):
            result[f'{event_type}_{idx}'] = text

    for event_type in ('stop_window', 'notification_window'):
        templates = theme_phrases.get(event_type, phrases['default'][event_type])
        for win_idx in range(10):
            for idx, template in enumerate(templates):
                text = template.replace('{window}', str(win_idx))
                result[f'{event_type}_{win_idx}_{idx}'] = text

    return result


POLLY_VOICES: dict[str, str] = {
    'male': 'Matthew',
    'female': 'Joanna',
}
```

- [ ] **Step 3: Update generate_speech (Polly) to use new phrase structure**

Replace the `generate_speech` function (lines 588-625) with:

```python
def generate_speech_polly(gender_filter: str | None = None, theme_filter: str | None = None) -> None:
    """Generate TTS speech WAV files using AWS Polly."""
    phrases = load_speech_phrases()
    genders = {gender_filter: POLLY_VOICES[gender_filter]} if gender_filter else POLLY_VOICES
    themes_to_gen = [theme_filter] if theme_filter else list(phrases.keys())

    for gender, voice_id in genders.items():
        for theme in themes_to_gen:
            expanded = expand_phrases(phrases, theme)
            speech_dir = SOUNDS_DIR / 'speech' / gender / theme
            speech_dir.mkdir(parents=True, exist_ok=True)
            count = 0

            for name, text in expanded.items():
                wav_path = speech_dir / f'{name}.wav'

                with tempfile.NamedTemporaryFile(suffix='.pcm', delete=False) as tmp:
                    tmp_path = Path(tmp.name)

                try:
                    result = subprocess.run(
                        [
                            'aws', 'polly', 'synthesize-speech',
                            '--engine', 'generative',
                            '--voice-id', voice_id,
                            '--output-format', 'pcm',
                            '--sample-rate', str(POLLY_SAMPLE_RATE),
                            '--text', text,
                            str(tmp_path),
                        ],
                        capture_output=True, text=True,
                    )
                    if result.returncode != 0:
                        print(f'  ERROR: Polly failed for {name}: {result.stderr.strip()}')
                        continue

                    wrap_pcm_in_wav(tmp_path, wav_path)
                    count += 1
                finally:
                    tmp_path.unlink(missing_ok=True)

            print(f'  -> {count} speech files ({gender}/{voice_id}) in speech/{gender}/{theme}/\n')
```

- [ ] **Step 4: Update CLI in main()**

Replace the `main` function (lines 633-655) with:

```python
def main() -> None:
    all_themes = list(THEMES.keys())
    parser = argparse.ArgumentParser(description='Generate bells-and-whistles notification sounds')
    parser.add_argument('--melodies-only', action='store_true', help='Only generate melodies')
    parser.add_argument('--speech-only', action='store_true', help='Only generate speech')
    parser.add_argument('--theme', choices=all_themes, help='Generate only one theme')
    parser.add_argument('--gender', choices=['male', 'female'], help='Generate only one gender (Polly)')
    parser.add_argument('--tts-provider', choices=['polly', 'elevenlabs'], default='polly',
                        help='TTS provider for speech generation (default: polly)')
    parser.add_argument('--api-key', help='ElevenLabs API key')
    parser.add_argument('--voice-id', help='ElevenLabs voice ID')
    args = parser.parse_args()

    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

    if not args.speech_only:
        print('=== Generating melodies ===\n')
        generate_melodies(args.theme)

    if not args.melodies_only:
        if args.tts_provider == 'elevenlabs':
            if not args.api_key or not args.voice_id:
                parser.error('--api-key and --voice-id are required for ElevenLabs')
            print('=== Generating speech (ElevenLabs) ===\n')
            generate_speech_elevenlabs(args.api_key, args.voice_id, args.theme)
        else:
            print('=== Generating speech (AWS Polly) ===\n')
            generate_speech_polly(args.gender, args.theme)

    print('Done!')
```

- [ ] **Step 5: Verify Polly path still works (dry run)**

```bash
python3 generate_sounds.py --melodies-only --theme beeps
```

Expected: Generates beeps melodies without errors (proves the refactored code at least parses).

- [ ] **Step 6: Commit**

```bash
git add generate_sounds.py
git commit -m "refactor: read speech phrases from JSON, support per-theme phrase generation"
```

### Task 5: Add ElevenLabs speech generation function

**Files:**
- Modify: `generate_sounds.py` (add `import json as json_mod` for urllib body encoding, add `import shutil` for ffmpeg check, add `generate_speech_elevenlabs` function after `generate_speech_polly`)

- [ ] **Step 1: Add imports**

At the top of `generate_sounds.py`, add after existing imports:

```python
import json as json_mod  # aliased to avoid shadowing the json we use for phrases
import shutil
import urllib.request
import urllib.error
```

Note: rename the existing `import json` (added in Task 4) to just use `json` for phrases too. Actually simpler: just use `json` for both — no alias needed since there's no name conflict. Add `shutil`, `urllib.request`, `urllib.error` to imports.

- [ ] **Step 2: Add generate_speech_elevenlabs function**

Add after `generate_speech_polly`:

```python
def generate_speech_elevenlabs(api_key: str, voice_id: str, theme_filter: str | None = None) -> None:
    """Generate TTS speech WAV files using ElevenLabs API."""
    if not shutil.which('ffmpeg'):
        print('  ERROR: ffmpeg not found. Install ffmpeg to generate ElevenLabs speech.')
        print('  Skipping speech generation.\n')
        return

    phrases = load_speech_phrases()
    themes_to_gen = [theme_filter] if theme_filter else list(phrases.keys())

    for theme in themes_to_gen:
        expanded = expand_phrases(phrases, theme)
        speech_dir = SOUNDS_DIR / 'speech' / 'elevenlabs' / voice_id / theme
        speech_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for name, text in expanded.items():
            wav_path = speech_dir / f'{name}.wav'

            try:
                url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
                body = json.dumps({
                    'text': text,
                    'model_id': 'eleven_multilingual_v2',
                }).encode()
                req = urllib.request.Request(
                    url,
                    data=body,
                    headers={
                        'xi-api-key': api_key,
                        'Content-Type': 'application/json',
                        'Accept': 'audio/mpeg',
                    },
                )
                with urllib.request.urlopen(req) as resp:
                    mp3_data = resp.read()

            except urllib.error.HTTPError as e:
                print(f'  ERROR: ElevenLabs API error for "{name}": {e.code} {e.reason}')
                continue
            except urllib.error.URLError as e:
                print(f'  ERROR: Network error for "{name}": {e.reason}')
                continue

            # Write MP3 to temp file, convert to WAV with ffmpeg
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(mp3_data)

            try:
                result = subprocess.run(
                    [
                        'ffmpeg', '-y', '-i', str(tmp_path),
                        '-ar', str(POLLY_SAMPLE_RATE),
                        '-ac', '1',
                        '-sample_fmt', 's16',
                        '-f', 'wav',
                        str(wav_path),
                    ],
                    capture_output=True, text=True,
                )
                if result.returncode != 0:
                    print(f'  ERROR: ffmpeg conversion failed for {name}: {result.stderr.strip()}')
                    continue

                count += 1
            finally:
                tmp_path.unlink(missing_ok=True)

        print(f'  -> {count} speech files (elevenlabs/{voice_id}) in speech/elevenlabs/{voice_id}/{theme}/\n')
```

- [ ] **Step 3: Verify the script parses**

```bash
python3 -c "import generate_sounds; print('OK')"
```

Expected: `OK` (no import errors).

- [ ] **Step 4: Verify ElevenLabs CLI flag validation**

```bash
python3 generate_sounds.py --speech-only --tts-provider elevenlabs 2>&1 | head -5
```

Expected: Error message about `--api-key and --voice-id are required`.

- [ ] **Step 5: Commit**

```bash
git add generate_sounds.py
git commit -m "feat: add ElevenLabs TTS speech generation via REST API + ffmpeg"
```

---

## Chunk 3: Runtime — notify-sound.sh Updates

### Task 6: Update notify-sound.sh for themed + randomized speech and ElevenLabs paths

**Files:**
- Modify: `hooks/notify-sound.sh:14-50` (config parsing and speech lookup)

- [ ] **Step 1: Update config parsing to extract TTS provider and voice ID**

Replace lines 14-25 (the config parsing block) with:

```bash
if [ -f "$CONFIG" ]; then
    eval "$(python3 -c "
import json, sys
c = json.load(open(sys.argv[1]))
print(f\"THEME={c.get('theme','beeps')}\")
print(f\"MODE={c.get('mode','sound_and_voice')}\")
print(f\"GENDER={c.get('gender','male')}\")
print(f\"TTS_PROVIDER={c.get('tts_provider','polly')}\")
print(f\"ELEVENLABS_VOICE_ID={c.get('elevenlabs_voice_id','')}\")
" "$CONFIG" 2>/dev/null)"
fi
THEME="${THEME:-beeps}"
MODE="${MODE:-sound_and_voice}"
GENDER="${GENDER:-male}"
TTS_PROVIDER="${TTS_PROVIDER:-polly}"
ELEVENLABS_VOICE_ID="${ELEVENLABS_VOICE_ID:-}"
```

- [ ] **Step 2: Replace speech lookup with theme-aware random selection**

Replace lines 33-50 (the speech WAV lookup block) with:

```bash
# Resolve speech base directory based on TTS provider
if [ "$TTS_PROVIDER" = "elevenlabs" ] && [ -n "$ELEVENLABS_VOICE_ID" ]; then
    SPEECH_BASE="$SOUNDS_DIR/speech/elevenlabs/$ELEVENLABS_VOICE_ID"
else
    SPEECH_BASE="$SOUNDS_DIR/speech/$GENDER"
fi

# Determine speech theme directory (try theme-specific, fall back to default)
if [ -d "$SPEECH_BASE/$THEME" ]; then
    SPEECH_DIR="$SPEECH_BASE/$THEME"
elif [ -d "$SPEECH_BASE/default" ]; then
    SPEECH_DIR="$SPEECH_BASE/default"
else
    SPEECH_DIR=""
fi

# Pick a random speech WAV
SPEECH=""
if [ "$MODE" != "sound_only" ] && [ -n "$SPEECH_DIR" ]; then
    if [ "$1" = "stop" ]; then
        PREFIX="stop"
    else
        PREFIX="notification"
    fi

    # Try window-specific phrases first
    if [ -n "$WIN" ]; then
        SPEECH_WAVS=("$SPEECH_DIR"/${PREFIX}_window_${WIN}_*.wav)
        if [ ${#SPEECH_WAVS[@]} -gt 0 ] && [ -f "${SPEECH_WAVS[0]}" ]; then
            SPEECH="${SPEECH_WAVS[$((RANDOM % ${#SPEECH_WAVS[@]}))]}"
        fi
    fi

    # Fall back to non-window phrases
    if [ -z "$SPEECH" ]; then
        SPEECH_WAVS=("$SPEECH_DIR"/${PREFIX}_[0-9]*.wav)
        if [ ${#SPEECH_WAVS[@]} -gt 0 ] && [ -f "${SPEECH_WAVS[0]}" ]; then
            SPEECH="${SPEECH_WAVS[$((RANDOM % ${#SPEECH_WAVS[@]}))]}"
        fi
    fi
fi
```

- [ ] **Step 3: Test the script runs without errors (dry run)**

```bash
bash hooks/notify-sound.sh stop
```

Expected: Plays a melody (or beeps if no theme configured). No bash errors. Speech may be skipped if speech files haven't been regenerated into the new directory structure yet.

- [ ] **Step 4: Commit**

```bash
git add hooks/notify-sound.sh
git commit -m "feat: support ElevenLabs paths, per-theme speech dirs, and random phrase selection"
```

---

## Chunk 4: Configuration + Documentation

### Task 7: Update configure-bells-and-whistles.md

**Files:**
- Modify: `commands/configure-bells-and-whistles.md`

- [ ] **Step 1: Rewrite the configure command**

Replace the entire contents of `commands/configure-bells-and-whistles.md` with:

```markdown
---
description: Install and configure bells-and-whistles notification sounds
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
---

You are the bells-and-whistles installer. Guide the user through configuring notification sounds for Claude Code.

## Steps

### 1. Ask notification mode
Use AskUserQuestion to ask:
- Question: "How should bells-and-whistles notify you?"
- Options: ["Sound + Voice", "Sound only", "Voice only"]

Map the response:
- "Sound + Voice" → `sound_and_voice`
- "Sound only" → `sound_only`
- "Voice only" → `voice_only`

### 2. Ask TTS provider (if voice enabled)
If the mode includes voice (`sound_and_voice` or `voice_only`), use AskUserQuestion:
- Question: "Which text-to-speech provider?"
- Options: ["AWS Polly (default)", "ElevenLabs"]

Map: "AWS Polly (default)" → `polly`, "ElevenLabs" → `elevenlabs`

If mode is `sound_only`, default to `polly`.

### 3a. If Polly: Ask voice gender
Use AskUserQuestion:
- Question: "Which voice?"
- Options: ["Male (Matthew)", "Female (Joanna)"]

Map: "Male (Matthew)" → `male`, "Female (Joanna)" → `female`

### 3b. If ElevenLabs: Ask for API key and voice ID
Use AskUserQuestion:
- Question: "Enter your ElevenLabs API key (from elevenlabs.io/app/settings/api-keys):"

Then use AskUserQuestion:
- Question: "Enter your ElevenLabs voice ID (from elevenlabs.io/app/voice-library):"

### 4. Ask theme
Use AskUserQuestion:
- Question: "Pick a notification sound theme:"
- Options: ["Videogame", "Disney Adults", "Anime", "Movie Addicts", "90s Rock", "Classical Music", "Beeps/Tones", "Chirps", "Cyberpunk 2077", "D&D / Fantasy"]

Map:
- "Videogame" → `videogame`
- "Disney Adults" → `disney`
- "Anime" → `anime`
- "Movie Addicts" → `movies`
- "90s Rock" → `90s_rock`
- "Classical Music" → `classical`
- "Beeps/Tones" → `beeps`
- "Chirps" → `chirps`
- "Cyberpunk 2077" → `cyberpunk`
- "D&D / Fantasy" → `dnd`

### 5. Write config
Write `${CLAUDE_PLUGIN_ROOT}/config.json`.

If Polly:
```json
{
  "mode": "<selected_mode>",
  "tts_provider": "polly",
  "gender": "<selected_gender>",
  "theme": "<selected_theme>"
}
```

If ElevenLabs:
```json
{
  "mode": "<selected_mode>",
  "tts_provider": "elevenlabs",
  "elevenlabs_api_key": "<api_key>",
  "elevenlabs_voice_id": "<voice_id>",
  "theme": "<selected_theme>"
}
```

### 6. Clean up old hooks
Read `~/.claude/settings.json`. If it contains hook entries under `Stop` or `Notification` that reference `~/.claude/hooks/notify-sound.sh`, remove those specific entries (but preserve any other hooks and all other settings). Write back the cleaned file.

### 7. Summary
Print a summary:
- Theme: <display name>
- Mode: <display name>
- TTS Provider: <display name>
- Voice: <gender or voice ID> (if applicable)
- Number of melody files available
- Number of speech files available
- Whether old hooks were cleaned up

Tell the user the plugin is now active and will play sounds on Stop and Notification events. If this is a fresh install, they may need to restart Claude Code and accept the plugin.
```

- [ ] **Step 2: Commit**

```bash
git add commands/configure-bells-and-whistles.md
git commit -m "feat: add ElevenLabs provider and new themes to configure command"
```

### Task 8: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the theme table**

Add Cyberpunk and D&D to the theme table (after the Chirps row):

```markdown
| **Cyberpunk 2077** | Neon synth drones, netrunner arpeggios, corpo alerts, braindance glitches |
| **D&D / Fantasy** | Tavern lutes, quest fanfares, spell casts, critical hits, dragon roars |
```

- [ ] **Step 2: Update the Voice section**

Replace the Voice section with:

```markdown
## Voice

Voice announcements use either **AWS Polly** (Matthew or Joanna) or **ElevenLabs**
(bring your own voice ID). If you run tmux, the voice tells you *which window*
finished — useful when you have six agents running and zero idea which one just
spoke up.

Voice is optional. The plugin ships pre-generated WAV files and works fine
without any TTS credentials.

### ElevenLabs setup

1. Get an API key from [elevenlabs.io/app/settings/api-keys](https://elevenlabs.io/app/settings/api-keys)
2. Pick a voice from the [Voice Library](https://elevenlabs.io/app/voice-library) and copy its voice ID
3. Run `/configure-bells-and-whistles` and select ElevenLabs as the TTS provider
4. Generate speech files:

```
python3 generate_sounds.py --speech-only --tts-provider elevenlabs --api-key YOUR_KEY --voice-id YOUR_VOICE_ID
```

Requires `ffmpeg` installed for MP3→WAV conversion.
```

- [ ] **Step 3: Update the Configuration section**

Replace the config JSON example and field docs:

```markdown
## Configuration

Edit `config.json` directly if you prefer:

```json
{
  "mode": "sound_and_voice",
  "tts_provider": "elevenlabs",
  "elevenlabs_api_key": "sk-...",
  "elevenlabs_voice_id": "pNInz6obpgDQGcFmaJgB",
  "theme": "cyberpunk"
}
```

**mode** — `sound_and_voice`, `sound_only`, or `voice_only`
**tts_provider** — `polly` (default) or `elevenlabs`
**gender** — `male` or `female` (Polly only)
**elevenlabs_api_key** — your ElevenLabs API key (ElevenLabs only)
**elevenlabs_voice_id** — your ElevenLabs voice ID (ElevenLabs only)
**theme** — one of: `videogame`, `disney`, `anime`, `movies`, `90s_rock`,
`classical`, `beeps`, `chirps`, `cyberpunk`, `dnd`
```

- [ ] **Step 4: Update the "Regenerating sounds" section**

Replace with:

```markdown
## Regenerating sounds

The pre-generated WAV files live in `sounds/`. To regenerate melodies (no
dependencies beyond Python 3):

```
python3 generate_sounds.py --melodies-only
```

To regenerate speech files with AWS Polly:

```
python3 generate_sounds.py --speech-only --tts-provider polly
```

To regenerate speech files with ElevenLabs (requires `ffmpeg`):

```
python3 generate_sounds.py --speech-only --tts-provider elevenlabs --api-key YOUR_KEY --voice-id YOUR_VOICE_ID
```

You can narrow the scope with `--theme` and `--gender` (Polly).

## Customizing speech phrases

Edit `speech_phrases.json` to change what the voice says. Each theme has arrays
of phrases for `stop`, `notification`, `stop_window`, and `notification_window`
events. Use `{window}` as a placeholder for the tmux window number. After editing,
regenerate speech files.
```

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: add ElevenLabs setup, new themes, and speech customization to README"
```

### Task 9: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update CLAUDE.md**

Update the Architecture section to mention `speech_phrases.json`. Update the Common Commands section to include ElevenLabs generation. Update Key Conventions to mention the new themes. Specifically:

In the Architecture bullet list, after the `config.json` bullet, add:
```
- **speech_phrases.json**: Editable speech phrase definitions per theme. Read at generation time only (not at runtime). Contains `stop`, `notification`, `stop_window`, `notification_window` phrase arrays per theme with `{window}` template support.
```

In the Common Commands section, add after the existing commands:
```bash
# Regenerate speech with ElevenLabs (requires ffmpeg)
python3 generate_sounds.py --speech-only --tts-provider elevenlabs --api-key KEY --voice-id ID

# Regenerate speech for one theme with ElevenLabs
python3 generate_sounds.py --speech-only --tts-provider elevenlabs --api-key KEY --voice-id ID --theme cyberpunk
```

In Key Conventions, update the themes list:
- Change "Each theme must have exactly 10 melodies." to "Each theme has exactly 10 melodies. Current themes: videogame, disney, anime, movies, 90s_rock, classical, beeps, chirps, cyberpunk, dnd."
- Add: "Speech phrases are defined in `speech_phrases.json`, not hardcoded in Python."
- Add: "ElevenLabs speech generation requires `ffmpeg` for MP3→WAV conversion."

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with ElevenLabs, speech_phrases.json, and new themes"
```

### Task 10: Update docstring in generate_sounds.py

**Files:**
- Modify: `generate_sounds.py:2`

- [ ] **Step 1: Update module docstring**

Change line 2 from:
```python
"""Generate notification melodies (7 themes x 10) and AWS Polly speech WAVs."""
```
to:
```python
"""Generate notification melodies (10 themes x 10) and TTS speech WAVs (Polly or ElevenLabs)."""
```

- [ ] **Step 2: Commit**

```bash
git add generate_sounds.py
git commit -m "chore: update generate_sounds.py docstring for new theme count and providers"
```
