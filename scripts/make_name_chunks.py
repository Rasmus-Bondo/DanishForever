# make_name_chunks.py <objects|creatures> - items_table_{obj1|cre1}.jsonl -> <kind>_en.json and <kind>_chunks_en/names_NNNN.json
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os, sys

KIND = sys.argv[1]
# usage: python make_name_chunks.py <kind> [file prefix]   (the prefix is the name given to scrape_table.py; default: the kind itself)
KNOWN = {"objects": "obj", "creatures": "cre", "achievements": "ach", "factions": "fac", "titles": "cti",
         "skills": "skl", "areas": "area"}
PREFIX = sys.argv[2] if len(sys.argv) > 2 else KNOWN.get(KIND, KIND)
NAMES_PER_CHUNK = int(sys.argv[3]) if len(sys.argv) > 3 else 300       # long texts: pass a smaller number

rows = {}
for f in sorted(glob.glob(f"items_table_{PREFIX}*.jsonl")):
    for line in open(f, encoding="utf-8"):
        for r in json.loads(line)["rows"]:
            if r["c1"] and r["c1"].strip():
                rows[r["c0"]] = {"id": r["c0"], "name": r["c1"].strip()}

json.dump([rows[i] for i in sorted(rows)], open(f"{KIND}_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

names = sorted({x["name"] for x in rows.values()}, key=lambda s: (s.lower(), s))   # sorted: similar names stay together
os.makedirs(f"{KIND}_chunks_en", exist_ok=True)
n = 0
for start in range(0, len(names), NAMES_PER_CHUNK):
    part = [{"i": start + k, "en": s} for k, s in enumerate(names[start:start + NAMES_PER_CHUNK])]
    with open(f"{KIND}_chunks_en/names_{start // NAMES_PER_CHUNK:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
    n += 1
print(KIND, len(rows), "rows;", len(names), "unique names;", n, "chunks")
