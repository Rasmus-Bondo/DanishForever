# make_gs_chunks.py - GlobalStrings tables (gs1-gs3) -> globalstrings_en.json and globalstrings_chunks_en/names_NNNN.json
# Only the UI groups are chunked; slash commands and features this client does not have are left out.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os

UI = {"ERR", "SPELL", "BINDING", "ACTION", "ITEM", "PROFESSIONS", "GUILD", "PVP", "CHAT", "LFG", "UNIT", "TOOLTIP",
      "CLASS", "AUCTION", "CHARACTER", "QUEST", "SOCIAL", "CALENDAR", "CONFIRM", "POWER", "HELPFRAME", "STAT",
      "COMBAT", "TALENT", "CHAR", "POSTMASTER", "NEWBIE", "DUNGEON", "PET", "OPTION", "BLIZZARD", "VOICEMACRO"}
PER_CHUNK = 150

rows = []
for f in sorted(glob.glob("items_table_gs*.jsonl")):
    for line in open(f, encoding="utf-8"):
        for r in json.loads(line)["rows"]:
            if (r["c1"] or "").strip() and (r["c2"] or "").strip():
                rows.append({"id": r["c0"], "tag": r["c2"].strip(), "text": r["c1"]})

json.dump(rows, open("globalstrings_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

chosen = sorted((r for r in rows if r["tag"].split("_")[0] in UI), key=lambda r: r["tag"])   # same-group strings stay together
seen, items = set(), []
for r in chosen:
    if r["text"] not in seen:                      # one translation per distinct text; the tag is context for the translator
        seen.add(r["text"])
        items.append(r)

os.makedirs("globalstrings_chunks_en", exist_ok=True)
n = 0
for start in range(0, len(items), PER_CHUNK):
    part = [{"i": start + k, "en": r["text"], "tag": r["tag"]} for k, r in enumerate(items[start:start + PER_CHUNK])]
    with open(f"globalstrings_chunks_en/names_{start // PER_CHUNK:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
    n += 1
print(len(rows), "strings in total;", len(items), "unique UI texts;", n, "chunks")
