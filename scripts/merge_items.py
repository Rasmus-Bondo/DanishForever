# merge_items.py - merge items_table_*.jsonl into items_en.json, restricted to the sitemap ids
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json

ids = {int(l) for l in open("sitemap_item_ids.txt") if l.strip()}
items = {}
for f in sorted(glob.glob("items_table_*.jsonl")):
    for line in open(f, encoding="utf-8"):
        for r in json.loads(line)["rows"]:
            if r["c0"] in ids and r["c1"]:
                items[r["c0"]] = {"id": r["c0"], "name": r["c1"].strip(), "desc": (r["c2"] or "").strip()}

out = [items[i] for i in sorted(items)]
json.dump(out, open("items_en.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

names = {i["name"] for i in out}
descs = {i["desc"] for i in out if i["desc"]}
print(len(out), "items;", len(names), "unique names;", len(descs), "unique descriptions")
print("name chars:", sum(map(len, names)), " desc chars:", sum(map(len, descs)))
