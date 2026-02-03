#!/usr/bin/env python3
"""Value Stocks Report Generator - Detailed Analysis Version"""

import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

VALUE_TICKERS = [
    # 금융
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BRK-B', 'V', 'MA', 'AXP',
    # 헬스케어
    'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT', 'BMY', 'CVS',
    # 소비재
    'PG', 'KO', 'PEP', 'WMT', 'COST', 'TGT', 'CL', 'GIS', 'K', 'MO',
    # 에너지
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'VLO', 'PSX', 'OXY', 'HAL',
    # 산업재
    'LMT', 'RTX', 'BA', 'CAT', 'DE', 'UNP', 'UPS', 'FDX', 'HON', 'GE',
    # 유틸리티
    'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL', 'WEC', 'ED'
]

def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='6mo')
        if hist.empty or len(hist) < 50:
            return None

        info = stock.info
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2]
        price_change = ((current_price - prev_price) / prev_price) * 100

        sma20 = hist['Close'].rolling(20).mean().iloc[-1]
        sma50 = hist['Close'].rolling(50).mean().iloc[-1]
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()

        # 점수 계산
        score = 50
        score_details = []

        # 배당 점수 (최대 25점)
        div_yield = info.get('dividendYield', 0) or 0
        if div_yield > 1:
            div_yield_pct = div_yield
            div_yield_decimal = div_yield / 100
        else:
            div_yield_pct = div_yield * 100
            div_yield_decimal = div_yield

        if div_yield_decimal > 0.04:
            score += 25
            score_details.append(f"고배당 {div_yield_pct:.1f}% (+25)")
        elif div_yield_decimal > 0.02:
            score += 15
            score_details.append(f"배당 {div_yield_pct:.1f}% (+15)")
        elif div_yield_decimal > 0.01:
            score += 10
            score_details.append(f"배당 {div_yield_pct:.1f}% (+10)")

        # PER 점수 (최대 15점)
        pe = info.get('trailingPE', 0) or 0
        if 0 < pe < 15:
            score += 15
            score_details.append(f"저PER {pe:.1f} (+15)")
        elif 0 < pe < 20:
            score += 10
            score_details.append(f"적정PER {pe:.1f} (+10)")

        # 수익성 점수 (최대 10점)
        profit_margin = info.get('profitMargins', 0) or 0
        if profit_margin > 0.15:
            score += 10
            score_details.append(f"고수익 {profit_margin*100:.1f}% (+10)")
        elif profit_margin > 0.1:
            score += 5
            score_details.append(f"수익성 {profit_margin*100:.1f}% (+5)")

        # 기술적 분석 (최대 10점)
        if current_price > sma20:
            score += 5
            score_details.append("SMA20 상회 (+5)")
        if current_price > sma50:
            score += 5
            score_details.append("SMA50 상회 (+5)")

        return {
            'ticker': ticker,
            'name': info.get('shortName', ticker),
            'price': current_price,
            'change': price_change,
            'score': min(score, 100),
            'score_details': score_details,
            'dividend': div_yield_pct,
            'pe': pe,
            'profit_margin': profit_margin * 100 if profit_margin else 0,
            'sma20': sma20,
            'sma50': sma50,
            'high_52w': high_52w,
            'low_52w': low_52w,
            'sector': info.get('sector', 'N/A'),
            'market_cap': info.get('marketCap', 0)
        }
    except Exception as e:
        print(f"  {ticker} 분석 실패: {e}")
        return None

