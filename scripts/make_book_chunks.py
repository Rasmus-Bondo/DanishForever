# make_book_chunks.py - vmangos page_text -> vmbooks_en.json and vmbooks_chunks_en/names_NNNN.json (unique texts, 30 per chunk)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import json, os, sqlite3
con = sqlite3.connect("file:vmangos_db/extracted/sqlite-dump/mangos.sqlite?mode=ro", uri=True)
texts = sorted({t.strip() for (t,) in con.execute("select text from page_text") if t and t.strip()}, key=lambda s: (s.lower(), s))
json.dump(texts, open("vmbooks_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
os.makedirs("vmbooks_chunks_en", exist_ok=True)
for s in range(0, len(texts), 30):
    with open(f"vmbooks_chunks_en/names_{s // 30:04d}.json", "w", encoding="utf-8") as f:
        json.dump([{"i": s + k, "en": t} for k, t in enumerate(texts[s:s + 30])], f, ensure_ascii=False, indent=1)
print(len(texts), "texts,", (len(texts) + 29) // 30, "chunks")
