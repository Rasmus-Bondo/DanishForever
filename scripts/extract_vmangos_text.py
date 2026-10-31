# extract_vmangos_text.py - English NPC gossip/speech text from the vmangos database snapshot (SQLite)
#   -> gossip_en.json   [{"key": <PolishForever hash>, "kinds": [...], "text": "<raw English>"}]
#   -> gossip_chunks_en/names_NNNN.json   [{"i", "en"}]   (the key is looked up again at build time via gossip_en.json)
# The key is PolishForever's: PF.Hash of the text with line breaks and $B/$N/$R/$C tokens removed (their Clean()).
# Only texts whose key also appears in PolishForever's Gossip.lua / Speech.lua are kept: that is the set of lines
# a player can meet in this client, and it lets us check that our hash and cleaning match theirs.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import json, math, os, re, sqlite3

BASE = os.getcwd()
PER_CHUNK = 60

def pf_hash(text):
    """Port of PF.Hash (PolishForever, MIT) with Lua number semantics."""
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

def polish_keys(path):
    keys = set()
    for l in open(path, encoding="utf-8"):
        m = re.match(r"^\[(\d+)\]=", l)
        if m:
            keys.add(int(m.group(1)))
    return keys

known = polish_keys(os.path.join(BASE, "Gossip.lua")) | polish_keys(os.path.join(BASE, "polishforever_src", "Data", "Speech.lua"))

con = sqlite3.connect(f"file:{BASE}/vmangos_db/extracted/sqlite-dump/mangos.sqlite?mode=ro", uri=True)
cur = con.cursor()
sources = [
    ("speech", "select male_text from broadcast_text"),
    ("speech", "select female_text from broadcast_text"),
    ("option", "select option_text from gossip_menu_option"),
    ("option", "select box_text from gossip_menu_option"),
    ("trainer", "select content_default from npc_trainer_greeting"),
    ("greeting", "select content_default from quest_greeting"),
    ("script", "select content_default from script_texts"),
]

found = {}
for kind, sql in sources:
    for (t,) in cur.execute(sql):
        if not t or not t.strip():
            continue
        key = pf_hash(clean(t))
        if key in known:
            entry = found.setdefault(key, {"key": key, "kinds": [], "text": t})
            if kind not in entry["kinds"]:
                entry["kinds"].append(kind)

items = sorted(found.values(), key=lambda e: (e["text"].lower(), e["key"]))     # similar lines stay together
json.dump(items, open(os.path.join(BASE, "gossip_en.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)

os.makedirs(os.path.join(BASE, "gossip_chunks_en"), exist_ok=True)
n = 0
for start in range(0, len(items), PER_CHUNK):
    part = [{"i": start + k, "en": e["text"]} for k, e in enumerate(items[start:start + PER_CHUNK])]
    with open(os.path.join(BASE, "gossip_chunks_en", f"names_{start // PER_CHUNK:04d}.json"), "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
    n += 1

chars = sum(len(e["text"]) for e in items)
missing = len(known) - len(found)
print(f"{len(items)} English texts kept ({chars} chars) in {n} chunks of {PER_CHUNK}")
print(f"Polish keys with no English text found in vmangos: {missing} of {len(known)}")
kinds = {}
for e in items:
    for k in e["kinds"]:
        kinds[k] = kinds.get(k, 0) + 1
print("by source:", kinds)
tok = {}
for e in items:
    for m in re.findall(r"\$[a-zA-Z]|\$\d+[a-zA-Z]|<[^>]{1,40}>|\$[gG][^;]*;", e["text"]):
        key = m if len(m) < 12 else m[:2]
        tok[key] = tok.get(key, 0) + 1
print("most common tokens:", sorted(tok.items(), key=lambda kv: -kv[1])[:14])
