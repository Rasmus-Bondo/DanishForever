# make_ml_chunks.py <MultiLanguage Database dir> - English tables of the MultiLanguage addon (Classic Era client data) -> translation batches
# for everything our data lacks: NPC names/titles, item names, spell names, quests (records) and progress/hand-in texts of old quests.
# Output: mlnames/mltitles/mlitems/mlspells_chunks_en/names_NNNN.json, mlq_chunks_en/chunk_NNNN.json, mlqextra_chunks_en + mlqextra_en.json
# Only English strings are taken from the repo (Blizzard game text), no translations.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, html, json, os, re, sys

DB = sys.argv[1].rstrip("\\/") + "\\"
FIELD = re.compile(r'(\w+) = (nil|"(?:[^"\\]|\\.)*")')

def unq(s):
    return None if s == "nil" else re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), s[1:-1])

def load(kind):
    out = {}
    for line in open(DB + f"{kind}\\enUS.lua", encoding="utf-8"):
        m = re.match(r"^\[(\d+)\] = \{(.*)\},?\s*$", line)
        if m:
            out[int(m.group(1))] = {k: unq(v) for k, v in FIELD.findall(m.group(2))}
    return out

strip = lambda s: re.sub(r"^\[q\d?\]", "", s or "").strip()

def chunks_en(*kinds):
    s = set()
    for k in kinds:
        for f in glob.glob(f"{k}_chunks_en/*.json"):
            for x in json.load(open(f, encoding="utf-8")):
                s.add(x["en"].strip())
    return s

known = set()
for f in glob.glob("*_chunks_en/*.json"):
    if os.path.basename(os.path.dirname(f)).startswith("ml"):
        continue
    try:
        known |= {x["en"].strip() for x in json.load(open(f, encoding="utf-8")) if isinstance(x, dict) and "en" in x}
    except (OSError, ValueError, KeyError):
        pass

INTERNAL = re.compile(r"^S\d\d\b|\(DNT\)|\bDNT\b|\bDMF P\d|\btest\b|\bunused\b|\bdeprecated\b|\bobsolete\b|\[|\bDND\b|\bQA\b|\bCamp KC\b|\bStalker\b|\bTrigger\b"
                      r"|\bVisual\b|\bCredit\b|\bBunny\b|\bDummy\b|\bPH\b|placeholder|^zz|\d{4,}|\bCosmetic\b|\bAgro \d|^AQ\d* |\(Reuse\)|^Monster - |^NPC |^\*|<UNUSED>|\bTEMP\b|\bPOI\b", re.I)

ITEM_INTERNAL = re.compile(r"^S\d\d\b|\bDNT\b|\btest\b|\bunused\b|\bdeprecated\b|\bobsolete\b|\[|^zz|\(Reuse\)|^Monster - |^NPC |^\*|<UNUSED>|\bTEMP\b|\bPLACEHOLDER\b", re.I)

def write_names(kind, texts):
    texts = sorted({t for t in texts if t and t.strip()}, key=lambda s: (s.lower(), s))
    d = f"{kind}_chunks_en"
    os.makedirs(d, exist_ok=True)
    per = 25 if kind in ("mlflavor",) else 300
    for start in range(0, len(texts), per):
        part = [{"i": start + k, "en": s} for k, s in enumerate(texts[start:start + per])]
        with open(f"{d}/names_{start // per:04d}.json", "w", encoding="utf-8") as f:
            json.dump(part, f, ensure_ascii=False, indent=1)
    print(f"{kind}: {len(texts)} strings in {(len(texts) + per - 1) // per} chunks")

# ---- NPCs
N = load("Npcs")
cre = chunks_en("creatures", "creatures2")
titles = chunks_en("titles")
names = [n for n in {v["name"].strip() for v in N.values() if v.get("name")} if n not in cre and n not in known and not INTERNAL.search(n)]
subs = [n for n in {v["subname"].strip() for v in N.values() if v.get("subname")} if n not in titles and n not in known and not INTERNAL.search(n)]
write_names("mlnames", names)
write_names("mltitles", subs)

# ---- items
I = load("Items")
have_items = chunks_en("items")
items = [n for n in {strip(v["name"]) for v in I.values() if v.get("name")} if n and n not in have_items and n not in known and not ITEM_INTERNAL.search(n)]
write_names("mlitems", items)
dropped = [n for n in {strip(v["name"]) for v in I.values() if v.get("name")} if n and n not in have_items and n not in known and ITEM_INTERNAL.search(n)]
print("   items dropped as internal:", len(dropped), sorted(dropped)[:8])

# ---- spells
S = load("Spells")
have_sp = chunks_en("spells")
spells = [n for n in {strip(v["name"]) for v in S.values() if v.get("name")} if n and n not in have_sp and n not in known and not INTERNAL.search(n)]
write_names("mlspells", spells)

# ---- item flavor texts: quoted lines of the tooltip
flavor_have = have_items | known              # items_chunks_en holds the names (names_*) and the flavor texts (desc_*)
fl = set()
for v in I.values():
    for ln in (v.get("additional_info") or "").split("\n"):
        ln = strip(ln)
        if len(ln) > 8 and ln.startswith('"') and ln.endswith('"'):
            t = ln[1:-1].strip()
            if t and t not in flavor_have:
                fl.add(t)
