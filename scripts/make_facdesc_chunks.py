# make_facdesc_chunks.py - wow.export Faction.csv (Description_lang) -> facdesc_chunks_en/names_NNNN.json (faction descriptions in the Reputation window)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import csv, json, os

rows = list(csv.DictReader(open(r"C:\Users\2000b\wow.export\Faction.csv", encoding="utf-8", newline=""), delimiter=";"))
texts = sorted({r["Description_lang"].strip() for r in rows if (r["Description_lang"] or "").strip()}, key=lambda s: (s.lower(), s))
os.makedirs("facdesc_chunks_en", exist_ok=True)
PER = 25
for start in range(0, len(texts), PER):
    part = [{"i": start + k, "en": s} for k, s in enumerate(texts[start:start + PER])]
    with open(f"facdesc_chunks_en/names_{start // PER:04d}.json", "w", encoding="utf-8") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
print(len(texts), "unique faction descriptions in", (len(texts) + PER - 1) // PER, "chunks")
