# crawl_quests.py
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import re, json, time, html, os, requests

BASE = "https://forever.warcraftdb.com"
HEADERS = {"User-Agent": "DanishForever-hobby-translation/0.1 (personal WoW addon project; contact: you@example.com)"}
OUT = "quests_en.jsonl"
DELAY = 1.5  # seconds between requests, be gentle

def clean(s):
    if not s: return s
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()

def get_ids():
    xml = requests.get(f"{BASE}/sitemap/quest.xml", headers=HEADERS, timeout=30).text
    return [int(i) for i in re.findall(r"/data/quest/(\d+)", xml)]

done = set()
if os.path.exists(OUT):
    with open(OUT, encoding="utf-8") as f:
        done = {json.loads(l)["id"] for l in f}

ids = [i for i in get_ids() if i not in done]
print(f"{len(ids)} quests to fetch")

with open(OUT, "a", encoding="utf-8") as f:
    for n, qid in enumerate(ids, 1):
        r = requests.get(f"{BASE}/api/data/node/quest/{qid}", headers=HEADERS, timeout=30)
        if r.status_code in (403, 429, 503):
            print(f"Got {r.status_code} at quest {qid}. Stopping. Don't work around this; ask the site.")
            break
        if r.status_code != 200:
            print("skip", qid, r.status_code); time.sleep(DELAY); continue
        d = r.json().get("data", {})
        rec = {
            "id": qid,
            "name": clean(d.get("name")),
            "log": clean(d.get("log_description")),
            "desc": clean(d.get("quest_description")),
            "progress": clean(d.get("quest_progress")),
            "complete": clean(d.get("quest_completion_log")),
            "objectives": [clean(o.get("description")) for o in d.get("objectives", [])],
        }
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if n % 100 == 0: print(n, "done")
        time.sleep(DELAY)