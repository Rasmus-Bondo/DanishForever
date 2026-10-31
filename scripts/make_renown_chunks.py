# make_renown_chunks.py - items_table_renown.jsonl (ID, name, description, toast text) -> renown_chunks_en/names_0000.json (unique strings)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import json, os

strings = set()
for line in open("items_table_renown.jsonl", encoding="utf-8"):
    for r in json.loads(line)["rows"]:
        for c in ("c1", "c2", "c3"):
            if r.get(c) and r[c].strip():
                strings.add(r[c].strip())
names = sorted(strings, key=lambda s: (s.lower(), s))
os.makedirs("renown_chunks_en", exist_ok=True)
with open("renown_chunks_en/names_0000.json", "w", encoding="utf-8") as f:
    json.dump([{"i": i, "en": s} for i, s in enumerate(names)], f, ensure_ascii=False, indent=1)
print(len(names), "unique strings in 1 chunk")
