import requests
from bs4 import BeautifulSoup
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline, MarianMTModel, MarianTokenizer
from google import genai
from gtts import gTTS
from dotenv import load_dotenv
import os
import time
import re
import json
from itertools import combinations
import base64
import io

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def load_nltk():
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    nltk.download('wordnet')

def ap_news_scraping(url, n_articles):
    iter_count = 0
    limit = 30
    articles = []
    titles = []
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        search_list = soup.find('div', class_='PageList-items')
        
        if search_list:
            item_divs = search_list.find_all('div', class_='PageList-items-item')
            while iter_count < limit:
                if len(articles) >= n_articles:
                    return articles, titles
                
                item = item_divs[iter_count]
                search_item = item.find('div', class_='PagePromo-content')

                date_header = item.find('div', class_='PagePromo-date')
                bsp_timestamp = date_header.find('bsp-timestamp')
                timestamp_ms = bsp_timestamp['data-timestamp']

                timestamp_s = int(timestamp_ms) / 1000
                dt_object = datetime.fromtimestamp(timestamp_s)
                human_readable_date = dt_object.strftime("%Y-%m-%d")
                print(human_readable_date)

                link = search_item.find('a', class_='Link')
                title = link.find('span')

                print(title.get_text())
                print(link['href'])

                article_response = requests.get(link['href'], headers=headers)
                article_page = BeautifulSoup(article_response.text, 'html.parser')
                
                story = article_page.find('bsp-story-page')
                if story:
                    story_body = story.find('div', class_='RichTextStoryBody')
                    if story_body:
                        story_para = story_body.find_all('p')
                        if story_para:
                            article_text = human_readable_date + '\n'
                            article_text += '\n'.join(para.get_text() for para in story_para)
                            articles.append(article_text)
                            titles.append(title.get_text())
                            print('✅ Successfully scraped')
                            print('')
                        else:
                            print('❌ Story paragraphs not found')
                            print('')
                    else:
                        print("❌ Story not found in Story tag")
                        print('')
                else:
                    print("❌ Story tag not found")
                    print('')
                    limit += 1
                
                iter_count += 1 

        else:
            print(f"❌ Content not found in HTML: {url}")
            print('')
            
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        print('')

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
    print(f'Time - {datetime.now().strftime("%H:%M:%S")}')
    print('We need to wait for ', 60 - now.second, ' seconds to refresh the APi request limit.')
    time.sleep(60 - now.second + 3)
    new_minute = datetime.now()
    print('Ready!! at ', {datetime.now().strftime("%H:%M:%S")})
    c_analysis = []
    
    for i, j in combinations(range(len(articles)), 2):
        if count % 14 == 0 and count != 0:
            now = datetime.now()
            print(f'15 requests served at -  {datetime.now().strftime("%H:%M:%S")}')
            print('We need to wait for ', 60 - now.second, 'seconds to refresh the API request limit.')
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
                4.  The word limit for both comparison and impact is 40 words. DO NOT EXCEED IT.
                5.  **DO NOT output the response in JSON format. Return the output as a list of strings.**
                6.  **The response MUST be a list of strings. Do not output in JSON or any other format.**

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
    print('Audio saved as output.mp3')
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    # Encode audio to Base64
    audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")
    return audio_base64

def final_sentiment_analysis_report(sentiments, comparative_analysis):
    now = datetime.now()
    print('* Overall sentimental report *')
    print(f'Time - {datetime.now().strftime("%H:%M:%S")}')
    print('We need to wait for ', 60 - now.second, 'seconds to refresh the API request limit')
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
