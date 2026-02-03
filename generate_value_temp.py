import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

VALUE_TICKERS = [
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BRK-B', 'V', 'MA', 'AXP',
    'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT', 'BMY', 'CVS',
    'PG', 'KO', 'PEP', 'WMT', 'COST', 'TGT', 'CL', 'GIS', 'K', 'MO',
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'VLO', 'PSX', 'OXY', 'HAL',
    'LMT', 'RTX', 'BA', 'CAT', 'DE', 'UNP', 'UPS', 'FDX', 'HON', 'GE',
    'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL', 'WEC', 'ED'
]

def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='6mo')
        if hist.empty or len(hist) < 20:
            return None

        info = stock.info
        current_price = hist['Close'].iloc[-1]
        sma20 = hist['Close'].rolling(20).mean().iloc[-1]

        score = 50
        div_yield = info.get('dividendYield', 0) or 0
        # yfinance가 소수(0.03) 또는 퍼센트(3.0)로 반환하는 경우 처리
        if div_yield > 1:
            div_yield_pct = div_yield
            div_yield_decimal = div_yield / 100
        else:
            div_yield_pct = div_yield * 100
            div_yield_decimal = div_yield

        if div_yield_decimal > 0.02: score += 15
        if div_yield_decimal > 0.04: score += 10
        if info.get('trailingPE', 100) and info['trailingPE'] < 20: score += 10
        if info.get('profitMargins', 0) and info['profitMargins'] > 0.1: score += 10
        if current_price > sma20: score += 5

        return {
            'ticker': ticker,
            'name': info.get('shortName', ticker),
            'price': current_price,
            'score': min(score, 100),
            'dividend': div_yield_pct,
            'sector': info.get('sector', 'N/A')
        }
    except:
        return None

stocks = []
for t in VALUE_TICKERS:
    result = analyze_stock(t)
    if result:
        stocks.append(result)
        print(f"  {t}: {result['score']}점")

stocks.sort(key=lambda x: x['score'], reverse=True)
recommended = [s for s in stocks if s['score'] >= 45]

now = datetime.now()
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
        .header {{ background: white; border-radius: 30px; padding: 35px; margin-bottom: 25px; box-shadow: 0 8px 0 #E8A838; border: 4px solid #5D4E37; text-align: center; }}
        .header h1 {{ color: #5D4E37; font-size: 2em; }}
        .header .date {{ color: #E8A838; margin-top: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .summary-card {{ background: linear-gradient(180deg, #FFF8DC, #FAEBD7); border-radius: 20px; padding: 20px; border: 3px solid #5D4E37; text-align: center; }}
        .summary-card .value {{ color: #FF6B35; font-size: 1.8em; font-weight: bold; }}
        .stock-card {{ background: white; border-radius: 20px; padding: 25px; margin-bottom: 15px; border: 3px solid #5D4E37; box-shadow: 0 5px 0 #E8A838; }}
        .stock-card h2 {{ color: #5D4E37; margin-bottom: 10px; }}
        .stock-card .ticker {{ color: #E8A838; }}
        .stock-card .score {{ background: #E8A838; color: white; padding: 8px 20px; border-radius: 20px; float: right; }}
        .stock-card .score.high {{ background: #4CAF50; }}
        .dividend {{ color: #4CAF50; font-weight: bold; }}
        .back-link {{ display: block; text-align: center; margin-bottom: 20px; color: #5D4E37; }}
        .footer {{ background: rgba(255,255,255,0.9); border-radius: 20px; padding: 20px; text-align: center; color: #7B6B4F; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-link">← 메인으로</a>
        <div class="header">
            <div style="font-size: 3em;">💰</div>
            <h1>Value Stocks Recommendations</h1>
            <div class="date">{now.strftime("%Y-%m-%d %H:%M")} UTC 업데이트</div>
        </div>
        <div class="summary">
            <div class="summary-card"><div class="label">분석 종목</div><div class="value">{len(stocks)}개</div></div>
            <div class="summary-card"><div class="label">추천 종목</div><div class="value">{len(recommended)}개</div></div>
        </div>
'''
for s in recommended[:20]:
    score_class = 'high' if s['score'] >= 70 else ''
    div_text = f" | <span class='dividend'>배당 {s['dividend']:.1f}%</span>" if s['dividend'] > 0 else ""
    html += f'''
        <div class="stock-card">
            <span class="score {score_class}">{s['score']}점</span>
            <h2>{s['name']}</h2>
            <span class="ticker">{s['ticker']}</span> | ${s['price']:.2f}{div_text}
        </div>'''

html += '''
        <div class="footer">⚠️ 본 리포트는 투자 참고 자료입니다.</div>
    </div>
</body>
</html>'''

with open('value_report.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\\nValue 리포트 생성 완료: {len(recommended)}개 추천")
