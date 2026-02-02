"""
뉴스 감성 분석기 (US Stocks)
StockNews 방식을 미국 주식에 적용
"""

import yfinance as yf
from datetime import datetime, timedelta
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
import time


class NewsSentimentAnalyzer:
    """
    미국 주식 뉴스 감성 분석 (20점 만점)
    - Yahoo Finance 뉴스 활용
    - TextBlob 감성 분석
    - 최근 7일 뉴스 분석
    """

    def __init__(self, ticker):
        self.ticker = ticker
        self.news_items = []

    def fetch_news(self):
        """Yahoo Finance에서 뉴스 가져오기"""
        try:
            stock = yf.Ticker(self.ticker)
            news = stock.news

            if not news:
                return []

            # 최근 7일 뉴스만
            week_ago = datetime.now() - timedelta(days=7)
            recent_news = []

            for item in news[:20]:  # 최대 20개
                try:
                    pub_date = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                    if pub_date >= week_ago:
                        recent_news.append({
                            'title': item.get('title', ''),
                            'publisher': item.get('publisher', ''),
                            'link': item.get('link', ''),
                            'date': pub_date
                        })
                except:
                    continue

            self.news_items = recent_news
            return recent_news

        except Exception as e:
            print(f"  News fetch error for {self.ticker}: {e}")
            return []

    def analyze_sentiment(self, text):
        """
        TextBlob으로 감성 분석
        Returns: -1.0 (매우 부정) ~ +1.0 (매우 긍정)
        """
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
            return sentiment
        except:
            return 0.0

    def calculate_news_score(self):
        """
        뉴스 감성 점수 계산 (20점 만점)

        채점 기준:
        - 뉴스 개수: 최대 5점 (많을수록 관심도 높음)
        - 평균 감성: 최대 10점 (긍정적일수록 높음)
        - 긍정 뉴스 비율: 최대 5점
        """
        news = self.fetch_news()

        if not news:
            return {
                'total_score': 0,
                'news_count': 0,
                'avg_sentiment': 0,
                'positive_ratio': 0,
                'details': []
            }

        # 1. 뉴스 개수 점수 (5점)
        news_count_score = min(len(news) / 10 * 5, 5)  # 10개 이상이면 만점

        # 2. 각 뉴스 감성 분석
        sentiments = []
        details = []

        for item in news:
            sentiment = self.analyze_sentiment(item['title'])
            sentiments.append(sentiment)
            details.append({
                'title': item['title'],
                'sentiment': sentiment,
                'date': item['date'].strftime('%Y-%m-%d')
            })

        # 3. 평균 감성 점수 (10점)
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        # -1~+1 범위를 0~10으로 변환
        avg_sentiment_score = (avg_sentiment + 1) / 2 * 10

        # 4. 긍정 뉴스 비율 점수 (5점)
        positive_count = sum(1 for s in sentiments if s > 0.1)
        positive_ratio = positive_count / len(sentiments) if sentiments else 0
        positive_ratio_score = positive_ratio * 5

        # 총점
        total_score = news_count_score + avg_sentiment_score + positive_ratio_score

        return {
            'total_score': round(total_score, 1),
            'news_count': len(news),
            'news_count_score': round(news_count_score, 1),
            'avg_sentiment': round(avg_sentiment, 3),
            'avg_sentiment_score': round(avg_sentiment_score, 1),
            'positive_ratio': round(positive_ratio, 2),
            'positive_ratio_score': round(positive_ratio_score, 1),
            'details': details[:5]  # 최근 5개만
        }


# 고급 버전: FinancialModelingPrep API 사용 (무료 250 calls/day)
class AdvancedNewsSentimentAnalyzer:
    """
    더 많은 뉴스 소스 활용 (옵션)
    - FinancialModelingPrep API
    - 무료: 250 calls/day
    - 더 많은 뉴스 소스 (Bloomberg, CNBC, etc.)
    """

    def __init__(self, ticker, api_key=None):
        self.ticker = ticker
        self.api_key = api_key or "demo"  # demo key for testing
        self.base_url = "https://financialmodelingprep.com/api/v3"

    def fetch_news(self):
        """FMP API로 뉴스 가져오기"""
        try:
            url = f"{self.base_url}/stock_news?tickers={self.ticker}&limit=50&apikey={self.api_key}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                news_data = response.json()

                # 최근 7일
                week_ago = datetime.now() - timedelta(days=7)
                recent_news = []

                for item in news_data:
                    try:
                        pub_date = datetime.strptime(item['publishedDate'], '%Y-%m-%d %H:%M:%S')
                        if pub_date >= week_ago:
                            recent_news.append({
                                'title': item.get('title', ''),
                                'text': item.get('text', ''),
                                'site': item.get('site', ''),
                                'date': pub_date
                            })
                    except:
                        continue

                return recent_news

            return []

        except Exception as e:
            print(f"  FMP API error: {e}")
            return []

    def analyze_sentiment(self, text):
        """감성 분석"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0

    def calculate_news_score(self):
        """뉴스 점수 계산 (본문 포함)"""
        news = self.fetch_news()

        if not news:
            return {'total_score': 0, 'news_count': 0}

        sentiments = []
        for item in news:
            # 제목 + 본문 모두 분석
            full_text = f"{item['title']} {item.get('text', '')}"
            sentiment = self.analyze_sentiment(full_text)
            sentiments.append(sentiment)

        # 점수 계산 (Basic 버전과 동일)
        news_count_score = min(len(news) / 15 * 5, 5)
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        avg_sentiment_score = (avg_sentiment + 1) / 2 * 10
        positive_ratio = sum(1 for s in sentiments if s > 0.1) / len(sentiments)
        positive_ratio_score = positive_ratio * 5

        total_score = news_count_score + avg_sentiment_score + positive_ratio_score

        return {
            'total_score': round(total_score, 1),
            'news_count': len(news),
            'avg_sentiment': round(avg_sentiment, 3),
            'positive_ratio': round(positive_ratio, 2)
        }


if __name__ == '__main__':
    # 테스트
    print("=" * 60)
    print("         News Sentiment Analyzer Test")
    print("=" * 60)
    print()

    test_tickers = ['AAPL', 'NVDA', 'TSLA']

    for ticker in test_tickers:
        print(f"\n[{ticker}]")
        print("-" * 40)

        analyzer = NewsSentimentAnalyzer(ticker)
        result = analyzer.calculate_news_score()

        print(f"Total Score:     {result['total_score']}/20")
        print(f"News Count:      {result['news_count']} ({result.get('news_count_score', 0)}/5)")
        print(f"Avg Sentiment:   {result['avg_sentiment']:.3f} ({result.get('avg_sentiment_score', 0)}/10)")
        print(f"Positive Ratio:  {result['positive_ratio']:.0%} ({result.get('positive_ratio_score', 0)}/5)")

        if result['details']:
            print("\nRecent News:")
            for i, news in enumerate(result['details'][:3], 1):
                sentiment_emoji = "+" if news['sentiment'] > 0 else "-" if news['sentiment'] < 0 else "o"
                print(f"  [{sentiment_emoji}] {news['title'][:60]}...")

        time.sleep(1)  # API 제한 방지

    print("\n" + "=" * 60)
