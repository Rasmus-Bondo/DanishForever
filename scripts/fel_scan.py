# fel_scan.py - list English key words starting with "Fel" in the addon tables (to decide which are the demonic "fel")
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))
import glob, re, collections
KEY = re.compile(r'^\s*\["((?:[^"\\]|\\.)*)"\]\s*=\s*"', re.M)
c = collections.Counter()
for p in glob.glob("addon/*.lua") + ["Data_Items.lua"]:
    t = open(p, encoding="utf-8").read()
    for m in KEY.finditer(t):
        k = m.group(1)
        if len(k) > 80:
            continue
        for w in re.findall(r"\b[Ff][Ee][Ll][A-Za-z']*", k):
            c[w] += 1
print(c.most_common(100))
