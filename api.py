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
from nltk.corpus import wordnet
from sentence_transformers import SentenceTransformer, util
import numpy as np
from transformers import MarianMTModel, MarianTokenizer
from gtts import gTTS


load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)


def load_nltk():
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    nltk.download('wordnet')

def topic_extractor(text):
    prompt = '''
        Extract the main topics from this article and return ONLY a list of topics in the exact format
        ["Topic1", "Topic2", "Topic3"]. Do not include any explanations, code, or additional text in your response.
        Topics should be at most 3 words. These topics are further used to check for common between other articles.
        So topics should be common topics. Not descriptive brief topics.
        The first letter of each topic should be capitalized.

        Article:
    '''
    prompt += text
    response = client.models.generate_content(
        model='gemini-1.5-flash', contents=prompt,
    )
    cleaned_response = response.text.strip()
    
    try:
        cleaned_response = re.sub(r'\\n|\\t|\\r|\\b|\\f|\\v|\\a|\\x', '', cleaned_response)
        cleaned_response = re.sub(r'``````', '', cleaned_response, flags=re.DOTALL)        
        topics = json.loads(cleaned_response)
        return topics
    except json.JSONDecodeError:
        print(f"Failed to parse response: {cleaned_response}")
        return []

def analyze_sentiment(text, max_length=512):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_length):
        chunk = ''.join(text[i:i+max_length])
        chunks.append(chunk)
    
    results = [sentiment_analyzer(chunk)[0] for chunk in chunks]
    positive_score = sum(result['score'] for result in results if result['label'] == 'POSITIVE') / len(results)
    negative_score = sum(result['score'] for result in results if result['label'] == 'NEGATIVE') / len(results)
    
    if positive_score > 0.6:
        return "Positive"
    elif negative_score > 0.6:
        return "Negative"
    else:
        return "Neutral"

def generate_summary(text, company, max_sentences=3):
    sentences = sent_tokenize(text)
    relevant_sentences = [sent for sent in sentences if company.lower() in sent.lower()]
    
    if not relevant_sentences:
        relevant_sentences = sentences
    
    stop_words = set(stopwords.words('english'))
    sentence_scores = {}
    for sent in relevant_sentences:
        words = nltk.word_tokenize(sent.lower())
        score = sum(1 for word in words if word not in stop_words)
        sentence_scores[sent] = score
    
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    return ' '.join(top_sentences)

def comparative_analysis(articles):
    count = 0
    now = datetime.now()
    print('Time at the start', now.minute, now.second)
    print('sleep for ', 60 - now.second, ' seconds')
    time.sleep(60 - now.second + 3)
    new_minute = datetime.now()
    print('ready at', new_minute.minute, new_minute.second)
    c_analysis = []
    
    for i, j in combinations(range(len(articles)), 2):
        if count % 15 == 0 and count != 0:
            now = datetime.now()
            print(f'15 requests served at -  {now.hour}:{now.minute}:{now.second}')
            print('wait for ', 60 - now.second, 'seconds to refresh the api request limit')
            time.sleep(60 - now.second + 3)
        
        prompt = f"""
                Do a comparative analysis on the following two articles:

                Article {i+1}: {articles[i]}

                Article {j+1}: {articles[j]}

                Provide a comparative analysis, focusing on both the comparison and the potential impact of these articles. Structure your response as a list containing two elements: the comparison and the impact, in that order.
                Ensure your analysis adheres to these guidelines:

                1.  Vary the starting article in your comparison. Sometimes begin with Article {i+1}, sometimes with Article {j+1}.
                2.  Maintain the same article order for both the comparison and impact sections.
                3.  Avoid repetitive phrasing; use diverse vocabulary and sentence structures for each comparison.
                4.  **DO NOT output the response in JSON format. Return the output as a list of strings.**
                5.  **The response MUST be a list of strings. Do not output in JSON or any other format.**

                Example Output:
                ["Article {i+1} emphasizes X, while Article {j+1} focuses on Y...", "The combined impact could lead to Z..."]

                Output format:
                ["Comparison of the articles...", "Impact of the articles..."]
        """
        
        response = client.models.generate_content(
            model='gemini-1.5-flash', contents=prompt,
        )
        count += 1
        text = response.text.replace("```", "")
        try:
            response_list = json.loads(text)
            c_analysis.append(response_list)
        except Exception as e:
            print('error', e)
            c_analysis.append(text)
    return c_analysis

