"""
일일 주식 추천 웹페이지 생성기
매일 업데이트되는 매수/매도 가격 추천 리포트
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, '.')

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

        # V3 퀀트 분석
        tech_v3 = TechnicalAnalyzerV3(df)
        result_v3 = tech_v3.calculate_total_score()

        # 테마 분석
        theme_analyzer = ThemeAnalyzer(ticker)
        theme_result = theme_analyzer.calculate_total_score()

        # 종목 정보
        info = stock.info
        name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        current_price = df['Close'].iloc[-1]
        change_pct = ((current_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100

        # 총점
        total_score = result_v3['total_score'] + theme_result['total_score']

        # 가격 추천
        price_rec = PriceRecommender(df, current_price)
        price_recommendation = price_rec.get_recommendation(strategy='moderate')

        return {
            'ticker': ticker,
            'name': name,
            'sector': sector,
            'current_price': current_price,
            'change_pct': change_pct,
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
        }
    except Exception as e:
        print(f"[ERROR] {ticker}: {e}")
        return None


def generate_html_report(stocks_data, title="Daily Stock Recommendations"):
    """HTML 리포트 생성"""

    current_date = datetime.now().strftime('%Y년 %m월 %d일')
    current_time = datetime.now().strftime('%H:%M:%S')

    # 점수별로 정렬
    stocks_data = sorted(stocks_data, key=lambda x: x['total_score'], reverse=True)

    # 섹터별로 그룹화
    sectors = {}
    for stock in stocks_data:
        sector = stock['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)

    # HTML 템플릿
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
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            color: #2d3748;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: #718096;
            font-size: 1.1em;
        }}

        .header .date {{
            color: #667eea;
            font-weight: bold;
            margin-top: 10px;
            font-size: 1.2em;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .summary-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}

        .summary-card:hover {{
            transform: translateY(-5px);
        }}

        .summary-card .label {{
            color: #718096;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}

        .summary-card .value {{
            color: #2d3748;
            font-size: 2em;
            font-weight: bold;
        }}

        .stock-card {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .stock-card:hover {{
            box-shadow: 0 15px 50px rgba(0,0,0,0.15);
            transform: translateY(-3px);
        }}

        .stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
        }}

        .stock-title {{
            flex: 1;
        }}

        .stock-title h2 {{
            color: #2d3748;
            font-size: 1.8em;
            margin-bottom: 5px;
        }}

        .stock-title .ticker {{
            color: #667eea;
            font-size: 1.1em;
            font-weight: bold;
        }}

        .stock-title .sector {{
            color: #718096;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .score-badge {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
            min-width: 100px;
        }}

        .score-badge.high {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}

        .score-badge.medium {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}

        .current-price {{
            display: flex;
            align-items: baseline;
            gap: 15px;
            margin-bottom: 25px;
        }}

        .current-price .price {{
            font-size: 2em;
            font-weight: bold;
            color: #2d3748;
        }}

        .current-price .change {{
            font-size: 1.2em;
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
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
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}

        .metric {{
            background: #f7fafc;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}

        .metric .label {{
            color: #718096;
            font-size: 0.8em;
            margin-bottom: 8px;
        }}

        .metric .value {{
            color: #2d3748;
            font-size: 1.3em;
            font-weight: bold;
        }}

        .price-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }}

        .price-box {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 20px;
        }}

        .price-box.buy {{
            background: linear-gradient(135deg, #e0f7fa 0%, #80deea 100%);
        }}

        .price-box.sell {{
            background: linear-gradient(135deg, #f3e5f5 0%, #ce93d8 100%);
        }}

        .price-box.stop {{
            background: linear-gradient(135deg, #ffebee 0%, #ef9a9a 100%);
        }}

        .price-box h3 {{
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}

        .price-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        }}

        .price-item:last-child {{
            border-bottom: none;
        }}

        .price-item .label {{
            color: #4a5568;
            font-weight: 500;
        }}

        .price-item .value {{
            color: #2d3748;
            font-weight: bold;
            font-size: 1.1em;
        }}

        .signal {{
            background: #edf2f7;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            border-left: 4px solid #667eea;
        }}

        .signal .label {{
            color: #718096;
            font-size: 0.9em;
            margin-bottom: 8px;
        }}

        .signal .value {{
            color: #2d3748;
            font-weight: 500;
            line-height: 1.6;
        }}

        .risk-reward {{
            background: #fff5f5;
            border: 2px solid #fc8181;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            text-align: center;
        }}

        .risk-reward .ratio {{
            font-size: 1.5em;
            font-weight: bold;
            color: #c53030;
        }}

        .footer {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: #718096;
            margin-top: 30px;
        }}

        .rank-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            color: #744210;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-right: 10px;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .stock-card {{
                page-break-inside: avoid;
            }}
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
"""

    # 각 종목 카드 생성
    for idx, stock in enumerate(stocks_data, 1):
        pr = stock['price_rec']

        # 점수에 따른 뱃지 클래스
        badge_class = 'high' if stock['total_score'] >= 60 else 'medium' if stock['total_score'] >= 50 else ''

        # 가격 변동에 따른 클래스
        change_class = 'positive' if stock['change_pct'] >= 0 else 'negative'
        change_sign = '+' if stock['change_pct'] >= 0 else ''

        html += f"""
        <div class="stock-card">
            <div class="stock-header">
                <div class="stock-title">
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
                <span class="price">${stock['current_price']:.2f}</span>
                <span class="change {change_class}">{change_sign}{stock['change_pct']:.2f}%</span>
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
        </div>
"""

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
</body>
</html>
"""

    return html


def main():
    """메인 함수"""
    print("일일 주식 추천 리포트 생성 중...\n")

    # 분석할 종목 리스트
    tickers = [
        # 반도체/AI
        'NVDA', 'AMD', 'AVGO', 'QCOM', 'MU',
        # 빅테크
        'MSFT', 'GOOGL', 'META', 'AAPL', 'AMZN',
        # 에너지
        'XOM', 'CVX', 'COP',
        # 방산
        'LMT', 'RTX', 'NOC', 'GD',
        # 금융
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

        # HTML 생성
        html_content = generate_html_report(stocks_data)

        # 파일 저장
        filename = f"daily_stock_report_{datetime.now().strftime('%Y%m%d')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n✅ 리포트 생성 완료: {filename}")
        print(f"📁 파일 위치: {filename}")
        print(f"\n브라우저에서 열기: file:///{filename}")

        # 자동으로 브라우저에서 열기 (옵션)
        import webbrowser
        import os
        webbrowser.open('file://' + os.path.abspath(filename))

    else:
        print("\n❌ 분석된 종목이 없습니다.")


if __name__ == '__main__':
    main()
