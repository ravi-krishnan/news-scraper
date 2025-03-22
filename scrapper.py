import requests
import json
from api import *
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

result = {}
articles = []
titles = []
summaries = []
sentiments = []
topics=[]

def ap_news_scraping(url):
    iter = 0
    limit = 3
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find article content - adjust selectors based on the site
        search_list = soup.find('div', class_='PageList-items')
        
        
        if search_list:
            item_divs = search_list.find_all('div', class_='PageList-items-item')
            while iter < limit:
                item = item_divs[iter]
                search_item = item.find('div', class_='PagePromo-content')

                date_header = item.find('div', class_='PagePromo-date')
                bsp_timestamp = date_header.find('bsp-timestamp')
                timestamp_ms = bsp_timestamp['data-timestamp']
                # print(timestamp_ms)

                # add fn
                timestamp_s = int(timestamp_ms) / 1000
                dt_object = datetime.fromtimestamp(timestamp_s)
                human_readable_date = dt_object.strftime("%Y-%m-%d")
                print(human_readable_date)


                link = search_item.find('a', class_='Link')
                title = link.find('span')

                print(title.get_text())
                print(link['href'])

                response = requests.get(link['href'], headers=headers)
                page = BeautifulSoup(response.text, 'html.parser')
                
                story = page.find('bsp-story-page')
                if story:
                    story_body = story.find('div', class_='RichTextStoryBody')
                    if story_body:
                        story_para = story_body.find_all('p')
                        if story_para:
                            article__=''
                            titles.append(title.get_text())
                            article__+=human_readable_date+'\n'
                            for para in story_para:
                                article__ += para.get_text() + '\n'
                            articles.append(article__)
                            print('✅successfully scraped')
                            print('')
                        else:
                            print('❌story paragraphs not found')
                            print('')
                        
                        
                    else:
                        print(f"❌ Story not found in Story tag")
                        print('')
                else:
                    print(f"❌ Story tag not found")
                    print('')
                    limit+=1
                
                iter+=1 

        else:
            print(f"❌ Content not found in HTML: {url}")
            print('')
            
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        print('')

# BBC only has 10 articles to offer at maximum
def bbc_news_scraping(url):
    iter = 0
    limit = 3
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        search_list = soup.find_all('div', class_="sc-c6f6255e-0 eGcloy")
        # print(search_list)
        if search_list:
            
            while iter < limit:
                item = search_list[iter]
                search_item = item.find('a', class_="sc-2e6baa30-0 gILusN")
                
                if search_item:
                    title = item.find('h2', class_ ="sc-87075214-3 cXFiLO")
                    if search_item['href'].startswith('https'):
                        link = search_item['href']
                    
                    else:
                        link = 'https://www.bbc.com'+search_item['href']
                    
                    print(title.get_text())
                    print(link)
                    response = requests.get(link, headers=headers)
                    page = BeautifulSoup(response.text, 'html.parser')
                    if page:
                        article = page.find('article')
                        if article:
                            text_blocks = article.find_all('div', class_='sc-18fde0d6-0 dlWCEZ')
                            article__ = ''
                            titles.append(title.get_text())
                            if text_blocks:
                                for text in text_blocks:
                                    article__+=text.get_text()
                                articles.append(article__)
                                print('✅ successfully scraped')
                                print('')
                            else:
                                print('❌ text blocks not found')
                                print('')
                                limit+=1
                        else:
                            print('❌ article not found')
                            print('')
                            limit+=1
                    else:
                        print('❌ page doesnt exit')
                        print('')
                        limit+=1
                    
                else:
                    print('❌ !!!!!!No RESULTS!!!!!!!!!!')
                    print('')
                
                iter+=1
                

        else:
            print('❌ Search not found')
            print('')
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        print('')


