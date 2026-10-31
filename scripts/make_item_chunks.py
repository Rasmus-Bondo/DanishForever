# make_item_chunks.py - unique item names and descriptions -> items_chunks_en/{names,desc}_NNNN.json
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import json, os

NAMES_PER_CHUNK, DESCS_PER_CHUNK = 300, 60

items = json.load(open("items_en.json", encoding="utf-8"))
names = sorted({i["name"] for i in items}, key=lambda s: (s.lower(), s))   # sorted: similar names stay together
descs = sorted({i["desc"] for i in items if i["desc"]}, key=lambda s: (s.lower(), s))

os.makedirs("items_chunks_en", exist_ok=True)

def write(prefix, strings, size):
    n = 0
    for start in range(0, len(strings), size):
        part = [{"i": start + k, "en": s} for k, s in enumerate(strings[start:start + size])]
        with open(f"items_chunks_en/{prefix}_{start // size:04d}.json", "w", encoding="utf-8") as f:
            json.dump(part, f, ensure_ascii=False, indent=1)
        n += 1
    return n

print(write("names", names, NAMES_PER_CHUNK), "name chunks;", write("desc", descs, DESCS_PER_CHUNK), "desc chunks")