def generate_html(stocks, top_stocks, other_stocks, now):
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Value Stocks - {now.strftime("%Y-%m-%d")}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Noto Sans KR', sans-serif; background: linear-gradient(180deg, #87CEEB 0%, #98D8C8 30%, #F7DC6F 70%, #FADBD8 100%); background-attachment: fixed; padding: 20px; min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .back-link {{ display: block; text-align: center; margin-bottom: 20px; color: #5D4E37; text-decoration: none; font-weight: 500; }}
        .header {{ background: white; border-radius: 30px; padding: 35px; margin-bottom: 25px; box-shadow: 0 8px 0 #E8A838; border: 4px solid #5D4E37; text-align: center; }}
        .header h1 {{ color: #5D4E37; font-size: 2em; text-shadow: 2px 2px 0 #FFF5BA; }}
        .header .subtitle {{ color: #7B6B4F; margin-top: 5px; }}
        .header .date {{ color: #E8A838; margin-top: 10px; font-weight: 600; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .summary-card {{ background: linear-gradient(180deg, #FFF8DC, #FAEBD7); border-radius: 20px; padding: 20px; border: 3px solid #5D4E37; text-align: center; box-shadow: 0 4px 0 #C4A35A; }}
        .summary-card .label {{ color: #7B6B4F; font-size: 0.85em; }}
        .summary-card .value {{ color: #FF6B35; font-size: 1.6em; font-weight: bold; }}
        .section-title {{ background: white; border-radius: 20px; padding: 15px 25px; margin: 25px 0 20px; border: 3px solid #5D4E37; box-shadow: 0 4px 0 #C4A35A; color: #5D4E37; font-size: 1.3em; text-align: center; }}
        .stock-card {{ background: linear-gradient(180deg, #FFFFFF 0%, #F5F5DC 100%); border-radius: 20px; padding: 25px; margin-bottom: 20px; border: 3px solid #5D4E37; box-shadow: 0 5px 0 #E8A838; transition: transform 0.2s; }}
        .stock-card:hover {{ transform: translateY(-3px); }}
        .stock-card.top {{ background: linear-gradient(180deg, #FFFACD 0%, #FFF8DC 100%); border: 4px solid #F5B041; }}
        .stock-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 2px dashed #C4A35A; }}
        .stock-info h2 {{ color: #5D4E37; font-size: 1.2em; margin-bottom: 5px; }}
        .stock-info .ticker {{ color: #E8A838; font-weight: 600; }}
        .stock-info .sector {{ color: #7B6B4F; font-size: 0.85em; }}
        .score-badge {{ background: #E8A838; color: white; padding: 10px 18px; border-radius: 20px; font-weight: bold; font-size: 1.1em; border: 3px solid #5D4E37; }}
        .score-badge.high {{ background: #4CAF50; }}
        .top-badge {{ background: linear-gradient(135deg, #F5B041 0%, #E8A838 100%); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8em; margin-left: 8px; border: 2px solid #5D4E37; }}
        .price-section {{ display: flex; align-items: baseline; gap: 12px; margin-bottom: 15px; flex-wrap: wrap; }}
        .price {{ font-size: 1.5em; font-weight: bold; color: #5D4E37; }}
        .change {{ padding: 4px 10px; border-radius: 10px; font-size: 0.9em; font-weight: 600; }}
        .change.positive {{ background: #E8F5E9; color: #2E7D32; }}
        .change.negative {{ background: #FFEBEE; color: #C62828; }}
        .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px; }}
        .metric {{ background: linear-gradient(180deg, #FFF8DC 0%, #FAEBD7 100%); padding: 12px; border-radius: 12px; text-align: center; border: 2px solid #C4A35A; }}
        .metric .label {{ color: #7B6B4F; font-size: 0.75em; }}
        .metric .value {{ color: #5D4E37; font-size: 1em; font-weight: bold; }}
        .metric.highlight {{ background: linear-gradient(135deg, #4CAF50, #45A049); border-color: #388E3C; }}
        .metric.highlight .label, .metric.highlight .value {{ color: white; }}
        .score-details {{ background: #F5F5DC; padding: 12px; border-radius: 12px; margin-top: 10px; }}
        .score-details .title {{ color: #5D4E37; font-weight: 600; margin-bottom: 8px; font-size: 0.9em; }}
        .score-details .item {{ color: #7B6B4F; font-size: 0.85em; padding: 3px 0; }}
        .footer {{ background: rgba(255,255,255,0.9); border-radius: 20px; padding: 20px; text-align: center; color: #7B6B4F; margin-top: 30px; border: 3px solid #C4A35A; }}
        @media (max-width: 768px) {{ .metrics {{ grid-template-columns: repeat(2, 1fr); }} }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-link">← 메인으로</a>
        <div class="header">
            <div style="font-size: 3em;">💰</div>
            <h1>Value Stocks Recommendations</h1>
            <div class="subtitle">가치주/배당주 중심 분석 (금융, 헬스케어, 에너지, 유틸리티)</div>
            <div class="date">{now.strftime("%Y-%m-%d %H:%M")} UTC 업데이트</div>
        </div>
        <div class="summary">
            <div class="summary-card"><div class="label">분석 종목</div><div class="value">{len(stocks)}개</div></div>
            <div class="summary-card"><div class="label">TOP 5</div><div class="value">{len(top_stocks)}개</div></div>
            <div class="summary-card"><div class="label">평균 배당률</div><div class="value">{sum(s["dividend"] for s in stocks)/len(stocks) if stocks else 0:.1f}%</div></div>
            <div class="summary-card"><div class="label">최고 점수</div><div class="value">{max(s["score"] for s in stocks) if stocks else 0}점</div></div>
        </div>
        <div class="section-title">🏆 TOP 5 추천 종목</div>
'''

    # TOP 5 종목 카드
    for i, s in enumerate(top_stocks):
        change_class = 'positive' if s['change'] >= 0 else 'negative'
        change_sign = '+' if s['change'] >= 0 else ''
        score_class = 'high' if s['score'] >= 80 else ''
        div_highlight = 'highlight' if s['dividend'] >= 3 else ''
        high_52w_pct = ((s['price'] - s['high_52w']) / s['high_52w'] * 100) if s['high_52w'] else 0
        score_items = ''.join(f'<div class="item">✓ {d}</div>' for d in s['score_details'])

        html += f'''
        <div class="stock-card top">
            <div class="stock-header">
                <div class="stock-info">
                    <h2>{s['name']}<span class="top-badge">TOP {i+1}</span></h2>
                    <span class="ticker">{s['ticker']}</span> | <span class="sector">{s['sector']}</span>
                </div>
                <span class="score-badge {score_class}">{s['score']}점</span>
            </div>
            <div class="price-section">
                <span class="price">${s['price']:.2f}</span>
                <span class="change {change_class}">{change_sign}{s['change']:.2f}%</span>
            </div>
            <div class="metrics">
                <div class="metric {div_highlight}"><div class="label">배당률</div><div class="value">{s['dividend']:.1f}%</div></div>
                <div class="metric"><div class="label">PER</div><div class="value">{s['pe']:.1f}</div></div>
                <div class="metric"><div class="label">수익률</div><div class="value">{s['profit_margin']:.1f}%</div></div>
                <div class="metric"><div class="label">52주 고점대비</div><div class="value">{high_52w_pct:.1f}%</div></div>
            </div>
            <div class="score-details">
                <div class="title">📊 점수 상세</div>
                {score_items}
            </div>
        </div>'''

    html += '<div class="section-title">📋 기타 추천 종목</div>'

    # 기타 종목 카드
    for s in other_stocks:
        change_class = 'positive' if s['change'] >= 0 else 'negative'
        change_sign = '+' if s['change'] >= 0 else ''
        score_class = 'high' if s['score'] >= 80 else ''

        html += f'''
        <div class="stock-card">
            <div class="stock-header">
                <div class="stock-info">
                    <h2>{s['name']}</h2>
                    <span class="ticker">{s['ticker']}</span> | <span class="sector">{s['sector']}</span>
                </div>
                <span class="score-badge {score_class}">{s['score']}점</span>
            </div>
            <div class="price-section">
                <span class="price">${s['price']:.2f}</span>
                <span class="change {change_class}">{change_sign}{s['change']:.2f}%</span>
                <span style="color: #4CAF50; font-weight: bold; margin-left: 10px;">배당 {s['dividend']:.1f}%</span>
            </div>
            <div class="metrics">
                <div class="metric"><div class="label">PER</div><div class="value">{s['pe']:.1f}</div></div>
                <div class="metric"><div class="label">수익률</div><div class="value">{s['profit_margin']:.1f}%</div></div>
                <div class="metric"><div class="label">SMA20</div><div class="value">${s['sma20']:.2f}</div></div>
                <div class="metric"><div class="label">SMA50</div><div class="value">${s['sma50']:.2f}</div></div>
            </div>
        </div>'''

    html += '''
        <div class="footer">⚠️ 본 리포트는 투자 참고 자료이며, 투자 판단의 책임은 투자자 본인에게 있습니다.</div>
    </div>
</body>
</html>'''

    return html

def main():
    print('Value Stocks 분석 중...')
    stocks = []
    for t in VALUE_TICKERS:
        result = analyze_stock(t)
        if result:
            stocks.append(result)
            print(f"  {t}: {result['score']}점")

    stocks.sort(key=lambda x: x['score'], reverse=True)
    top_stocks = stocks[:5]
    other_stocks = stocks[5:30]

    now = datetime.now()
    html = generate_html(stocks, top_stocks, other_stocks, now)

    with open('value_report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\nValue 리포트 생성 완료: {len(stocks)}개 종목 분석")

if __name__ == '__main__':
    main()
