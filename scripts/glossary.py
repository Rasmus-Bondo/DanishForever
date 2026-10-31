# glossary.py
# Master glossary lives in glossary.json ({"English": "Dansk"}).
#   python glossary.py migrate   one-off: build glossary.json from glossary.txt
#   python glossary.py export    rewrite glossary.txt (sorted, human-readable) from glossary.json
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import json, os, re, sys, time

MASTER = "glossary.json"
TXT = "glossary.txt"
MAX_ENTRIES = 200

def load():
    if not os.path.exists(MASTER):
        return {}
    with open(MASTER, encoding="utf-8") as f:
        return json.load(f)

LOCK = "glossary.lock"

def acquire_lock():
    """Several translation runs may merge at once; only one may write the master at a time."""
    for _ in range(1200):
        try:
            return os.open(LOCK, os.O_CREAT | os.O_EXCL)
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(LOCK) > 60:      # stale lock from a killed run
                    os.remove(LOCK)
            except OSError:
                pass
            time.sleep(0.1)
    raise RuntimeError("could not lock the glossary")

def release_lock(fd):
    os.close(fd)
    try:
        os.remove(LOCK)
    except OSError:
        pass

def save(g):
    tmp = MASTER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(g.items(), key=lambda kv: kv[0].lower())), f, ensure_ascii=False, indent=0)
    os.replace(tmp, MASTER)                      # readers never see a half-written file

def export_txt(g):
    with open(TXT, "w", encoding="utf-8") as f:
        for e, d in sorted(g.items(), key=lambda kv: kv[0].lower()):
            f.write(f"{e} = {d}\n")

def parse_lines(text):
    for line in text.splitlines():
        e, sep, d = line.partition(" = ")
        if sep and e.strip() and d.strip():
            yield e.strip(), d.strip()

def merge_file(path):
    """Add terms from a 'English = Dansk' file; existing terms are never overwritten. Returns count added."""
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8-sig") as f:
        new = list(parse_lines(f.read()))
    fd = acquire_lock()
    try:
        g = load()                               # read inside the lock so no run's terms are lost
        added = 0
        for e, d in new:
            if e not in g:
                g[e] = d
                added += 1
        if added:
            save(g)
            export_txt(g)
    finally:
        release_lock(fd)
    return added

def words(s):
    return {w for w in re.findall(r"[A-Za-z']+", s) if len(w) >= 5 and w[0].isupper()}

def subset(texts, limit=MAX_ENTRIES):
    """Entries relevant to the given texts: whole-term hits first, then entries sharing a capitalised word."""
    g = load()
    blob = "\n".join(t for t in texts if t)
    # whole-word matches only, so "Key" does not match inside "Keybinding"
    hits = [(e, d) for e, d in g.items()
            if e in blob and re.search(r"(?<!\w)" + re.escape(e) + r"(?!\w)", blob)]
    seen = {e for e, _ in hits}
    wb = words(blob)
    partial = [(e, d) for e, d in g.items() if e not in seen and words(e) & wb]
    return (hits + partial)[:limit]

def migrate():
    g = {}
    with open(TXT, encoding="utf-8-sig") as f:
        for e, d in parse_lines(f.read()):
            g.setdefault(e, d)
    save(g)
    export_txt(g)
    print(len(g), "terms in", MASTER)

if __name__ == "__main__":
    {"migrate": migrate, "export": lambda: export_txt(load())}[sys.argv[1]]()
