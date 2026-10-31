# build_items_lua.py - items_chunks_da/*.json -> Data_Items.lua (English text -> Danish text)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re

PH = re.compile(r"<(?:Name|Class|Race)>")

def lua_val(s):
    s = re.sub(r" +\n", "\n", s)
    s = re.sub(r"\n +", "\n", s)
    s = re.sub(r" {2,}", " ", s)
    return json.dumps(s, ensure_ascii=False)

def lua_key(s):
    return json.dumps(s, ensure_ascii=False)       # exact: the key must match the game's text byte for byte

def load(prefix):
    table, bad = {}, 0
    for f in sorted(glob.glob(f"items_chunks_da/{prefix}_*.json")):
        for x in json.load(open(f, encoding="utf-8")):
            en, da = x.get("en"), x.get("da")
            if (not en or not isinstance(da, str) or not da.strip()
                    or sorted(PH.findall(en)) != sorted(PH.findall(da))
                    or en.count("\n") != da.count("\n")):
                bad += 1
                continue
            table[en] = da
    return table, bad

names, bad_n = load("names")
descs, bad_d = load("desc")

with open("Data_Items.lua", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\n")
    for var, table in (("ItemNames", names), ("ItemDescs", descs)):
        f.write(f"ns.{var} = {{\n")
        for en, da in sorted(table.items()):
            f.write(f"  [{lua_key(en)}] = {lua_val(da)},\n")
        f.write("}\n")

print(len(names), "item names,", len(descs), "descriptions written;", bad_n + bad_d, "entries skipped")
