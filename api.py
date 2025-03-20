from transformers import pipeline

# Initialize sentiment analysis pipeline with DistilBERT
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


# def analyze_sentiment(text, max_length=512):
#     # Split text into chunks 
#     words = text.split()
#     chunks=[]
#     for i in range(0, len(words), max_length):
#         chunk = ''.join(text[i:i+max_length])
#         chunks.append(chunk)
    
#     # Analyze sentiment for each chunk
#     results = [sentiment_analyzer(chunk)[0] for chunk in chunks]
#     # Determine overall sentiment based on average scores
#     positive_score = sum(result['score'] for result in results if result['label'] == 'POSITIVE') / len(results)
#     negative_score = sum(result['score'] for result in results if result['label'] == 'NEGATIVE') / len(results)
    
#     if positive_score > 0.6:
#         return "positive"
#     elif negative_score > 0.6:
#         return "negative"
#     else:
#         return "neutral"


# Initialize summarization pipeline

def generate_summary(text, max_length=300):

    words = text.split()
    # if len(words) <= 1024:  # BART's max input length
    #     summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
    #     return summary[0]['summary_text']
    # else:
    # For very long texts, summarize chunks and then summarize the combined summaries
    #     chunks = [' '.join(words[i:i+1024]) for i in range(0, len(words), 1024)]
    #     summaries = [summarizer(chunk, max_length=100, min_length=30, do_sample=False)[0]['summary_text'] for chunk in chunks]
    #     combined_summary = ' '.join(summaries)
    chunks = []
    token_limit = 1024
    for i in range(0, len(words), token_limit):
        chunk = ''.join(text[i: i+token_limit])
        # print(chunk, '\n ==================== \n')
        chunks.append(chunk)
    
    combined_summary = ''
    for chunk in chunks:
        summary = summarizer(chunk, max_length=200, min_length=30, do_sample=False)
        # print(summary)
        '''
            summary format : 
                [{'summary_text': 'Tesla sales plunged 45% in Europe in January, 
                according to research firm Jato Dynamics. That comes after a report of falling sales in California,
                its biggest U.S. market. “I don’t even want to drive it,” said Model 3 owner John Parnell.'}]
        '''
        combined_summary+=summary[0]['summary_text']
    print('no of chunks',len(chunks))
    print(combined_summary, '\n')

    if len(combined_summary.split()) > 1024:
        return generate_summary(combined_summary, max_length)
    else:
        return combined_summary
        
        # If the combined summary is still too long, summarize it again
        # if len(combined_summary.split()) > 1024:
        #     return generate_summary(combined_summary, max_length)
        # else:
        #     final_summary = summarizer(combined_summary, max_length=max_length, min_length=30, do_sample=False)
        #     return final_summary[0]['summary_text']
