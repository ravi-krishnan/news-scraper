from transformers import pipeline
from dotenv import load_dotenv
from google import genai
import os
from itertools import combinations

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def topic_extractor(text):

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
    return (response.text)


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
    # print('no of chunks',len(chunks))
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


def comparative_analysis(articles):
    count=0
    c_analysis=[]
    for i, j in combinations(range(len(articles)), 2):
        count+=1
        prompt = f'''
                    Do comparative analysis on these two articles
                    Article {i+1} = {articles[i]},
                    Article {j+1} =  {articles[j]}

                    This is an example of the expected output
                    {{
                    "Comparison": "Article {i+1} highlights Tesla's strong sales, while Article {j+1} discusses regulatory issues.",
                    "Impact": "The article {i+1} boosts confidence in Tesla's market growth,while the article {j+1} raises concerns about future regulatory hurdles."
                    }}
                    Ignore all additonal texts, I would only be requiring the output. 
                    
                '''
        response = client.models.generate_content(
            model='gemini-1.5-flash', contents=prompt, 
        )
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

for i in comparative_analysis(hc_summaries):
    print(i,'\n')
        