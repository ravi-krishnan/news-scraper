# NY times have paywall issue.
import requests
from api import analyze_sentiment
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
articles = []

def test_scrapability(url):
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Attempt to find elements you're interested in
        # For example, finding all article titles
        titles = soup.find_all('h3')
        if titles:
            print("scrapable")
        else:
            print("found dynamically loaded content")
    except Exception as e:
        print(f"Error: {e}")


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
                print(timestamp_ms)

                # add fn
                timestamp_s = int(timestamp_ms) / 1000
                dt_object = datetime.fromtimestamp(timestamp_s)
                human_readable_date = dt_object.strftime("%Y-%m-%d")
                print(human_readable_date)


                link = search_item.find('a', class_='Link')
                span = link.find('span')

                print(span.get_text())
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


            # for i, item in enumerate(item_divs, 1):
            #     search_item = item.find('div', class_='PagePromo-content')
            #     link = search_item.find('a', class_='Link')
            #     span = link.find('span')
            #     print(span.get_text())
            #     print(link['href'])
                
            #     response = requests.get(link['href'], headers=headers)
            #     page = BeautifulSoup(response.text, 'html.parser')
                
            #     story = page.find('bsp-story-page')
            #     if story:
            #         story_body = story.find('div', class_='RichTextStoryBody')
            #         if story_body:
            #             print(story_body.get_text())
                        
            #         else:
            #             print(f"❌ Story not found in Story tag")
            #     else:
            #         print(f"❌ Story tag not found")
            #     print('==========================================')
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
                    search_item_title = item.find('h2', class_ ="sc-87075214-3 cXFiLO")
                    if search_item['href'].startswith('https'):
                        link = search_item['href']
                    
                    else:
                        link = 'https://www.bbc.com'+search_item['href']
                    
                    print(search_item_title.get_text())
                    print(link)
                    response = requests.get(link, headers=headers)
                    page = BeautifulSoup(response.text, 'html.parser')
                    if page:
                        article = page.find('article')
                        if article:
                            text_blocks = article.find_all('div', class_='sc-18fde0d6-0 dlWCEZ')
                            article__ = ''
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


search_query = input('Search -- ')
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




# url = 'https://www.india.com/'
# test_scrapability(url)

print(len(articles))
with open("output.txt", "w") as file:
    for text in articles:
        file.write(text + "\n"+"*"*100 +'\n')

for i in articles:
    print(analyze_sentiment(i))