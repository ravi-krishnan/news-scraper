from utils import (ap_news_scraping, generate_summary, analyze_sentiment, topic_extractor,
                   comparative_analysis, find_common_and_unique_topics_flexible,
                   final_sentiment_analysis_report, text_to_hi_audio)


def process_search_query(search_query):
    N_ARTICLES = 10
    ap_url = f"https://apnews.com/search?q={search_query}+company&s=0"
    
    articles, titles = ap_news_scraping(ap_url, N_ARTICLES)
    
    summaries = []
    sentiments = []
    topics = []
    
    for i, article in enumerate(articles):
        summary = generate_summary(article, f"{search_query} company")
        sentiment = analyze_sentiment(summary)
        topic = topic_extractor(summary)
        
        sentiments.append(sentiment)
        summaries.append(summary)
        topics.append(topic)

    sentiment_counter = {}
    for sentiment in sentiments:
        sentiment_counter[sentiment] = sentiment_counter.get(sentiment, 0) + 1

    comparative_analysis_result = comparative_analysis(summaries)
    common_topics, unique_topic_lists = find_common_and_unique_topics_flexible(topics)

    result = {
        "Company": search_query,
        "Articles": [
            {
                "Title": titles[i],
                "Summary": summaries[i],
                "Topics": topics[i],
                "Sentiment": sentiments[i],
            }
            for i in range(len(articles))
        ],
        "Comparative Sentiment Score": {
            "Sentiment Distribution": sentiment_counter,
            "Coverage Differences": [
                {
                    "Comparison": combined[0],
                    "Impact": combined[1]
                }
                for combined in comparative_analysis_result
            ],
            "Topic Overlap": {
                "Common Topics": ['/'.join(str(topic) for topic in topic_groups) for topic_groups in common_topics],
            }
        }
    }

    for i, unique_topics in enumerate(unique_topic_lists):
        result["Comparative Sentiment Score"]["Topic Overlap"][f"Unique Topics in Article {i+1}"] = unique_topics

    final_sentiment_analysis = final_sentiment_analysis_report(sentiment_counter, result["Comparative Sentiment Score"]["Coverage Differences"])
    hindi_audio = text_to_hi_audio(final_sentiment_analysis)

    result["Final Sentiment Analysis"] = final_sentiment_analysis
    result["Audio"] = hindi_audio
    return result
