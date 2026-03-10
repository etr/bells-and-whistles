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

### 1. Check prerequisites
Verify `aws` CLI is available by running `which aws`. If not found, warn the user that voice features require AWS CLI with Polly access, and offer to proceed with sound-only mode.

### 2. Ask notification mode
Use AskUserQuestion to ask:
- Question: "How should bells-and-whistles notify you?"
- Options: ["Sound + Voice", "Sound only", "Voice only"]

Map the response:
- "Sound + Voice" → `sound_and_voice`
- "Sound only" → `sound_only`
- "Voice only" → `voice_only`

### 3. Ask voice gender (if voice enabled)
If the mode includes voice (`sound_and_voice` or `voice_only`), use AskUserQuestion:
- Question: "Which voice?"
- Options: ["Male (Matthew)", "Female (Joanna)"]

Map: "Male (Matthew)" → `male`, "Female (Joanna)" → `female`

If mode is `sound_only`, default gender to `male` (doesn't matter, won't be used).

### 4. Ask theme
Use AskUserQuestion:
- Question: "Pick a notification sound theme:"
- Options: ["Videogame", "Disney Adults", "Anime", "Movie Addicts", "90s Rock", "Classical Music", "Beeps/Tones", "Chirps"]

Map:
- "Videogame" → `videogame`
- "Disney Adults" → `disney`
- "Anime" → `anime`
- "Movie Addicts" → `movies`
- "90s Rock" → `90s_rock`
- "Classical Music" → `classical`
- "Beeps/Tones" → `beeps`
- "Chirps" → `chirps`

### 5. Write config
Write `${CLAUDE_PLUGIN_ROOT}/config.json` with:
```json
{
  "mode": "<selected_mode>",
  "gender": "<selected_gender>",
  "theme": "<selected_theme>"
}
```

### 6. Clean up old hooks
Read `~/.claude/settings.json`. If it contains hook entries under `Stop` or `Notification` that reference `~/.claude/hooks/notify-sound.sh`, remove those specific entries (but preserve any other hooks and all other settings). Write back the cleaned file.

### 7. Summary
Print a summary:
- Theme: <display name>
- Mode: <display name>
- Gender: <display name> (if applicable)
- Number of melody files available
- Number of speech files available
- Whether old hooks were cleaned up

Tell the user the plugin is now active and will play sounds on Stop and Notification events. If this is a fresh install, they may need to restart Claude Code and accept the plugin.
