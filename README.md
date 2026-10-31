# DanishUI - "Dansk (scuffed)"

A joke, deliberately scuffed Danish translation addon for **World of Warcraft Classic** (the "Forever" beta, Interface 16001).
Quest text, items, spells, NPC names and gossip, books, achievements, tooltips and most of the UI strings are translated
literally and playfully. Machine-translated, one pass, no regrets.

**Status:** not tested in game yet (the beta is not playable until 2026-11-05). Expect bugs; please open an issue.

## Install
Copy the `DanishUI` folder into
`World of Warcraft\_classic_beta_\Interface\AddOns\`
(it is about 17 MB), then start the game or type `/reload`. `/dui status` shows what is loaded.

## Repository layout
- `DanishUI/` - the addon (generated Lua data files plus `Core.lua`).
- `scripts/` - the Python tools that scraped sources, ran the translation and built the Lua files.
  They expect a `work/` folder with source data (chunks, glossary, database dumps) that is **not** included
  here because it is large and contains third-party data. They are published for reference.

## Credits and licences
Code and original work: MIT (see LICENSE).

See `DanishUI/CREDITS.txt`. In short: gossip keys, the Polish text used for a few hundred quests and the line patterns
come from [PolishForever](https://github.com/JSlomian/PolishForever) by Jan Slomian (code MIT, data CC BY 4.0);
English game text was compared against the [MultiLanguage](https://github.com/rubenzantingh/MultiLanguage) addon by Ruben Zantingh.
All Danish text was translated by Claude.

World of Warcraft and all game text are the property of Blizzard Entertainment. This is an unofficial fan project and is not affiliated with Blizzard.

## In-game commands
- `/dui status` shows which hooks and data tables loaded.
- `/dui tr <text>` shows how a line is translated, step by step (type `||` for a `|`).
- `/dui tipdebug on|off` prints tooltip lines live (green = translated, yellow = still English).
- `/dui capture on|off` and `/dui missed [clear]` save English interface text for the next translation batch.
- `/dui globals on|off` replaces the game's own string variables (needs `/reload`, can cause taint in rare cases).

## Tested so far
Loaded and used on Classic Era (2026-10-31). Many tooltip, window and chat fixes came out of that test; see the commit history.