from transformers import pipeline
from dotenv import load_dotenv
from google import genai
import os
from itertools import combinations
import time
from datetime import datetime
import re
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from transformers import pipeline

# Download necessary NLTK resources

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def load_nltk():
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')

def topic_extractor(text):
    # time.sleep(3)
    prompt = '''
        Extract the main topics from this article and return ONLY a Python list of topics in the exact format
        ["topic1", "topic2", "topic3"]. Do not include any explanations, code, or additional text in your response.
        Topics should be at most 3 words. These topics are further used to check for common between other articles.
        So topics should be common topics. Not descriptive brief topics.

        Article:
    '''

    prompt+=text
    response = client.models.generate_content(
        model='gemini-1.5-flash', contents=prompt, 
    )
    cleaned_response = response.text.strip()
    
    # Remove unwanted characters and convert to JSON list
    try:
        # Remove backslashes and other unwanted characters
        cleaned_response = re.sub(r'\\n|\\t|\\r|\\b|\\f|\\v|\\a|\\x', '', cleaned_response)
        cleaned_response = re.sub(r'``````', '', cleaned_response, flags=re.DOTALL)        
        # Load as JSON
        topics = json.loads(cleaned_response)
        return topics
    except json.JSONDecodeError:
        print(f"Failed to parse response: {cleaned_response}")
        return []


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
        return "Positive"
    elif negative_score > 0.6:
        return "Negative"
    else:
        return "Neutral"


def generate_summary(text, company,  max_sentences=3):
    # Tokenize sentences
    sentences = sent_tokenize(text)
    
    # Filter sentences containing the company name
    relevant_sentences = [sent for sent in sentences if company.lower() in sent.lower()]
    
    # If no sentences mention the company, use the entire text
    if not relevant_sentences:
        relevant_sentences = sentences
    
    # Use a simple extractive approach to select top sentences
    stop_words = set(stopwords.words('english'))
    sentence_scores = {}
    for sent in relevant_sentences:
        words = nltk.word_tokenize(sent.lower())
        score = sum(1 for word in words if word not in stop_words)
        sentence_scores[sent] = score
    
    # Sort sentences by score and select top ones
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    
    return ' '.join(top_sentences)

def comparative_analysis(articles):
    count=0
    now = datetime.now()
    print('Time at the start', now.minute, now.second)
    print('sleep for ', 60-now.second,' seconds')
    time.sleep(60-now.second+3)
    new_minute = datetime.now()
    print('ready at', new_minute.minute, new_minute.second)
    c_analysis=[]
    for i, j in combinations(range(len(articles)), 2):

        if count%15 == 0 and count!=0:
            now = datetime.now()
            print(f'15 requests served at -  {now.hour}:{now.minute}:{now.second}')
            
            print('wait for ', 60-now.second, 'seconds to refresh the api request limit')
            time.sleep(60 - now.second + 3)
            
        prompt = f"""
                    Do a comparative analysis on these two articles:
                    Article {i+1}: {articles[i]}
                    Article {j+1}: {articles[j]}

                    To make the comparisons more natural and varied:
                    1.  Randomly choose which article to describe first. Sometimes start with Article {i+1}, sometimes with Article {j+1}.
                    2.  But keep the same order for both comparison and impact. If Article{i+1} is discussed first in comparison then It should be discussed first in Impact as well.
                    3.  Avoid using the exact same phrasing to describe Article {i+1} or Article {j+1} in every comparison.
                    4.  Use diverse sentence structures and vocabulary to make each comparison unique.

                    Here's an example of the a scenario and the desired output:
                    Suppose Article{i+1} was about Tesla company's strong sales and performance and 
                    Article {j+1} was anout the regulatory challenges faced by the company.

                    The output should look like this:

                    {{
                        "Comparison": "In contrast to Article {j+1}, which outlines regulatory challenges, Article {i+1} highlights Tesla's strong sales performance.",
                        "Impact": "While the regulatory issues raised in Article {j+1} may cause concern, Article {i+1}'s sales data suggests continued market growth."
                    }}

                    Remember, only provide the string output. Avoid any additional text.
                """
        
        response = client.models.generate_content(
            model='gemini-1.5-flash', contents=prompt, 
        )
        count+=1
        c_analysis.append(response.text)
    return c_analysis

hc_summaries = [

    'Presidential tweets his support for Tesla CEO Elon Musk. Trump calls Musk a ‘great guy’ and says he is ‘proud’ of him.',
    'Tesla sales plunged 45% in Europe in January, according to research firm Jato Dynamics. That comes after a report of falling sales in California, its biggest U.S. market. “I don’t even want to drive it,” said Model 3 owner John Parnell.',
    'A Chinese court ordered Zhang to pay more than $23,000 in damages and publicly apologize to the $1.1 trillion company. Over the last four years, Tesla has sued at least six car owners in China.Tesla won all 11 cases for which AP could determine the verdicts. Two judgments, including Zhang’s, are on appeal. One case was settled out of court.Tesla officials in China and the United States did not reply to requests for comment. Tesla has profited from the largesse of the Chinese state, winning unprecedented regulatory benefits, below-market rate loans and large tax breaks.Tesla won nearly 90% of civil cases over safety, quality or contract disputes, AP finds. Journalists told AP they have been instructed to avoid negative coverage of the automaker.',
    "People protesting against Tesla should be labelled domestic terrorists, says President Donald Trump. Trump sat in the driver's seat of a brand new red Tesla that he said he planned to buy, with Elon Musk in the passenger seat.",
    'The issue affects more than 46,000 trucks made starting in November 2023. It comes as Tesla grapples with falling sales amid a backlash against the firm.',
    'US Attorney General Pam Bondi said the damage to Tesla cars, dealerships and charging stations was "domestic terrorism" There is no specific US law against domestic terrorism, but prosecutors can request longer prison sentences.'
    ]
