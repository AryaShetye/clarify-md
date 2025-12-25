import json

with open("data/clarify_md_dataset.json") as f:
    data = json.load(f)

emotion_data = []

for row in data:
    labels = [e["emotion"] for e in row["emotional_signals"]]
    emotion_data.append({
        "text": row["patient_narrative"],
        "labels": labels
    })

with open("data/emotion_train.jsonl", "w") as f:
    for r in emotion_data:
        f.write(json.dumps(r) + "\n")
