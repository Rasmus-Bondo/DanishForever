# make_spell_chunks.py - merge items_table_spn*.jsonl (spell names) -> spells_en.json and spells_chunks_en/names_NNNN.json
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os

NAMES_PER_CHUNK = 300

ids = {int(l) for l in open("sitemap_spell_ids.txt") if l.strip()}
spells = {}
for f in sorted(glob.glob("items_table_spn*.jsonl")):
    for line in open(f, encoding="utf-8"):
        for r in json.loads(line)["rows"]:
            if r["c0"] in ids and r["c1"] and r["c1"].strip():
                spells[r["c0"]] = {"id": r["c0"], "name": r["c1"].strip()}

json.dump([spells[i] for i in sorted(spells)], open("spells_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

names = sorted({s["name"] for s in spells.values()}, key=lambda s: (s.lower(), s))   # sorted: similar names stay together
os.makedirs("spells_chunks_en", exist_ok=True)
n = 0
for start in range(0, len(names), NAMES_PER_CHUNK):
    part = [{"i": start + k, "en": s} for k, s in enumerate(names[start:start + NAMES_PER_CHUNK])]
    with open(f"spells_chunks_en/names_{start // NAMES_PER_CHUNK:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
    n += 1
print(len(spells), "spells;", len(names), "unique names;", n, "chunks")
