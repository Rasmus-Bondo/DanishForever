# fel_to_hel.py [--apply] - demonic "fel" was translated "ond"/"Fel-"/"Fæl-"; make it "hel" everywhere.
# 1) Exact tables (["English"] = "Danish"): only entries whose English key contains the demonic fel word are changed.
# 2) Prose (quests, gossip, books, descriptions): only compounds whose suffix was learned from step 1 (Ondhund, Ondskov, ...) plus Fel-/Felwood/Felhunter.
# Without --apply it only prints what would change.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))
import glob, re, sys, collections

APPLY = "--apply" in sys.argv
FILES = glob.glob("addon/*.lua") + ["Data_Items.lua", "Data_Quests.lua"]
ENTRY = re.compile(r'\["((?:[^"\\]|\\.)*)"\](\s*=\s*)"((?:[^"\\]|\\.)*)"')
# English key words that mean demonic fel (Felstone Field, Felix, Feline, fellow, felt ... are not)
FELKEY = re.compile(r"\b(?:[Ff]el|Fel(?:wood|cloth|heart|guard|hound|hunter|weave|weaver|blood|sworn|steed|paw|musk|vine|fire|bane|stalker|bat|bloom|beast|slayer|hide|ore|striker|blade|bough|bark|bind|moon|iron))(?=$|[^A-Za-z])|\bFelGuard|\bfelhunter", re.I)
FELKEY_EXCL = re.compile(r"\bFell|Felstone|Feline|Felix|Felicia|fellow|Felt\b|Felder|Felt ", re.I)
EVILKEY = re.compile(r"\b(?:Wicked|Evil|Malevolent|Vile)\b", re.I)

def is_fel(key):
    if FELKEY_EXCL.search(key) and not re.search(r"\bFel(?:wood|cloth|heart|guard|hound|hunter|weave)", key, re.I):
        return bool(re.search(r"\bFel\b", key))
    return bool(FELKEY.search(key))

ABS = [("Fælmusk", "Helmusk"), ("Fel-jæger", "Hel-jæger"), ("Fæl-jæger", "Hel-jæger"), ("Felhunter", "Hel-jæger"), ("Felwood", "Helskoven"), ("Felguard", "Helvagt"),
       ("Felcloth", "Helstof"), ("Felfire", "Helild"), ("Felheart", "Helhjerte"), ("Felhound", "Helhund"), ("Felweave", "Helvæv")]

def cap(m, s):
    return s.capitalize() if m[0].isupper() else s.lower()

def conv_entry(k, v, long=False):
    """Danish value of an entry whose English key is about fel."""
    o = v
    for a, b in ABS:
        v = re.sub(r"\b" + a, b, v)
    v = re.sub(r"\bFel(?=[-\s]|$)", "Hel", v)
    if not long:
        v = re.sub(r"\bOndt\b", "Hel", v)
    # Ond / ond at a word start: compounds (Ondrustning), or the separate word "Ond "; not ondskab/ondsind/ondart (real "evil")
    v = re.sub(r"\b([Oo])nd(?!sk[ae]b|sind|art|es?\b)(?=[a-zæøå\- ])", lambda m: "H" + "el" if m.group(1) == "O" else "hel", v) if not long else v
    if not long and not EVILKEY.search(k):
        v = re.sub(r"\b([Oo])nde(?= )", lambda m: "Hel" if m.group(1) == "O" else "hel", v)
    return v

changed = collections.Counter(); samples = []; suffixes = collections.Counter(); filedata = {}
for p in FILES:
    t = open(p, "rb").read().decode("utf-8")
    filedata[p] = t
    for m in ENTRY.finditer(t):
        k, v = m.group(1), m.group(3)
        if len(k) <= 80 and is_fel(k):
            for w in re.findall(r"\b[Oo]nd([a-zæøå][a-zæøå]+)", v):
                if not re.match(r"sk[ae]b|sind|art", w):
                    suffixes[w] += 1
SUF = [s for s, c in suffixes.items() if len(s) >= 3]
print("learned suffixes:", sorted(SUF))
PROSE = re.compile(r"\b([Oo])nd(?=(?:" + "|".join(sorted(map(re.escape, SUF), key=len, reverse=True)) + r"))")

def conv_prose(v):
    v = PROSE.sub(lambda m: "H" + "el" if m.group(1) == "O" else "hel", v)
    for a, b in ABS:
        v = re.sub(r"\b" + a, b, v)
    return re.sub(r"\bFel(?=-)", "Hel", v)

for p, t in filedata.items():
    def sub(m):
        k, eq, v = m.group(1), m.group(2), m.group(3)
        nv = conv_entry(k, v) if (len(k) <= 80 and is_fel(k)) else conv_prose(v)
        if nv != v:
            changed[p] += 1
            if len(samples) < 400:
                samples.append((k[:50], v[:60], nv[:60]))
        return '["' + k + '"]' + eq + '"' + nv + '"'
    nt = ENTRY.sub(sub, t)
    # quest records use n="", l="", d="" etc. in Data_Quests.lua and "[hash] = " lines in Data_Gossip.lua: handled by the same prose rule
    if p.endswith("Data_Quests.lua") or p.endswith("Data_Gossip.lua"):
        n2 = conv_prose(nt)
        if n2 != nt:
            changed[p] += 1
        nt = n2
    if APPLY and nt != t:
        open(p, "wb").write(nt.encode("utf-8"))
# capture chunks (en/da pairs) so that a rebuild of Captured.lua keeps the change
import json
cc = 0
for f in glob.glob("capture_chunks_da/names_*.json"):
    rows = json.load(open(f, encoding="utf-8"))
    en = {r["i"]: r["en"] for r in json.load(open(f.replace("_da", "_en"), encoding="utf-8"))} if os.path.exists(f.replace("_da", "_en")) else {}
    dirty = False
    for r in rows:
        k = r.get("en") or en.get(r.get("i"), "")
        d = r.get("da")
        if k and d and len(k) <= 80 and is_fel(k):
            nd = conv_entry(k, d)
            if nd != d:
                r["da"] = nd; dirty = True; cc += 1
    if APPLY and dirty:
        json.dump(rows, open(f, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print(cc, "capture chunk rows changed")
print(sum(changed.values()), "entries/files changed in", len(changed), "files")
import random
random.seed(1)
for s in random.sample(samples, min(40, len(samples))):
    print(s)
