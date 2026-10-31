# make_patx_chunks.py <PolishForever Patterns.lua> - English tooltip/UI line patterns -> translatable templates with {1} {2} placeholders
# Each PolishForever entry starts with an English Lua pattern ("^Increases your haste by ([%d%.,%-]+)%%%.$"). We keep the pattern as the matcher
# and translate the template "Increases your haste by {1}%." into Danish with the same {k} placeholders.
# Output: patx_en.json [{"i", "pat", "tpl"}] and patx_chunks_en/names_NNNN.json [{"i", "en"}]. Only patterns that our spell templates do not already cover.
# PolishForever data is CC BY 4.0 (credit: CREDITS.txt); only the English patterns are used here.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os, re, sys

PER_CHUNK = 80
src = open(sys.argv[1], encoding="utf-8").read().split("\n")

def unlua(s):
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), s)

pats = set()
for ln in src:
    m = re.match(r'^\{"((?:[^"\\]|\\.)*)",(.*)\},?$', ln)
    if m:
        pats.add(unlua(m.group(1)))

CAP = re.compile(r"\((?:[^()%]|%.)*\)")
RETAIL = re.compile(r"\b(?:house|housing|neighborhood|endeavor|decor|anima|covenant|garrison|warband|delve|renown|dragonrid|dragonflight|shadowlands|"
                    r"legion|artifact|azerite|mythic\+|follower|mission table|transmog|battle pet|pet battle|collection|paragon|heirloom|"
                    r"discord|cpu|memory|latency|addon|bnet|battle\.net|raid finder|looking for group|keystone|affix|world quest|"
                    r"profession specialization|crafting order|crafter|spark|trait|talent tree|loadout|spec(?:ialization)? tree)", re.I)

def template(p):
    """English Lua pattern -> text with {k} placeholders, or None when the pattern is too complex"""
    s = p
    if s.startswith("^"):
        s = s[1:]
    if s.endswith("$") and not s.endswith("%$"):
        s = s[:-1]
    if re.search(r"\|[HWKcTAn4r]|\|r|:[^:;\s]+;", s):          # hyperlink, colour and plural markup
        return None
    k = 0
    def cap(m):
        nonlocal k
        k += 1
        return "\x00%d\x01" % k
    t = CAP.sub(cap, s)
    if re.search(r"(?<!%)[\[\]\*\+\-\?\.\(\)]", t.replace("%%", "")):     # classes/quantifiers outside captures
        return None
    t = re.sub(r"%(.)", r"\1", t)
    t = re.sub(r"\x00(\d+)\x01", r"{\1}", t)
    return t, k

# our spell templates, to skip what the spell matcher already covers (same skeleton idea as the coverage check)
def norm(s):
    s = re.sub(r"\s+", " ", s).strip().lower()
    return re.sub(r"(?:§\s*)+", "§ ", s).strip()
have = set()
for f in glob.glob("spells_chunks_en/desc_*.json"):
    for x in json.load(open(f, encoding="utf-8")):
        t = re.sub(r"\$\{[^}]*\}|\$<[^>]*>|\$\?[^\[\s]*|\$[/*]?\d*[A-Za-z]\d*;?|\[|\]|\$[lLgG][^;]*;", "§", x["en"])
        have.add(norm(t.replace("%", "")))
def skel(tpl):
    return norm(re.sub(r"\{\d+\}", "§", tpl))

items, skipped = [], {"complex": 0, "retail": 0, "covered": 0, "short": 0}
seen = set()
for p in sorted(pats):
    r = template(p)
    if r is None:
        skipped["complex"] += 1
        continue
    tpl, k = r
    lit = re.sub(r"\{\d+\}", "", tpl).strip()
    if k == 0 or len(lit) < 6:
        skipped["short"] += 1                     # no capture = exact string (other tables' job); almost no literal text = too generic
        continue
    if RETAIL.search(tpl):
        skipped["retail"] += 1
        continue
    if skel(tpl) in have:
        skipped["covered"] += 1
        continue
    if tpl in seen:
        continue
    seen.add(tpl)
    items.append({"pat": p, "tpl": tpl})
# longest literal first is not needed here; keep alphabetical so similar lines stay together
items.sort(key=lambda e: (e["tpl"].lower(), e["tpl"]))
for i, e in enumerate(items):
    e["i"] = i
json.dump(items, open("patx_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
os.makedirs("patx_chunks_en", exist_ok=True)
for f in glob.glob("patx_chunks_en/*.json"):
    os.remove(f)
for start in range(0, len(items), PER_CHUNK):
    part = [{"i": e["i"], "en": e["tpl"]} for e in items[start:start + PER_CHUNK]]
    with open(f"patx_chunks_en/names_{start // PER_CHUNK:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
print(len(pats), "PolishForever patterns ->", len(items), "templates in", (len(items) + PER_CHUNK - 1) // PER_CHUNK, "chunks; skipped:", skipped)
import random
random.seed(3)
for e in random.sample(items, 12):
    print("  ", e["tpl"][:140])
