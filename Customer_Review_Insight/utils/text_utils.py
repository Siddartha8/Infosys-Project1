import re
import spacy
from nltk.corpus import stopwords

# load spacy model once
nlp = spacy.load("en_core_web_sm")
NLTK_STOPS = set(stopwords.words("english"))

def clean_and_tokenize(text: str):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    doc = nlp(text)
    return [
        token.lemma_ for token in doc
        if token.lemma_ not in NLTK_STOPS
        and not token.is_punct
        and token.lemma_.strip()
    ]

def cleaned_string(text: str):
    """Returns a single cleaned string (lemmas, stopwords removed)."""
    return " ".join(clean_and_tokenize(text))
