import json

with open("data/clarify_md_dataset.json") as f:
    data = json.load(f)

risk_data = []

for row in data:
    risk_data.append({
        "text": row["patient_narrative"],
        "label": row["risk_level"]
    })

with open("data/risk_train.jsonl", "w") as f:
    for r in risk_data:
        f.write(json.dumps(r) + "\n")
