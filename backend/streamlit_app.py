import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from news_analyzer import analyze_news_sentiment

st.set_page_config(page_title="Stock News Sentiment Analyzer", layout="wide")
st.title("Stock News Sentiment Analyzer")

symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT, TSLA):", value="AAPL")

if st.button("Analyze News"):
    with st.spinner("Analyzing news and sentiment..."):
        news = analyze_news_sentiment(symbol)
        if not news:
            st.warning("No news found for this ticker.")
        else:
            # Prepare DataFrame for plotting
            df = pd.DataFrame(news)
            df['sentiment_score'] = df['sentiment'].map({'positive': 1, 'neutral': 0, 'negative': -1})
            # Plot price and sentiment
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=df['price'],
                x=df.index,
                mode='lines+markers',
                name='Stock Price',
                yaxis='y1',
                line=dict(color='royalblue')
            ))
            fig.add_trace(go.Scatter(
                y=df['sentiment_score'],
                x=df.index,
                mode='lines+markers',
                name='Sentiment Score',
                yaxis='y2',
                line=dict(color='orange')
            ))
            fig.update_layout(
                title=f"{symbol} Price and News Sentiment Over Headlines",
                xaxis_title="News Item Index (Most Recent to Oldest)",
                yaxis=dict(title='Stock Price', side='left'),
                yaxis2=dict(title='Sentiment Score', overlaying='y', side='right', range=[-1.1, 1.1]),
                legend=dict(x=0.01, y=0.99)
            )
            st.plotly_chart(fig, use_container_width=True)
            # Show news headlines and stats as before
            for idx, item in enumerate(news, 1):
                st.markdown(f"**{idx}. {item['headline']}**")
                col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
                col1.markdown(f"Sentiment: :{'green' if item['sentiment']=='positive' else 'red' if item['sentiment']=='negative' else 'orange'}[{item['sentiment'].capitalize()}]")
                col2.metric("% Positive", f"{item['stats']['positive']:.1f}%")
                col3.metric("% Negative", f"{item['stats']['negative']:.1f}%")
                col4.metric("% Neutral", f"{item['stats']['neutral']:.1f}%")
                col5.metric("Price", f"{item['price'] if item['price'] is not None else 'N/A'}")
                st.divider()
