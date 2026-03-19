---
description: Unmute notification sounds globally or for the current session/tab
allowed-tools:
  - Bash
  - AskUserQuestion
---

You are the bells-and-whistles unmute command. Unmute notification sounds globally or for the current session/tmux tab.

## Steps

### 1. Detect environment

Run these bash commands to gather state:

```bash
# Mute state lives one level above the versioned plugin root so it survives upgrades
MUTE_DIR="${CLAUDE_PLUGIN_ROOT}/.."

# Get TTY for this session
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
TTY_ID=""
[ -n "$MY_TTY" ] && TTY_ID=$(echo "$MY_TTY" | sed 's|^/dev/||; s|/|_|g')

# Check if in tmux and get window index (for display only)
WIN=""
IN_TMUX=no
if [ -n "$TMUX_PANE" ]; then
    IN_TMUX=yes
    WIN=$(tmux display-message -t "$TMUX_PANE" -p '#{window_index}' 2>/dev/null)
fi
echo "MY_TTY=$MY_TTY TTY_ID=$TTY_ID WIN=$WIN IN_TMUX=$IN_TMUX"

# Check current mute state
echo "GLOBAL_MUTED=$([ -f "$MUTE_DIR/.mute_all" ] && echo yes || echo no)"
if [ -n "$TTY_ID" ]; then
    echo "SESSION_MUTED=$([ -f "$MUTE_DIR/.mute_tty_${TTY_ID}" ] && echo yes || echo no)"
fi

# List all per-session mute files
ls "$MUTE_DIR"/.mute_tty_* 2>/dev/null || echo "No per-session mutes"
```

### 2. Check if anything is muted

If nothing is muted at all, tell the user "Notifications are not muted." and stop — do not prompt or take any action.

### 3. Handle arguments or prompt

Check the user's argument (the text after `/unmute`):

- **Argument is `all`** → unmute everything (remove `.mute_all` AND all `.mute_tty_*` files)
- **Argument is `tab N`** (where N is a number, e.g. `tab 3`) → requires tmux. Resolve the TTY of tab N:
  ```bash
  TARGET_TTY=$(tmux display-message -t ":$N" -p '#{pane_tty}' 2>/dev/null)
  TARGET_TTY_ID=$(echo "$TARGET_TTY" | sed 's|^/dev/||; s|/|_|g')
  ```
  Remove `$MUTE_DIR/.mute_tty_${TARGET_TTY_ID}`. If not in tmux, inform the user that `unmute tab N` requires tmux. If global mute is active, offer to unmute globally instead using AskUserQuestion with options: ["Unmute globally", "Cancel"]
- **Argument is `tab`** (no number) → unmute current session via its TTY
  - If TTY detection failed, inform the user and offer to unmute globally if global mute is active
- **No argument + only one type of mute active** → unmute that directly (no prompt needed):
  - Only global mute → remove `.mute_all`
  - Only current session muted → remove `.mute_tty_${TTY_ID}`
- **No argument + multiple mute types active** → use AskUserQuestion:
  - Question: "What would you like to unmute?"
  - Options: ["Everything (global + all sessions)", "This tab only (tab N)"] (replace N with window index if in tmux, otherwise use "This session only")
  - Map: "Everything ..." → remove all mute files, "This tab/session only ..." → remove current session mute file
- **No argument + NOT in tmux + global mute active** → unmute globally (no prompt needed)

### 4. Execute

Run the appropriate bash command:

- **Unmute everything**: `rm -f "$MUTE_DIR/.mute_all" "$MUTE_DIR"/.mute_tty_*`
- **Unmute global only**: `rm -f "$MUTE_DIR/.mute_all"`
- **Unmute session only**: `rm -f "$MUTE_DIR/.mute_tty_${TTY_ID}"` (use the resolved TTY_ID for the target)

### 5. Confirm

Print the resulting mute state. Examples:
- "All notifications unmuted. Sounds will play normally."
- "Tab 3 unmuted. Global mute is still active — run `/unmute all` to unmute everything."
- "Tab 3 unmuted. Sounds will play normally."
- "This session unmuted. Sounds will play normally." (when outside tmux)
