# test_patx.py - round trip of every pattern in addon/PatternsX.lua without a Lua interpreter:
# build an English sample from the English template, check that the Lua pattern (converted to a Python regex) matches it,
# fill the Danish template from the captures and make sure no {k} is left over. Reports problems; exit code 1 if any.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import itertools, json, re, sys

def lua_to_re(p):
    out, i, prev_single = [], 0, False
    while i < len(p):
        c = p[i]
        if c == "%" and i + 1 < len(p):
            n = p[i + 1]
            cls = {"d": r"\d", "a": "[A-Za-z]", "s": r"\s", "w": r"\w", "l": "[a-z]", "u": "[A-Z]", "p": r"[!-/:-@\[-`{-~]", "x": "[0-9A-Fa-f]"}
            out.append(cls.get(n, re.escape(n))); i += 2; prev_single = True; continue
        if c == "[":
            j = i + 1
            if j < len(p) and p[j] == "^":
                j += 1
            while j < len(p) and p[j] != "]":
                j += 2 if p[j] == "%" else 1
            inner = p[i + 1:j]
            conv, k = [], 0
            while k < len(inner):
                if inner[k] == "%" and k + 1 < len(inner):
                    n = inner[k + 1]
                    conv.append({"d": r"\d", "a": "A-Za-z", "s": r"\s", "w": r"\w"}.get(n, re.escape(n))); k += 2
                else:
                    conv.append("\\-" if inner[k] == "-" and k + 1 == len(inner) else re.escape(inner[k]) if inner[k] not in "^-" else inner[k]); k += 1
            out.append("[" + "".join(conv) + "]"); i = j + 1; prev_single = True; continue
        if c == "-" and prev_single:
            out.append("*?"); i += 1; prev_single = False; continue
        if c in "*+?":
            out.append(c); i += 1; prev_single = False; continue
        if c in "()^$":
            out.append(c); i += 1; prev_single = False; continue
        if c == ".":
            out.append("."); i += 1; prev_single = True; continue
        out.append(re.escape(c)); i += 1; prev_single = True
    return "".join(out)

src = open("addon/PatternsX.lua", encoding="utf-8").read()
entries = re.findall(r'^    \{("(?:[^"\\]|\\.)*"), ("(?:[^"\\]|\\.)*"), ("(?:[^"\\]|\\.)*"), ("(?:[^"\\]|\\.)*")\},$', src, re.M)
bad, ok = [], 0
CAND = ["5", "Foo Bar", "15 sec", "1,200"]
for pat_s, da_s, lit_s, first_s in entries:
    pat, da, lit, first = (json.loads(x) for x in (pat_s, da_s, lit_s, first_s))
    try:
        rx = re.compile(lua_to_re(pat), re.S)
    except re.error as e:
        bad.append((pat[:70], "regex: " + str(e))); continue
    k = len(re.findall(r"\{\d+\}", da)) and max(int(x) for x in re.findall(r"\{(\d+)\}", da))
    ncap = rx.groups
    tpl_en = None
    if ncap < k:
        bad.append((pat[:70], f"template uses {{{k}}} but pattern has {ncap} captures")); continue
    # build the sample from the pattern: replace each capture group with a candidate and test
    parts = re.split(r"(\((?:[^()%]|%.)*\))", pat.lstrip("^").rstrip("$"))
    caps_idx = [n for n, s in enumerate(parts) if s.startswith("(") and s.endswith(")") and n % 2 == 1]
    found = None
    for combo in itertools.islice(itertools.product(CAND, repeat=min(len(caps_idx), 4)), 0, 300):
        vals = list(combo) + [combo[-1]] * (len(caps_idx) - len(combo))
        text = "".join(vals[caps_idx.index(n)] if n in caps_idx else re.sub(r"%(.)", r"\1", s) for n, s in enumerate(parts))
        m = rx.fullmatch(text)
        if m and lit in text:
            found = (text, m); break
    if not found:
        bad.append((pat[:70], "no sample text matches the pattern (or the literal part is not in the text)")); continue
    text, m = found
    out = re.sub(r"\{(\d+)\}", lambda g: m.group(int(g.group(1))) or "", da)
    if "{" in out:
        bad.append((pat[:70], "placeholder left in output: " + out[:60])); continue
    ok += 1
print(f"{len(entries)} entries | round trip ok: {ok} | problems: {len(bad)}")
for b in bad[:25]:
    print("  ", b)
sys.exit(1 if bad else 0)
