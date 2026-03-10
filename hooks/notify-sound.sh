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
" "$CONFIG" 2>/dev/null)"
fi
THEME="${THEME:-beeps}"
MODE="${MODE:-sound_and_voice}"
GENDER="${GENDER:-male}"

SOUNDS_DIR="$PLUGIN_ROOT/sounds"

# Get tmux window index if in tmux
WIN=""
[ -n "$TMUX_PANE" ] && WIN=$(tmux display-message -t "$TMUX_PANE" -p '#{window_index}' 2>/dev/null)

# Determine speech WAV based on event type ($1: "stop" or "notification")
SPEECH_DIR="$SOUNDS_DIR/speech/$GENDER"
SPEECH=""
if [ "$MODE" != "sound_only" ]; then
    if [ "$1" = "stop" ]; then
        if [ -n "$WIN" ] && [ -f "$SPEECH_DIR/stop_window_${WIN}.wav" ]; then
            SPEECH="$SPEECH_DIR/stop_window_${WIN}.wav"
        elif [ -f "$SPEECH_DIR/stop.wav" ]; then
            SPEECH="$SPEECH_DIR/stop.wav"
        fi
    else
        if [ -n "$WIN" ] && [ -f "$SPEECH_DIR/notification_window_${WIN}.wav" ]; then
            SPEECH="$SPEECH_DIR/notification_window_${WIN}.wav"
        elif [ -f "$SPEECH_DIR/notification.wav" ]; then
            SPEECH="$SPEECH_DIR/notification.wav"
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
