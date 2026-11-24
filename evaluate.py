"""Compare the rules against a majority-class baseline on postings YOU labelled."""
import csv, sys
from collections import Counter
from screener.rules import screen, load_profile

path = sys.argv[1] if len(sys.argv) > 1 else "data/postings_sample.csv"
profile = load_profile()
rows = list(csv.DictReader(open(path, encoding="utf-8")))
labels = [r["my_label"] for r in rows]
majority = Counter(labels).most_common(1)[0][0]
preds = [screen(r, profile).label for r in rows]

acc = sum(p == y for p, y in zip(preds, labels)) / len(rows)
base = sum(majority == y for y in labels) / len(rows)
print(f"Postings: {len(rows)}")
print(f"Rules accuracy:    {acc:.0%}")
print(f"Majority baseline: {base:.0%}  (always '{majority}')")
risky_true = [i for i, y in enumerate(labels) if y == "Risky"]
caught = sum(preds[i] == "Risky" for i in risky_true)
print(f"Risky postings caught: {caught}/{len(risky_true)}")
for r, p, y in zip(rows, preds, labels):
    if p != y:
        print(f"MISS {r['id']}: predicted {p}, you labelled {y}")