def find_common_and_unique_topics_flexible(topics_list, similarity_threshold=0.7):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    common_topics = []
    unique_topics_lists = [list(topics) for topics in topics_list]

    all_topics = [topic for sublist in topics_list for topic in sublist]
    embeddings = model.encode(all_topics, convert_to_tensor=True)

    for i in range(len(topics_list)):
        for j in range(i + 1, len(topics_list)):
            for topic1 in topics_list[i]:
                for topic2 in topics_list[j]:
                    embedding1 = embeddings[all_topics.index(topic1)]
                    embedding2 = embeddings[all_topics.index(topic2)]
                    cosine_similarity = util.cos_sim(embedding1, embedding2).item()

                    if cosine_similarity >= similarity_threshold and topic1 != topic2:
                        found_group1 = next((group for group in common_topics if topic1 in group), None)
                        found_group2 = next((group for group in common_topics if topic2 in group), None)

                        if found_group1 and found_group2:
                            if found_group1 != found_group2:
                                common_topics.remove(found_group1)
                                common_topics.remove(found_group2)
                                common_topics.append(list(set(found_group1 + found_group2)))
                        elif found_group1:
                            found_group1.append(topic2)
                        elif found_group2:
                            found_group2.append(topic1)
                        else:
                            common_topics.append([topic1, topic2])

    for group in common_topics:
        for topic in group:
            for unique_list in unique_topics_lists:
                if topic in unique_list:
                    unique_list.remove(topic)

    return common_topics, unique_topics_lists

def text_to_hi_audio(text):
    model_name = "Helsinki-NLP/opus-mt-en-hi"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
    hindi_text = tokenizer.decode(translated[0], skip_special_tokens=True)

    tts = gTTS(text=hindi_text, lang='hi')
    tts.save("output.mp3")
    return 'Audio saved as output.mp3'

def final_sentiment_analysis_report(sentiments, comparative_analysis):
    now = datetime.now()
    print('Final sentimental analysis')
    print('Time now:', now.minute, now.second)
    print('sleep for', 60 - now.second, 'seconds')
    time.sleep(60 - now.second + 3)
    prompt = f"""
    Analyze the provided "Sentiment Distribution" and "Coverage Differences" data to generate a concise "Final Sentiment Analysis" string. 

    The output must be a single string summarizing the overall market sentiment and potential stock impact based on the input data. Do not include any additional explanatory text or helper messages.

    Example input:
    "Sentiment Distribution": {{
        "Positive": 1,
        "Negative": 1,
        "Neutral": 0
        }},
        "Coverage Differences": [
        {{
        "Comparison": "Article 1 highlights Tesla's strong sales, while Article 2 discusses regulatory issues.",
        "Impact": "The first article boosts confidence in Tesla's market growth, while the second raises concerns about future regulatory hurdles."
        }},
        {{
        "Comparison": "Article 1 is focused on financial success and innovation, whereas Article 2 is about legal challenges and risks.",
        "Impact": "Investors may react positively to growth news but stay cautious due to regulatory scrutiny."
        }}
        ]

    Example expected output:
    "Tesla's latest news coverage is mostly positive. Potential stock growth expected."

    Input:
    {{
        "Sentiment Distribution": {sentiments}
        "Coverage Differences": {comparative_analysis}
    }}

    Output:
    """
    response = client.models.generate_content(
        model='gemini-1.5-flash', contents=prompt, 
    )
    return response.text

hc_summaries = [

    'Presidential tweets his support for Tesla CEO Elon Musk. Trump calls Musk a ‘great guy’ and says he is ‘proud’ of him.',
    'Tesla sales plunged 45% in Europe in January, according to research firm Jato Dynamics. That comes after a report of falling sales in California, its biggest U.S. market. “I don’t even want to drive it,” said Model 3 owner John Parnell.',
    'A Chinese court ordered Zhang to pay more than $23,000 in damages and publicly apologize to the $1.1 trillion company. Over the last four years, Tesla has sued at least six car owners in China.Tesla won all 11 cases for which AP could determine the verdicts. Two judgments, including Zhang’s, are on appeal. One case was settled out of court.Tesla officials in China and the United States did not reply to requests for comment. Tesla has profited from the largesse of the Chinese state, winning unprecedented regulatory benefits, below-market rate loans and large tax breaks.Tesla won nearly 90% of civil cases over safety, quality or contract disputes, AP finds. Journalists told AP they have been instructed to avoid negative coverage of the automaker.',
    "People protesting against Tesla should be labelled domestic terrorists, says President Donald Trump. Trump sat in the driver's seat of a brand new red Tesla that he said he planned to buy, with Elon Musk in the passenger seat.",
    'The issue affects more than 46,000 trucks made starting in November 2023. It comes as Tesla grapples with falling sales amid a backlash against the firm.',
    'US Attorney General Pam Bondi said the damage to Tesla cars, dealerships and charging stations was "domestic terrorism" There is no specific US law against domestic terrorism, but prosecutors can request longer prison sentences.'
    ]
