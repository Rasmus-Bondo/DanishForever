# scrape_missing_quests.py - fetch Forever quests (id >= 90000) that Data_Quests.lua does not have, append to quests_en.jsonl
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))
import re, json, time, html, requests
BASE = "https://forever.warcraftdb.com"
HEADERS = {"User-Agent": "DanishForever-hobby-translation/0.1 (personal WoW addon project)"}
def clean(s):
    if not s: return s
    s = re.sub(r"<br\s*/?>", "\n", s); s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()
dq = open("Data_Quests.lua", encoding="utf-8").read()
ids = sorted(int(i) for i in re.findall(r"/data/quest/(\d+)", requests.get(BASE + "/sitemap/quest.xml", headers=HEADERS, timeout=30).text))
done = {json.loads(l)["id"] for l in open("quests_en.jsonl", encoding="utf-8")}
todo = [i for i in ids if i >= 90000 and i not in done and not re.search(r"\[%d\]\s*=" % i, dq)]
print(len(todo), "to fetch", flush=True)
with open("quests_en.jsonl", "a", encoding="utf-8") as f:
    for n, qid in enumerate(todo, 1):
        r = requests.get(f"{BASE}/api/data/node/quest/{qid}", headers=HEADERS, timeout=30)
        if r.status_code in (403, 429, 503):
            print(f"Got {r.status_code} at quest {qid}. Stopping."); break
        if r.status_code != 200:
            print("skip", qid, r.status_code); time.sleep(1.5); continue
        d = r.json().get("data", {})
        rec = {"id": qid, "name": clean(d.get("name")), "log": clean(d.get("log_description")), "desc": clean(d.get("quest_description")),
               "progress": clean(d.get("quest_progress")), "complete": clean(d.get("quest_completion_log")),
               "objectives": [clean(o.get("description")) for o in d.get("objectives", [])]}
        f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
        if n % 100 == 0: print(n, "done", flush=True)
        time.sleep(1.5)
print("finished")