# scrape_new_names.py <item|spell|npc|object> - names of Forever IDs that work\<kind>s_en.json lacks -> new_<kind>_names.jsonl (resumable)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))
import re, json, sys, time, requests
BASE = "https://forever.warcraftdb.com"
HEADERS = {"User-Agent": "DanishForever-hobby-translation/0.1 (personal WoW addon project)"}
kind = sys.argv[1]
src = {"item": "items_en.json", "spell": "spells_en.json", "npc": "creatures_en.json", "object": "objects_en.json"}[kind]
have = {int(r["id"]) for r in json.load(open(src, encoding="utf-8"))}
ids = sorted(int(i) for i in re.findall(r"/data/%s/(\d+)" % kind, requests.get(f"{BASE}/sitemap/{kind}.xml", headers=HEADERS, timeout=30).text))
out = f"new_{kind}_names.jsonl"
done = {json.loads(l)["id"] for l in open(out, encoding="utf-8")} if os.path.exists(out) else set()
todo = [i for i in ids if i not in have and i not in done]
print(kind, len(todo), "to fetch", flush=True)
with open(out, "a", encoding="utf-8") as f:
    for n, i in enumerate(todo, 1):
        try:
            r = requests.get(f"{BASE}/api/data/node/{kind}/{i}", headers=HEADERS, timeout=30)
        except requests.RequestException as e:
            print("error", i, e); time.sleep(10); continue
        if r.status_code in (403, 429, 503):
            print(f"Got {r.status_code} at {kind} {i}. Stopping."); sys.exit(1)
        if r.status_code == 200:
            d = r.json().get("data", {})
            if d.get("name"):
                f.write(json.dumps({"id": i, "name": d["name"]}, ensure_ascii=False) + "\n"); f.flush()
        if n % 200 == 0: print(n, "done", flush=True)
        time.sleep(1.2)
print("finished", kind)