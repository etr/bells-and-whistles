#!/bin/bash
# Play a notification melody + optional TTS speech when Claude Code needs attention.
# Cross-platform: WSL, macOS, native Linux. Falls back to terminal bell over SSH.
# Reads config from $CLAUDE_PLUGIN_ROOT/config.json for theme, mode, and gender.

# Drain stdin (hook receives JSON on stdin)
cat > /dev/null 2>/dev/null &

# Resolve plugin root
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(readlink -f "$BASH_SOURCE")")")}"

# Read config (defaults: theme=beeps, mode=sound_and_voice, gender=male)
CONFIG="$PLUGIN_ROOT/config.json"
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

SOUNDS_DIR="$PLUGIN_ROOT/sounds"

# Get tmux window index if in tmux
WIN=""
[ -n "$TMUX_PANE" ] && WIN=$(tmux display-message -t "$TMUX_PANE" -p '#{window_index}' 2>/dev/null)

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

# Platform detection
if grep -qiE 'microsoft|wsl' /proc/version 2>/dev/null; then
    PLAT=wsl
elif [ "$(uname)" = "Darwin" ]; then
    PLAT=mac
else
    PLAT=linux
fi

# SSH fallback: just bell (skip for WSL — SSH_CONNECTION is always set)
if [ -n "$SSH_CONNECTION" ] && [ "$PLAT" != "wsl" ]; then
    printf '\a'
    exit 0
fi

# Pick a random melody WAV from the theme directory
MELODY=""
if [ "$MODE" != "voice_only" ]; then
    THEME_DIR="$SOUNDS_DIR/$THEME"
    if [ -d "$THEME_DIR" ]; then
        WAVS=("$THEME_DIR"/*.wav)
        if [ ${#WAVS[@]} -gt 0 ] && [ -f "${WAVS[0]}" ]; then
            MELODY="${WAVS[$((RANDOM % ${#WAVS[@]}))]}"
        fi
    fi
fi

# Nothing to play — beep and exit
if [ -z "$MELODY" ] && [ -z "$SPEECH" ]; then
    if [ "$PLAT" = "wsl" ]; then
        powershell.exe -NoProfile -Command "[Console]::Beep(600,150);[Console]::Beep(800,150)" &>/dev/null &
    else
        printf '\a'
    fi
    exit 0
fi

# Build and run playback command
case $PLAT in
    wsl)
        CMD=""
        if [ -n "$MELODY" ]; then
            WIN_MELODY=$(wslpath -w "$MELODY")
            CMD="(New-Object System.Media.SoundPlayer '$WIN_MELODY').PlaySync()"
        fi
        if [ -n "$SPEECH" ]; then
            WIN_SPEECH=$(wslpath -w "$SPEECH")
            [ -n "$CMD" ] && CMD="$CMD; "
            CMD="${CMD}(New-Object System.Media.SoundPlayer '$WIN_SPEECH').PlaySync()"
        fi
        powershell.exe -NoProfile -Command "$CMD" &>/dev/null &
        ;;
    mac)
        ([ -n "$MELODY" ] && afplay "$MELODY" 2>/dev/null
         [ -n "$SPEECH" ] && afplay "$SPEECH" 2>/dev/null) &
        ;;
    linux)
        ([ -n "$MELODY" ] && { aplay -q "$MELODY" 2>/dev/null || paplay "$MELODY" 2>/dev/null; }
         [ -n "$SPEECH" ] && { aplay -q "$SPEECH" 2>/dev/null || paplay "$SPEECH" 2>/dev/null; }) &
        ;;
esac

exit 0
