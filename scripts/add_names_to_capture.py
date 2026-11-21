# add_names_to_capture.py <item|spell|npc|object> ... - new_<kind>_names.jsonl (from scrape_new_names.py): names that no addon table translates yet
# become capture chunks (capture_state.json + capture_chunks_en/names_NNNN.json, numbered from 0100 up). Then: run_items.py capture, build_capture_lua.py.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))
import glob, json, re, sys

ADDON = r"C:\Program Files (x86)\World of Warcraft\_forever_\Interface\AddOns\DanishForever"
PER_CHUNK = 60
unlua = lambda s: s.replace('\\"', '"').replace("\\\\", "\\")
keys = set()
for p in glob.glob(ADDON + "/*.lua"):
    t = open(p, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r'^\s*\["((?:[^"\\]|\\.)*)"\]\s*=', t, re.M):
        keys.add(unlua(m.group(1)))
state = json.load(open("capture_state.json", encoding="utf-8"))
names = []
for kind in sys.argv[1:]:
    for line in open(f"new_{kind}_names.jsonl", encoding="utf-8"):
        n = json.loads(line)["name"].strip()
        if n and n not in keys and n not in state["items"] and n not in names:
            names.append(n)
nums = [int(re.search(r"(\d+)", os.path.basename(f)).group(1)) for f in glob.glob("capture_chunks_*/names_*.json")]
start = max([99] + [x for x in nums if x < 900]) + 1
rows = []
for n in names:
    i = state["next"]; state["next"] += 1
    state["items"][n] = {"i": i, "pat": False}
    rows.append({"i": i, "en": n})
os.makedirs("capture_chunks_en", exist_ok=True)
for c, s in enumerate(range(0, len(rows), PER_CHUNK)):
    json.dump(rows[s:s + PER_CHUNK], open(f"capture_chunks_en/names_{start + c:04d}.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
json.dump(state, open("capture_state.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=0)
print(len(rows), "names ->", (len(rows) + PER_CHUNK - 1) // PER_CHUNK, "chunks from", start)
