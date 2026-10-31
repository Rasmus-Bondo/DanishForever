# build_qextra_lua.py - qextra_chunks_da/*.json + qextra_en.json -> addon/QuestExtra.lua
# Adds the Danish progress (p) and hand-in (c) text to quests that already exist in ns.Quests. Load it after Data_Quests.lua.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re

import sys

PH = re.compile(r"<(?:Name|Class|Race)>")
KIND = sys.argv[1] if len(sys.argv) > 1 else "qextra"                   # qextra (vmangos source) or qplextra (Polish source)
OUT = sys.argv[2] if len(sys.argv) > 2 else "QuestExtra.lua"

def lua_val(s):
    s = re.sub(r" +\n", "\n", s)
    s = re.sub(r"\n +", "\n", s)
    s = re.sub(r" {2,}", " ", s)
    return json.dumps(s, ensure_ascii=False)

da_of, skipped = {}, 0
for f in sorted(glob.glob(f"{KIND}_chunks_da/names_*.json")):
    for x in json.load(open(f, encoding="utf-8")):
        en, da = x.get("en"), x.get("da")
        if (not en or not isinstance(da, str) or not da.strip()
                or sorted(PH.findall(en)) != sorted(PH.findall(da)) or en.count("\n") != da.count("\n")):
            skipped += 1
            continue
        da_of[en] = da

by_quest = {}
for key, en in json.load(open(f"{KIND}_en.json", encoding="utf-8")).items():
    if en in da_of:
        qid, field = key.split(":")
        by_quest.setdefault(int(qid), {})[field] = da_of[en]

with open(f"addon/{OUT}", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\n\n-- Progress (p) and hand-in (c) texts for quests whose other texts are in Data_Quests.lua\n")
    f.write("local extra = {\n")
    for qid in sorted(by_quest):
        parts = ", ".join(f"{k}={lua_val(v)}" for k, v in sorted(by_quest[qid].items()))
        f.write(f"  [{qid}] = {{{parts}}},\n")
    f.write("}\nfor id, t in pairs(extra) do\n    local q = ns.Quests[id]\n    if q then\n"
            "        if t.p and not q.p then q.p = t.p end\n        if t.c and not q.c then q.c = t.c end\n    end\nend\n")
print(len(by_quest), "quests extended in addon/" + OUT + ";", skipped, "texts skipped")
