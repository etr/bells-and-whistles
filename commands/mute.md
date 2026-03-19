---
description: Mute notification sounds globally or for the current session/tab
allowed-tools:
  - Bash
  - AskUserQuestion
---

You are the bells-and-whistles mute command. Mute notification sounds globally or for the current session/tmux tab.

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
```

### 2. Report current state

If anything is already muted, tell the user what's currently muted before proceeding.

### 3. Handle arguments or prompt

Check the user's argument (the text after `/mute`):

- **Argument is `all`** → mute globally
- **Argument is `tab N`** (where N is a number, e.g. `tab 3`) → requires tmux. Resolve the TTY of tab N:
  ```bash
  TARGET_TTY=$(tmux display-message -t ":$N" -p '#{pane_tty}' 2>/dev/null)
  TARGET_TTY_ID=$(echo "$TARGET_TTY" | sed 's|^/dev/||; s|/|_|g')
  ```
  If not in tmux, inform the user that `mute tab N` requires tmux and offer to mute globally instead using AskUserQuestion with options: ["Mute globally", "Cancel"]
- **Argument is `tab`** (no number) → mute current session via its TTY
  - If TTY detection failed, inform the user and offer to mute globally instead
- **No argument + in tmux** → use AskUserQuestion:
  - Question: "What would you like to mute?"
  - Options: ["All tabs (global mute)", "This tab only (tab N)"] (replace N with the actual window index)
  - Map: "All tabs (global mute)" → mute globally, "This tab only ..." → mute current session
- **No argument + NOT in tmux** → use AskUserQuestion:
  - Question: "What would you like to mute?"
  - Options: ["All sessions (global mute)", "This session only"]
  - Map: "All sessions (global mute)" → mute globally, "This session only" → mute current session

### 4. Execute

Run the appropriate bash command:

- **Global mute**: `touch "$MUTE_DIR/.mute_all"`
- **Session/tab mute**: `touch "$MUTE_DIR/.mute_tty_${TTY_ID}"` (use the resolved TTY_ID for the target)

### 5. Confirm

Print the resulting mute state. Examples:
- "Notifications muted globally. Run `/unmute` to re-enable."
- "Notifications muted for this session. Run `/unmute` to re-enable." (when outside tmux)
- "Notifications muted for tab 3. Other tabs will still play sounds. Run `/unmute` to re-enable." (when in tmux, show tab number for clarity)
