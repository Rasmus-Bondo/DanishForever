# add_gossip_extra.py <npc_lines_extra.json> - append extra English NPC lines (from vmangos) to gossip_en.json and cut new gossip_chunks_en files
# Existing entries keep their index, so the translations already in gossip_chunks_da stay valid. Safe to run twice (known keys are skipped).
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import json, math, os, re, sys

PER_CHUNK = 60

def pf_hash(text):
    """Port of PF.Hash (PolishForever, MIT) with Lua number semantics - same as extract_vmangos_text.py."""
    b = text.encode("utf-8")
    if not b:
        return 0
    counter, n = 1, len(b)
    for i in range(1, n + 1, 3):
        counter = math.fmod(counter * 8161, 4294967279)
        counter += b[i - 1] * 16776193
        counter += (b[i] if i < n else (n - i + 256)) * 8372226
        counter += (b[i + 1] if i + 1 < n else (n - i + 256)) * 3932164
    return int(math.fmod(counter, 4294967291))

def clean(t):
    t = re.sub(r"[\r\n]", "", t)
    return re.sub(r"\$[BbNnRrCc]\$?", "", t)

items = json.load(open("gossip_en.json", encoding="utf-8"))
have = {e["key"] for e in items}
start = len(items)
added = []
for x in json.load(open(sys.argv[1], encoding="utf-8")):
    key = pf_hash(clean(x["text"]))
    if key in have:
        continue
    have.add(key)
    added.append({"key": key, "kinds": [x["kind"]], "text": x["text"]})
added.sort(key=lambda e: (e["text"].lower(), e["key"]))
items += added
json.dump(items, open("gossip_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

for k in range(0, len(added), PER_CHUNK):
    part = [{"i": start + k + j, "en": e["text"]} for j, e in enumerate(added[k:k + PER_CHUNK])]
    name = f"gossip_chunks_en/names_{(start + PER_CHUNK - 1) // PER_CHUNK + k // PER_CHUNK:04d}.json"
    with open(name, "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
    print(name, len(part), "lines, i =", part[0]["i"], "-", part[-1]["i"])
print(len(added), "lines added;", len(items), "in gossip_en.json")
