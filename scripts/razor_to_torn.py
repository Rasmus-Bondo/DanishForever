# razor_to_torn.py [--apply] - "Razor" was translated "Barber" (Razorfen = "Rasorhegn"); make it "Torne" everywhere.
# 1) Exact tables (["English"] = "Danish"): only entries whose English key has a word starting with Razor are changed.
# 2) Prose (quests, gossip, books): only "Barber"+suffix compounds whose suffix was learned from step 1, and Rasorhegn.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))
import glob, re, sys, collections, json

APPLY = "--apply" in sys.argv
FILES = glob.glob("addon/*.lua") + ["Data_Items.lua", "Data_Quests.lua"]
ENTRY = re.compile(r'\["((?:[^"\\]|\\.)*)"\](\s*=\s*)"((?:[^"\\]|\\.)*)"')
RAZ = re.compile(r"\bRazor", re.I)
BARB = re.compile(r"(?<![A-Za-zæøå])([Bb])arber(?=[a-zæøåA-ZÆØÅ\- ]|$)")

def torne(m):
    word = m.string[m.end():m.end() + 1]
    base = "Torn" if not re.match(r"[a-zæøåA-ZÆØÅ\-]", word) else "Torne"
    return base if m.group(1) == "B" else base.lower()

def conv_entry(v):
    v = v.replace("Rasorhegn", "Tornehegn").replace("rasorhegn", "tornehegn")
    return BARB.sub(torne, v)

filedata = {}; suffixes = collections.Counter()
for p in FILES:
    t = open(p, "rb").read().decode("utf-8")
    filedata[p] = t
    for m in ENTRY.finditer(t):
        k, v = m.group(1), m.group(3)
        if len(k) <= 80 and RAZ.search(k):
            for w in re.findall(r"(?<![A-Za-zæøå])[Bb]arber([a-zæøå]{2,})", v):
                suffixes[w] += 1
SUF = sorted([s for s in suffixes if s not in ("ens",)], key=len, reverse=True)
print("learned suffixes:", SUF)
PROSE = re.compile(r"(?<![A-Za-zæøå])([Bb])arber(?=(?:" + "|".join(map(re.escape, SUF)) + r"))")

def conv_prose(v):
    v = v.replace("Rasorhegn", "Tornehegn").replace("rasorhegn", "tornehegn")
    return PROSE.sub(torne, v)

changed = collections.Counter(); samples = []
for p, t in filedata.items():
    def sub(m):
        k, eq, v = m.group(1), m.group(2), m.group(3)
        nv = conv_entry(v) if (len(k) <= 80 and RAZ.search(k)) else conv_prose(v)
        if nv != v:
            changed[p] += 1
            samples.append((k[:45], v[:45], nv[:45]))
        return '["' + k + '"]' + eq + '"' + nv + '"'
    nt = ENTRY.sub(sub, t)
    if p.endswith("Data_Quests.lua") or p.endswith("Data_Gossip.lua"):
        n2 = conv_prose(nt)
        if n2 != nt:
            changed[p] += 1
        nt = n2
    if APPLY and nt != t:
        open(p, "wb").write(nt.encode("utf-8"))

cc = 0
for f in glob.glob("capture_chunks_da/names_*.json") + glob.glob("chunks_da/*.json") + glob.glob("gossip_chunks_da/*.json"):
    raw = open(f, "rb").read().decode("utf-8")
    nr = conv_prose(raw)
    if nr != raw:
        cc += 1
        if APPLY:
            open(f, "wb").write(nr.encode("utf-8"))
print(sum(changed.values()), "entries/files changed in", len(changed), "files;", cc, "chunk files with Rasorhegn/compound changes")
import random
random.seed(2)
for s in random.sample(samples, min(30, len(samples))):
    print(s)
