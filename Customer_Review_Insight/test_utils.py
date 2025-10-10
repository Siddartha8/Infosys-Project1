from utils.text_utils import cleaned_string
from utils.sentiment import analyze_sentiment

test_text = "I love this fantastic product!"

# Test text cleaning
cleaned = cleaned_string(test_text)
print("Cleaned text:", cleaned)

# Test sentiment analysis
result = analyze_sentiment(test_text)
print("Sentiment result:", result)
