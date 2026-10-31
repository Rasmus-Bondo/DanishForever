# build_emotes_lua.py - emotes_chunks_da/*.json -> addon/EmoteData.lua  (English template -> Danish template, %s = a name)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re

pairs, skipped = [], 0
for f in sorted(glob.glob("emotes_chunks_da/names_*.json")):
    for x in json.load(open(f, encoding="utf-8")):
        en, da = x.get("en"), x.get("da")
        # same number of %s, and no format code other than %s / %1$s style
        if (not en or not isinstance(da, str) or not da.strip()
                or en.count("%s") != len(re.findall(r"%(?:\d+\$)?s", da))
                or re.search(r"%(?!\d*\$?s)", da.replace("%%", ""))):
            skipped += 1
            continue
        pairs.append((en, da.strip()))

with open("addon/EmoteData.lua", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\n\n-- Emote chat lines: English template -> Danish template. %s is a player or NPC name.\n")
    f.write("ns.EmoteTemplates = {\n")
    for en, da in sorted(pairs):
        f.write(f"    {{{json.dumps(en, ensure_ascii=False)}, {json.dumps(da, ensure_ascii=False)}}},\n")
    f.write("}\n")
print(len(pairs), "emote templates written;", skipped, "skipped")
