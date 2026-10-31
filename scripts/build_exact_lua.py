# build_exact_lua.py - translated name chunks -> addon/<File>.lua, merged into ns.Exact (existing entries are kept)
# usage: python build_exact_lua.py skills Skills.lua [factions Factions.lua ...]
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re, sys

PH = re.compile(r"<(?:Name|Class|Race)>")

def build(kind, filename):
    table, skipped = {}, 0
    for f in sorted(glob.glob(f"{kind}_chunks_da/names_*.json")):
        for x in json.load(open(f, encoding="utf-8")):
            en, da = x.get("en"), x.get("da")
            if (not en or not isinstance(da, str) or not da.strip()
                    or sorted(PH.findall(en)) != sorted(PH.findall(da))):
                skipped += 1
                continue
            table[en] = da.strip()
    with open(f"addon/{filename}", "w", encoding="utf-8") as f:
        f.write("local _, ns = ...\n\n")
        f.write(f"-- {kind}: English -> Danish. Entries already in ns.Exact (hand-made) are kept.\n")
        f.write("local names = {\n")
        for en, da in sorted(table.items()):
            f.write(f"    [{json.dumps(en, ensure_ascii=False)}] = {json.dumps(da, ensure_ascii=False)},\n")
        f.write("}\nfor en, da in pairs(names) do\n    if ns.Exact[en] == nil then ns.Exact[en] = da end\nend\n")
    print(kind, len(table), "names written to addon/" + filename, f"({skipped} skipped)")

args = sys.argv[1:]
for kind, filename in zip(args[::2], args[1::2]):
    build(kind, filename)
