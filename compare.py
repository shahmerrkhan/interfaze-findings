import json
runs = []
for i in range(1, 6):
    d = json.load(open(f"run_{i}.json"))
    p = json.loads(d["choices"][0]["message"]["content"])
    runs.append({o["label"]: o["bounds"] for o in p["result"]["detected_objects"]})
common = set.intersection(*[set(r) for r in runs])
print("labels in all 5 runs:", sorted(common))
for label in sorted(common):
    for i, r in enumerate(runs, 1):
        b = r[label]
        print(label, i, b["top_left"], b["bottom_right"])

