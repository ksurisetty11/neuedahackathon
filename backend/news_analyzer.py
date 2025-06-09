import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import requests
from typing import List, Dict
from dotenv import load_dotenv
from transformers import pipeline
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

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

def get_price_on_date(symbol: str, date_str: str):
    try:
        # Parse the date string (Alpaca news uses ISO format, e.g., '2025-06-09T13:45:00Z')
        date = pd.to_datetime(date_str).date()
        # Fetch 2 days to ensure we get the previous close
        data = yf.Ticker(symbol).history(start=date - timedelta(days=1), end=date + timedelta(days=1))
        if len(data) == 0:
            return None, None
        # Find the row for the news date (or the previous trading day if news is after market close)
        if str(date) in data.index.astype(str):
            price = data.loc[str(date), 'Close']
        else:
            # Use the last available close before the news date
            price = data['Close'].iloc[-1]
        # Calculate price change from previous close
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else price
        price_change = ((price - prev_close) / prev_close) * 100 if prev_close else 0
        return float(price), float(price_change)
    except Exception as e:
        print(f"Price fetch error: {e}")
        return None, None

def analyze_news_sentiment(symbol: str):
    news_items = fetch_alpaca_news(symbol)
    analyzed = []
    pos_count = 0
    neg_count = 0
    neu_count = 0
    total = 0
    for item in news_items:
        headline = item.get('headline', '')
        # Try to get the published date from Alpaca news (may be 'created_at' or 'published_at')
        date_str = item.get('created_at') or item.get('published_at')
        price, price_change = get_price_on_date(symbol, date_str) if date_str else (None, None)
        sentiment = transformer_sentiment(headline)
        total += 1
        if sentiment == 'positive':
            pos_count += 1
        elif sentiment == 'negative':
            neg_count += 1
        else:
            neu_count += 1
        percent_positive = (pos_count / total * 100) if total else 0
        percent_negative = (neg_count / total * 100) if total else 0
        percent_neutral = (neu_count / total * 100) if total else 0
        analyzed.append({
            'headline': headline,
            'sentiment': sentiment,
            'stats': {
                'positive': percent_positive,
                'negative': percent_negative,
                'neutral': percent_neutral
            },
            'price': price,
            'price_change_pct': price_change,
            'date': date_str
        })
    return analyzed

# Example usage:
if __name__ == "__main__":
    symbol = "AAPL"
    news = analyze_news_sentiment(symbol)
    import json
    print(json.dumps({"news": news}, indent=2))
    with open("news_output.json", "w") as f:
        json.dump({"news": news}, f, indent=2)