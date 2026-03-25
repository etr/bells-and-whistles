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

### 2. Ask theme
Use AskUserQuestion:
- Question: "Pick a notification sound theme:"
- Options: ["Videogame", "Disney Adults", "Anime", "Movie Addicts", "90s Rock", "Classical Music", "Beeps/Tones", "Chirps", "Cyberpunk 2077", "D&D / Fantasy"]

Map:
- "Videogame" → `videogame`
- "Disney Adults" → `disney`
- "Anime" → `anime`
- "Movie Addicts" → `movies`
- "90s Rock" → `90s_rock`
- "Classical Music" → `classical`
- "Beeps/Tones" → `beeps`
- "Chirps" → `chirps`
- "Cyberpunk 2077" → `cyberpunk`
- "D&D / Fantasy" → `dnd`

### 3. Check for themed phrases (if voice enabled)
If the mode includes voice (`sound_and_voice` or `voice_only`):

Read `${CLAUDE_PLUGIN_ROOT}/speech_phrases.json`. Check if the selected theme has its own entry (i.e., a key other than `"default"` matching the theme name).

If the theme has custom phrases, use AskUserQuestion:
- Question: "The [theme] theme has custom themed phrases (e.g., '[first stop phrase from the theme]'). Use themed phrases or standard ones?"
- Options: ["Themed phrases", "Standard phrases"]

Set `use_themed_phrases`:
- "Themed phrases" → `true`
- "Standard phrases" → `false`

If the theme does NOT have custom phrases, set `use_themed_phrases` to `false`.

If mode is `sound_only`, set `use_themed_phrases` to `false`.

### 4. Ask accent and gender (if voice enabled AND NOT using themed phrases)
If the mode includes voice (`sound_and_voice` or `voice_only`) AND `use_themed_phrases` is `false`:

Use AskUserQuestion to ask accent:
- Question: "Which accent?"
- Options: ["US English", "UK English"]

Map: "US English" → `us`, "UK English" → `uk`

Then use AskUserQuestion to ask voice gender:
- Question: "Which voice?"
- If accent is `us`: Options: ["Male (Stephen)", "Female (Tiffany)"]
- If accent is `uk`: Options: ["Male (Brian)", "Female (Amy)"]

Map the first word: "Male ..." → `male`, "Female ..." → `female`

If mode is `sound_only` OR `use_themed_phrases` is `true`, default accent to `us` and gender to `male`.

### 5. Ask voice style (if voice enabled)
If the mode includes voice (`sound_and_voice` or `voice_only`), use AskUserQuestion:
- Question: "What should the voice announce?"
- Options: ["Full sentences (e.g. 'Job completed on window 5!')", "Just the window number (e.g. '5')"]

Map:
- "Full sentences (e.g. 'Job completed on window 5!')" → `full_sentence`
- "Just the window number (e.g. '5')" → `number_only`

If mode is `sound_only`, default voice_style to `full_sentence`.

### 6. Write config
Write `${CLAUDE_PLUGIN_ROOT}/config.json` with:
```json
{
  "mode": "<selected_mode>",
  "accent": "<selected_accent>",
  "gender": "<selected_gender>",
  "voice_style": "<selected_voice_style>",
  "theme": "<selected_theme>",
  "use_themed_phrases": <true_or_false>
}
```

### 7. Detect WSL powershell path
Before writing config (or immediately after), check if running on WSL:
```bash
grep -qiE 'microsoft|wsl' /proc/version 2>/dev/null
```

If on WSL, auto-detect `powershell.exe` using this fallback chain:
1. `command -v powershell.exe 2>/dev/null`
2. Check `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`
3. Check `/mnt/c/Windows/SysWOW64/WindowsPowerShell/v1.0/powershell.exe`

If found, add `"wsl_powershell_path": "<detected_path>"` to the config JSON written in step 6.

If not found, warn the user: "Could not find powershell.exe — sound playback on WSL may not work. You can set `wsl_powershell_path` in config.json manually."

If not on WSL, skip this step entirely.

### 8. Clean up old hooks
Read `~/.claude/settings.json`. If it contains hook entries under `Stop` or `Notification` that reference `~/.claude/hooks/notify-sound.sh`, remove those specific entries (but preserve any other hooks and all other settings). Write back the cleaned file.

### 9. Summary
Print a summary:
- Theme: <display name>
- Mode: <display name>
- Speech: "themed phrases" or "standard (<accent> <gender>)" (if applicable)
- Voice style: <display name> (if applicable)
- Number of melody files available
- Number of speech files available
- Whether old hooks were cleaned up

Tell the user the plugin is now active and will play sounds on Stop and Notification events. If this is a fresh install, they may need to restart Claude Code and accept the plugin.
