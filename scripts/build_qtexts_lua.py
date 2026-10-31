# build_qtexts_lua.py - qtexts_chunks_da/*.json -> addon/QuestTexts.lua (English variant text -> Danish)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re

PH = re.compile(r"<(?:Name|Class|Race)>")

def lua_val(s):
    s = re.sub(r" +\n", "\n", s)
    s = re.sub(r"\n +", "\n", s)
    s = re.sub(r" {2,}", " ", s)
    return json.dumps(s, ensure_ascii=False)

table, skipped = {}, 0
for f in sorted(glob.glob("qtexts_chunks_da/names_*.json")):
    for x in json.load(open(f, encoding="utf-8")):
        en, da = x.get("en"), x.get("da")
        if (not en or not isinstance(da, str) or not da.strip()
                or sorted(PH.findall(en)) != sorted(PH.findall(da)) or en.count("\n") != da.count("\n")):
            skipped += 1
            continue
        table[en] = da

with open("addon/QuestTexts.lua", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\n\n-- Class/race variants of quest texts: English text -> Danish\nns.QuestTexts = {\n")
    for en, da in sorted(table.items()):
        f.write(f"  [{json.dumps(en, ensure_ascii=False)}] = {lua_val(da)},\n")
    f.write("}\n")
print(len(table), "quest texts written to addon/QuestTexts.lua;", skipped, "skipped")
