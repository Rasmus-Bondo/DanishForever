# make_spell_desc_chunks.py - unique spell descriptions, aura descriptions and rank texts -> spells_chunks_en/desc_NNNN.json
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os

PER_CHUNK = 50

ids = {int(l) for l in open("sitemap_spell_ids.txt") if l.strip()}
texts = set()
for f in sorted(glob.glob("items_table_spd*.jsonl")):
    for line in open(f, encoding="utf-8"):
        for r in json.loads(line)["rows"]:
            if r["c0"] in ids:
                for col in ("c1", "c2", "c3"):        # description, aura description, rank text
                    t = (r[col] or "").strip()
                    if t:
                        texts.add(t)

texts = sorted(texts, key=lambda s: (s.lower(), s))
os.makedirs("spells_chunks_en", exist_ok=True)
n = 0
for start in range(0, len(texts), PER_CHUNK):
    part = [{"i": start + k, "en": s} for k, s in enumerate(texts[start:start + PER_CHUNK])]
    with open(f"spells_chunks_en/desc_{start // PER_CHUNK:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
    n += 1
print(len(texts), "unique texts;", n, "chunks")
