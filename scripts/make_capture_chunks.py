# make_capture_chunks.py - English UI/tooltip lines captured in game (/dui capture on) -> translatable chunks
# Reads DanishUI.lua from every WoW SavedVariables folder, drops text that is already Danish / already translated by the
# addon / meaningless, turns changing numbers into {1} {2} ... placeholders, and writes ONLY NEW entries as
# capture_chunks_en/names_NNNN.json ({"i", "en"}). capture_state.json remembers what was seen, so every run adds to it.
# Then: python scripts\run_items.py capture ; python scripts\build_capture_lua.py ; install work\addon\Captured.lua
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re, sys

WOW = r"C:\Program Files (x86)\World of Warcraft"
ADDON = os.path.join(WOW, "_classic_beta_", "Interface", "AddOns", "DanishUI")
PER_CHUNK = 60
NUM = re.compile(r"\d+(?:[.,]\d+)*")
COLOR = re.compile(r"\|c[0-9a-fA-F]{8}|\|r|\|n|\|T[^|]*\|t|\|H[^|]*\|h|\|h|\|A[^|]*\|a|\|K[^|]*\|k")

def unlua(s):
    s = re.sub(r"\\(\d{1,3})", lambda m: chr(int(m.group(1))) if int(m.group(1)) < 128 else m.group(0), s)
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t", "r": "\r"}.get(m.group(1), m.group(1)), s)

def captured():
    out = []
    for p in glob.glob(os.path.join(WOW, "*", "WTF", "Account", "*", "SavedVariables", "DanishUI.lua")):
        txt = open(p, encoding="utf-8", errors="replace").read()
        out += [unlua(m.group(1)) for m in re.finditer(r'^\["((?:[^"\\]|\\.)*)"\] = true,$', txt, re.M)]
    return out

def known_keys():
    keys = set()
    for p in glob.glob(os.path.join(ADDON, "*.lua")):
        if os.path.basename(p) in ("Captured.lua",):
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'^\s*\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', txt, re.M):
            keys.add(unlua(m.group(1)))
            keys.add(unlua(m.group(2)))           # Danish values too: text that is already Danish is not "missing"
        for m in re.finditer(r'^\s*\["((?:[^"\\]|\\.)*)"\]\s*=', txt, re.M):
            keys.add(unlua(m.group(1)))
        for m in re.finditer(r'^\s*[A-Za-z_]\w*\s*=\s*"((?:[^"\\]|\\.)*)"', txt, re.M):     # GlobalStrings: TAG = "Danish"
            keys.add(unlua(m.group(1)))
    return keys

WORD = re.compile(r"[A-Za-zÆØÅæøåéüÉ]{3,}")

def vocabularies():
    """words that appear in the English keys / Danish values of the addon's own tables"""
    en_w, da_w = set(), set()
    for p in glob.glob(os.path.join(ADDON, "*.lua")):
        if os.path.basename(p) == "Captured.lua":
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'^\s*\["((?:[^"\\]|\\.)*)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', txt, re.M):
            en_w.update(w.lower() for w in WORD.findall(unlua(m.group(1))))
            da_w.update(w.lower() for w in WORD.findall(unlua(m.group(2))))
        for m in re.finditer(r'^\s*[A-Za-z_]\w*\s*=\s*"((?:[^"\\]|\\.)*)"', txt, re.M):
            da_w.update(w.lower() for w in WORD.findall(unlua(m.group(1))))
    return en_w, da_w

EN_WORDS, DA_WORDS = vocabularies()

def looks_danish(text):
    """only words we know from our Danish translations, none that is English-only: skip (already translated text seen again)"""
    words = [w.lower() for w in WORD.findall(COLOR.sub(" ", text))]
    da_only = [w for w in words if w in DA_WORDS and w not in EN_WORDS]
    en_only = [w for w in words if w in EN_WORDS and w not in DA_WORDS]
    return len(da_only) >= 1 and not en_only

state_path = "capture_state.json"
state = json.load(open(state_path, encoding="utf-8")) if os.path.exists(state_path) else {"next": 0, "items": {}}
known = known_keys()
seen_in_game = captured()
new, skipped = [], {"danish": 0, "known": 0, "meaningless": 0, "old": 0}
for text in sorted(set(seen_in_game)):
    if re.search(r"[æøåÆØÅ]", text) or text.startswith("DanishUI") or looks_danish(text):
        skipped["danish"] += 1
        continue
    if re.search(r"\|c(?![0-9a-fA-F]{8})", text) or re.search(r"\|c[0-9a-fA-F]{8}#", text):
        skipped["meaningless"] += 1           # broken colour code, or a Battle.net tag (name#1234): nothing to translate
        continue
    if "|Hchannel" in text or re.match(r"^\{?\d*\}?\.?(General|Trade|LocalDefense|LookingForGroup|world|WorldDefense|GuildRecruitment)", text):
        skipped["meaningless"] += 1           # chat channel names are matched by the game itself; translating them would break channels
        continue
    plain = NUM.sub("", COLOR.sub("", text))
    if not re.search(r"[A-Za-z]{3}", plain) or len(text) > 400:
        skipped["meaningless"] += 1
        continue
    if text in known:
        skipped["known"] += 1
        continue
    # numbers -> {k}
    k = 0
    def num(m):
        global k
        k += 1
        return "{%d}" % k
    # colour/link codes (|cffffd100 ...) are kept as they are; only numbers outside them become placeholders
    pieces = re.split("(" + COLOR.pattern + ")", text)
    tpl = "".join(p if n % 2 else NUM.sub(num, p) for n, p in enumerate(pieces))
    is_pat = k > 0
    key = tpl
    if key in state["items"]:
        skipped["old"] += 1
        continue
    i = state["next"]
    state["next"] += 1
    state["items"][key] = {"i": i, "pat": is_pat}
    new.append({"i": i, "en": tpl})

os.makedirs("capture_chunks_en", exist_ok=True)
existing = len(glob.glob("capture_chunks_en/names_*.json"))
for n, start in enumerate(range(0, len(new), PER_CHUNK)):
    with open(f"capture_chunks_en/names_{existing + n:04d}.json", "w", encoding="utf-8") as f:
        json.dump(new[start:start + PER_CHUNK], f, ensure_ascii=False, indent=1)
json.dump(state, open(state_path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("captured lines:", len(set(seen_in_game)), "| new:", len(new), "| skipped:", skipped,
      "| chunks written:", (len(new) + PER_CHUNK - 1) // PER_CHUNK)
for e in new[:15]:
    print("  ", e["en"][:120].replace("\n", "\\n"))
