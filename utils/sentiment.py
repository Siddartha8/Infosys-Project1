from transformers import pipeline

# Cardiff NLP model gives 3-class output (neg, neu, pos)
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
sentiment_pipeline = pipeline("sentiment-analysis", model=MODEL_NAME)

def analyze_sentiment(text: str):
    """
    Run Hugging Face sentiment model on text and return a dict {label, score}.
    """
    result = sentiment_pipeline(text, truncation=True)[0]
    label = result["label"]
    # Cardiff model uses LABEL_0/1/2, so remap:
    if label.startswith("LABEL_"):
        mapping = {"LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"}
        label = mapping[label]
    return {"label": label, "score": float(result["score"])}
