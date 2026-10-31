# build_zones_lua.py - map names (items_table_map1.jsonl) + glossary -> addon/Zones.lua (English -> Danish, merged into ns.Exact)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json
import glossary

# names the glossary does not have yet (built from its existing terms)
NEW = {
    "The Barrens": "Ødemarken",
    "Eastern Plaguelands": "Østlige Pestlande",
    "The Hinterlands": "Baglandet",
    "Stranglethorn Vale": "Kvælerdorn-dalen",
    "Un'Goro Crater": "Un'Goro-krateret",
    "Stormwind City": "Stormvind By",
}

# PvP zones and other places that are not in the map table (Alterac Valley, Warsong Gulch, Arathi Basin
# and Darkspear Islands are in it already)
EXTRA = {
    "Mak'gora Arena": "Mak'gora-arena",
    "Random Battleground": "Tilfældig Slagmark",
    "Random Epic Battleground": "Tilfældig Episk Slagmark",
    "Battle for Blackrock": "Kampen om Sortklippe",
    "Battle for Gilneas": "Kampen om Gilnæas",              # same wording as the map table
}

g = glossary.load()
rows =[r for f in sorted(glob.glob("items_table_map*.jsonl")) for l in open(f, encoding="utf-8") for r in json.loads(l)["rows"]]

table, added = {}, []
for r in rows:
    name = (r["c1"] or "").strip()
    if not name:
        continue
    da = g.get(name) or NEW.get(name)
    if not da:
        print("no translation for", name)
        continue
    table[name] = da
    if name not in g:
        added.append(f"{name} = {da}")

for name, da in EXTRA.items():
    table[name] = g.get(name) or da
    if name not in g:
        added.append(f"{name} = {da}")

with open("zones_terms.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(added) + "\n")
print("new glossary terms added:", glossary.merge_file("zones_terms.txt"))

with open("addon/Zones.lua", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\n\n-- Zone and continent names (from the map table); merged into the fixed-word table\n")
    f.write("local zones = {\n")
    for en, da in sorted(table.items()):
        f.write(f"    [{json.dumps(en, ensure_ascii=False)}] = {json.dumps(da, ensure_ascii=False)},\n")
    f.write("}\nfor en, da in pairs(zones) do ns.Exact[en] = da end\n")
print(len(table), "zone names written")
