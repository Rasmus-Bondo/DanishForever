# make_csvmisc_chunks.py - wow.export CSVs (mail templates, spell ranges, dungeon lock messages, skill texts) -> csvmisc_chunks_en/names_NNNN.json
# Only texts that no other table already covers; mail test strings are dropped. Mail tokens ($N, $B ...) become <Name>, \n ...
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import csv, glob, json, os, re

BASE = r"C:\Users\2000b\wow.export" + "\\"
SKIP_FILES = ("Data_Gossip.lua", "BookData.lua", "SpellDescs.lua", "GlobalStrings.lua")

known = set()
for f in glob.glob("*_chunks_en/*.json"):
    if f.startswith("csvmisc"):
        continue
    try:
        known |= {x["en"].strip() for x in json.load(open(f, encoding="utf-8")) if isinstance(x, dict) and "en" in x}
    except (OSError, ValueError, KeyError):
        pass
lua = "".join(open(f, encoding="utf-8").read() for f in glob.glob("addon/*.lua") if os.path.basename(f) not in SKIP_FILES)

def covered(t):
    return t in known or json.dumps(t, ensure_ascii=False) in lua

def rows(name):
    return list(csv.DictReader(open(BASE + name, encoding="utf-8", newline=""), delimiter=";"))

def convert(s):
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"\$[Bb]", "\n", s)
    s = re.sub(r"\$[Nn]", "<Name>", s)
    s = re.sub(r"\$[Cc]", "<Class>", s)
    s = re.sub(r"\$[Rr]", "<Race>", s)
    s = re.sub(r"\$[Gg]\s*([^:;]*?)\s*:\s*([^;]*?)\s*;", lambda m: m.group(1), s)
    return s.strip()

JUNK = re.compile(r"^\W*(?:this is a )?test\b|\btest mail\b|^\W*$", re.I)
found = {"mail": set(), "range": set(), "lock": set(), "skill": set()}
for r in rows("MailTemplate.csv"):
    t = convert(r["Body_lang"] or "")
    if t and not JUNK.search(t):
        found["mail"].add(t)
for r in rows("SpellRange.csv"):
    for c in ("DisplayName_lang", "DisplayNameShort_lang"):
        if (r[c] or "").strip():
            found["range"].add(r[c].strip())
for r in rows("MapDifficultyXCondition.csv"):
    if (r["FailureDescription_lang"] or "").strip():
        found["lock"].add(r["FailureDescription_lang"].strip())
for r in rows("SkillLine.csv"):
    for c in ("DisplayName_lang", "AlternateVerb_lang", "Description_lang"):
        if (r[c] or "").strip():
            found["skill"].add(r[c].strip())

texts = set()
for kind, s in found.items():
    new = {t for t in s if not covered(t)}
    print(kind, len(s), "unique;", len(new), "new")
    texts |= new
texts = sorted(texts, key=lambda s: (s.lower(), s))
os.makedirs("csvmisc_chunks_en", exist_ok=True)
PER = 25
for start in range(0, len(texts), PER):
    part = [{"i": start + k, "en": s} for k, s in enumerate(texts[start:start + PER])]
    with open(f"csvmisc_chunks_en/names_{start // PER:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
print(len(texts), "texts in", (len(texts) + PER - 1) // PER, "chunks")
