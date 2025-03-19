import requests
from bs4 import BeautifulSoup
import time
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
            print("Site appears to be scrapeable with BeautifulSoup.")
        else:
            print("Content might be loaded dynamically.")
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
                        articles.append(story_body.get_text())
                        print('✅ ==========================================')
                        
                    else:
                        print(f"❌ Story not found in Story tag")
                else:
                    print(f"❌ Story tag not found")
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
            
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")

# BBC only has 10 articles to offer at maximum
def bbc_news_scraping(url):
    iter = 0
    limit = 3
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        search_list = soup.find_all('div', class_="sc-c6f6255e-0 eGcloy")
        print(search_list)
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
                                print('✅ =================================================')
                            else:
                                print('❌ text blocks not found')
                                limit+=1
                        else:
                            print('❌ article not found')
                            limit+=1
                    else:
                        print('❌ page doesnt exit')
                        limit+=1
                    
                else:
                    print('❌ !!!!!!!!!No RESULTS!!!!!!!!!!')
                
                iter+=1
                

        else:
            print('❌ Search not found')
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")


def news_scraping(url):
    iter = 0
    limit = 3
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        search_list = soup.find('div', class_="search-results")
        print(search_list)
        if search_list:
            for search_item in search_list:
                if search_item:
                    # print(search_item)
                    link = search_item.find('a', class_="u-clickable-card__link")
                    print(link['href'])
                    print(link.find('span').get_text())
                    print('\n')
                else:
                    print('search item not found')
        else:
            print('❌ search list not found')
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")


search_query = input('Search -- ')
# print('--------------------------------AP NEWS--------------------------------------')
# ap_url="https://apnews.com/search?q="+search_query+"&s=0"
# print(ap_url)
# ap_news_scraping(ap_url)

# print('--------------------------------BBC--------------------------------------')
# bbc_url ="https://www.bbc.com/search?q="+search_query
# print(bbc_url)
# bbc_news_scraping(bbc_url)


print('--------------------------------XXX--------------------------------------')
url ="https://www.aljazeera.com/search/"+search_query
print(url)
news_scraping(url)


# url = 'https://www.india.com/'
# test_scrapability(url)

print(len(articles))