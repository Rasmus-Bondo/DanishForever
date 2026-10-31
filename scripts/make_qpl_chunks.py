# make_qpl_chunks.py <PolishForever Quests.lua> <pf_gap_ids.json> - Polish source text -> two batches
#   qpl_chunks_en/chunk_NNNN.json : quests that exist in the game but that vmangos and warcraftdb lack (record format of chunks_en, texts in Polish)
#   qplextra_chunks_en/names_NNNN.json + qplextra_en.json : progress/hand-in texts (Polish) for old quests that still lack them
# PolishForever data is CC BY 4.0 (credit: CREDITS.txt). Tokens are normalised to the form our other quest texts use.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import json, os, re, sys

PF, IDS = sys.argv[1], sys.argv[2]
ids = json.load(open(IDS))
STR = re.compile(r'"((?:[^"\\]|\\.)*)"')

def convert(s):
    s = re.sub(r"\\(.)", lambda m: {"n": "\n", "t": " "}.get(m.group(1), m.group(1)), s)
    s = s.replace("NEW_LINE", "\n")
    s = re.sub(r"\$[Bb]", "\n", s)
    s = re.sub(r"\$[Nn]", "<Name>", s)
    s = re.sub(r"\$[Cc]", "<Class>", s)
    s = re.sub(r"\$[Rr]", "<Race>", s)
    s = re.sub(r"\$\d+o\w?", "X", s)                                                     # "$1oa" = the required item count
    s = re.sub(r"\$[Gg]\s*([^:;]*?)\s*:\s*([^;]*?)\s*;", lambda m: m.group(1), s)      # gender switch -> first form
    s = re.sub(r" +\n", "\n", s)
    return s.strip() or None

P = {}
for line in open(PF, encoding="utf-8"):
    m = re.match(r"^\[(\d+)\]=\{(.*)\},?\s*$", line)
    if m:
        f = STR.findall(m.group(2))
        if len(f) >= 5:
            P[int(m.group(1))] = [convert(x) for x in f[:5]]          # title, log, desc, progress, complete

TEST = re.compile(r"\btest\b|\bunused\b|\bdnd\b|\[ph\]", re.I)
quests, skipped = [], []
for qid in ids["b_pfonly"]:
    t, log, desc, prog, comp = P[qid]
    if not t or TEST.search(t):
        skipped.append((qid, t))
        continue
    quests.append({"id": qid, "name": t, "log": log, "desc": desc, "progress": prog, "complete": comp, "objectives": []})
os.makedirs("qpl_chunks_en", exist_ok=True)
for start in range(0, len(quests), 25):
    with open(f"qpl_chunks_en/chunk_{start // 25:04d}.json", "w", encoding="utf-8") as f:
        json.dump(quests[start:start + 25], f, ensure_ascii=False, indent=1)
print(len(quests), "Forever-only quests in", (len(quests) + 24) // 25, "chunks; skipped:", skipped)

mapping = {}
for qid in ids["a_need"]:
    if qid in P:
        for key, idx in (("p", 3), ("c", 4)):
            if P[qid][idx]:
                mapping[f"{qid}:{key}"] = P[qid][idx]
json.dump(mapping, open("qplextra_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
texts = sorted(set(mapping.values()), key=lambda s: (s.lower(), s))
os.makedirs("qplextra_chunks_en", exist_ok=True)
for start in range(0, len(texts), 25):
    part = [{"i": start + k, "en": s} for k, s in enumerate(texts[start:start + 25])]
    with open(f"qplextra_chunks_en/names_{start // 25:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
print(len(mapping), "progress/hand-in texts for old quests;", len(texts), "unique in", (len(texts) + 24) // 25, "chunks")
