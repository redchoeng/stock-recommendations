"""
일일 주식 추천 웹페이지 생성기 V2
- 눈에 편한 색상
- TOP 5 강조
- 더보기 버튼
- 섹터별 탭
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import sys
sys.path.insert(0, '.')

# 한국 시간대 (UTC+9)
KST = timezone(timedelta(hours=9))

from quant_trading.technical_analyzer_v3 import TechnicalAnalyzerV3
from quant_trading.theme_analyzer import ThemeAnalyzer
from quant_trading.price_recommender import PriceRecommender


def analyze_stock_for_report(ticker):
    """리포트용 종목 분석"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period='2y')

        if df.empty or len(df) < 180:
            return None

        tech_v3 = TechnicalAnalyzerV3(df)
        result_v3 = tech_v3.calculate_total_score()

        theme_analyzer = ThemeAnalyzer(ticker)
        theme_result = theme_analyzer.calculate_total_score()

        info = stock.info
        name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        current_price = df['Close'].iloc[-1]
        previous_close = df['Close'].iloc[-2]
        change_pct = ((current_price - previous_close) / previous_close) * 100

        # 프리마켓/정규장 실시간 가격
        premarket_price = info.get('preMarketPrice')
        premarket_change = info.get('preMarketChangePercent')
        regular_market_price = info.get('regularMarketPrice')
        regular_market_change = info.get('regularMarketChangePercent')

        total_score = result_v3['total_score'] + theme_result['total_score']

        # 가격 추천은 최신 가격 기준
        latest_price = regular_market_price or current_price
        price_rec = PriceRecommender(df, latest_price)
        price_recommendation = price_rec.get_recommendation(strategy='moderate')

        return {
            'ticker': ticker,
            'name': name,
            'sector': sector,
            'current_price': current_price,
            'previous_close': previous_close,
            'change_pct': change_pct,
            'premarket_price': premarket_price,
            'premarket_change': premarket_change,
            'regular_market_price': regular_market_price,
            'regular_market_change': regular_market_change,
            'total_score': total_score,
            'v3_score': result_v3['total_score'],
            'theme_score': theme_result['total_score'],
            'momentum': result_v3['momentum_score'],
            'mean_reversion': result_v3['mean_reversion_score'],
            'trend': result_v3['trend_score'],
            'volatility': result_v3['volatility_score'],
            'signal': result_v3['signals'],
            'theme': theme_result['matched_theme'],
            'price_rec': price_recommendation,
            'news_headlines': theme_result.get('positive_headlines', []),
        }
    except Exception as e:
        print(f"[ERROR] {ticker}: {e}")
        return None


