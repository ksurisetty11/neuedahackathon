from flask import Flask, jsonify, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('output.html')  # Your HTML file from earlier

@app.route('/api/news')
def get_news():
    symbol = request.args.get('symbol', '').lower()
    with open('news_output.json') as f:
        data = json.load(f)
    
    all_news = data.get('news', [])
    
    # Filter based on ticker symbol in the headline
    filtered_news = [item for item in all_news if symbol in item['headline'].lower()]
    
    # Recalculate sentiment stats
    total = len(filtered_news)
    pos = sum(1 for i in filtered_news if i['sentiment'] == 'positive')
    neg = sum(1 for i in filtered_news if i['sentiment'] == 'negative')
    neu = sum(1 for i in filtered_news if i['sentiment'] == 'neutral')
    
    stats = {
        "positive": (pos / total * 100) if total else 0.0,
        "negative": (neg / total * 100) if total else 0.0,
        "neutral": (neu / total * 100) if total else 0.0
    }

    return jsonify(news=filtered_news, stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
