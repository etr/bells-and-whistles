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

### 2. Ask accent (if voice enabled)
If the mode includes voice (`sound_and_voice` or `voice_only`), use AskUserQuestion:
- Question: "Which accent?"
- Options: ["US English", "UK English"]

Map: "US English" → `us`, "UK English" → `uk`

If mode is `sound_only`, default accent to `us` (doesn't matter, won't be used).

### 2b. Ask voice gender (if voice enabled)
If the mode includes voice (`sound_and_voice` or `voice_only`), use AskUserQuestion:
- Question: "Which voice?"
- If accent is `us`: Options: ["Male (Stephen)", "Female (Tiffany)"]
- If accent is `uk`: Options: ["Male (Brian)", "Female (Amy)"]

Map the first word: "Male ..." → `male`, "Female ..." → `female`

If mode is `sound_only`, default gender to `male` (doesn't matter, won't be used).

### 2c. Ask voice style (if voice enabled)
If the mode includes voice (`sound_and_voice` or `voice_only`), use AskUserQuestion:
- Question: "What should the voice announce?"
- Options: ["Full sentences (e.g. 'Job completed on window 5!')", "Just the window number (e.g. '5')"]

Map:
- "Full sentences (e.g. 'Job completed on window 5!')" → `full_sentence`
- "Just the window number (e.g. '5')" → `number_only`

If mode is `sound_only`, default voice_style to `full_sentence` (doesn't matter, won't be used).

### 3. Ask theme
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

### 4. Write config
Write `${CLAUDE_PLUGIN_ROOT}/config.json` with:
```json
{
  "mode": "<selected_mode>",
  "accent": "<selected_accent>",
  "gender": "<selected_gender>",
  "voice_style": "<selected_voice_style>",
  "theme": "<selected_theme>"
}
```

### 5. Clean up old hooks
Read `~/.claude/settings.json`. If it contains hook entries under `Stop` or `Notification` that reference `~/.claude/hooks/notify-sound.sh`, remove those specific entries (but preserve any other hooks and all other settings). Write back the cleaned file.

### 6. Summary
Print a summary:
- Theme: <display name>
- Mode: <display name>
- Accent: <display name> (if applicable)
- Gender: <display name> (if applicable)
- Voice style: <display name> (if applicable)
- Number of melody files available
- Number of speech files available
- Whether old hooks were cleaned up

Tell the user the plugin is now active and will play sounds on Stop and Notification events. If this is a fresh install, they may need to restart Claude Code and accept the plugin.
