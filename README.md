# bells-and-whistles

A Claude Code plugin that plays notification sounds when your agent finishes
working or needs your attention. Because staring at a terminal, waiting, is no
way to live.

## What it does

Claude Code fires two events you care about: **Stop** (the agent finished) and
**Notification** (it wants permission or has a question). This plugin intercepts
both and plays a sound. Optionally, it speaks too — "Job completed!" or "Hey!
Back to work!" — so you can keep your eyes on the other monitor, guilt-free.

## Themes

Pick one. You will not be quizzed.

| Theme | Flavor |
|---|---|
| **Videogame** | Zelda secrets, Mario coins, MGS alerts, FF victory fanfares |
| **Disney** | "When You Wish Upon a Star," "Let It Go," and eight more you already know by heart |
| **Anime** | Evangelion brass, Sailor Moon transformations, Cowboy Bebop jazz stabs |
| **Movies** | Star Wars, Jaws, the Imperial March — the whole cinema lobby |
| **90s Rock** | Smoke on the Water, Enter Sandman, Seven Nation Army riffs in pure sine waves |
| **Classical** | Beethoven's Fifth, Fur Elise, Ride of the Valkyries |
| **Beeps** | Clean, professional tones for people who attend stand-ups with their camera on |
| **Chirps** | Robins, canaries, chickadees — an aviary in your terminal |
| **Cyberpunk 2077** | Neon drones, netrunner arpeggios, corpo alerts — Night City in sine waves |
| **D&D / Fantasy** | Tavern lutes, quest fanfares, spell casts — roll for initiative |

Each theme contains 10 short melodies. The plugin picks one at random, so
repetition stays tolerable.

## Voice

Voice announcements use **AWS Polly** (Stephen, Tiffany, Brian, or Amy).
If you run tmux, the voice tells you *which window* finished — useful when you
have six agents running and zero idea which one just spoke up.

Voice is optional. The plugin ships pre-generated WAV files and works fine
without AWS credentials.

### Themed phrases

The Cyberpunk and D&D themes include themed speech phrases — "Flatline
complete, choom!" instead of "Job completed!" Themed phrases are selected
randomly from a pool, so you get variety.

You can choose between themed and standard phrases during configuration. Edit
`speech_phrases.json` to customize or add your own phrases, then regenerate
with `generate_sounds.py`.

### ElevenLabs (alternative TTS)

You can use [ElevenLabs](https://elevenlabs.io) instead of AWS Polly to
generate speech with any voice from their library. ElevenLabs is a
generation-time alternative — at runtime the plugin just plays WAV files
regardless of which provider generated them.

To generate speech with ElevenLabs:

```bash
# Using --api-key flag
python3 generate_sounds.py --speech-only --tts-provider elevenlabs \
    --api-key YOUR_KEY --voice-id YOUR_VOICE_ID --accent us --gender male

# Or using environment variable
export ELEVENLABS_API_KEY=your_key
python3 generate_sounds.py --speech-only --tts-provider elevenlabs \
    --voice-id YOUR_VOICE_ID --accent us --gender male
```

The `--accent` and `--gender` flags determine which speech slot to overwrite
(for standard phrases) and which voice to select from the config mapping (if
`--voice-id` is not provided). For themed phrases, the output always goes to
`sounds/speech/themed/{theme}/`.

You can also configure a voice mapping in `config.json` so you don't need
`--voice-id` each time:

```json
{
  "elevenlabs_voices": {
    "us": {"male": "voice_id_1", "female": "voice_id_2"},
    "uk": {"male": "voice_id_3"}
  }
}
```

ElevenLabs requires `ffmpeg` for MP3→WAV conversion.

## Installation

Install from the Groundwork Marketplace. Add the marketplace once:

```
claude plugin marketplace add etr/groundwork-marketplace
```

Then install the plugin:

```
claude plugin install bells-and-whistles@groundwork-marketplace
```

Run the built-in setup command to choose your theme, mode, and voice:

```
/configure-bells-and-whistles
```

That writes a `config.json` in the plugin root and cleans up any old hook
configurations.

To update later:

```
claude plugin update bells-and-whistles@groundwork-marketplace
```

### Manual installation

If you prefer to clone the repo yourself:

```
claude plugins add /path/to/bells-and-whistles
```

## Muting

Silence notifications without changing your configuration:

```
/mute          # mute globally (or choose scope if in tmux)
/mute all      # mute all tabs
/mute tab      # mute just the current tmux window
```

```
/unmute        # unmute (auto-detects what's muted)
/unmute all    # unmute everything
/unmute tab    # unmute just the current tmux window
```

Per-tab mute requires tmux. Mute state persists until you unmute or delete the
marker files (`.mute_all`, `.mute_window_*`) from the plugin root.

## Configuration

Edit `config.json` directly if you prefer:

```json
{
  "mode": "sound_and_voice",
  "accent": "us",
  "gender": "male",
  "voice_style": "full_sentence",
  "theme": "cyberpunk",
  "use_themed_phrases": true
}
```

**mode** — `sound_and_voice`, `sound_only`, or `voice_only`

**accent** — `us` or `uk` (used for standard phrases; ignored when `use_themed_phrases` is true)

**gender** — `male` or `female` (used for standard phrases; ignored when `use_themed_phrases` is true)

**voice_style** — `full_sentence` or `number_only`

**theme** — one of: `videogame`, `disney`, `anime`, `movies`, `90s_rock`,
`classical`, `beeps`, `chirps`, `cyberpunk`, `dnd`

**use_themed_phrases** — `true` to use themed speech phrases (if available for
the selected theme), `false` to use standard "Job completed!" phrases

## Customizing phrases

Speech phrases live in `speech_phrases.json`. Each theme can define its own
phrases for `stop`, `notification`, `stop_window`, and `notification_window`
events. The `{window}` placeholder in window templates is replaced with the
tmux window number (0-9) at generation time.

After editing `speech_phrases.json`, regenerate speech files:

```bash
python3 generate_sounds.py --speech-only
```

## Platform support

| Platform | Playback method |
|---|---|
| WSL | `powershell.exe` via `System.Media.SoundPlayer` |
| macOS | `afplay` |
| Linux | `aplay`, falling back to `paplay` |
| SSH | Terminal bell (`\a`) — dignity preserved |

## Regenerating sounds

The pre-generated WAV files live in `sounds/`. To regenerate melodies (no
dependencies beyond Python 3):

```
python3 generate_sounds.py --melodies-only
```

To regenerate speech files (requires AWS CLI with Polly access):

```
python3 generate_sounds.py --speech-only
```

You can narrow the scope with `--theme`, `--accent`, and `--gender`.

## License

MIT — see [LICENSE](LICENSE).

## Special Thanks
- https://github.com/jackmarketon for Elevenlabs integration, D&D/Cyberpunk audio, and configurable phrases.
