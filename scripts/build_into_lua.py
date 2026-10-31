# build_into_lua.py <kind> <File.lua> <ns table> - translated chunks -> addon/<File>.lua that adds English -> Danish pairs to an existing table
# (existing entries are kept). Like build_exact_lua.py, but for tables other than ns.Exact, e.g. ns.ItemNames or ns.ItemDescs.
# usage: python build_into_lua.py mlitems ItemNames2.lua ItemNames [mlflavor ItemDescs2.lua ItemDescs ...]
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re, sys

PH = re.compile(r"<(?:Name|Class|Race)>")

def build(kind, filename, table_name):
    table, skipped = {}, 0
    for f in sorted(glob.glob(f"{kind}_chunks_da/*_*.json")):
        for x in json.load(open(f, encoding="utf-8")):
            en, da = x.get("en"), x.get("da")
            if (not en or not isinstance(da, str) or not da.strip()
                    or sorted(PH.findall(en)) != sorted(PH.findall(da)) or en.count("\n") != da.count("\n")):
                skipped += 1
                continue
            table[en.strip()] = da.strip()
    with open(f"addon/{filename}", "w", encoding="utf-8") as f:
        f.write("local _, ns = ...\n\n")
        f.write(f"-- {kind}: English -> Danish, added to ns.{table_name}. Entries that are already there are kept.\n")
        f.write("local names = {\n")
        for en, da in sorted(table.items()):
            f.write(f"    [{json.dumps(en, ensure_ascii=False)}] = {json.dumps(da, ensure_ascii=False)},\n")
        f.write(f"}}\nns.{table_name} = ns.{table_name} or {{}}\nfor en, da in pairs(names) do\n"
                f"    if ns.{table_name}[en] == nil then ns.{table_name}[en] = da end\nend\n")
    print(kind, len(table), "entries written to addon/" + filename, f"({skipped} skipped)")

args = sys.argv[1:]
for kind, filename, table_name in zip(args[::3], args[1::3], args[2::3]):
    build(kind, filename, table_name)
