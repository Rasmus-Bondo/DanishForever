# make_vm_quest_chunks.py <PolishForever Quests.lua> - quests PolishForever covers that we lack -> vmangos text -> chunks_en/chunk_NNNN.json
# Same record format as the scraped quests (id, name, log, desc, progress, complete, objectives). Test quests are filtered out
# and listed in vm_quests_skipped.json. Existing chunk numbering is kept; new chunks have 25 quests, ordered by quest ID.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os, re, sqlite3, sys

THEIRS = {int(m.group(1)) for l in open(sys.argv[1], encoding="utf-8") for m in [re.match(r"^\[(\d+)\]=\{", l)] if m}
known = set()
for f in glob.glob("chunks_en/*.json"):
    known |= {q["id"] for q in json.load(open(f, encoding="utf-8"))}

con = sqlite3.connect("file:vmangos_db/extracted/sqlite-dump/mangos.sqlite?mode=ro", uri=True)
con.row_factory = sqlite3.Row
best = {}                                    # one row per quest: the latest patch
for r in con.execute("select * from quest_template order by patch"):
    best[r["entry"]] = r

# a title that marks a test/unused quest, or body text that says so (a plain word like "test" is common in real quests)
TITLE_TEST = re.compile(r"test quest|test kill|^test \d+$|\bdnd\b|<nyi>|\[ph\]|\bunused\b|\bdeprecated\b|\bobsolete\b|placeholder|^zz|<txt>"
                        r"|do not use|don'?t use|\bdebug\b|\(\d+\)\w*$|^\W*$", re.I)
BODY_TEST = re.compile(r"test quest|new test again|^\s*(?:test|todo|tbd|placeholder)\b|<nyi>|\[ph\]|do not use|unused quest", re.I)

def convert(s):
    """vmangos text tokens -> the form used by the scraped quests"""
    if not s:
        return None
    s = s.replace("\r", "")
    s = re.sub(r"\$[Bb]", "\n", s)
    s = re.sub(r"\$[Nn]", "<Name>", s)
    s = re.sub(r"\$[Cc]", "<Class>", s)
    s = re.sub(r"\$[Rr]", "<Race>", s)
    s = re.sub(r"\$[Gg]\s*([^:;]*?)\s*:\s*([^;]*?)\s*;", lambda m: m.group(1), s)      # "$g lad : lass;" -> male form
    s = s.strip()
    return s or None

new, skipped = [], []
for qid in sorted(THEIRS - known):
    r = best.get(qid)
    if r is None:
        continue
    title = (r["Title"] or "").strip()
    text = " ".join((r[c] or "") for c in ("Details", "Objectives", "OfferRewardText", "RequestItemsText"))
    if not title or TITLE_TEST.search(title) or BODY_TEST.search(text):
        skipped.append({"id": qid, "title": title, "why": "no title" if not title else "test pattern",
                        "text": text.strip()[:120]})
        continue
    objectives = [convert(r[f"ObjectiveText{i}"]) for i in range(1, 5)]
    new.append({"id": qid, "name": title, "log": convert(r["Objectives"]), "desc": convert(r["Details"]),
                "progress": convert(r["RequestItemsText"]), "complete": convert(r["OfferRewardText"]),
                "objectives": [o for o in objectives if o]})

json.dump(skipped, open("vm_quests_skipped.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
last = max(int(re.search(r"(\d+)", os.path.basename(f)).group(1)) for f in glob.glob("chunks_en/chunk_*.json"))
first = last + 1
for start in range(0, len(new), 25):
    last += 1
    with open(f"chunks_en/chunk_{last:04d}.json", "w", encoding="utf-8") as f:
        json.dump(new[start:start + 25], f, ensure_ascii=False, indent=1)
print(len(THEIRS - known), "missing;", len(new), "new quests in chunks", first, "-", last, ";", len(skipped), "skipped (see vm_quests_skipped.json)")
