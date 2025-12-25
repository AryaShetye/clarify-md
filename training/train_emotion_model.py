from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
import torch

dataset = load_dataset("json", data_files="data/emotion_train.jsonl")

label_list = list({l for r in dataset["train"] for l in r["labels"]})
label2id = {l: i for i, l in enumerate(label_list)}
id2label = {i: l for l, i in label2id.items()}

def encode_labels(example):
    vec = [0] * len(label_list)
    for l in example["labels"]:
        vec[label2id[l]] = 1
    example["labels"] = vec
    return example

dataset = dataset.map(encode_labels)

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding=True)

dataset = dataset.map(tokenize, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(label_list),
    problem_type="multi_label_classification",
    id2label=id2label,
    label2id=label2id
)

args = TrainingArguments(
    output_dir="models/emotion_finetuned",
    per_device_train_batch_size=8,
    num_train_epochs=3,
    logging_steps=50,
    save_strategy="epoch",
    evaluation_strategy="no"
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset["train"]
)

trainer.train()