def generate_stock_card_html(stock, idx, is_top5=False):
    """개별 종목 카드 HTML 생성"""
    pr = stock['price_rec']

    badge_class = 'top5' if is_top5 else 'high' if stock['total_score'] >= 60 else 'medium' if stock['total_score'] >= 50 else ''
    change_class = 'positive' if stock['change_pct'] >= 0 else 'negative'
    change_sign = '+' if stock['change_pct'] >= 0 else ''

    top5_badge = f'<span class="top5-label">TOP {idx}</span>' if is_top5 else ''

    return f"""
    <div class="stock-card {'top5-card' if is_top5 else ''}">
        <div class="stock-header">
            <div class="stock-title">
                {top5_badge}
                <span class="rank-badge">#{idx}</span>
                <h2>{stock['name']}</h2>
                <div class="ticker">{stock['ticker']}</div>
                <div class="sector">{stock['sector']} | {stock['theme']}</div>
            </div>
            <div class="score-badge {badge_class}">
                {stock['total_score']:.0f}점
            </div>
        </div>

        <div class="current-price">
            <div class="price-row">
                <span class="price-label">전날 종가:</span>
                <span class="price">${stock['current_price']:.2f}</span>
                <span class="change {change_class}">{change_sign}{stock['change_pct']:.2f}%</span>
            </div>
            {f'''
            <div class="price-row premarket">
                <span class="price-label">프리마켓:</span>
                <span class="price">${stock['premarket_price']:.2f}</span>
                <span class="change {'positive' if stock['premarket_change'] >= 0 else 'negative'}">{'+' if stock['premarket_change'] >= 0 else ''}{stock['premarket_change']:.2f}%</span>
            </div>
            ''' if stock.get('premarket_price') else ''}
            {f'''
            <div class="price-row regular">
                <span class="price-label">현재가:</span>
                <span class="price">${stock['regular_market_price']:.2f}</span>
                <span class="change {'positive' if stock['regular_market_change'] >= 0 else 'negative'}">{'+' if stock['regular_market_change'] >= 0 else ''}{stock['regular_market_change']:.2f}%</span>
            </div>
            ''' if stock.get('regular_market_price') else ''}
        </div>

        <div class="metrics">
            <div class="metric">
                <div class="label">Momentum</div>
                <div class="value">{stock['momentum']}/30</div>
            </div>
            <div class="metric">
                <div class="label">Mean Rev</div>
                <div class="value">{stock['mean_reversion']}/20</div>
            </div>
            <div class="metric">
                <div class="label">Trend</div>
                <div class="value">{stock['trend']}/15</div>
            </div>
            <div class="metric">
                <div class="label">Volatility</div>
                <div class="value">{stock['volatility']}/10</div>
            </div>
            <div class="metric">
                <div class="label">Theme</div>
                <div class="value">{stock['theme_score']}/25</div>
            </div>
        </div>

        <div class="price-section">
            <div class="price-box buy">
                <h3>💰 매수 가격</h3>
                <div class="price-item">
                    <span class="label">추천가</span>
                    <span class="value">${pr['entry']['price']:.2f}</span>
                </div>
                <div class="price-item">
                    <span class="label">공격적</span>
                    <span class="value">${pr['entry']['all_options']['aggressive']:.2f}</span>
                </div>
                <div class="price-item">
                    <span class="label">보수적</span>
                    <span class="value">${pr['entry']['all_options']['conservative']:.2f}</span>
                </div>
            </div>

            <div class="price-box sell">
                <h3>🎯 매도 목표가</h3>
                <div class="price-item">
                    <span class="label">1차 목표</span>
                    <span class="value">${pr['exit']['target_1']:.2f} (+{pr['exit']['expected_profit_1']:.1f}%)</span>
                </div>
                <div class="price-item">
                    <span class="label">2차 목표</span>
                    <span class="value">${pr['exit']['target_2']:.2f} (+{pr['exit']['expected_profit_2']:.1f}%)</span>
                </div>
                <div class="price-item">
                    <span class="label">3차 목표</span>
                    <span class="value">${pr['exit']['target_3']:.2f} (+{pr['exit']['expected_profit_3']:.1f}%)</span>
                </div>
            </div>

            <div class="price-box stop">
                <h3>⚠️ 손절 가격</h3>
                <div class="price-item">
                    <span class="label">추천가</span>
                    <span class="value">${pr['stop_loss']['price']:.2f} ({pr['stop_loss']['expected_loss']:.1f}%)</span>
                </div>
                <div class="price-item">
                    <span class="label">타이트</span>
                    <span class="value">${pr['stop_loss']['all_options']['tight']:.2f}</span>
                </div>
                <div class="price-item">
                    <span class="label">여유</span>
                    <span class="value">${pr['stop_loss']['all_options']['wide']:.2f}</span>
                </div>
            </div>
        </div>

        <div class="signal">
            <div class="label">📡 시그널</div>
            <div class="value">{stock['signal']}</div>
        </div>

        <div class="risk-reward">
            <div>리스크/리워드 비율</div>
            <div class="ratio">{pr['risk_reward_ratio']:.2f}:1</div>
        </div>

        {f'''
        <div class="news-section">
            <div class="news-title">📰 관련 뉴스</div>
            <ul class="news-list">
                {"".join(f'<li>{headline}</li>' for headline in stock.get('news_headlines', [])[:3])}
            </ul>
        </div>
        ''' if stock.get('news_headlines') else ''}
    </div>
    """