print("   candidate flavor texts not in our data:", len(fl))
write_names("mlflavor", fl)

# ---- quests
def conv(s):
    if not s:
        return None
    s = html.unescape(s).replace("\xa0", " ").replace("\r", "")
    s = re.sub(r"<name>", "<Name>", s, flags=re.I)
    s = re.sub(r"<class>", "<Class>", s, flags=re.I)
    s = re.sub(r"<race>", "<Race>", s, flags=re.I)
    s = re.sub(r"\$[Bb]", "\n", s)
    s = re.sub(r"\$[Nn]", "<Name>", s)
    s = re.sub(r"\$[Cc]", "<Class>", s)
    s = re.sub(r"\$[Rr]", "<Race>", s)
    s = re.sub(r"\$[Gg]\s*([^:;]*?)\s*:\s*([^;]*?)\s*;", lambda m: m.group(1), s)
    s = re.sub(r" +\n", "\n", s)
    return s.strip() or None

Q = load("Quests")
ours = {}
for f in glob.glob("chunks_en/*.json") + glob.glob("qpl_chunks_en/*.json"):
    for q in json.load(open(f, encoding="utf-8")):
        ours[q["id"]] = q
TITLE_TEST = re.compile(r"test quest|test kill|^test \d+$|\bdnd\b|<nyi>|\[ph\]|\bunused\b|\bdeprecated\b|\bobsolete\b|placeholder|^zz|<txt>|do not use|don'?t use|\bdebug\b|\(\d+\)\w*$|^\W*$|\(old\)|\bTEMP\b|\breuse\b|<change|\bcopy\b", re.I)
BODY_TEST = re.compile(r"test quest|new test again|^\s*(?:test|todo|tbd|placeholder)\b|<nyi>|\[ph\]|do not use|unused quest", re.I)
HEADER = re.compile(r"\s*(?:Upon completion of this quest you will gain:|You will receive:|The following spell will be cast on you:"
                    r"|You will (?:also )?(?:be able to )?(?:choose|receive)[^:\n]*:|Rewards)\s*$", re.I)

def clean_quest(objective, description):
    """the source sometimes glues the description and a rewards header onto the objective; cut them off"""
    log, desc = conv(objective), conv(description)
    if log and desc and len(desc) > 30:
        lc, dc = re.sub(r"\s+", " ", log), re.sub(r"\s+", " ", desc)[:40]
        i = lc.find(dc)
        if i > 0:
            log = lc[:i].strip()
    log = HEADER.sub("", log).strip() if log else log
    desc = HEADER.sub("", desc).strip() if desc else desc
    return log or None, desc or None

for d in ("mlq_chunks_en", "mlqextra_chunks_en"):               # regenerated from scratch: no stale chunk files
    if os.path.isdir(d):
        for f in glob.glob(d + "/*.json"):
            os.remove(f)
new, skipped = [], []
for qid in sorted(set(Q) - set(ours)):
    v = Q[qid]
    title = conv(v.get("title"))
    log_, desc_ = clean_quest(v.get("objective"), v.get("description"))
    rec = {"id": qid, "name": title, "log": log_, "desc": desc_,
           "progress": conv(v.get("progress")), "complete": conv(v.get("completion")), "objectives": []}
    text = " ".join(rec[k] or "" for k in ("log", "desc", "progress", "complete"))
    if (not title or TITLE_TEST.search(title) or BODY_TEST.search(text) or re.search(r"\$\w", text + title)
            or not any(rec[k] for k in ("log", "desc", "progress", "complete"))):
        skipped.append((qid, title))
        continue
    new.append(rec)
os.makedirs("mlq_chunks_en", exist_ok=True)
for start in range(0, len(new), 25):
    with open(f"mlq_chunks_en/chunk_{start // 25:04d}.json", "w", encoding="utf-8") as f:
        json.dump(new[start:start + 25], f, ensure_ascii=False, indent=1)
print(f"mlq: {len(new)} new quests in {(len(new) + 24) // 25} chunks; skipped {len(skipped)}: {[t for _, t in skipped][:12]}")

# ---- progress/hand-in texts for old quests that still have neither (after vmangos and Polish fills)
filled = set()
for fn in ("qextra_en.json", "qplextra_en.json"):
    if os.path.exists(fn):
        filled |= {int(k.split(":")[0]) for k in json.load(open(fn, encoding="utf-8"))}
mapping = {}
for qid, q in ours.items():
    if qid in Q and qid not in filled and not q["progress"] and not q["complete"]:
        for key, col in (("p", "progress"), ("c", "completion")):
            t = conv(Q[qid].get(col))
            if t and not re.search(r"\$\w", t):
                mapping[f"{qid}:{key}"] = t
json.dump(mapping, open("mlqextra_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
texts = sorted(set(mapping.values()), key=lambda s: (s.lower(), s))
os.makedirs("mlqextra_chunks_en", exist_ok=True)
for start in range(0, len(texts), 25):
    part = [{"i": start + k, "en": s} for k, s in enumerate(texts[start:start + 25])]
    with open(f"mlqextra_chunks_en/names_{start // 25:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
print(f"mlqextra: {len(mapping)} texts for old quests, {len(texts)} unique in {(len(texts) + 24) // 25} chunks")
