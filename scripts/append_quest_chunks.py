# append_quest_chunks.py - quests in quests_en.jsonl that are not in any chunks_en/ file yet -> new chunk files (existing numbering is kept)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os, re

known = set()
for f in glob.glob("chunks_en/*.json"):
    known |= {q["id"] for q in json.load(open(f, encoding="utf-8"))}

new = []
for line in open("quests_en.jsonl", encoding="utf-8"):
    q = json.loads(line)
    if q["id"] not in known:
        new.append(q)

last = max(int(re.search(r"(\d+)", os.path.basename(f)).group(1)) for f in glob.glob("chunks_en/chunk_*.json"))
for start in range(0, len(new), 25):
    last += 1
    with open(f"chunks_en/chunk_{last:04d}.json", "w", encoding="utf-8") as f:
        json.dump(new[start:start + 25], f, ensure_ascii=False, indent=1)
print(len(new), "new quests in", (len(new) + 24) // 25, "new chunk files")