def generate_html_report(stocks_data, title="Daily Stock Recommendations"):
    """HTML 리포트 생성"""

    kst_now = datetime.now(KST)
    current_date = kst_now.strftime('%Y년 %m월 %d일')
    current_time = kst_now.strftime('%H:%M:%S')

    stocks_data = sorted(stocks_data, key=lambda x: x['total_score'], reverse=True)

    # 섹터별 그룹화
    sectors = {}
    for stock in stocks_data:
        sector = stock['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)

    # TOP 5와 나머지 분리
    top5_stocks = stocks_data[:5]
    other_stocks = stocks_data[5:]

    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {current_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            padding: 20px;
            min-height: 100vh;
            color: #2d3748;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 15px;
            padding: 35px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .header h1 {{
            color: #1a202c;
            font-size: 2.2em;
            margin-bottom: 8px;
        }}

        .header .subtitle {{
            color: #4a5568;
            font-size: 1em;
        }}

        .header .date {{
            color: #4299e1;
            font-weight: 600;
            margin-top: 10px;
            font-size: 1.1em;
        }}

        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }}

        .tab {{
            background: white;
            border: 2px solid #e2e8f0;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
            color: #4a5568;
        }}

        .tab:hover {{
            border-color: #4299e1;
            color: #4299e1;
        }}

        .tab.active {{
            background: #4299e1;
            border-color: #4299e1;
            color: white;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}

        .summary-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .summary-card .label {{
            color: #718096;
            font-size: 0.85em;
            margin-bottom: 8px;
        }}

        .summary-card .value {{
            color: #2d3748;
            font-size: 1.8em;
            font-weight: bold;
        }}

        .portfolio-calculator {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 25px;
            color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }}

        .portfolio-calculator h2 {{
            margin-bottom: 20px;
            font-size: 1.8em;
        }}

        .calculator-input {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
        }}

        .calculator-input label {{
            display: block;
            color: #2d3748;
            font-weight: 600;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}

        .calculator-input input {{
            width: 100%;
            padding: 15px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1.3em;
            font-weight: bold;
            color: #2d3748;
        }}

        .calculator-input input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .calculate-btn {{
            background: #48bb78;
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .calculate-btn:hover {{
            background: #38a169;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(72, 187, 120, 0.3);
        }}

        .portfolio-result {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 25px;
            color: #2d3748;
            display: none;
        }}

        .portfolio-result.show {{
            display: block;
        }}

        .portfolio-result h3 {{
            margin-bottom: 20px;
            color: #667eea;
            font-size: 1.5em;
        }}

        .portfolio-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        .portfolio-table th {{
            background: #f7fafc;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #e2e8f0;
            font-weight: 600;
            color: #4a5568;
        }}

        .portfolio-table td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
        }}

        .portfolio-table tr:hover {{
            background: #f7fafc;
        }}

        .portfolio-table .ticker {{
            font-weight: bold;
            color: #667eea;
        }}

        .portfolio-table .amount {{
            font-weight: bold;
            color: #48bb78;
        }}

        .section-title {{
            font-size: 1.6em;
            color: #1a202c;
            margin: 30px 0 20px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .section-title::before {{
            content: '';
            width: 4px;
            height: 28px;
            background: #4299e1;
            border-radius: 2px;
        }}

        .stock-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }}

        .stock-card:hover {{
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}

        .top5-card {{
            border: 3px solid #f6ad55;
            background: linear-gradient(to right, #fff, #fffaf0);
        }}

        .top5-label {{
            display: inline-block;
            background: linear-gradient(135deg, #f6ad55 0%, #ed8936 100%);
            color: white;
            padding: 6px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            margin-right: 10px;
        }}

        .stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e2e8f0;
        }}

        .stock-title {{
            flex: 1;
        }}

        .stock-title h2 {{
            color: #1a202c;
            font-size: 1.5em;
            margin-bottom: 5px;
        }}

        .stock-title .ticker {{
            color: #4299e1;
            font-size: 1em;
            font-weight: 600;
        }}

        .stock-title .sector {{
            color: #718096;
            font-size: 0.85em;
            margin-top: 5px;
        }}

        .score-badge {{
            background: #4299e1;
            color: white;
            padding: 12px 25px;
            border-radius: 40px;
            font-size: 1.3em;
            font-weight: bold;
            text-align: center;
            min-width: 90px;
        }}

        .score-badge.top5 {{
            background: linear-gradient(135deg, #f6ad55 0%, #ed8936 100%);
            font-size: 1.5em;
        }}

        .score-badge.high {{
            background: #48bb78;
        }}

        .score-badge.medium {{
            background: #4299e1;
        }}

        .current-price {{
            margin-bottom: 20px;
        }}

        .price-row {{
            display: flex;
            align-items: baseline;
            gap: 12px;
            margin-bottom: 8px;
        }}

        .price-row.premarket {{
            opacity: 0.9;
            border-left: 3px solid #4299e1;
            padding-left: 8px;
        }}

        .price-row.regular {{
            opacity: 1;
            border-left: 3px solid #48bb78;
            padding-left: 8px;
            font-weight: 600;
        }}

        .price-label {{
            font-size: 0.9em;
            color: #718096;
            min-width: 90px;
        }}

        .current-price .price {{
            font-size: 1.5em;
            font-weight: bold;
            color: #1a202c;
        }}

        .current-price .change {{
            font-size: 1.0em;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 15px;
        }}

        .current-price .change.positive {{
            background: #c6f6d5;
            color: #22543d;
        }}

        .current-price .change.negative {{
            background: #fed7d7;
            color: #742a2a;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }}

        .metric {{
            background: #f7fafc;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }}

        .metric .label {{
            color: #718096;
            font-size: 0.75em;
            margin-bottom: 6px;
        }}

        .metric .value {{
            color: #2d3748;
            font-size: 1.2em;
            font-weight: bold;
        }}

        .price-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}

        .price-box {{
            background: #f7fafc;
            border-radius: 12px;
            padding: 18px;
            border: 2px solid #e2e8f0;
        }}

        .price-box.buy {{
            border-color: #4299e1;
            background: #ebf8ff;
        }}

        .price-box.sell {{
            border-color: #9f7aea;
            background: #faf5ff;
        }}

        .price-box.stop {{
            border-color: #fc8181;
            background: #fff5f5;
        }}

        .price-box h3 {{
            color: #2d3748;
            margin-bottom: 12px;
            font-size: 1em;
        }}

        .price-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }}

        .price-item:last-child {{
            border-bottom: none;
        }}

        .price-item .label {{
            color: #4a5568;
            font-weight: 500;
            font-size: 0.9em;
        }}

        .price-item .value {{
            color: #1a202c;
            font-weight: bold;
        }}

        .signal {{
            background: #edf2f7;
            padding: 12px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 3px solid #4299e1;
        }}

        .signal .label {{
            color: #718096;
            font-size: 0.85em;
            margin-bottom: 6px;
        }}

        .signal .value {{
            color: #2d3748;
            font-weight: 500;
            line-height: 1.5;
        }}

        .risk-reward {{
            background: #fff5f5;
            border: 2px solid #fc8181;
            border-radius: 8px;
            padding: 12px;
            margin-top: 15px;
            text-align: center;
        }}

        .risk-reward .ratio {{
            font-size: 1.3em;
            font-weight: bold;
            color: #c53030;
        }}

        .show-more-btn {{
            display: block;
            width: 100%;
            max-width: 400px;
            margin: 30px auto;
            padding: 15px 30px;
            background: white;
            border: 2px solid #4299e1;
            color: #4299e1;
            font-size: 1.1em;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .show-more-btn:hover {{
            background: #4299e1;
            color: white;
        }}

        #other-stocks {{
            display: none;
        }}

        #other-stocks.show {{
            display: block;
        }}

        .footer {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            color: #718096;
            margin-top: 30px;
            font-size: 0.9em;
        }}

        .rank-badge {{
            display: inline-block;
            background: #edf2f7;
            color: #4a5568;
            padding: 4px 12px;
            border-radius: 15px;
            font-weight: 600;
            margin-right: 8px;
            font-size: 0.9em;
        }}

        /* 검색 박스 스타일 */
        .search-box {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            position: relative;
        }}

        .search-box input {{
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1.1em;
            box-sizing: border-box;
            transition: all 0.3s;
        }}

        .search-box input:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        .search-results {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border-radius: 0 0 12px 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-height: 400px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        }}

        .search-results.show {{
            display: block;
        }}

        .search-result-item {{
            padding: 15px 20px;
            border-bottom: 1px solid #e2e8f0;
            cursor: pointer;
            transition: background 0.2s;
        }}

        .search-result-item:hover {{
            background: #f7fafc;
        }}

        .search-result-item:last-child {{
            border-bottom: none;
        }}

        .search-result-ticker {{
            font-weight: 700;
            color: #2d3748;
            font-size: 1.1em;
        }}

        .search-result-name {{
            color: #718096;
            font-size: 0.9em;
            margin-left: 10px;
        }}

        .search-result-score {{
            float: right;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 15px;
        }}

        .search-result-score.high {{
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
        }}

        .search-result-score.medium {{
            background: linear-gradient(135deg, #ecc94b, #d69e2e);
            color: white;
        }}

        .search-result-score.low {{
            background: #e2e8f0;
            color: #718096;
        }}

        .no-results {{
            padding: 20px;
            text-align: center;
            color: #a0aec0;
        }}

        /* 뉴스 섹션 스타일 */
        .news-section {{
            margin-top: 20px;
            padding: 15px;
            background: linear-gradient(135deg, #f7fafc, #edf2f7);
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}

        .news-title {{
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 12px;
            font-size: 1em;
        }}

        .news-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .news-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
            color: #4a5568;
            font-size: 0.9em;
            line-height: 1.5;
        }}

        .news-list li:last-child {{
            border-bottom: none;
        }}

        .news-list li:before {{
            content: "•";
            color: #667eea;
            margin-right: 8px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Daily Stock Recommendations</h1>
            <div class="subtitle">검증된 퀀트 전략 기반 매수/매도 가격 추천</div>
            <div class="date">{current_date} {current_time} 업데이트</div>
        </div>

        <!-- 종목 검색 -->
        <div class="search-box">
            <input type="text" id="stockSearch" placeholder="🔍 종목 검색 (티커 또는 종목명)" onkeyup="searchStocks()">
            <div id="searchResults" class="search-results"></div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <div class="label">분석 종목 수</div>
                <div class="value">{len(stocks_data)}개</div>
            </div>
            <div class="summary-card">
                <div class="label">평균 점수</div>
                <div class="value">{sum(s['total_score'] for s in stocks_data) / len(stocks_data):.1f}</div>
            </div>
            <div class="summary-card">
                <div class="label">추천 종목 (60점 이상)</div>
                <div class="value">{sum(1 for s in stocks_data if s['total_score'] >= 60)}개</div>
            </div>
            <div class="summary-card">
                <div class="label">최고 점수</div>
                <div class="value">{max(s['total_score'] for s in stocks_data):.0f}점</div>
            </div>
        </div>

        <!-- 포트폴리오 계산기 -->
        <div class="portfolio-calculator">
            <h2>💰 포트폴리오 계산기</h2>
            <p style="margin-bottom: 20px; opacity: 0.95;">시드머니를 입력하면 TOP 10 종목의 점수 기반 포트폴리오 구성을 확인할 수 있습니다</p>

            <div class="calculator-input">
                <label for="seedMoney">💵 투자 금액 (USD)</label>
                <input type="number" id="seedMoney" placeholder="예: 10000" min="100" step="100">
            </div>

            <button class="calculate-btn" onclick="calculatePortfolio()">📊 포트폴리오 계산하기</button>

            <div id="portfolioResult" class="portfolio-result">
                <h3>📈 추천 포트폴리오 구성</h3>
                <div id="portfolioContent"></div>
            </div>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="showTab('all')">전체</div>
"""

    # 섹터 탭 생성
    for sector in sorted(sectors.keys()):
        if sector != 'N/A':
            html += f'            <div class="tab" onclick="showTab(\'{sector}\')">{sector} ({len(sectors[sector])})</div>\n'

    html += """
        </div>

        <div id="tab-all" class="tab-content active">
            <h2 class="section-title">🏆 TOP 5 추천 종목</h2>
"""

    # TOP 5 종목 카드
    for idx, stock in enumerate(top5_stocks, 1):
        html += generate_stock_card_html(stock, idx, is_top5=True)

    html += f"""
            <button class="show-more-btn" onclick="toggleOtherStocks()">
                <span id="show-more-text">▼ 나머지 {len(other_stocks)}개 종목 보기</span>
            </button>

            <div id="other-stocks">
                <h2 class="section-title">📋 기타 종목</h2>
"""

    # 나머지 종목 카드
    for idx, stock in enumerate(other_stocks, 6):
        html += generate_stock_card_html(stock, idx, is_top5=False)

    html += """
            </div>
        </div>
"""

    # 섹터별 탭 컨텐츠
    for sector, sector_stocks in sorted(sectors.items()):
        if sector != 'N/A':
            html += f'        <div id="tab-{sector}" class="tab-content">\n'
            html += f'            <h2 class="section-title">{sector} 섹터 ({len(sector_stocks)}개)</h2>\n'

            # 섹터 내에서도 점수순 정렬
            sector_stocks_sorted = sorted(sector_stocks, key=lambda x: x['total_score'], reverse=True)
            for idx, stock in enumerate(sector_stocks_sorted, 1):
                html += generate_stock_card_html(stock, idx, is_top5=False)

            html += '        </div>\n'

    html += """
        <div class="footer">
            <p><strong>※ 면책 조항</strong></p>
            <p>본 리포트는 투자 참고 자료이며, 투자 판단 및 결과에 대한 책임은 투자자 본인에게 있습니다.</p>
            <p>손절가는 반드시 지켜서 리스크를 관리하시기 바랍니다.</p>
            <p style="margin-top: 15px; color: #a0aec0;">
                Powered by 검증된 퀀트 전략 (Jegadeesh & Titman 1993, De Bondt & Thaler 1985, Hurst et al. 2013)
            </p>
        </div>
    </div>

    <script>
        // 검색용 전체 종목 데이터
        const allStocksData = """ + str([{
            'ticker': s['ticker'],
            'name': s['name'],
            'total_score': s['total_score'],
            'current_price': s.get('regular_market_price') or s['current_price'],
            'sector': s.get('sector', 'N/A'),
            'entry': s['price_rec']['entry']['price'],
            'target_1': s['price_rec']['exit']['target_1'],
            'stop_loss': s['price_rec']['stop_loss']['price'],
        } for s in stocks_data]).replace("'", '"') + """;

        function searchStocks() {
            const query = document.getElementById('stockSearch').value.toUpperCase().trim();
            const resultsDiv = document.getElementById('searchResults');

            if (query.length === 0) {
                resultsDiv.classList.remove('show');
                return;
            }

            const matches = allStocksData.filter(s =>
                s.ticker.toUpperCase().includes(query) ||
                s.name.toUpperCase().includes(query)
            );

            if (matches.length === 0) {
                resultsDiv.innerHTML = '<div class="no-results">검색 결과가 없습니다</div>';
            } else {
                let html = '';
                matches.forEach(s => {
                    const scoreClass = s.total_score >= 60 ? 'high' : s.total_score >= 50 ? 'medium' : 'low';
                    const grade = s.total_score >= 70 ? '강력추천' : s.total_score >= 60 ? '추천' : s.total_score >= 50 ? '관망' : '비추천';
                    html += `
                        <div class="search-result-item" onclick="showStockDetail('${s.ticker}')">
                            <span class="search-result-ticker">${s.ticker}</span>
                            <span class="search-result-name">${s.name}</span>
                            <span class="search-result-score ${scoreClass}">${s.total_score.toFixed(0)}점 ${grade}</span>
                            <div style="clear:both; margin-top: 8px; font-size: 0.85em; color: #718096;">
                                매수가: $${s.entry.toFixed(2)} | 목표가: $${s.target_1.toFixed(2)} | 손절가: $${s.stop_loss.toFixed(2)}
                            </div>
                        </div>
                    `;
                });
                resultsDiv.innerHTML = html;
            }
            resultsDiv.classList.add('show');
        }

        function showStockDetail(ticker) {
            // 해당 종목 카드로 스크롤
            const cards = document.querySelectorAll('.stock-card');
            for (const card of cards) {
                if (card.querySelector('.ticker')?.textContent === ticker) {
                    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    card.style.boxShadow = '0 0 0 3px #667eea';
                    setTimeout(() => { card.style.boxShadow = ''; }, 2000);
                    break;
                }
            }
            document.getElementById('searchResults').classList.remove('show');
            document.getElementById('stockSearch').value = '';
        }

        // 검색창 외부 클릭 시 결과 숨기기
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-box')) {
                document.getElementById('searchResults').classList.remove('show');
            }
        });

        function showTab(tabName) {
            // 모든 탭 컨텐츠 숨기기
            var contents = document.getElementsByClassName('tab-content');
            for (var i = 0; i < contents.length; i++) {
                contents[i].classList.remove('active');
            }

            // 모든 탭 버튼 비활성화
            var tabs = document.getElementsByClassName('tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }

            // 선택한 탭 표시
            if (tabName === 'all') {
                document.getElementById('tab-all').classList.add('active');
                event.target.classList.add('active');
            } else {
                document.getElementById('tab-' + tabName).classList.add('active');
                event.target.classList.add('active');
            }
        }

        function toggleOtherStocks() {
            var otherStocks = document.getElementById('other-stocks');
            var showMoreText = document.getElementById('show-more-text');

            if (otherStocks.classList.contains('show')) {
                otherStocks.classList.remove('show');
                showMoreText.textContent = '▼ 나머지 """ + str(len(other_stocks)) + """개 종목 보기';
            } else {
                otherStocks.classList.add('show');
                showMoreText.textContent = '▲ 접기';
            }
        }

        // 포트폴리오 계산 함수
        const stocksData = """ + str([{
            'ticker': s['ticker'],
            'name': s['name'],
            'total_score': s['total_score'],
            'current_price': s.get('regular_market_price') or s['current_price'],
        } for s in stocks_data[:10]]).replace("'", '"') + """;

        function calculatePortfolio() {
            const seedMoney = parseFloat(document.getElementById('seedMoney').value);

            if (!seedMoney || seedMoney < 100) {
                alert('투자 금액을 100 USD 이상 입력해주세요.');
                return;
            }

            // TOP 10 종목만 사용
            const topStocks = stocksData.slice(0, 10);

            // 점수 기반 가중치 계산
            const totalScore = topStocks.reduce((sum, stock) => sum + stock.total_score, 0);

            let portfolioHTML = '<table class="portfolio-table">';
            portfolioHTML += '<thead><tr>';
            portfolioHTML += '<th>순위</th>';
            portfolioHTML += '<th>티커</th>';
            portfolioHTML += '<th>종목명</th>';
            portfolioHTML += '<th>점수</th>';
            portfolioHTML += '<th>배분 비율</th>';
            portfolioHTML += '<th>투자 금액</th>';
            portfolioHTML += '<th>현재가</th>';
            portfolioHTML += '<th>매수 수량</th>';
            portfolioHTML += '</tr></thead><tbody>';

            let totalAllocated = 0;

            topStocks.forEach((stock, index) => {
                const weight = (stock.total_score / totalScore) * 100;
                const allocation = seedMoney * (stock.total_score / totalScore);
                const shares = Math.floor(allocation / stock.current_price);
                const actualInvestment = shares * stock.current_price;

                totalAllocated += actualInvestment;

                portfolioHTML += '<tr>';
                portfolioHTML += `<td>${index + 1}</td>`;
                portfolioHTML += `<td class="ticker">${stock.ticker}</td>`;
                portfolioHTML += `<td>${stock.name}</td>`;
                portfolioHTML += `<td>${stock.total_score.toFixed(1)}</td>`;
                portfolioHTML += `<td>${weight.toFixed(1)}%</td>`;
                portfolioHTML += `<td class="amount">$${actualInvestment.toFixed(2)}</td>`;
                portfolioHTML += `<td>$${stock.current_price.toFixed(2)}</td>`;
                portfolioHTML += `<td><strong>${shares}</strong>주</td>`;
                portfolioHTML += '</tr>';
            });

            portfolioHTML += '</tbody></table>';

            const remaining = seedMoney - totalAllocated;

            portfolioHTML += `<div style="margin-top: 20px; padding: 15px; background: #f7fafc; border-radius: 8px;">`;
            portfolioHTML += `<div style="font-size: 1.2em; margin-bottom: 10px;"><strong>📊 투자 요약</strong></div>`;
            portfolioHTML += `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">`;
            portfolioHTML += `<div><span style="color: #718096;">총 투자 금액:</span> <strong style="color: #2d3748;">$${seedMoney.toFixed(2)}</strong></div>`;
            portfolioHTML += `<div><span style="color: #718096;">실제 투자액:</span> <strong style="color: #48bb78;">$${totalAllocated.toFixed(2)}</strong></div>`;
            portfolioHTML += `<div><span style="color: #718096;">잔액:</span> <strong style="color: #ed8936;">$${remaining.toFixed(2)}</strong></div>`;
            portfolioHTML += `<div><span style="color: #718096;">포트폴리오 구성:</span> <strong style="color: #667eea;">${topStocks.length}개 종목</strong></div>`;
            portfolioHTML += `</div></div>`;

            document.getElementById('portfolioContent').innerHTML = portfolioHTML;
            document.getElementById('portfolioResult').classList.add('show');

            // 결과로 스크롤
            document.getElementById('portfolioResult').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    </script>
</body>
</html>
"""

    return html


def main():
    """메인 함수"""
    print("일일 주식 추천 리포트 생성 중...\n")

    tickers = [
        'NVDA', 'AMD', 'AVGO', 'QCOM', 'MU',
        'MSFT', 'GOOGL', 'META', 'AAPL', 'AMZN',
        'XOM', 'CVX', 'COP',
        'LMT', 'RTX', 'NOC', 'GD',
        'JPM', 'BAC', 'GS', 'WFC',
    ]

    print(f"분석 중: {len(tickers)}개 종목\n")

    stocks_data = []
    for idx, ticker in enumerate(tickers, 1):
        print(f"[{idx}/{len(tickers)}] {ticker}... ", end='', flush=True)
        result = analyze_stock_for_report(ticker)
        if result:
            stocks_data.append(result)
            print(f"완료 (점수: {result['total_score']:.0f})")
        else:
            print("실패")

    if stocks_data:
        print(f"\n총 {len(stocks_data)}개 종목 분석 완료!")

        # 50점 이하 종목 제외
        before_filter = len(stocks_data)
        stocks_data = [s for s in stocks_data if s['total_score'] >= 50]
        filtered_out = before_filter - len(stocks_data)
        if filtered_out > 0:
            print(f"[제외] {filtered_out}개 종목 제외 (50점 미만)")
        print(f"[추천 대상] {len(stocks_data)}개 종목")

        html_content = generate_html_report(stocks_data)

        filename = f"daily_stock_report_{datetime.now(KST).strftime('%Y%m%d')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n리포트 생성 완료: {filename}")
        print(f"파일 위치: {filename}")

        import webbrowser
        import os
        webbrowser.open('file://' + os.path.abspath(filename))

    else:
        print("\n분석된 종목이 없습니다.")


if __name__ == '__main__':
    main()
