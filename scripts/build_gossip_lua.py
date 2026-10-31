# build_gossip_lua.py - gossip_en.json + gossip_chunks_da/*.json -> addon/Data_Gossip.lua
# ns.Gossip[PolishForever-style hash of the cleaned English text] = Danish text (with $n/$g/$b tokens kept)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json
en = json.load(open("gossip_en.json", encoding="utf-8"))
da = {}
for f in sorted(glob.glob("gossip_chunks_da/names_*.json")):
    for x in json.load(open(f, encoding="utf-8")):
        if isinstance(x.get("da"), str) and x["da"].strip():
            da[x["i"]] = x["da"].strip()
n = 0
with open("addon/Data_Gossip.lua", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\n\n-- NPC gossip, quest greetings and speech: hash of the English text -> Danish.\n-- The English keys follow PolishForever's hashing scheme (github.com/JSlomian/PolishForever, MIT; its data CC BY 4.0).\nns.Gossip = {\n")
    for i, e in enumerate(en):
        if i in da:
            f.write(f"    [{e['key']}] = {json.dumps(da[i], ensure_ascii=False)},\n")
            n += 1
    f.write("}\n")
print(n, "of", len(en), "written")
