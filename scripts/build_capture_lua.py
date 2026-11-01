# build_capture_lua.py - capture_state.json + capture_chunks_da/*.json -> addon/Captured.lua
# Lines without numbers become exact entries; lines with {k} placeholders become Lua patterns (numbers -> captures).
# Captured.lua only answers when nothing else in the addon translated the text (Core.lua calls ns.translateCaptured last).
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re

state = json.load(open("capture_state.json", encoding="utf-8"))
by_id = {v["i"]: (k, v["pat"]) for k, v in state["items"].items()}
da = {}
for f in sorted(glob.glob("capture_chunks_da/names_*.json")):
    for x in json.load(open(f, encoding="utf-8")):
        if isinstance(x.get("da"), str) and x["da"].strip() and x.get("i") in by_id:
            da[x["i"]] = x["da"]

KEEP = {"PvP", "(PvP)", "Idol", "Invasion"}        # the user wants these left alone ("PvP" must never become "SmS")
for i, t in list(da.items()):
    if by_id[i][0] in KEEP or "Dansk (scuffed)" in by_id[i][0] or re.fullmatch(r"\(Rang \{1\}\)", by_id[i][0]):
        da[i] = by_id[i][0]

def q(s):
    return json.dumps(s, ensure_ascii=False)

TOK = re.compile(r"\{(\d+)\}")
exact, pats = [], []
for i, t in sorted(da.items()):
    en, is_pat = by_id[i]
    if re.match(r"^\{1\}:\{2\} \w+ .*says:", en):
        continue                                # timestamped chat lines (contain player names)
    if re.search(r"'s Pet$", en) or en.startswith("title of "):
        continue                                # player pet names / another addon's placeholder text
    if en in ("CBuHkC", "Djudjaro's Pet") or en.startswith("Wendigo-man"):   # last one is already Danish ("Wendigo Mane")
        continue                                # random channel name / a player's pet name
    if "Dansk (scuffed)" in en or "Danish Forever" in en or "DanishForever" in en:
        continue                                # the addon's own name in the AddOns list / minimap text
    if re.match(r"^Your .+ reputation has (?:increased|decreased) by", en):
        continue                                # Core.lua has one general rule for these; no per-faction entries
    if not is_pat:
        exact.append((en, t))
        continue
    if sorted(TOK.findall(en)) != sorted(TOK.findall(t)):
        continue
    parts = TOK.split(en)                       # literal, k, literal, k, ...
    pat = "^" + "".join(re.sub(r"([^\w\s])", r"%\1", p) if n % 2 == 0 else "([%d%.,]+)" for n, p in enumerate(parts)) + "$"
    lit = max(parts[0::2], key=len)
    pats.append((len(lit), pat, t, lit))
pats.sort(key=lambda p: -p[0])

with open("addon/Captured.lua", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\n\n-- Text captured in game that no other table covered, translated afterwards (build_capture_lua.py).\n")
    f.write("local exact = {\n")
    for en, t in exact:
        f.write(f"    [{q(en)}] = {q(t)},\n")
    f.write("}\nlocal list = {\n")
    for _, pat, t, lit in pats:
        f.write(f"    {{{q(pat)}, {q(t)}, {q(lit)}}},\n")
    f.write("}\n")
    f.write('''
local cache, cached = {}, 0

function ns.translateCaptured(text)
    local v = exact[text]
    if v then return v end
    local hit = cache[text]
    if hit ~= nil then return hit or nil end
    local result = false
    for i = 1, #list do
        local p = list[i]
        if text:find(p[3], 1, true) then
            local caps = { text:match(p[1]) }
            if caps[1] then
                result = (p[2]:gsub("{(%d+)}", function(k) return caps[tonumber(k)] or "" end))
                break
            end
        end
    end
    cached = cached + 1
    if cached > 3000 then cache, cached = {}, 1 end
    cache[text] = result
    return result or nil
end
''')
print(len(exact), "exact +", len(pats), "pattern entries ->", len(da), "translated of", len(by_id), "captured")
