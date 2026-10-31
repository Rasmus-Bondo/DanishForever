# build_books_lua.py - vmbooks + pagetext translations -> addon/Books.lua
# ns.Books[English text with all whitespace removed] = Danish text   (whitespace differs between sources)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import glob, json, re
def key(s): return re.sub(r"\s+", "", s)
books = {}
texts = json.load(open("vmbooks_en.json", encoding="utf-8"))
for f in sorted(glob.glob("vmbooks_chunks_da/names_*.json")):
    for x in json.load(open(f, encoding="utf-8")):
        if isinstance(x.get("da"), str) and x["da"].strip():
            books[key(x["en"])] = x["da"].strip()
for f in sorted(glob.glob("pagetext_chunks_da/names_*.json")):
    for x in json.load(open(f, encoding="utf-8")):
        if isinstance(x.get("da"), str) and x["da"].strip():
            books.setdefault(key(x["en"]), x["da"].strip())
with open("addon/BookData.lua", "w", encoding="utf-8") as f:
    f.write("local _, ns = ...\n\n-- Books, letters and signs: English text without whitespace -> Danish text (see build_books_lua.py).\nns.Books = {\n")
    for k, v in sorted(books.items()):
        f.write(f"    [{json.dumps(k, ensure_ascii=False)}] = {json.dumps(v, ensure_ascii=False)},\n")
    f.write("}\n")
print(len(books), "books written")