def news_scraping(url):
    iter = 0
    limit = 3
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find('div', class_="css-8xl60i")
        search_list = search_results.find('ol')
        search_items = search_list.find_all('li', class_='css-1l4w6pd', limit=3)
        if search_items:
            for search_item in search_items:
                if search_item:
                    link = search_item.find('a')
                    print('https://nytimes.com/'+link['href'])
                    print(link.find('h4').get_text())

                    response = requests.get('https://nytimes.com/'+link['href'], headers=headers)
                    page = BeautifulSoup(response.text, 'html.parser')
                    if page:
                        stories  = page.find_all('p', class_='css-at9mc1 evys1bk0')
                        print(stories)
                        article__ = ''
                        if stories:
                            for story in stories:
                                print(story.get_text())
                                article__+=story.get_text()
                                
                            print(article__)

                        else:
                            print('!!story boards doesnt exist')
                    else:
                        print('!! Page doesnt exist')
                    print('\n')
                else:
                    print('search item not found')
        else:
            print('!!! search list not found')
    except Exception as e:
        print(f" Error scraping {url}: {e}")


# search_query = input('Search -- ')
search_query = 'tesla'

print('--------------------------------AP NEWS--------------------------------------')
ap_url="https://apnews.com/search?q="+search_query+"+company&s=0"
print(ap_url,'\n')
ap_news_scraping(ap_url)

print('--------------------------------BBC--------------------------------------')
bbc_url ="https://www.bbc.com/search?q="+search_query+"+company"
print(bbc_url, '\n')
bbc_news_scraping(bbc_url)


# print('--------------------------------NEWS--------------------------------------')
# today = datetime.now()
# if today.month == 1:
#     prev = today.replace(year=today.year-1, month=12)
# else:
#     prev = today.replace(month=today.month-1)

# today = today.strftime('%Y-%m-%d')
# prev_month = prev.strftime('%Y-%m-%d')

# url ="https://www.nytimes.com/search?dropmab=false&endDate="+today+"&lang=en&query=tesla&sort=best&startDate="+prev_month
# print(url)
# news_scraping(url)



print('No of articles:',len(articles))
with open("articles.txt", "w") as file:
    for text in articles:
        file.write(text + "\n"+"*"*100 +'\n')

for i in range(len(articles)):
    print('⭐', titles[i])
    sentiment = analyze_sentiment(articles[i])
    summary = generate_summary(articles[i])
    topic = topic_extractor(summary)
    sentiments.append(sentiment)
    summaries.append(summary)
    topics.append(topic)
    print('')


print(summaries)

hc_summaries = [
    'Presidential tweets his support for Tesla CEO Elon Musk. Trump calls Musk a ‘great guy’ and says he is ‘proud’ of him.',
    'Tesla sales plunged 45% in Europe in January, according to research firm Jato Dynamics. That comes after a report of falling sales in California, its biggest U.S. market. “I don’t even want to drive it,” said Model 3 owner John Parnell.',
    'A Chinese court ordered Zhang to pay more than $23,000 in damages and publicly apologize to the $1.1 trillion company. Over the last four years, Tesla has sued at least six car owners in China.Tesla won all 11 cases for which AP could determine the verdicts. Two judgments, including Zhang’s, are on appeal. One case was settled out of court.Tesla officials in China and the United States did not reply to requests for comment. Tesla has profited from the largesse of the Chinese state, winning unprecedented regulatory benefits, below-market rate loans and large tax breaks.Tesla won nearly 90% of civil cases over safety, quality or contract disputes, AP finds. Journalists told AP they have been instructed to avoid negative coverage of the automaker.',
    "People protesting against Tesla should be labelled domestic terrorists, says President Donald Trump. Trump sat in the driver's seat of a brand new red Tesla that he said he planned to buy, with Elon Musk in the passenger seat.",
    'The issue affects more than 46,000 trucks made starting in November 2023. It comes as Tesla grapples with falling sales amid a backlash against the firm.',
    'US Attorney General Pam Bondi said the damage to Tesla cars, dealerships and charging stations was "domestic terrorism" There is no specific US law against domestic terrorism, but prosecutors can request longer prison sentences.'
    ]


result["Company"] = search_query
result["Articles"] = [{
                        "Title": titles[i],
                        "Summary": summaries[i],
                        "Topics": topics[i],
                        "Sentiment":sentiments[i],
                        
                        }
                      for i in range(len(articles))]

with open('result.json', 'w') as file:
    json.dump(result, file, indent=4)

print("JSON file created successfully!")
print(result)