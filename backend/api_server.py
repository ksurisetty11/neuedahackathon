from flask import Flask, request, jsonify
from news_analyzer import analyze_news_sentiment
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/news')
def get_news():
    symbol = request.args.get('symbol', 'AAPL')
    news, stats = analyze_news_sentiment(symbol)
    return jsonify({'news': news, 'stats': stats})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
