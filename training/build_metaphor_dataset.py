import json

with open("data/clarify_md_dataset.json") as f:
    data = json.load(f)

pairs = []

for row in data:
    if row["metaphorical_phrases"]:
        pairs.append({
            "input": f"Patient: {row['patient_narrative']}",
            "target": row["clinical_interpretation"]
        })

with open("data/metaphor_train.jsonl", "w") as f:
    for p in pairs:
        f.write(json.dumps(p) + "\n")
