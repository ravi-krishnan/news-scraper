import requests
import json
from api import *
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

N_ARTICLES = 10

result = {}
articles = []
titles = []
summaries = []
sentiments = []
topics=[]



# pep 8
def ap_news_scraping(url, n_articles):
    iter_count = 0
    limit = 30
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        search_list = soup.find('div', class_='PageList-items')
        
        if search_list:
            item_divs = search_list.find_all('div', class_='PageList-items-item')
            while iter_count < limit:
                if len(articles) >= n_articles:
                    break
                
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
# BBC only has 10 articles to offer at maximum



search_query = 'Tesla'
# search_query = input('Search -- ')

# print('--------------------------------BBC--------------------------------------')
# bbc_url ="https://www.bbc.com/search?q="+search_query+"+company"
# print(bbc_url, '\n')
# bbc_news_scraping(bbc_url, n_articles)

print('--------------------------------AP NEWS--------------------------------------')
ap_url = f"https://apnews.com/search?q={search_query}+company&s=0"
print(ap_url, '\n')
ap_news_scraping(ap_url, N_ARTICLES)

print('No of articles:', len(articles))


load_nltk()
for i, article in enumerate(articles):
    print('⭐', titles[i])
    summary = generate_summary(article, f"{search_query} company")
    print('Summary created..')
    sentiment = analyze_sentiment(summary)
    print('Sentiment analyzed..')
    topic = topic_extractor(summary)
    print('Topics extracted..')
    sentiments.append(sentiment)
    summaries.append(summary)
    topics.append(topic)
    print('')

sentiment_counter = {}
for sentiment in sentiments:
    sentiment_counter[sentiment] = sentiment_counter.get(sentiment, 0) + 1

comparative_analysis_result = comparative_analysis(summaries)

common_topics, unique_topic_lists = find_common_and_unique_topics_flexible(topics)

result["Company"] = search_query
result["Articles"] = [
    {
        "Title": titles[i],
        "Summary": summaries[i],
        "Topics": topics[i],
        "Sentiment": sentiments[i],
    }
    for i in range(len(articles))
]

result["Comparative Sentiment Score"] = {
    "Sentiment Distribution": {},
    "Coverage Differences": [],
    "Topic Overlap": {
        "Common Topics": [],
    }
}

result["Comparative Sentiment Score"]["Sentiment Distribution"] = sentiment_counter

for comparison, impact in comparative_analysis_result:
    comparative_analysis = {
        "Comparison": comparison,
        "Impact": impact
    }
    result["Comparative Sentiment Score"]["Coverage Differences"].append(comparative_analysis)

result["Comparative Sentiment Score"]["Topic Overlap"]["Common Topics"] = []

for topic_groups in common_topics:
    similar_topics = '/'.join(str(topic) for topic in topic_groups)
    result["Comparative Sentiment Score"]["Topic Overlap"]["Common Topics"].append(similar_topics)

for i, unique_topics in enumerate(unique_topic_lists):
    result["Comparative Sentiment Score"]["Topic Overlap"][f"Unique Topics in Article {i+1}"] = unique_topics

final_sentiment_analysis = final_sentiment_analysis_report(sentiment_counter, result["Comparative Sentiment Score"]["Coverage Differences"])
hindi_audio = text_to_hi_audio(final_sentiment_analysis)

result["Final Sentiment Analysis"] = final_sentiment_analysis
result["Audio"] = '/news-scraper/output.mp3'

with open('result.json', 'w') as file:
    json.dump(result, file, indent=4)

print("JSON file created successfully!")



































# def bbc_news_scraping(url):
#     iter = 0
#     limit = 10
#     try:
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         search_list = soup.find_all('div', class_="sc-c6f6255e-0 eGcloy")
#         # print(search_list)
#         if search_list:
            
#             while iter < limit:
#                 if len(articles) == n_articles:
#                     iter = limit+1

#                 else:

#                     item = search_list[iter]
#                     search_item = item.find('a', class_="sc-2e6baa30-0 gILusN")
                    
#                     if search_item:
#                         title = item.find('h2', class_ ="sc-87075214-3 cXFiLO")
#                         if search_item['href'].startswith('https'):
#                             link = search_item['href']
                        
#                         else:
#                             link = 'https://www.bbc.com'+search_item['href']
                        
#                         print(title.get_text())
#                         print(link)
#                         response = requests.get(link, headers=headers)
#                         page = BeautifulSoup(response.text, 'html.parser')
#                         if page:
#                             article = page.find('article')
#                             if article:
#                                 text_blocks = article.find_all('div', class_='sc-18fde0d6-0 dlWCEZ')
#                                 article__ = ''
#                                 titles.append(title.get_text())
#                                 if text_blocks:
#                                     for text in text_blocks:
#                                         article__+=text.get_text()

#                                     articles.append(article__)

#                                     print('✅ successfully scraped')
#                                     print('')
#                                 else:
#                                     print('❌ text blocks not found')
#                                     print('')
#                                     limit+=1
#                             else:
#                                 print('❌ article not found')
#                                 print('')
#                                 limit+=1
#                         else:
#                             print('❌ page doesnt exit')
#                             print('')
#                             limit+=1
                        
#                     else:
#                         print('❌ !!!!!!No RESULTS!!!!!!!!!!')
#                         print('')
                    
#                     iter+=1
                    

#         else:
#             print('❌ Search not found')
#             print('')
#     except Exception as e:
#         print(f"❌ Error scraping {url}: {e}")
#         print('')
# def news_scraping(url):
#     iter = 0
#     limit = 3
#     try:
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         search_results = soup.find('div', class_="css-8xl60i")
#         search_list = search_results.find('ol')
#         search_items = search_list.find_all('li', class_='css-1l4w6pd', limit=3)
#         if search_items:
#             for search_item in search_items:
#                 if search_item:
#                     link = search_item.find('a')
#                     print('https://nytimes.com/'+link['href'])
#                     print(link.find('h4').get_text())

#                     response = requests.get('https://nytimes.com/'+link['href'], headers=headers)
#                     page = BeautifulSoup(response.text, 'html.parser')
#                     if page:
#                         stories  = page.find_all('p', class_='css-at9mc1 evys1bk0')
#                         print(stories)
#                         article__ = ''
#                         if stories:
#                             for story in stories:
#                                 print(story.get_text())
#                                 article__+=story.get_text()
                                
#                             print(article__)

#                         else:
#                             print('!!story boards doesnt exist')
#                     else:
#                         print('!! Page doesnt exist')
#                     print('\n')
#                 else:
#                     print('search item not found')
#         else:
#             print('!!! search list not found')
#     except Exception as e:
#         print(f" Error scraping {url}: {e}")
