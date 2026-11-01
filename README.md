# Danish Forever

A joke, deliberately scuffed Danish translation addon for **World of Warcraft Classic** (the "Forever" beta, Interface 16001,
and Classic Era). Quests, items, spells, NPC names and gossip, books, achievements, tooltips, chat links and most of the
interface are translated literally and playfully. Machine-translated, one pass, no regrets.

**Status:** used and tested on Classic Era since 2026-10-31. The Forever beta is not playable until 2026-11-05, so it is
untested there. Expect bugs and mixed English/Danish text; please open an issue.

## Install
1. Copy the `DanishForever` folder into `World of Warcraft\_classic_era_\Interface\AddOns\` (Classic Era) or
   `World of Warcraft\_classic_beta_\Interface\AddOns\` (Forever beta). It is about 17 MB.
2. Start the game and make sure **Danish Forever** is ticked on the character screen. On Classic Era you may have to tick
   "Load out of date AddOns", or add your client's number to the `## Interface:` line of `DanishForever.toc`.
3. Type `/df status` to see what loaded.

Renamed from "DanishUI" on 2026-11-01. If you have the old `DanishUI` folder, delete it. The slash command is now `/df`.

## Commands
- `/df status` shows which hooks and data tables loaded.
- `/df tr <text>` shows how a line is translated, step by step (type `||` for a `|`).
- `/df tipdebug on|off` prints tooltip lines live (green = translated, yellow = still English).
- `/df capture on|off` and `/df missed [clear]` save English interface text so it can be translated in the next batch.
- `/df globals on|off` replaces the game's own string variables (needs `/reload`, can cause taint in rare cases).

## Repository layout
- `DanishForever/` - the addon (generated Lua data files plus `Core.lua`).
- `scripts/` - the Python tools that scraped sources, ran the translation and built the Lua files. They expect a `work/`
  folder with source data (chunks, glossary, database dumps) that is **not** included here because it is large and
  contains third-party data. They are published for reference.

## Credits and licences
See `DanishForever/CREDITS.txt`. In short: gossip keys, the Polish text used for a few hundred quests and the line patterns
come from [PolishForever](https://github.com/JSlomian/PolishForever) by Jan Slomian (code MIT, data CC BY 4.0);
English game text was compared against the [MultiLanguage](https://github.com/rubenzantingh/MultiLanguage) addon by Ruben Zantingh.
All Danish text was translated by Claude. Code and original work: MIT (see `LICENSE`).

World of Warcraft and all game text are the property of Blizzard Entertainment. This is an unofficial fan project and is not affiliated with Blizzard.