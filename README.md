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

Each theme contains 10 short melodies. The plugin picks one at random, so
repetition stays tolerable.

## Voice

Voice announcements use AWS Polly (Matthew or Joanna). If you run tmux, the
voice tells you *which window* finished — useful when you have six agents
running and zero idea which one just spoke up.

Voice is optional. The plugin ships pre-generated WAV files and works fine
without AWS credentials.

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
/install-bells-and-whistles
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

## Configuration

Edit `config.json` directly if you prefer:

```json
{
  "mode": "sound_and_voice",
  "gender": "male",
  "theme": "videogame"
}
```

**mode** — `sound_and_voice`, `sound_only`, or `voice_only`
**gender** — `male` or `female` (ignored in `sound_only` mode)
**theme** — one of: `videogame`, `disney`, `anime`, `movies`, `90s_rock`,
`classical`, `beeps`, `chirps`

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

You can narrow the scope with `--theme` and `--gender`.

## License

Do what you want with it. If the Zelda secret-discovery sound helps you ship
faster, that is reward enough.
