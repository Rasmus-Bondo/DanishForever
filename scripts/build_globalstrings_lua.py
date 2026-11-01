# build_globalstrings_lua.py - globalstrings_chunks_da/*.json + globalstrings_en.json -> addon/GlobalStrings.lua
# ns.GlobalStrings = { TAG = "Danish text" } for every tag whose English text was translated.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re

FORMAT_ISSUES = re.compile(r"\|[HTAK]")        # links/icons/atlas are kept as translated, only counted below

def lua_val(s):
    s = s.replace("\\32", " ")            # Blizzard's dump writes a trailing space as the literal text \32 ("%s says:\32")
    s = re.sub(r" +\n", "\n", s)
    s = re.sub(r"\n +", "\n", s)
    return json.dumps(s, ensure_ascii=False)

da_by_en = {}
for f in sorted(glob.glob("globalstrings_chunks_da/names_*.json")):
    for x in json.load(open(f, encoding="utf-8")):
        if isinstance(x.get("da"), str) and x["da"].strip():
            da_by_en[x["en"]] = x["da"]

rows = json.load(open("globalstrings_en.json", encoding="utf-8"))
table, no_translation = {}, 0
for r in rows:
    da = da_by_en.get(r["text"])
    if da is None:
        no_translation += 1
        continue
    table[r["tag"]] = da

# context fixes: the cloak slot is "Kappe"; every other "Back" (buttons) is "Tilbage", never "Ryg"
CLOAK_TAGS = {"BACKSLOT", "INVTYPE_CLOAK", "HEIRLOOMS_CATEGORY_BACK"}
for r in rows:
    if r["text"] == "Back" and r["tag"] in table:
        table[r["tag"]] = "Kappe" if r["tag"] in CLOAK_TAGS else "Tilbage"

# the game term "Charm" (mind control) is "Charme", not "Amulet" (the jewellery word)
if table.get("LOSS_OF_CONTROL_DISPLAY_CHARM") == "Amuleret":
    table["LOSS_OF_CONTROL_DISPLAY_CHARM"] = "Charmeret"
if "OPTION_LOSS_OF_CONTROL_FULL" in table:
    table["OPTION_LOSS_OF_CONTROL_FULL"] = table["OPTION_LOSS_OF_CONTROL_FULL"].replace("Forvis, Amulet,", "Forvis, Charme,")

with open("addon/GlobalStrings.lua", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\n\n-- The game's own UI strings (GlobalStrings): TAG -> Danish.\n")
    f.write("-- Globals.lua turns these into fixed-word entries and, if you switch it on, replaces the game's variables.\n")
    f.write("ns.GlobalStrings = {\n")
    for tag, da in sorted(table.items()):
        f.write(f"    {tag} = {lua_val(da)},\n" if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", tag) else f"    [{json.dumps(tag)}] = {lua_val(da)},\n")
    f.write("}\n")
print(len(table), "tags written;", no_translation, "rows had no translation (groups that were left out)")
