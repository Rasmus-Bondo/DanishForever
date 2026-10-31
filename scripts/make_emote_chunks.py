# make_emote_chunks.py - EmotesTextData.csv (exported with wow.export, ';' separated) -> emotes_chunks_en/names_NNNN.json
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import csv, json, os, re

PER_CHUNK = 150
rows = []
with open("wowexport/EmotesTextData.csv", encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f, delimiter=";"):
        t = (r.get("Text_lang") or "").strip()
        if t:
            rows.append({"id": int(r["ID"]), "text": t, "emote": r.get("EmotesTextID", "")})

json.dump(rows, open("emotes_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

seen, items = set(), []
for r in sorted(rows, key=lambda r: (int(r["emote"] or 0), r["id"])):      # lines of one emote stay together
    if r["text"] not in seen:
        seen.add(r["text"])
        items.append(r["text"])

os.makedirs("emotes_chunks_en", exist_ok=True)
n = 0
for start in range(0, len(items), PER_CHUNK):
    part = [{"i": start + k, "en": t} for k, t in enumerate(items[start:start + PER_CHUNK])]
    with open(f"emotes_chunks_en/names_{start // PER_CHUNK:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
    n += 1
print(len(rows), "emote lines with text;", len(items), "unique;", n, "chunks")
print("format codes used:", sorted({t for x in items for t in re.findall(r"%[0-9$]*[sdf]|\|[a-zA-Z]", x)}))
