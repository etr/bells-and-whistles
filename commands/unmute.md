---
description: Unmute notification sounds globally or for the current tmux tab
allowed-tools:
  - Bash
  - AskUserQuestion
---

You are the bells-and-whistles unmute command. Unmute notification sounds globally or for the current tmux window/tab.

## Steps

### 1. Detect environment

Run these bash commands to gather state:

```bash
# Mute state lives one level above the versioned plugin root so it survives upgrades
MUTE_DIR="${CLAUDE_PLUGIN_ROOT}/.."

# Check if in tmux and get window index
WIN=""
if [ -n "$TMUX_PANE" ]; then
    WIN=$(tmux display-message -t "$TMUX_PANE" -p '#{window_index}' 2>/dev/null)
fi
echo "WIN=$WIN"

# Check current mute state
echo "GLOBAL_MUTED=$([ -f "$MUTE_DIR/.mute_all" ] && echo yes || echo no)"
if [ -n "$WIN" ]; then
    echo "WINDOW_MUTED=$([ -f "$MUTE_DIR/.mute_window_${WIN}" ] && echo yes || echo no)"
fi

# List all window mute files
ls "$MUTE_DIR"/.mute_window_* 2>/dev/null || echo "No per-window mutes"
```

### 2. Check if anything is muted

If nothing is muted at all, tell the user "Notifications are not muted." and stop — do not prompt or take any action.

### 3. Handle arguments or prompt

Check the user's argument (the text after `/unmute`):

- **Argument is `all`** → unmute everything (remove `.mute_all` AND all `.mute_window_*` files)
- **Argument is `tab`** → unmute current tmux window only
  - If NOT in tmux, inform the user that per-tab unmute requires tmux. If global mute is active, offer to unmute globally instead using AskUserQuestion with options: ["Unmute globally", "Cancel"]
- **No argument + only one type of mute active** → unmute that directly (no prompt needed):
  - Only global mute → remove `.mute_all`
  - Only current window muted → remove `.mute_window_N`
- **No argument + multiple mute types active** → use AskUserQuestion:
  - Question: "What would you like to unmute?"
  - Options: ["Everything (global + all tabs)", "This tab only (window N)"] (replace N with the actual window index)
  - Map: "Everything ..." → remove all mute files, "This tab only ..." → remove current window mute file
- **No argument + NOT in tmux + global mute active** → unmute globally (no prompt needed)

### 4. Execute

Run the appropriate bash command:

- **Unmute everything**: `rm -f "$MUTE_DIR/.mute_all" "$MUTE_DIR"/.mute_window_*`
- **Unmute global only**: `rm -f "$MUTE_DIR/.mute_all"`
- **Unmute window only**: `rm -f "$CLAUDE_PLUGIN_ROOT/.mute_window_N"` (replace N with the window index)

### 5. Confirm

Print the resulting mute state. Examples:
- "All notifications unmuted. Sounds will play normally."
- "Tab 3 unmuted. Global mute is still active — run `/unmute all` to unmute everything."
- "Tab 3 unmuted. Sounds will play normally."
