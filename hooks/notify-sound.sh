#!/bin/bash
# Play a notification melody + optional TTS speech when Claude Code needs attention.
# Cross-platform: WSL, macOS, native Linux. Falls back to terminal bell over SSH.
# Reads config from $CLAUDE_PLUGIN_ROOT/config.json for theme, mode, and gender.

# Read hook JSON from stdin
HOOK_JSON=$(cat)

# For stop events: skip sub-agents and plan-mode exits
if [ "$1" = "stop" ]; then
    # Skip completion sound for sub-agents (only main agent should notify)
    AGENT_ID=$(python3 -c "
import json, sys
d = json.loads(sys.argv[1])
print(d.get('agent_id', ''))
" "$HOOK_JSON" 2>/dev/null)
    if [ -n "$AGENT_ID" ]; then
        exit 0
    fi

    # Skip when exiting plan mode (not a real job completion)
    TRANSCRIPT=$(python3 -c "
import json, sys, os
d = json.loads(sys.argv[1])
p = d.get('transcript_path', '')
print(os.path.expanduser(p))
" "$HOOK_JSON" 2>/dev/null)
    if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
        if tail -n 5 "$TRANSCRIPT" | grep -q 'ExitPlanMode'; then
            exit 0
        fi
    fi
fi

# Resolve plugin root
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(readlink -f "$BASH_SOURCE")")")}"

# Mute state lives one level above the versioned plugin root so it survives upgrades
MUTE_DIR="${PLUGIN_ROOT}/.."

# Exit if globally muted
[ -f "$MUTE_DIR/.mute_all" ] && exit 0

# Read config (defaults: theme=beeps, mode=sound_and_voice, accent=us, gender=male, voice_style=full_sentence)
CONFIG="$PLUGIN_ROOT/config.json"
if [ -f "$CONFIG" ]; then
    eval "$(python3 -c "
import json, shlex, sys
c = json.load(open(sys.argv[1]))
print(f'THEME={shlex.quote(c.get(\"theme\",\"beeps\"))}')
print(f'MODE={shlex.quote(c.get(\"mode\",\"sound_and_voice\"))}')
print(f'ACCENT={shlex.quote(c.get(\"accent\",\"us\"))}')
print(f'GENDER={shlex.quote(c.get(\"gender\",\"male\"))}')
print(f'VOICE_STYLE={shlex.quote(c.get(\"voice_style\",\"full_sentence\"))}')
print(f'USE_THEMED_PHRASES={shlex.quote(str(c.get(\"use_themed_phrases\",False)).lower())}')
print(f'WSL_POWERSHELL_PATH={shlex.quote(c.get(\"wsl_powershell_path\",\"\"))}')
" "$CONFIG" 2>/dev/null)"
fi
THEME="${THEME:-beeps}"
MODE="${MODE:-sound_and_voice}"
ACCENT="${ACCENT:-us}"
GENDER="${GENDER:-male}"
VOICE_STYLE="${VOICE_STYLE:-full_sentence}"
USE_THEMED_PHRASES="${USE_THEMED_PHRASES:-false}"

SOUNDS_DIR="$PLUGIN_ROOT/sounds"

# Get TTY for this session and check per-session mute
MY_TTY=""
if [ -n "$TMUX_PANE" ]; then
    MY_TTY=$(tmux display-message -t "$TMUX_PANE" -p '#{pane_tty}' 2>/dev/null)
else
    _pid=$$
    while [ "$_pid" -gt 1 ]; do
        _raw=$(ps -o tty= -p "$_pid" 2>/dev/null | tr -d ' ')
        if [ -n "$_raw" ] && [ "$_raw" != "?" ]; then
            MY_TTY="/dev/$_raw"
            break
        fi
        _new_pid=$(ps -o ppid= -p "$_pid" 2>/dev/null | tr -d ' ')
        [ "$_new_pid" = "$_pid" ] && break
        _pid="$_new_pid"
    done
fi
if [ -n "$MY_TTY" ]; then
    TTY_ID=$(echo "$MY_TTY" | sed 's|^/dev/||; s|/|_|g')
    [ -f "$MUTE_DIR/.mute_tty_${TTY_ID}" ] && exit 0
fi

# Get tmux window index (for speech file selection only)
WIN=""
[ -n "$TMUX_PANE" ] && WIN=$(tmux display-message -t "$TMUX_PANE" -p '#{window_index}' 2>/dev/null)

# Resolve speech directory based on themed/standard preference
if [ "$USE_THEMED_PHRASES" = "true" ] && [ -d "$SOUNDS_DIR/speech/themed/$THEME" ]; then
    SPEECH_DIR="$SOUNDS_DIR/speech/themed/$THEME"
else
    SPEECH_DIR="$SOUNDS_DIR/speech/$ACCENT/$GENDER"
fi

# Pick a speech WAV
SPEECH=""
if [ "$MODE" != "sound_only" ] && [ -d "$SPEECH_DIR" ]; then
    if [ "$VOICE_STYLE" = "number_only" ]; then
        # Number-only mode: just announce the window number (no speech if not in tmux)
        if [ -n "$WIN" ] && [ -f "$SPEECH_DIR/number_${WIN}.wav" ]; then
            SPEECH="$SPEECH_DIR/number_${WIN}.wav"
        fi
    else
        # Full sentence mode (default) — random phrase selection
        if [ "$1" = "stop" ]; then
            PREFIX="stop"
        else
            PREFIX="notification"
        fi

        # Try window-specific phrases first (randomized)
        if [ -n "$WIN" ]; then
            SPEECH_WAVS=("$SPEECH_DIR"/${PREFIX}_window_${WIN}_*.wav)
            if [ ${#SPEECH_WAVS[@]} -gt 0 ] && [ -f "${SPEECH_WAVS[0]}" ]; then
                SPEECH="${SPEECH_WAVS[$((RANDOM % ${#SPEECH_WAVS[@]}))]}"
            fi
        fi

        # Fall back to non-window phrases (randomized)
        if [ -z "$SPEECH" ]; then
            SPEECH_WAVS=("$SPEECH_DIR"/${PREFIX}_[0-9]*.wav)
            if [ ${#SPEECH_WAVS[@]} -gt 0 ] && [ -f "${SPEECH_WAVS[0]}" ]; then
                SPEECH="${SPEECH_WAVS[$((RANDOM % ${#SPEECH_WAVS[@]}))]}"
            fi
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

# Resolve powershell.exe for WSL
if [ "$PLAT" = "wsl" ]; then
    POWERSHELL="${WSL_POWERSHELL_PATH:-}"
    if [ -z "$POWERSHELL" ] || [ ! -x "$POWERSHELL" ]; then
        POWERSHELL=$(command -v powershell.exe 2>/dev/null || true)
    fi
    if [ -z "$POWERSHELL" ]; then
        for _ps in /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe \
                   /mnt/c/Windows/SysWOW64/WindowsPowerShell/v1.0/powershell.exe; do
            [ -x "$_ps" ] && POWERSHELL="$_ps" && break
        done
    fi
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
    if [ "$PLAT" = "wsl" ] && [ -n "$POWERSHELL" ]; then
        "$POWERSHELL" -NoProfile -Command "[Console]::Beep(600,150);[Console]::Beep(800,150)" &>/dev/null &
    else
        printf '\a'
    fi
    exit 0
fi

# Build and run playback command
case $PLAT in
    wsl)
        if [ -n "$POWERSHELL" ]; then
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
            "$POWERSHELL" -NoProfile -Command "$CMD" &>/dev/null &
        else
            printf '\a'
        fi
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
