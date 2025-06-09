import os
import requests
from typing import List, Dict
from dotenv import load_dotenv
from transformers import pipeline

# Load environment variables from .env file
load_dotenv()

# Load sentiment analysis pipeline once, explicitly using PyTorch
sentiment_pipeline = pipeline("sentiment-analysis", framework="pt")

def transformer_sentiment(text: str) -> str:
    result = sentiment_pipeline(text)[0]
    label = result["label"].lower()
    if "positive" in label:
        return "positive"
    elif "negative" in label:
        return "negative"
    else:
        return "neutral"

def fetch_alpaca_news(symbol: str, limit: int = 50) -> List[Dict]:
    api_key = os.getenv('ALPACA_API_KEY', 'YOUR_ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_API_SECRET', 'YOUR_ALPACA_API_SECRET')
    print(f"Loaded API Key: {api_key}")  # Debug: show loaded API key
    url = f'https://data.alpaca.markets/v1beta1/news?symbols={symbol}&limit={limit}'
    headers = {
        'Apca-Api-Key-Id': api_key,
        'Apca-Api-Secret-Key': api_secret
    }
    response = requests.get(url, headers=headers)
    print(f"API Response Status: {response.status_code}")  # Debug: show status code
    if response.status_code == 200:
        news = response.json().get('news', [])
        print(f"Fetched {len(news)} news items.")  # Debug: show number of news items
        return news
    else:
        print(f"API Error: {response.text}")  # Debug: show error message
        return []

def analyze_news_sentiment(symbol: str) -> List[Dict]:
    news_items = fetch_alpaca_news(symbol)
    analyzed = []
    pos_count = 0
    neg_count = 0
    neu_count = 0
    for idx, item in enumerate(news_items, 1):
        headline = item.get('headline', '')
        sentiment = transformer_sentiment(headline)
        analyzed.append({
            'headline': headline,
            'sentiment': sentiment
        })
        if sentiment == 'positive':
            pos_count += 1
        elif sentiment == 'negative':
            neg_count += 1
        else:
            neu_count += 1
        total = idx
        percent_positive = (pos_count / total * 100) if total else 0
        percent_negative = (neg_count / total * 100) if total else 0
        percent_neutral = (neu_count / total * 100) if total else 0
        print(f"{headline} => {sentiment} | Stats so far: Positive: {percent_positive:.1f}% | Negative: {percent_negative:.1f}% | Neutral: {percent_neutral:.1f}%")
    return analyzed

# Example usage:
if __name__ == "__main__":
    symbol = "AAPL"
    results = analyze_news_sentiment(symbol)
    for r in results:
        print(f"{r['headline']} => {r['sentiment']}")