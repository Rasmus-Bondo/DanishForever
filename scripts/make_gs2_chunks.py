# make_gs2_chunks.py - the rest of the GlobalStrings (groups not chunked by make_gs_chunks.py) -> globalstrings_chunks_en/names_0065+.json
# Leaves out slash commands and retail-only features (housing, garrison, covenants, ...).
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os

UI = {"ERR", "SPELL", "BINDING", "ACTION", "ITEM", "PROFESSIONS", "GUILD", "PVP", "CHAT", "LFG", "UNIT", "TOOLTIP",
      "CLASS", "AUCTION", "CHARACTER", "QUEST", "SOCIAL", "CALENDAR", "CONFIRM", "POWER", "HELPFRAME", "STAT",
      "COMBAT", "TALENT", "CHAR", "POSTMASTER", "NEWBIE", "DUNGEON", "PET", "OPTION", "BLIZZARD", "VOICEMACRO"}
SKIP = {"SLASH", "HOUSING", "HOUSE", "HUD", "GARRISON", "BOOST2", "SPLASH", "COVENANT", "NPEV2", "NPE", "CAA", "ARTIFACT",
        "AZERITE", "PERKS", "RAF", "VAS", "VRN", "CDMSND", "GAMEPAD", "VOICE", "NARRATION", "RPE", "TOKEN", "CLUB",
        "COMMUNITIES", "VIDEO", "ORDER", "CRAFTING", "RADIAL", "WEEKLY", "PING", "VISITABLE", "SHOW", "ENABLE",
        "COMPACT", "CHALLENGE", "TRANSMOG"}
PER_CHUNK = 150

done = set()
for f in glob.glob("globalstrings_chunks_en/names_*.json"):
    done |= {x["en"] for x in json.load(open(f, encoding="utf-8"))}
start_chunk = len(glob.glob("globalstrings_chunks_en/names_*.json"))

rows = json.load(open("globalstrings_en.json", encoding="utf-8"))
chosen = sorted((r for r in rows if r["tag"].split("_")[0] not in UI | SKIP and (r["text"] or "").strip()), key=lambda r: r["tag"])
seen, items = set(), []
for r in chosen:
    if r["text"] not in done and r["text"] not in seen:
        seen.add(r["text"]); items.append(r)

n = 0
for s in range(0, len(items), PER_CHUNK):
    part = [{"i": 100000 + s + k, "en": r["text"], "tag": r["tag"]} for k, r in enumerate(items[s:s + PER_CHUNK])]
    with open(f"globalstrings_chunks_en/names_{start_chunk + s // PER_CHUNK:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
    n += 1
print(len(items), "texts in", n, "new chunks, starting at", start_chunk)
