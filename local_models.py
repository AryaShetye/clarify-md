from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification
)

# Shared generation model
GEN_MODEL_NAME = "google/flan-t5-small"
gen_tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL_NAME)
gen_model = AutoModelForSeq2SeqLM.from_pretrained(GEN_MODEL_NAME)

generator = pipeline(
    "text2text-generation",
    model=gen_model,
    tokenizer=gen_tokenizer,
    device=-1
)

# Emotion classifier
emotion_classifier = pipeline(
    "text-classification",
    model="bhadresh-savani/distilbert-base-uncased-emotion",
    top_k=None
)

# Risk (zero-shot)
risk_classifier = pipeline(
    "zero-shot-classification",
    model="typeform/distilbert-base-uncased-mnli"
)
