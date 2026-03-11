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

### 2. Ask TTS provider (if voice enabled)
If the mode includes voice (`sound_and_voice` or `voice_only`), use AskUserQuestion:
- Question: "Which text-to-speech provider?"
- Options: ["AWS Polly (default)", "ElevenLabs"]

Map: "AWS Polly (default)" → `polly`, "ElevenLabs" → `elevenlabs`

If mode is `sound_only`, default to `polly`.

### 3a. If Polly: Ask accent
Use AskUserQuestion:
- Question: "Which accent?"
- Options: ["US English", "UK English"]

Map: "US English" → `us`, "UK English" → `uk`

### 3b. If Polly: Ask voice gender
Use AskUserQuestion:
- Question: "Which voice?"
- If accent is `us`: Options: ["Male (Stephen)", "Female (Tiffany)"]
- If accent is `uk`: Options: ["Male (Brian)", "Female (Amy)"]

Map the first word: "Male ..." → `male`, "Female ..." → `female`

### 3c. If Polly: Ask voice style
Use AskUserQuestion:
- Question: "What should the voice announce?"
- Options: ["Full sentences (e.g. 'Job completed on window 5!')", "Just the window number (e.g. '5')"]

Map:
- "Full sentences (e.g. 'Job completed on window 5!')" → `full_sentence`
- "Just the window number (e.g. '5')" → `number_only`

### 3d. If ElevenLabs: Ask for API key and voice ID
Use AskUserQuestion:
- Question: "Enter your ElevenLabs API key (from elevenlabs.io/app/settings/api-keys):"

Then use AskUserQuestion:
- Question: "Enter your ElevenLabs voice ID (from elevenlabs.io/app/voice-library):"

### 4. Ask theme
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

### 5. Write config
Write `${CLAUDE_PLUGIN_ROOT}/config.json`.

If Polly:
```json
{
  "mode": "<selected_mode>",
  "tts_provider": "polly",
  "accent": "<selected_accent>",
  "gender": "<selected_gender>",
  "voice_style": "<selected_voice_style>",
  "theme": "<selected_theme>"
}
```

If ElevenLabs:
```json
{
  "mode": "<selected_mode>",
  "tts_provider": "elevenlabs",
  "elevenlabs_api_key": "<api_key>",
  "elevenlabs_voice_id": "<voice_id>",
  "theme": "<selected_theme>"
}
```

### 6. Clean up old hooks
Read `~/.claude/settings.json`. If it contains hook entries under `Stop` or `Notification` that reference `~/.claude/hooks/notify-sound.sh`, remove those specific entries (but preserve any other hooks and all other settings). Write back the cleaned file.

### 7. Summary
Print a summary:
- Theme: <display name>
- Mode: <display name>
- TTS Provider: <display name>
- Accent: <display name> (if Polly)
- Voice: <gender or voice ID> (if applicable)
- Voice style: <display name> (if Polly)
- Number of melody files available
- Number of speech files available
- Whether old hooks were cleaned up

Tell the user the plugin is now active and will play sounds on Stop and Notification events. If this is a fresh install, they may need to restart Claude Code and accept the plugin.
