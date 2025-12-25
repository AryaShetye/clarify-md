from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)

dataset = load_dataset("json", data_files="data/risk_train.jsonl")

labels = ["low", "moderate", "high"]
label2id = {l: i for i, l in enumerate(labels)}
id2label = {i: l for l, i in label2id.items()}

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def preprocess(batch):
    enc = tokenizer(batch["text"], truncation=True, padding=True)
    enc["labels"] = label2id[batch["label"]]
    return enc

dataset = dataset.map(preprocess)

model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=3,
    id2label=id2label,
    label2id=label2id
)

args = TrainingArguments(
    output_dir="models/risk_finetuned",
    per_device_train_batch_size=8,
    num_train_epochs=3,
    logging_steps=50
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset["train"]
)

trainer.train()
