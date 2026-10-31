import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import json, os
os.makedirs("chunks_en", exist_ok=True)
quests = [json.loads(l) for l in open("quests_en.jsonl", encoding="utf-8")]
for i in range(0, len(quests), 25):
    with open(f"chunks_en/chunk_{i//25:04d}.json", "w", encoding="utf-8") as f:
        json.dump(quests[i:i+25], f, ensure_ascii=False, indent=1)