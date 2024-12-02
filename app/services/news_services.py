import requests
from flask import current_app
import random

def fetch_latest_news():
    api_key = 'c837c86742e740c18ddc42ecfb52852e'
    # Query for relevant topics
    query = "education OR technology OR health OR sport"
    url = f'https://newsapi.org/v2/everything?q={query}&language=en&apiKey={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        news_data = response.json()
        return news_data.get('articles', [])
    except Exception as e:
        current_app.logger.error(f'Error fetching news: {str(e)}')
        return []

def get_random_news():
    all_news = fetch_latest_news()
    # Filter for articles with images
    filtered_news = [article for article in all_news if article.get('urlToImage')]
    # Limit to 16 random articles
    return random.sample(filtered_news, min(len(filtered_news), 16))
