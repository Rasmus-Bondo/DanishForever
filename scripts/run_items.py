# run_items.py [items|spells] - translate <kind>_chunks_en/*.json with Haiku (resumable, validates each chunk, retries)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os, re, subprocess, sys
import glossary

KIND = sys.argv[1] if len(sys.argv) > 1 else "items"
RULES = {"items": "rules/CLAUDE_items.md", "spells": "rules/CLAUDE_spells.md",
         "objects": "rules/CLAUDE_names.md", "creatures": "rules/CLAUDE_names.md", "achievements": "rules/CLAUDE_names.md",
         "factions": "rules/CLAUDE_names.md", "titles": "rules/CLAUDE_names.md", "skills": "rules/CLAUDE_names.md",
         "globalstrings": "rules/CLAUDE_gs.md", "qtexts": "rules/CLAUDE_qtext.md", "areas": "rules/CLAUDE_names.md", "enchants": "rules/CLAUDE_spells.md", "pagetext": "rules/CLAUDE_qtext.md", "qextra": "rules/CLAUDE_qtext.md", "facdesc": "rules/CLAUDE_qtext.md", "patx": "rules/CLAUDE_patx.md", "mlnames": "rules/CLAUDE_names.md", "mltitles": "rules/CLAUDE_names.md", "mlitems": "rules/CLAUDE_items.md", "mlflavor": "rules/CLAUDE_items.md", "mlspells": "rules/CLAUDE_spells.md", "mlqextra": "rules/CLAUDE_qtext.md", "qplextra": "rules/CLAUDE_qpl.md", "csvmisc": "rules/CLAUDE_names.md", "emotes": "rules/CLAUDE_gs.md", "gossip": "rules/CLAUDE_gossip.md", "vmbooks": "rules/CLAUDE_books.md", "capture": "rules/CLAUDE_capture.md"}.get(KIND, "rules/CLAUDE_names.md")      # any other table of names uses the names rules
EN_DIR, DA_DIR = f"{KIND}_chunks_en", f"{KIND}_chunks_da"

PH = re.compile(r"<(?:Name|Class|Race)>")
MAX_TRIES = 3

# Spell-template tokens that must survive translation unchanged: ${...}, $<var>, $?a123, [ ], $s1, $d, $1279976m1, $/1000;
# $lsecond:seconds; plural switches may change their words, but there must be the same number of them.
SPELL_TOKEN = re.compile(r"\$\{.*?\}|\$<[^>]*>|\$\?[^\[\s]*|[\[\]]|\$/?\d*[A-Za-z]\d*;?")
SPELL_PLURAL = re.compile(r"\$[lLgG][^;]*;")           # plural ($l) and gender ($g) switches: words may change, count may not

# GlobalStrings: printf codes (%s, %d, %1$s, %.1f), colour/icon/link codes, line breaks.
FORMAT_TOKEN = re.compile(r"%(?:\d+\$)?[-+#0]*\d*(?:\.\d+)?[sdfcxXuig]|\|c[0-9a-fA-F]{8}|\|r|\|T[^|]*\|t|\|H[^|]*\|h|\|h|\|n|\|K[^|]*\|k|\|A[^|]*\|a")
UNNUMBERED = re.compile(r"%(?!\d+\$)[-+#0]*\d*(?:\.\d+)?[sdfcxXuig]")

def format_tokens_ok(en, da):
    # a literal percent sign is written "%" in some strings and "%%" in others: treat them as the same
    en, da = en.replace("%%", "%"), da.replace("%%", "%")
    if sorted(FORMAT_TOKEN.findall(en)) != sorted(FORMAT_TOKEN.findall(da)):
        return False
    # unnumbered codes are filled in order, so their types must keep the same order
    return [t[-1] for t in UNNUMBERED.findall(en)] == [t[-1] for t in UNNUMBERED.findall(da)] \
        or any("$" in t for t in FORMAT_TOKEN.findall(da))

def spell_tokens_ok(en, da):
    en_plural, da_plural = SPELL_PLURAL.findall(en), SPELL_PLURAL.findall(da)
    if len(en_plural) != len(da_plural):
        return False
    return sorted(SPELL_TOKEN.findall(SPELL_PLURAL.sub("", en))) == sorted(SPELL_TOKEN.findall(SPELL_PLURAL.sub("", da)))

os.makedirs(DA_DIR, exist_ok=True)
os.makedirs("glossary_chunks", exist_ok=True)

def valid(en_path, da_path):
    try:
        en = json.load(open(en_path, encoding="utf-8"))
        da = json.load(open(da_path, encoding="utf-8"))
        if len(en) != len(da):
            return False
        for a, b in zip(en, da):
            if a["i"] != b["i"] or not isinstance(b.get("da"), str) or not b["da"].strip():
                return False
            if sorted(PH.findall(a["en"])) != sorted(PH.findall(b["da"])):
                return False
            if a["en"].count("\n") != b["da"].count("\n"):
                return False
            if KIND in ("spells", "enchants", "gossip") and not spell_tokens_ok(a["en"], b["da"]):
                return False
            if KIND in ("patx", "capture") and (sorted(re.findall(r"\{\d+\}", a["en"])) != sorted(re.findall(r"\{\d+\}", b["da"]))
                                   or a["en"].count("%") != b["da"].count("%")):
                return False
            if KIND == "vmbooks" and (sorted(re.findall(r"</?[A-Za-z]+>|\$[A-Za-z]", a["en"])) != sorted(re.findall(r"</?[A-Za-z]+>|\$[A-Za-z]", b["da"]))):
                return False
            if KIND in ("globalstrings", "enchants", "criteria", "emotes", "capture") and not format_tokens_ok(a["en"], b["da"]):
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError):
        return False

# names first (they set the vocabulary), then descriptions
files = sorted(glob.glob(f"{EN_DIR}/names_*.json")) + sorted(glob.glob(f"{EN_DIR}/desc_*.json"))
if os.environ.get("REVERSE"):                      # a second job can work from the end while the first works from the start
    files.reverse()
failed = []
for f in files:
    out = f.replace(EN_DIR, DA_DIR)
    if os.path.exists(out) and valid(f, out):
        continue                                   # resumable
    stem = os.path.splitext(os.path.basename(f))[0]
    gfile = f"glossary_chunks/{KIND}_{stem}.txt"
    nfile = f"glossary_chunks/{KIND}_{stem}_new.txt"
    for attempt in range(1, MAX_TRIES + 1):
        data = json.load(open(f, encoding="utf-8"))
        with open(gfile, "w", encoding="utf-8") as g:
            for e, d in glossary.subset((x["en"] for x in data), limit=400):
                g.write(f"{e} = {d}\n")
        for p in (out, nfile):
            if os.path.exists(p): os.remove(p)
        prompt = (f"Ignore the quest rules in CLAUDE.md. Follow {RULES}. "
                  f"Translate {f} and write it to {out}. "
                  f"Glossary for this chunk: {gfile}. Write new terms to {nfile}. Reply with just: done")
        subprocess.run(f'claude -p "{prompt}" --model haiku --permission-mode acceptEdits', shell=True)
        if os.path.exists(out) and valid(f, out):
            print(stem, "ok - new terms merged:", glossary.merge_file(nfile), flush=True)
            break
        print(stem, "failed validation, attempt", attempt, flush=True)
    else:
        failed.append(stem)
        if os.path.exists(out): os.replace(out, out + ".bad")      # replace: an older .bad file may exist

print("finished;", len(failed), "chunks failed:", failed)

