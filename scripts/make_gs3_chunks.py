# make_gs3_chunks.py - the GlobalStrings that make_gs_chunks.py and make_gs2_chunks.py left out (retail-only features: housing, garrison, covenants, ...)
# -> globalstrings_chunks_en/names_NNNN.json (new files after the existing ones). Slash commands (SLASH_*) stay out: translating them would break them.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os

PER_CHUNK = 150
done = set()
for f in glob.glob("globalstrings_chunks_en/names_*.json"):
    done |= {x["en"] for x in json.load(open(f, encoding="utf-8"))}
start_chunk = len(glob.glob("globalstrings_chunks_en/names_*.json"))

rows = json.load(open("globalstrings_en.json", encoding="utf-8"))
seen, items = set(), []
for r in sorted(rows, key=lambda r: r["tag"]):
    t = r["text"] or ""
    if not t.strip() or r["tag"].split("_")[0] == "SLASH" or t in done or t in seen:
        continue
    seen.add(t)
    items.append(r)

for s in range(0, len(items), PER_CHUNK):
    part = [{"i": 300000 + s + k, "en": r["text"], "tag": r["tag"]} for k, r in enumerate(items[s:s + PER_CHUNK])]
    with open(f"globalstrings_chunks_en/names_{start_chunk + s // PER_CHUNK:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
print(len(items), "texts in", (len(items) + PER_CHUNK - 1) // PER_CHUNK, "new chunks, starting at", start_chunk)
