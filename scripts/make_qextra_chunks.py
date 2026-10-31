# make_qextra_chunks.py - progress/complete texts that the old scraped quests lack -> vmangos text -> qextra_en.json and qextra_chunks_en/names_NNNN.json
# Only quests whose chunks_en record has a null progress/complete, and only for ids below 10000-chunk new quests (those already carry both).
# qextra_en.json maps "<id>:<p|c>" to the English text; the chunks hold the unique texts ({"i", "en"}, 25 per chunk).
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os, re, sqlite3

OLD = {}                                          # id -> en record, from the quests scraped earlier (chunk_0000 .. chunk_9999)
for f in glob.glob("chunks_en/chunk_*.json"):
    if int(re.search(r"(\d+)", os.path.basename(f)).group(1)) >= 10002:
        continue
    for q in json.load(open(f, encoding="utf-8")):
        OLD[q["id"]] = q

con = sqlite3.connect("file:vmangos_db/extracted/sqlite-dump/mangos.sqlite?mode=ro", uri=True)
con.row_factory = sqlite3.Row
best = {}
for r in con.execute("select * from quest_template order by patch"):
    best[r["entry"]] = r

def convert(s):
    if not s:
        return None
    s = s.replace("\r", "")
    s = re.sub(r"\$[Bb]", "\n", s)
    s = re.sub(r"\$[Nn]", "<Name>", s)
    s = re.sub(r"\$[Cc]", "<Class>", s)
    s = re.sub(r"\$[Rr]", "<Race>", s)
    s = re.sub(r"\$[Gg]\s*([^:;]*?)\s*:\s*([^;]*?)\s*;", lambda m: m.group(1), s)
    return s.strip() or None

mapping, missing_in_vm = {}, 0
for qid, q in sorted(OLD.items()):
    r = best.get(qid)
    if r is None:
        missing_in_vm += 1
        continue
    for key, col in (("p", "RequestItemsText"), ("c", "OfferRewardText")):
        have = q["progress"] if key == "p" else q["complete"]
        text = convert(r[col])
        if text and not have:
            mapping[f"{qid}:{key}"] = text

json.dump(mapping, open("qextra_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
texts = sorted(set(mapping.values()), key=lambda s: (s.lower(), s))
os.makedirs("qextra_chunks_en", exist_ok=True)
for start in range(0, len(texts), 25):
    part = [{"i": start + k, "en": s} for k, s in enumerate(texts[start:start + 25])]
    with open(f"qextra_chunks_en/names_{start // 25:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
print(len(OLD), "old quests;", missing_in_vm, "not in vmangos;", len(mapping), "texts to add;", len(texts), "unique;",
      (len(texts) + 24) // 25, "chunks")
