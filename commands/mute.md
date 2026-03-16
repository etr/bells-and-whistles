---
description: Mute notification sounds globally or for the current tmux tab
allowed-tools:
  - Bash
  - AskUserQuestion
---

You are the bells-and-whistles mute command. Mute notification sounds globally or for the current tmux window/tab.

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
```

### 2. Report current state

If anything is already muted, tell the user what's currently muted before proceeding.

### 3. Handle arguments or prompt

Check the user's argument (the text after `/mute`):

- **Argument is `all`** → mute globally
- **Argument is `tab`** → mute current tmux window
  - If NOT in tmux, inform the user that per-tab mute requires tmux and offer to mute globally instead using AskUserQuestion with options: ["Mute globally", "Cancel"]
- **No argument + in tmux** → use AskUserQuestion:
  - Question: "What would you like to mute?"
  - Options: ["All tabs (global mute)", "This tab only (window N)"] (replace N with the actual window index)
  - Map: "All tabs (global mute)" → mute globally, "This tab only ..." → mute current window
- **No argument + NOT in tmux** → mute globally (no prompt needed)

### 4. Execute

Run the appropriate bash command:

- **Global mute**: `touch "$MUTE_DIR/.mute_all"`
- **Window mute**: `touch "$MUTE_DIR/.mute_window_N"` (replace N with the window index)

### 5. Confirm

Print the resulting mute state. Examples:
- "Notifications muted globally. Run `/unmute` to re-enable."
- "Notifications muted for tab 3. Other tabs will still play sounds. Run `/unmute` to re-enable."
