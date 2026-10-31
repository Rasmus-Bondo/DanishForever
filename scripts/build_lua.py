# build_lua.py
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, os, re

PH = re.compile(r"<(?:Name|Class|Race)>")
FIELDS = ("name", "log", "desc", "progress", "complete")

def good(en, da):
    try:
        if da["id"] != en["id"] or len(da["objectives"]) != len(en["objectives"]):
            return False
        for k in FIELDS:
            a, b = en[k], da[k]
            if (a is None) != (b is None):
                return False
            if a and (sorted(PH.findall(a)) != sorted(PH.findall(b))
                      or a.count("\n") != b.count("\n")):
                return False
        return True
    except (KeyError, TypeError, AttributeError):
        return False

def lua(s):
    s = re.sub(r" +\n", "\n", s)      # space before a line break
    s = re.sub(r"\n +", "\n", s)      # space after a line break
    s = re.sub(r" {2,}", " ", s)      # double spaces
    return json.dumps(s, ensure_ascii=False)

def load_chunk(path):
    """Accepts a JSON array or one JSON object per line. Returns None if unreadable."""
    raw = open(path, encoding="utf-8").read().strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        try:
            data = [json.loads(l) for l in raw.splitlines() if l.strip()]
        except json.JSONDecodeError:
            return None
    return data if isinstance(data, list) else None

out, bad, objmap, namemap, seen_ids = [], [], {}, {}, set()
for f in sorted(glob.glob("chunks_en/*.json")) + sorted(glob.glob("qpl_chunks_en/*.json")) + sorted(glob.glob("mlq_chunks_en/*.json")):      # qpl: translated from Polish, mlq: MultiLanguage (Classic Era) English
    d = f.replace("chunks_en", "chunks_da")
    if not os.path.exists(d):
        continue
    en_list = json.load(open(f, encoding="utf-8"))
    da_list = load_chunk(d)
    if da_list is None:
        bad.append(d)
        continue
    da_by_id = {q.get("id"): q for q in da_list if isinstance(q, dict)}
    for en in en_list:
        da = da_by_id.get(en["id"])
        if da and good(en, da):
            if en["id"] in seen_ids:               # the same quest in two chunk files (early test chunk): keep the first
                continue
            seen_ids.add(en["id"])
            if en["name"] and da["name"]:
                namemap[en["name"]] = da["name"]
            for e, d_ in zip(en["objectives"], da["objectives"]):
                if e and d_:
                    objmap[e] = d_
            parts = {"n": da["name"], "l": da["log"], "d": da["desc"],
                     "p": da["progress"], "c": da["complete"]}
            out.append(f'  [{en["id"]}] = {{'
                       + ", ".join(f"{k}={lua(v)}" for k, v in parts.items() if v)
                       + "},\n")
        else:
            bad.append(f'{d} quest {en["id"]}')

with open("Data_Quests.lua", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\nns.Quests = {\n" + "".join(out) + "}\n")
    f.write("ns.Obj = {\n")
    for e, d_ in sorted(objmap.items()):
        f.write(f"  [{json.dumps(e, ensure_ascii=False)}] = {lua(d_)},\n")
    f.write("}\n")
    f.write("ns.QuestNames = {\n")                 # English quest title -> Danish, for the tracker and quest log list
    for e, d_ in sorted(namemap.items()):
        f.write(f"  [{json.dumps(e, ensure_ascii=False)}] = {lua(d_)},\n")
    f.write("}\n")

print(len(out), "quests written;", len(bad), "failed validation")
for b in bad[:30]:
    print("  redo:", b)