from transformers import pipeline

# Initialize sentiment analysis pipeline with DistilBERT
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(text, max_length=512):
    # Split text into chunks 
    words = text.split()
    chunks=[]
    for i in range(0, len(words), max_length):
        chunk = ''.join(text[i:i+max_length])
        chunks.append(chunk)
    
    # Analyze sentiment for each chunk
    results = [sentiment_analyzer(chunk)[0] for chunk in chunks]
    
    # Determine overall sentiment based on average scores
    positive_score = sum(result['score'] for result in results if result['label'] == 'POSITIVE') / len(results)
    negative_score = sum(result['score'] for result in results if result['label'] == 'NEGATIVE') / len(results)
    
    if positive_score > 0.6:
        return "positive"
    elif negative_score > 0.6:
        return "negative"
    else:
        return "neutral"


