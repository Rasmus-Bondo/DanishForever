# run_quests.py [part total] - translate chunks_en/*.json that have no valid chunks_da file yet with Haiku (resumable, validates, retries)
# Like run_chunks.py, but each chunk is checked the way build_lua.py checks it, with 3 tries and a .bad file on failure.
# To use two parallel jobs: python run_quests.py 0 2   and   python run_quests.py 1 2
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os, re, subprocess, sys
import glossary

PART, TOTAL = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 1)
PREFIX = sys.argv[3] if len(sys.argv) > 3 else ""             # e.g. "qpl": qpl_chunks_en -> qpl_chunks_da
RULES = sys.argv[4] if len(sys.argv) > 4 else "CLAUDE.md"
EN_DIR, DA_DIR = f"{PREFIX}_chunks_en" if PREFIX else "chunks_en", f"{PREFIX}_chunks_da" if PREFIX else "chunks_da"
PH = re.compile(r"<(?:Name|Class|Race)>")
FIELDS = ("name", "log", "desc", "progress", "complete")
MAX_TRIES = 3

os.makedirs(DA_DIR, exist_ok=True)
os.makedirs("glossary_chunks", exist_ok=True)

def good(en, da):
    try:
        if da["id"] != en["id"] or len(da["objectives"]) != len(en["objectives"]):
            return False
        for k in FIELDS:
            a, b = en[k], da[k]
            if (a is None) != (b is None):
                return False
            if a and (not isinstance(b, str) or not b.strip() or sorted(PH.findall(a)) != sorted(PH.findall(b))
                      or a.count("\n") != b.count("\n")):
                return False
        return all((e is None) == (d is None) and (not e or (isinstance(d, str) and d.strip()))
                   for e, d in zip(en["objectives"], da["objectives"]))
    except (KeyError, TypeError, AttributeError):
        return False

def valid(en_path, da_path):
    try:
        en = json.load(open(en_path, encoding="utf-8"))
        da = json.load(open(da_path, encoding="utf-8"))
        return isinstance(da, list) and len(en) == len(da) and all(good(a, b) for a, b in zip(en, da))
    except (OSError, ValueError, TypeError):
        return False

def chunk_texts(quests):
    for q in quests:
        for k in FIELDS:
            yield q.get(k)
        yield from q.get("objectives", [])

files = sorted(glob.glob(f"{EN_DIR}/*.json"), key=lambda f: int(re.search(r"(\d+)", os.path.basename(f)).group(1)))
if len(sys.argv) > 5 and sys.argv[5] == "reverse":              # a second job can work from the end while the first works from the start
    files.reverse()
failed = []
for n, f in enumerate(files):
    if n % TOTAL != PART:
        continue
    out = f.replace(EN_DIR, DA_DIR)
    if os.path.exists(out) and valid(f, out):
        continue                                   # resumable
    stem = os.path.splitext(os.path.basename(f))[0]
    gfile = f"glossary_chunks/{PREFIX + '_' if PREFIX else ''}{stem}.txt"
    nfile = f"glossary_chunks/{PREFIX + '_' if PREFIX else ''}{stem}_new.txt"
    for attempt in range(1, MAX_TRIES + 1):
        quests = json.load(open(f, encoding="utf-8"))
        with open(gfile, "w", encoding="utf-8") as g:
            for e, d in glossary.subset(chunk_texts(quests)):
                g.write(f"{e} = {d}\n")
        for p in (out, nfile):
            if os.path.exists(p): os.remove(p)
        prompt = ((f"Translate {f} per CLAUDE.md and write it to {out}. " if RULES == "CLAUDE.md" else
                   f"Ignore the other quest rules in CLAUDE.md. Translate {f} per {RULES} and write it to {out}. ")
                  + f"Glossary for this chunk: {gfile}. Write new terms to {nfile}. Reply with just: done")
        subprocess.run(f'claude -p "{prompt}" --model haiku --permission-mode acceptEdits', shell=True)
        if os.path.exists(out) and valid(f, out):
            print(stem, "ok - new terms merged:", glossary.merge_file(nfile), flush=True)
            break
        print(stem, "failed validation, attempt", attempt, flush=True)
    else:
        failed.append(stem)
        if os.path.exists(out): os.replace(out, out + ".bad")

print("finished;", len(failed), "chunks failed:", failed)
