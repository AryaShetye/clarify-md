from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Trainer,
    TrainingArguments
)

dataset = load_dataset("json", data_files="data/metaphor_train.jsonl")

tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

def preprocess(batch):
    model_inputs = tokenizer(
        batch["input"], truncation=True, padding=True
    )
    labels = tokenizer(
        batch["target"], truncation=True, padding=True
    )
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

dataset = dataset.map(preprocess, batched=True)

args = TrainingArguments(
    output_dir="models/metaphor_finetuned",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    logging_steps=50,
    save_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset["train"]
)

trainer.train()
