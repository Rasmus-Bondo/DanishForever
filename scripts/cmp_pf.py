import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import re, json, glob, sqlite3, math, sys
pf = sys.argv[1]
def pf_hash(text):
    b = text.encode("utf-8")
    if not b: return 0
    counter, n = 1, len(b)
    for i in range(1, n + 1, 3):
        counter = math.fmod(counter * 8161, 4294967279)
        counter += b[i - 1] * 16776193
        counter += (b[i] if i < n else (n - i + 256)) * 8372226
        counter += (b[i + 1] if i + 1 < n else (n - i + 256)) * 3932164
    return int(math.fmod(counter, 4294967291))

# ---- quests ----
theirs = {int(m.group(1)) for l in open(pf + r"\Quests.lua", encoding="utf-8") for m in [re.match(r"^\[(\d+)\]=\{", l)] if m}
ours = set()
for f in glob.glob("chunks_en/*.json"):
    for q in json.load(open(f, encoding="utf-8")):
        ours.add(q["id"])
print("quests: theirs", len(theirs), "ours", len(ours), "both", len(theirs & ours), "only theirs", len(theirs - ours), "only ours", len(ours - theirs))

con = sqlite3.connect("file:vmangos_db/extracted/sqlite-dump/mangos.sqlite?mode=ro", uri=True)
cols = [r[1] for r in con.execute("pragma table_info(quest_template)")]
tcol = "Title" if "Title" in cols else [c for c in cols if c.lower() in ("title", "name")][0]
vm = {r[0]: r[1] for r in con.execute(f"select entry, {tcol} from quest_template")}
miss = sorted(theirs - ours)
print("their quest ids we lack:", len(miss), "| of those in vmangos:", sum(i in vm for i in miss))
print("sample:", [(i, vm.get(i)) for i in miss[:15]])
print("quests we have that they don't, sample:", sorted(ours - theirs)[:15])

# ---- creatures ----
th = {int(m.group(1)) for l in open(pf + r"\Creatures.lua", encoding="utf-8") for m in [re.match(r"^\[(\d+)\]=", l)] if m}
ours_names = {x["name"] for x in json.load(open("creatures_en.json", encoding="utf-8"))}
oh = {pf_hash(n) for n in ours_names}
print("creatures: theirs", len(th), "ours", len(ours_names), "hash overlap", len(th & oh), "theirs-only", len(th - oh))
vmn = {}
ccols = [r[1] for r in con.execute("pragma table_info(creature_template)")]
ncol = "name" if "name" in ccols else "Name"
for (n,) in con.execute(f"select {ncol} from creature_template"):
    if n: vmn[pf_hash(n)] = n
only = [vmn[h] for h in th - oh if h in vmn]
print("their-only creature hashes resolvable to a vmangos name:", len(only), "of", len(th - oh))
json.dump(sorted(set(only)), open("creatures_missing_vs_pf.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("sample:", sorted(set(only))[:25])
