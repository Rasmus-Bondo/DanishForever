# scrape_table.py <name> <token>
# Pages through a forever.warcraftdb.com data-table embed token and saves rows to items_table_<name>.jsonl
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import json, os, sys, time, requests

BASE = "https://forever.warcraftdb.com/api/v1/table/"
HEADERS = {"User-Agent": "DanishForever-hobby-translation/0.1 (personal WoW addon project; contact: you@example.com)"}
DELAY = 1.0

name, token = sys.argv[1], sys.argv[2]
OUT = f"items_table_{name}.jsonl"

done = set()
if os.path.exists(OUT):
    with open(OUT, encoding="utf-8") as f:
        done = {json.loads(l)["page"] for l in f}

page, pages, prev_first = 1, None, None
with open(OUT, "a", encoding="utf-8") as f:
    while pages is None or page <= pages:
        if page in done:
            page += 1; continue
        try:
            r = requests.get(BASE + token, params={"page": page}, headers=HEADERS, timeout=30)
        except requests.RequestException as e:
            print("error", page, e); time.sleep(10); continue
        if r.status_code in (403, 429, 503):
            print(f"Got {r.status_code} at page {page}. Stopping. Don't work around this; ask the site.")
            break
        if r.status_code != 200:
            print("skip", page, r.status_code); time.sleep(DELAY); page += 1; continue
        d = r.json()
        pages = d.get("pages", 1)
        rows = d.get("rows", [])
        if not rows or d.get("page") != page:
            break
        f.write(json.dumps({"page": page, "rows": rows}, ensure_ascii=False) + "\n")
        f.flush()
        if page % 50 == 0: print(page, "of", pages, flush=True)
        page += 1
        time.sleep(DELAY)
print("finished", name)
