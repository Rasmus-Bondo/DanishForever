# seed_glossary_from_patterns.py - hand-made fixed words in addon/Patterns.lua -> glossary.json (existing terms are kept)
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import re
import glossary

src = open("addon/Patterns.lua", encoding="utf-8").read()
exact_block = src.split("local patterns")[0]
pairs = re.findall(r'\["([^"]+)"\]\s*=\s*"([^"]+)"', exact_block)

# pattern phrases: add("Item Level %d", "Genstandsniveau %d") - only the ones without placeholders are glossary terms
phrases = re.findall(r'add\("([^"]+)",\s*"([^"]+)"\)', src)
phrases = [(e, d) for e, d in phrases if "%" not in e and "<" not in e]

with open("patterns_terms.txt", "w", encoding="utf-8") as f:
    for en, da in pairs + phrases:
        f.write(f"{en} = {da}\n")
print(len(pairs), "fixed words,", len(phrases), "phrases; terms added to glossary:", glossary.merge_file("patterns_terms.txt"))
