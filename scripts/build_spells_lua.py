# build_spells_lua.py - spells_chunks_da/desc_*.json -> addon/SpellDescs.lua
# Spell descriptions as the game shows them have the numbers filled in ("Lasts 30 sec."), so each English text with
# $s1/$d style tokens becomes a Lua pattern; the captured values are written into the Danish text.
#   ns.SpellDescExact[english] = danish                      (texts without tokens)
#   ns.SpellDescTemplates[first 8 bytes of literal] = { {pattern, durations, part, part, ...}, ... }
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re

TOKEN = re.compile(r"\$[lL][^:;$]*:[^;$]*;|\$\d*[A-Za-z]\d*|\$\d+")
BAD = ("$?", "${", "$<", "$[", "$@", "$g", "$G", "$*", "$/", "$(")

def norm(s): return s.replace("\r\n", "\n").replace("\r", "\n").strip()
def esc(s): return re.sub(r"([^A-Za-z0-9])", r"%\1", s)
def lua(s): return json.dumps(s, ensure_ascii=False)

pairs = {}
for f in sorted(glob.glob("spells_chunks_da/desc_*.json")):
    for x in json.load(open(f, encoding="utf-8")):
        if isinstance(x.get("da"), str) and x["da"].strip() and x.get("en"):
            pairs[norm(x["en"])] = norm(x["da"])


# --- conditionals: "$?a123[if talent][otherwise]" -> one pair per branch (English and Danish expanded in step) ---
MATH = re.compile(r"\$\{[^{}]*\}(?:\.\d+)?|\$<[^<>]*>|\$@\w+")
GENDER = re.compile(r"\$[gG]\s*([^:;$]*?)\s*:\s*([^;$]*?)\s*;")
CAP = 16

def branches(s, start):
    """s[start] is the '[' of a branch group; returns (inner text, index after the closing ']')"""
    depth, i = 0, start
    while i < len(s):
        if s[i] == "[": depth += 1
        elif s[i] == "]":
            depth -= 1
            if depth == 0: return s[start + 1:i], i + 1
        i += 1
    return None, None

def expand(s):
    """all variants of s with every $?cond[A][B] replaced by A or B; None if it cannot be parsed"""
    i = s.find("$?")
    if i < 0: return [s]
    j = s.find("[", i)
    if j < 0: return None
    outs, k = [], j
    while True:
        inner, k2 = branches(s, k)
        if inner is None: return None
        outs.append(inner)
        k = k2
        if k < len(s) and s[k] == "[":            # the else branch
            inner, k2 = branches(s, k)
            if inner is None: return None
            outs.append(inner); k = k2
            break
        if k < len(s) and s[k] == "?":            # another condition: ?a123[...]
            k = s.find("[", k)
            if k < 0: return None
            continue
        outs.append("")                          # no else branch: nothing is shown
        break
    rest = expand(s[k:])
    if rest is None: return None
    res = []
    for o in outs:
        eo = expand(o)
        if eo is None: return None
        for a in eo:
            for b in rest:
                res.append(s[:i] + a + b)
                if len(res) > CAP: return None
    return res

def variants(en, da):
    """[(en, da), ...] one per branch; None when the English and Danish do not line up"""
    maths = {}
    for m in MATH.findall(en):
        maths.setdefault(m, "$v%d" % (len(maths) + 1))
    for m, t in maths.items():
        en, da = en.replace(m, t), da.replace(m, t)
    if MATH.search(da): return None
    ev, dv = expand(en), expand(da)
    if not ev or not dv or len(ev) != len(dv): return None
    out = []
    for e, d in zip(ev, dv):
        for gi in (1, 2):                         # male / female form of "$g him:her;"
            out.append((GENDER.sub(lambda m: m.group(gi), e), GENDER.sub(lambda m: m.group(gi), d)))
    return list(dict.fromkeys(out))

extra = {}
for en, da in list(pairs.items()):
    if "$?" in en or MATH.search(en) or GENDER.search(en):
        v = variants(en, da)
        if v:
            for e, d in v:
                e, d = norm(e), norm(d)
                if e and d and e not in pairs: extra[e] = d
pairs.update(extra)
print(len(extra), "extra texts from conditional branches")
exact, buckets, skipped = {}, {}, 0
for en, da in pairs.items():
    if any(b in en for b in BAD) or any(b in da for b in BAD):
        if "$" not in en: exact[en] = da
        else: skipped += 1
        continue
    en_toks = TOKEN.findall(en)
    if not en_toks:
        exact[en] = da
        continue
    # English side: pattern. plural switches in English match a word, other tokens a captured value.
    pat, idx, first, durs, pos, n = "^", 0, {}, [], 0, 0
    lit_prefix = None
    for m in TOKEN.finditer(en):
        lit = en[pos:m.start()]
        if lit_prefix is None: lit_prefix = lit
        pat += esc(lit)
        pos = m.end()
        t = m.group(0)
        if t[1] in "lL" and ":" in t:
            pat += "%a+"
        else:
            n += 1
            pat += "(.-)"
            first.setdefault(t, n)
            if re.fullmatch(r"\$\d*d", t): durs.append(n)
    pat += esc(en[pos:]) + "$"
    # Danish side: parts
    parts, pos, ok, last_num = [], 0, True, None
    for m in TOKEN.finditer(da):
        if m.start() > pos: parts.append(da[pos:m.start()])
        pos = m.end()
        t = m.group(0)
        if t[1] in "lL" and ":" in t:
            a, b = t[2:-1].split(":", 1)
            if last_num is None: ok = False; break
            parts.append((a, b, last_num))
        else:
            if t not in first: ok = False; break
            parts.append(first[t]); last_num = first[t]
    if not ok:
        skipped += 1; continue
    if pos < len(da): parts.append(da[pos:])
    key = (lit_prefix or "").encode("utf-8")[:8].decode("utf-8", "ignore") if lit_prefix else ""
    # bucket key must be the first 8 BYTES; recompute as raw bytes
    kb = (lit_prefix or "").encode("utf-8")[:8]
    key = kb.decode("latin-1")
    buckets.setdefault(key, []).append((pat, durs, parts, len(lit_prefix or "")))

def lbytes(k):   # emit a bucket key made of raw bytes as a Lua escaped string
    return '"' + "".join(chr(c) if 32 <= c < 127 and chr(c) not in '"\\' else "\\%03d" % c for c in k.encode("latin-1")) + '"'

with open("addon/SpellDescs.lua", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\n\n-- Spell and aura descriptions (see build_spells_lua.py). Matching code is in SpellMatch.lua.\n")
    f.write("ns.SpellDescExact = {\n")
    for en, da in sorted(exact.items()):
        f.write(f"    [{lua(en)}] = {lua(da)},\n")
    f.write("}\n\nns.SpellDescTemplates = {\n")
    for key in sorted(buckets):
        f.write(f"    [{lbytes(key)}] = {{\n")
        for pat, durs, parts, _ in sorted(buckets[key], key=lambda e: -e[3]):
            ps = ", ".join(lua(p) if isinstance(p, str) else (str(p) if isinstance(p, int) else "{%s, %s, %d}" % (lua(p[0]), lua(p[1]), p[2])) for p in parts)
            f.write(f"        {{{lua(pat)}, {{{', '.join(map(str, durs))}}}, {ps}}},\n")
        f.write("    },\n")
    f.write("}\n")
print(len(exact), "exact;", sum(len(v) for v in buckets.values()), "templates in", len(buckets), "buckets;", skipped, "skipped")

