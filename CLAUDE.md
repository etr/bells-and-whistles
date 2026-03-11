# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

bells-and-whistles is a Claude Code plugin that plays notification sounds (and optional voice announcements via AWS Polly) when Claude Code fires **Stop** or **Notification** events. It ships pre-generated WAV files and works without any external dependencies beyond a system audio player.

## Architecture

- **Plugin manifest**: `.claude-plugin/plugin.json` — declares the plugin name/version for Claude Code.
- **Hooks**: `hooks/hooks.json` registers shell hooks for `Stop` and `Notification` (permission_prompt, elicitation_dialog) events. These invoke `hooks/notify-sound.sh` with `stop` or `notification` as the argument.
- **notify-sound.sh**: Main runtime script. Reads `config.json`, picks a random melody WAV from the selected theme, optionally queues a speech WAV, and plays them via platform-specific commands (`afplay` on macOS, `aplay`/`paplay` on Linux, `powershell.exe` on WSL, terminal bell over SSH). Drains stdin first since hooks receive JSON on stdin.
- **config.json**: User configuration — `mode` (sound_and_voice | sound_only | voice_only), `gender` (male | female), `theme` (videogame | disney | anime | movies | 90s_rock | classical | beeps | chirps).
- **speech_phrases.json**: Editable speech phrase definitions per theme. Read at generation time only (not at runtime). Contains `stop`, `notification`, `stop_window`, `notification_window` phrase arrays per theme with `{window}` template support.
- **generate_sounds.py**: Pure-Python WAV generator (no dependencies beyond stdlib). Defines all melody note sequences as `(freq_hz, duration_ms)` tuples in the `THEMES` dict. Also generates speech WAVs via AWS Polly CLI.
- **commands/configure-bells-and-whistles.md**: Slash command definition that walks users through interactive setup.
- **sounds/**: Pre-generated WAVs organized as `sounds/<theme>/<melody>.wav` and `sounds/speech/<gender>/<phrase>.wav`. 8 themes × 10 melodies each, plus speech files for stop/notification with tmux window variants.

## Common Commands

```bash
# Regenerate melody WAVs (no dependencies beyond Python 3)
python3 generate_sounds.py --melodies-only

# Regenerate only one theme
python3 generate_sounds.py --melodies-only --theme videogame

# Regenerate speech WAVs (requires AWS CLI with Polly access)
python3 generate_sounds.py --speech-only

# Regenerate speech for one gender
python3 generate_sounds.py --speech-only --gender male

# Regenerate everything
python3 generate_sounds.py

# Regenerate speech with ElevenLabs (requires ffmpeg)
python3 generate_sounds.py --speech-only --tts-provider elevenlabs --api-key KEY --voice-id ID

# Regenerate speech for one theme with ElevenLabs
python3 generate_sounds.py --speech-only --tts-provider elevenlabs --api-key KEY --voice-id ID --theme cyberpunk
```

## Key Conventions

- Melodies must be ≤2 seconds. Shorter is preferred.
- Melody definitions are `list[tuple[float, int]]` where freq=0 means silence.
- Each theme has exactly 10 melodies. Current themes: videogame, disney, anime, movies, 90s_rock, classical, beeps, chirps, cyberpunk, dnd.
- Speech uses AWS Polly `generative` engine with voices Matthew (male) and Joanna (female).
- WAV files are 16-bit mono at 44100 Hz (melodies) or 16000 Hz (speech/Polly).
- The plugin uses `$CLAUDE_PLUGIN_ROOT` to resolve paths at runtime.
- Speech phrases are defined in `speech_phrases.json`, not hardcoded in Python.
- ElevenLabs speech generation requires `ffmpeg` for MP3→WAV conversion.
