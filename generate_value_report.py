"""
가치주/배당주 추천 웹페이지 생성기
- 기술주 제외, 가치/배당 중심 분석
- 밥값 점수 강화 (ROE, 배당, PER)

점수 체계 (100점 만점):
- 밥값 점수: 45점 (ROE, 마진, 배당, PER)
- 기술적 분석: 25점 (모멘텀, 추세)
- 정책 수혜: 15점 (방산, 인프라, IRA)
- 안정성: 15점 (변동성, 베타)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import sys
import time
import concurrent.futures
sys.path.insert(0, '.')

# 한국 시간대 (UTC+9)
KST = timezone(timedelta(hours=9))


def get_value_tickers():
    """가치주/배당주 종목 목록 가져오기"""
    try:
        from value_tickers import get_value_list
        tickers = get_value_list()
        print(f"가치주/배당주 {len(tickers)}개 로드 완료")
        return tickers
    except Exception as e:
        print(f"[WARNING] 종목 목록 로드 실패: {e}")
        return None


from quant_trading.technical_analyzer_v3 import TechnicalAnalyzerV3
from quant_trading.price_recommender import PriceRecommender
from quant_trading.valuation_analyzer import ValuationAnalyzer
from quant_trading.policy_analyzer import PolicyAnalyzer


def calculate_stability_score(df, info):
    """
    안정성 점수 (15점 만점)
    - 변동성 (7점): 낮을수록 좋음
    - 베타 (8점): 1 이하면 높은 점수
    """
    score = 0
    reasons = []

    # 1. 변동성 (7점) - 연간 변동성 기준
    try:
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std() * (252 ** 0.5) * 100  # 연환산 %

        if volatility <= 15:
            score += 7
            reasons.append(f"매우 낮은 변동성 {volatility:.1f}%")
        elif volatility <= 20:
            score += 6
            reasons.append(f"낮은 변동성 {volatility:.1f}%")
        elif volatility <= 25:
            score += 5
            reasons.append(f"보통 변동성 {volatility:.1f}%")
        elif volatility <= 30:
            score += 3
            reasons.append(f"높은 변동성 {volatility:.1f}%")
        elif volatility <= 40:
            score += 1
            reasons.append(f"매우 높은 변동성 {volatility:.1f}%")
        else:
            reasons.append(f"극심한 변동성 {volatility:.1f}%")
    except:
        volatility = 0

    # 2. 베타 (8점)
    try:
        beta = info.get('beta', 1.0)
        if beta is None:
            beta = 1.0

        if beta <= 0.5:
            score += 8
            reasons.append(f"방어주 (베타 {beta:.2f})")
        elif beta <= 0.8:
            score += 7
            reasons.append(f"저베타 {beta:.2f}")
        elif beta <= 1.0:
            score += 5
            reasons.append(f"시장 수준 베타 {beta:.2f}")
        elif beta <= 1.2:
            score += 3
            reasons.append(f"고베타 {beta:.2f}")
        else:
            score += 1
            reasons.append(f"매우 고베타 {beta:.2f}")
    except:
        beta = 1.0

    return {
        'score': score,
        'volatility': volatility,
        'beta': beta,
        'reasons': ', '.join(reasons)
    }


def calculate_enhanced_valuation(ticker, info):
    """
    강화된 밥값 점수 (45점 만점)
    - 기존 밸류에이션 (35점)
    - 배당 (10점 추가)
    """
    # 기존 밸류에이션 점수
    valuation = ValuationAnalyzer(ticker)
    base_result = valuation.calculate_total_score()
    base_score = base_result['total_score']  # 35점 만점

    # 배당 추가 점수 (10점)
    dividend_score = 0
    dividend_yield = info.get('dividendYield', 0) or 0
    # yfinance가 소수(0.03) 또는 퍼센트(3.0)로 반환하는 경우 처리
    if dividend_yield > 1:
        # 이미 퍼센트로 반환된 경우 (예: 3.0 = 3%)
        dividend_yield_pct = dividend_yield
    else:
        # 소수로 반환된 경우 (예: 0.03 = 3%)
        dividend_yield_pct = dividend_yield * 100

    if dividend_yield_pct >= 4.0:
        dividend_score = 10
        div_reason = f"고배당 {dividend_yield_pct:.2f}%"
    elif dividend_yield_pct >= 3.0:
        dividend_score = 8
        div_reason = f"우수 배당 {dividend_yield_pct:.2f}%"
    elif dividend_yield_pct >= 2.0:
        dividend_score = 6
        div_reason = f"양호 배당 {dividend_yield_pct:.2f}%"
    elif dividend_yield_pct >= 1.0:
        dividend_score = 4
        div_reason = f"배당 {dividend_yield_pct:.2f}%"
    elif dividend_yield_pct > 0:
        dividend_score = 2
        div_reason = f"소액 배당 {dividend_yield_pct:.2f}%"
    else:
        dividend_score = 0
        div_reason = "무배당"

    total_score = base_score + dividend_score

    return {
        'total_score': total_score,
        'base_score': base_score,
        'dividend_score': dividend_score,
        'dividend_yield': dividend_yield_pct,
        'dividend_reason': div_reason,
        'roe': base_result['roe'],
        'operating_margin': base_result['operating_margin'],
        'is_profitable': base_result['is_profitable'],
        'verdict': base_result['verdict']
    }


def analyze_value_stock(ticker):
    """
    가치주 분석

    점수 체계 (100점 만점):
    - 밥값 점수: 45점 (ROE, 마진, 배당)
    - 기술적 분석: 25점
    - 정책 수혜: 15점
    - 안정성: 15점
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period='2y')

        if df.empty or len(df) < 180:
            return None

        info = stock.info

        # 1. 기술적 분석 (25점 만점으로 스케일)
        tech_v3 = TechnicalAnalyzerV3(df)
        result_v3 = tech_v3.calculate_total_score()
        tech_score = (result_v3['total_score'] / 65) * 25

        # 2. 강화된 밥값 점수 (45점 만점)
        valuation_result = calculate_enhanced_valuation(ticker, info)
        valuation_score = valuation_result['total_score']

        # 3. 정책 수혜 점수 (15점 만점으로 스케일)
        policy = PolicyAnalyzer(ticker)
        policy_result = policy.calculate_total_score()
        policy_score = (policy_result['total_score'] / 20) * 15

        # 4. 안정성 점수 (15점 만점)
        stability_result = calculate_stability_score(df, info)
        stability_score = stability_result['score']

        # 총점 계산 (100점 만점)
        total_score = valuation_score + tech_score + policy_score + stability_score

        name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        current_price = df['Close'].iloc[-1]
        previous_close = df['Close'].iloc[-2]
        change_pct = ((current_price - previous_close) / previous_close) * 100

        # 가격 추천
        regular_market_price = info.get('regularMarketPrice') or current_price
        price_rec = PriceRecommender(df, regular_market_price)
        price_recommendation = price_rec.get_recommendation(strategy='conservative')

        return {
            'ticker': ticker,
            'name': name,
            'sector': sector,
            'current_price': current_price,
            'previous_close': previous_close,
            'change_pct': change_pct,
            'regular_market_price': regular_market_price,
            'total_score': total_score,
            # 점수 상세
            'valuation_score': valuation_score,
            'tech_score': tech_score,
            'policy_score': policy_score,
            'stability_score': stability_score,
            # 밥값 상세
            'roe': valuation_result['roe'],
            'operating_margin': valuation_result['operating_margin'],
            'dividend_yield': valuation_result['dividend_yield'],
            'dividend_reason': valuation_result['dividend_reason'],
            'is_profitable': valuation_result['is_profitable'],
            'valuation_verdict': valuation_result['verdict'],
            # 정책 상세
            'policy_summary': policy_result['policy_summary'],
            'policy_verdict': policy_result['verdict'],
            # 안정성 상세
            'volatility': stability_result['volatility'],
            'beta': stability_result['beta'],
            'stability_reason': stability_result['reasons'],
            # 기술적 분석
            'momentum': result_v3['momentum_score'],
            'trend': result_v3['trend_score'],
            'signal': result_v3['signals'],
            'price_rec': price_recommendation,
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

    current = stock.get('regular_market_price') or stock['current_price']

    # 배당 뱃지
    dividend_badge = ''
    if stock['dividend_yield'] >= 3.0:
        dividend_badge = f'<span class="dividend-badge high">배당 {stock["dividend_yield"]:.1f}%</span>'
    elif stock['dividend_yield'] >= 1.5:
        dividend_badge = f'<span class="dividend-badge">배당 {stock["dividend_yield"]:.1f}%</span>'

    return f"""
    <div class="stock-card {'top5-card' if is_top5 else ''}">
        <div class="stock-header">
            <div class="stock-title">
                {top5_badge}
                <span class="rank-badge">#{idx}</span>
                <h2>{stock['name']}</h2>
                <div class="ticker">{stock['ticker']} {dividend_badge}</div>
                <div class="sector">{stock['sector']}</div>
            </div>
            <div class="score-badge {badge_class}">
                {stock['total_score']:.0f}점
            </div>
        </div>

        <div class="current-price">
            <div class="price-row">
                <span class="price-label">현재가:</span>
                <span class="price">${current:.2f}</span>
                <span class="change {change_class}">{change_sign}{stock['change_pct']:.2f}%</span>
            </div>
        </div>

        <div class="metrics">
            <div class="metric clickable {'highlight' if stock.get('valuation_score', 0) >= 30 else ''}" onclick="showScoreCriteria('valuation')">
                <div class="label">밥값+배당</div>
                <div class="value">{stock.get('valuation_score', 0):.0f}/45</div>
            </div>
            <div class="metric clickable {'highlight' if stock.get('tech_score', 0) >= 15 else ''}" onclick="showScoreCriteria('technical')">
                <div class="label">기술적</div>
                <div class="value">{stock.get('tech_score', 0):.0f}/25</div>
            </div>
            <div class="metric clickable {'highlight' if stock.get('stability_score', 0) >= 10 else ''}" onclick="showScoreCriteria('stability')">
                <div class="label">안정성</div>
                <div class="value">{stock.get('stability_score', 0):.0f}/15</div>
            </div>
            <div class="metric clickable {'highlight' if stock.get('policy_score', 0) >= 8 else ''}" onclick="showScoreCriteria('policy')">
                <div class="label">정책</div>
                <div class="value">{stock.get('policy_score', 0):.0f}/15</div>
            </div>
        </div>

        <div class="verdict-section">
            <div class="verdict-item {'profitable' if stock.get('is_profitable') else 'unprofitable'}">
                <span class="verdict-label">ROE:</span>
                <span class="verdict-value">{stock.get('roe', 0):.1f}%</span>
                <span class="verdict-desc">| {stock.get('dividend_reason', '')}</span>
            </div>
            <div class="verdict-item">
                <span class="verdict-label">안정성:</span>
                <span class="verdict-value">베타 {stock.get('beta', 1):.2f}</span>
                <span class="verdict-desc">| 변동성 {stock.get('volatility', 0):.1f}%</span>
            </div>
            <div class="verdict-item">
                <span class="verdict-label">정책:</span>
                <span class="verdict-value">{stock.get('policy_summary', '없음')}</span>
            </div>
        </div>

        <div class="price-section">
            <div class="price-box buy">
                <h3>매수 가격</h3>
                <div class="price-item">
                    <span class="label">추천가</span>
                    <span class="value">${pr['entry']['price']:.2f}</span>
                </div>
                <div class="price-item">
                    <span class="label">보수적</span>
                    <span class="value">${pr['entry']['all_options']['conservative']:.2f}</span>
                </div>
            </div>

            <div class="price-box sell">
                <h3>매도 목표가</h3>
                <div class="price-item">
                    <span class="label">1차</span>
                    <span class="value">${pr['exit']['target_1']:.2f} (+{pr['exit']['expected_profit_1']:.1f}%)</span>
                </div>
                <div class="price-item">
                    <span class="label">2차</span>
                    <span class="value">${pr['exit']['target_2']:.2f} (+{pr['exit']['expected_profit_2']:.1f}%)</span>
                </div>
            </div>

            <div class="price-box stop">
                <h3>손절 가격</h3>
                <div class="price-item">
                    <span class="label">추천가</span>
                    <span class="value">${pr['stop_loss']['price']:.2f} ({pr['stop_loss']['expected_loss']:.1f}%)</span>
                </div>
            </div>
        </div>

        <div class="signal">
            <div class="label">시그널</div>
            <div class="value">{stock['signal']}</div>
        </div>
    </div>
    """


def generate_html_report(stocks_data, title="Value Stocks Daily Recommendations"):
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

    top5_stocks = stocks_data[:5]
    other_stocks = stocks_data[5:]

    # 고배당 종목
    high_dividend = [s for s in stocks_data if s['dividend_yield'] >= 3.0]

    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {current_date}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans KR', -apple-system, sans-serif;
            background: linear-gradient(180deg, #87CEEB 0%, #98D8C8 30%, #F7DC6F 70%, #FADBD8 100%);
            background-attachment: fixed;
            padding: 20px;
            min-height: 100vh;
            color: #5D4E37;
            position: relative;
            overflow-x: hidden;
        }}

        /* 구름 애니메이션 */
        .cloud {{
            position: fixed;
            background: white;
            border-radius: 50px;
            opacity: 0.8;
            animation: float 25s infinite linear;
            z-index: 0;
        }}
        .cloud::before, .cloud::after {{
            content: '';
            position: absolute;
            background: white;
            border-radius: 50%;
        }}
        .cloud-1 {{ width: 100px; height: 40px; top: 10%; left: -100px; animation-delay: 0s; }}
        .cloud-1::before {{ width: 50px; height: 50px; top: -25px; left: 15px; }}
        .cloud-1::after {{ width: 35px; height: 35px; top: -15px; left: 55px; }}
        .cloud-2 {{ width: 120px; height: 45px; top: 25%; left: -120px; animation-delay: -8s; }}
        .cloud-2::before {{ width: 55px; height: 55px; top: -30px; left: 20px; }}
        .cloud-2::after {{ width: 40px; height: 40px; top: -18px; left: 65px; }}
        .cloud-3 {{ width: 80px; height: 35px; top: 40%; left: -80px; animation-delay: -16s; }}
        .cloud-3::before {{ width: 40px; height: 40px; top: -20px; left: 10px; }}
        .cloud-3::after {{ width: 30px; height: 30px; top: -12px; left: 40px; }}

        @keyframes float {{
            0% {{ transform: translateX(0); }}
            100% {{ transform: translateX(calc(100vw + 200px)); }}
        }}

        /* 반짝이 효과 */
        .sparkle {{
            position: fixed;
            width: 10px;
            height: 10px;
            background: #FFD700;
            clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
            animation: sparkle 2s infinite;
            z-index: 1;
        }}
        @keyframes sparkle {{
            0%, 100% {{ opacity: 0; transform: scale(0); }}
            50% {{ opacity: 1; transform: scale(1); }}
        }}

        .container {{ max-width: 1400px; margin: 0 auto; position: relative; z-index: 10; }}
        .header {{
            background: white;
            border-radius: 30px;
            padding: 35px;
            margin-bottom: 25px;
            box-shadow: 0 8px 0 #E8A838, 0 12px 20px rgba(0,0,0,0.15);
            border: 4px solid #5D4E37;
            text-align: center;
        }}
        .header h1 {{ color: #5D4E37; font-size: 2.2em; margin-bottom: 8px; text-shadow: 2px 2px 0 #FFF5BA; }}
        .header .subtitle {{ color: #7B6B4F; font-size: 1em; }}
        .header .date {{ color: #E8A838; font-weight: 600; margin-top: 10px; }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        .summary-card {{
            background: linear-gradient(180deg, #FFF8DC 0%, #FAEBD7 100%);
            border-radius: 20px;
            padding: 20px;
            border: 3px solid #5D4E37;
            box-shadow: 0 4px 0 #C4A35A;
            text-align: center;
        }}
        .summary-card .label {{ color: #7B6B4F; font-size: 0.85em; margin-bottom: 8px; }}
        .summary-card .value {{ color: #FF6B35; font-size: 1.6em; font-weight: bold; text-shadow: 1px 1px 0 #5D4E37; }}

        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .tab {{
            background: white;
            border: 3px solid #5D4E37;
            padding: 12px 25px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s;
            color: #5D4E37;
            box-shadow: 0 4px 0 #C4A35A;
        }}
        .tab:hover {{ transform: translateY(-2px); box-shadow: 0 6px 0 #C4A35A; }}
        .tab.active {{ background: #E8A838; border-color: #5D4E37; color: white; box-shadow: 0 4px 0 #C4842F; }}

        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        .section-title {{
            font-size: 1.4em;
            color: #5D4E37;
            margin: 30px 0 20px 0;
            display: flex;
            align-items: center;
            gap: 10px;
            background: white;
            padding: 15px 25px;
            border-radius: 20px;
            border: 3px solid #5D4E37;
            box-shadow: 0 4px 0 #C4A35A;
        }}

        .stock-card {{
            background: linear-gradient(180deg, #FFFFFF 0%, #F5F5DC 100%);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
            border: 3px solid #5D4E37;
            box-shadow: 0 5px 0 #E8A838, 0 8px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        .stock-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 0 #E8A838, 0 15px 25px rgba(0,0,0,0.15);
        }}
        .top5-card {{
            border: 4px solid #F5B041;
            background: linear-gradient(180deg, #FFFACD 0%, #FFF8DC 100%);
            box-shadow: 0 6px 0 #E8A838, 0 10px 20px rgba(0,0,0,0.15);
        }}
        .top5-card:hover {{
            box-shadow: 0 12px 0 #E8A838, 0 18px 30px rgba(0,0,0,0.15);
        }}

        .top5-label {{
            background: linear-gradient(135deg, #F5B041 0%, #E8A838 100%);
            color: white;
            padding: 6px 15px;
            border-radius: 15px;
            font-weight: bold;
            font-size: 0.85em;
            margin-right: 10px;
            border: 2px solid #5D4E37;
        }}

        .stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px dashed #C4A35A;
        }}
        .stock-title h2 {{ color: #5D4E37; font-size: 1.3em; margin-bottom: 5px; }}
        .stock-title .ticker {{ color: #E8A838; font-size: 0.95em; font-weight: 600; }}
        .stock-title .sector {{ color: #7B6B4F; font-size: 0.8em; margin-top: 5px; }}

        .dividend-badge {{
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 0.75em;
            margin-left: 8px;
            border: 2px solid #388E3C;
        }}
        .dividend-badge.high {{ background: #2E7D32; }}

        .score-badge {{
            background: #E8A838;
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 1.2em;
            font-weight: bold;
            border: 3px solid #5D4E37;
            box-shadow: 0 3px 0 #C4842F;
        }}
        .score-badge.top5 {{ background: linear-gradient(135deg, #F5B041 0%, #E8A838 100%); box-shadow: 0 4px 0 #C4842F; }}
        .score-badge.high {{ background: #4CAF50; box-shadow: 0 3px 0 #388E3C; }}

        .rank-badge {{
            background: linear-gradient(180deg, #FFF8DC 0%, #FAEBD7 100%);
            color: #5D4E37;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            margin-right: 8px;
            border: 2px solid #C4A35A;
        }}

        .current-price {{ margin-bottom: 15px; }}
        .price-row {{
            display: flex;
            align-items: baseline;
            gap: 12px;
        }}
        .price-label {{ color: #7B6B4F; font-size: 0.9em; }}
        .current-price .price {{ font-size: 1.4em; font-weight: bold; color: #5D4E37; }}
        .current-price .change {{
            font-size: 0.95em;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 12px;
            border: 2px solid;
        }}
        .change.positive {{ background: #E8F5E9; color: #2E7D32; border-color: #4CAF50; }}
        .change.negative {{ background: #FFEBEE; color: #C62828; border-color: #E53935; }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }}
        .metric {{
            background: linear-gradient(180deg, #FFF8DC 0%, #FAEBD7 100%);
            padding: 12px;
            border-radius: 15px;
            text-align: center;
            border: 2px solid #C4A35A;
        }}
        .metric .label {{ color: #7B6B4F; font-size: 0.75em; margin-bottom: 4px; }}
        .metric .value {{ color: #5D4E37; font-size: 1.1em; font-weight: bold; }}
        .metric.highlight {{ background: linear-gradient(135deg, #4CAF50, #45A049); border-color: #388E3C; }}
        .metric.highlight .label, .metric.highlight .value {{ color: white; }}

        .metric.clickable {{
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .metric.clickable:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 10px rgba(232, 168, 56, 0.3);
        }}

        .score-tooltip {{
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(180deg, #FFFFFF 0%, #FFF8DC 100%);
            border-radius: 25px;
            padding: 25px;
            box-shadow: 0 10px 0 #C4A35A, 0 15px 40px rgba(0,0,0,0.3);
            z-index: 10000;
            max-width: 450px;
            width: 90%;
            border: 4px solid #5D4E37;
            max-height: 80vh;
            overflow-y: auto;
        }}
        .score-tooltip.show {{ display: block; }}
        .score-tooltip-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.6);
            z-index: 9999;
        }}
        .score-tooltip-overlay.show {{ display: block; }}
        .score-tooltip h3 {{
            color: #5D4E37;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 3px solid #E8A838;
            padding-bottom: 10px;
        }}
        .score-tooltip .close-btn {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: #E53935;
            border: 2px solid #5D4E37;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            font-size: 1.2em;
            cursor: pointer;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .score-tooltip .close-btn:hover {{ background: #C62828; }}
        .score-tooltip .criteria-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .score-tooltip .criteria-list li {{
            padding: 8px 0;
            border-bottom: 2px dashed #C4A35A;
            font-size: 0.9em;
            color: #5D4E37;
        }}
        .score-tooltip .criteria-list li:last-child {{ border-bottom: none; }}
        .score-tooltip .section-header {{
            font-weight: 700;
            color: #E8A838;
            background: linear-gradient(180deg, #FFF8DC 0%, #FAEBD7 100%);
            padding: 10px;
            margin: 8px -10px;
            border-radius: 10px;
            border: 2px solid #C4A35A;
        }}

        .verdict-section {{
            background: linear-gradient(180deg, #E8F4FD 0%, #D6EAF8 100%);
            border-radius: 15px;
            padding: 12px 15px;
            margin-bottom: 15px;
            border: 2px solid #E8A838;
        }}
        .verdict-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 5px;
            font-size: 0.85em;
        }}
        .verdict-label {{ color: #5D4E37; min-width: 70px; font-weight: 600; }}
        .verdict-value {{ color: #5D4E37; font-weight: 500; }}
        .verdict-desc {{ color: #7B6B4F; font-size: 0.9em; }}
        .verdict-item.profitable .verdict-value {{ color: #4CAF50; }}
        .verdict-item.unprofitable .verdict-value {{ color: #E53935; }}

        .price-section {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 15px;
        }}
        .price-box {{
            background: linear-gradient(180deg, #FFF8DC 0%, #FAEBD7 100%);
            border-radius: 15px;
            padding: 15px;
            border: 3px solid #5D4E37;
        }}
        .price-box.buy {{ border-color: #5BA3E0; background: linear-gradient(180deg, #E8F4FD 0%, #D6EAF8 100%); }}
        .price-box.sell {{ border-color: #9B59B6; background: linear-gradient(180deg, #F5EEF8 0%, #E8DAEF 100%); }}
        .price-box.stop {{ border-color: #E53935; background: linear-gradient(180deg, #FFEBEE 0%, #FFCDD2 100%); }}
        .price-box h3 {{ color: #5D4E37; margin-bottom: 10px; font-size: 0.9em; }}
        .price-item {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            font-size: 0.85em;
            border-bottom: 2px dashed rgba(93, 78, 55, 0.2);
        }}
        .price-item:last-child {{ border-bottom: none; }}
        .price-item .label {{ color: #7B6B4F; }}
        .price-item .value {{ color: #5D4E37; font-weight: 600; }}

        .signal {{
            background: linear-gradient(180deg, #E8F4FD 0%, #D6EAF8 100%);
            padding: 10px;
            border-radius: 12px;
            margin-top: 12px;
            border: 2px solid #E8A838;
        }}
        .signal .label {{ color: #7B6B4F; font-size: 0.8em; margin-bottom: 4px; }}
        .signal .value {{ color: #5D4E37; font-size: 0.85em; }}

        .show-more-btn {{
            display: block;
            width: 100%;
            max-width: 300px;
            margin: 25px auto;
            padding: 12px 25px;
            background: white;
            border: 3px solid #5D4E37;
            color: #5D4E37;
            font-size: 1em;
            border-radius: 20px;
            cursor: pointer;
            font-family: 'Noto Sans KR', sans-serif;
            box-shadow: 0 4px 0 #C4A35A;
            transition: all 0.2s;
        }}
        .show-more-btn:hover {{ transform: translateY(2px); box-shadow: 0 2px 0 #C4A35A; }}

        #other-stocks {{ display: none; }}
        #other-stocks.show {{ display: block; }}

        .footer {{
            background: rgba(255,255,255,0.9);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            color: #7B6B4F;
            margin-top: 30px;
            font-size: 0.85em;
            border: 3px solid #C4A35A;
        }}

        @media (max-width: 768px) {{
            .metrics {{ grid-template-columns: repeat(2, 1fr); }}
            .price-section {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <!-- 구름들 -->
    <div class="cloud cloud-1"></div>
    <div class="cloud cloud-2"></div>
    <div class="cloud cloud-3"></div>

    <!-- 반짝이들 -->
    <div class="sparkle" style="top: 15%; left: 10%;"></div>
    <div class="sparkle" style="top: 25%; right: 15%; animation-delay: 0.5s;"></div>
    <div class="sparkle" style="top: 45%; left: 8%; animation-delay: 1s;"></div>
    <div class="sparkle" style="top: 65%; right: 12%; animation-delay: 1.5s;"></div>

    <div class="container">
        <div class="header">
            <div style="font-size: 3em; margin-bottom: 10px;">💰</div>
            <h1>Value Stocks Recommendations</h1>
            <div class="subtitle">가치주/배당주 중심 분석 (기술주 제외)</div>
            <div class="date">{current_date} {current_time} 업데이트</div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <div class="label">분석 종목</div>
                <div class="value">{len(stocks_data)}개</div>
            </div>
            <div class="summary-card">
                <div class="label">평균 점수</div>
                <div class="value">{sum(s['total_score'] for s in stocks_data) / len(stocks_data):.1f}</div>
            </div>
            <div class="summary-card">
                <div class="label">고배당 (3%+)</div>
                <div class="value">{len(high_dividend)}개</div>
            </div>
            <div class="summary-card">
                <div class="label">최고 점수</div>
                <div class="value">{max(s['total_score'] for s in stocks_data):.0f}점</div>
            </div>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="showTab('all')">전체</div>
            <div class="tab" onclick="showTab('dividend')">고배당</div>
"""

    for sector in sorted(sectors.keys()):
        if sector != 'N/A':
            html += f'            <div class="tab" onclick="showTab(\'{sector}\')">{sector} ({len(sectors[sector])})</div>\n'

    html += f"""
        </div>

        <div id="tab-all" class="tab-content active">
            <h2 class="section-title">TOP 5 추천 종목</h2>
"""

    for idx, stock in enumerate(top5_stocks, 1):
        html += generate_stock_card_html(stock, idx, is_top5=True)

    html += f"""
            <button class="show-more-btn" onclick="toggleOtherStocks()">
                <span id="show-more-text">나머지 {len(other_stocks)}개 종목 보기</span>
            </button>
            <div id="other-stocks">
                <h2 class="section-title">기타 종목</h2>
"""

    for idx, stock in enumerate(other_stocks, 6):
        html += generate_stock_card_html(stock, idx, is_top5=False)

    html += """
            </div>
        </div>

        <div id="tab-dividend" class="tab-content">
            <h2 class="section-title">고배당 종목 (3% 이상)</h2>
"""

    for idx, stock in enumerate(sorted(high_dividend, key=lambda x: x['dividend_yield'], reverse=True), 1):
        html += generate_stock_card_html(stock, idx, is_top5=False)

    html += """
        </div>
"""

    for sector, sector_stocks in sorted(sectors.items()):
        if sector != 'N/A':
            html += f'        <div id="tab-{sector}" class="tab-content">\n'
            html += f'            <h2 class="section-title">{sector} ({len(sector_stocks)}개)</h2>\n'
            for idx, stock in enumerate(sorted(sector_stocks, key=lambda x: x['total_score'], reverse=True), 1):
                html += generate_stock_card_html(stock, idx, is_top5=False)
            html += '        </div>\n'

    html += """
        <div class="footer">
            <p><strong>면책 조항</strong></p>
            <p>본 리포트는 투자 참고 자료이며, 투자 판단의 책임은 투자자 본인에게 있습니다.</p>
        </div>
    </div>

    <!-- 점수 기준 팝업 -->
    <div class="score-tooltip-overlay" id="scoreOverlay" onclick="hideScoreCriteria()"></div>
    <div class="score-tooltip" id="scoreTooltip">
        <button class="close-btn" onclick="hideScoreCriteria()">&times;</button>
        <h3 id="scoreTooltipTitle"></h3>
        <ul class="criteria-list" id="scoreTooltipContent"></ul>
    </div>

    <script>
        const scoreCriteria = {
            valuation: {
                title: '밥값+배당 점수 (45점 만점)',
                subtitle: '실체 있는 기업인가? + 배당 수익',
                criteria: [
                    { label: 'ROE/ROA (15점)', items: [
                        'ROE 20% 이상: 15점 (밥값 제대로 함)',
                        'ROE 15-20%: 12점',
                        'ROE 10-15%: 9점',
                        'ROE 5-10%: 6점',
                        'ROE 0-5%: 3점',
                        'ROE 음수: 0점 (도태 대상)'
                    ]},
                    { label: '영업이익률 (10점)', items: [
                        '20% 이상: 10점 (고마진)',
                        '15-20%: 8점',
                        '10-15%: 6점',
                        '5-10%: 4점',
                        '0-5%: 2점',
                        '음수: 0점'
                    ]},
                    { label: '성장성 + 흑자 (10점)', items: [
                        '매출 20% 성장 + 이익 10% 성장: 10점',
                        '매출 10% 성장 + 흑자: 8점',
                        '적자 + 고성장: 최대 3점',
                        '적자 + 저성장: 0점'
                    ]},
                    { label: '배당 (10점 추가)', items: [
                        '배당률 4% 이상: 10점 (고배당)',
                        '배당률 3-4%: 8점',
                        '배당률 2-3%: 6점',
                        '배당률 1-2%: 4점',
                        '배당률 0-1%: 2점',
                        '무배당: 0점'
                    ]}
                ]
            },
            technical: {
                title: '기술적 분석 점수 (25점 만점)',
                subtitle: '모멘텀 + 추세 + 평균회귀',
                criteria: [
                    { label: '모멘텀 (10점)', items: [
                        'RSI 과매수/과매도 구간 분석',
                        'MACD 시그널 교차',
                        '가격 모멘텀 강도'
                    ]},
                    { label: '평균회귀 (7점)', items: [
                        '볼린저 밴드 위치',
                        '이동평균선 괴리율',
                        '과매도 반등 시그널'
                    ]},
                    { label: '추세 (8점)', items: [
                        '이동평균선 배열 (골든/데드크로스)',
                        '추세선 지지/저항',
                        'ADX 추세 강도'
                    ]}
                ]
            },
            stability: {
                title: '안정성 점수 (15점 만점)',
                subtitle: '변동성과 시장 민감도',
                criteria: [
                    { label: '변동성 (7점) - 낮을수록 좋음', items: [
                        '연간 변동성 15% 이하: 7점 (매우 안정)',
                        '변동성 15-20%: 6점',
                        '변동성 20-25%: 5점 (보통)',
                        '변동성 25-30%: 3점',
                        '변동성 30-40%: 1점',
                        '변동성 40% 이상: 0점 (고위험)'
                    ]},
                    { label: '베타 (8점) - 1 이하가 방어적', items: [
                        '베타 0.5 이하: 8점 (방어주)',
                        '베타 0.5-0.8: 7점 (저베타)',
                        '베타 0.8-1.0: 5점 (시장 수준)',
                        '베타 1.0-1.2: 3점 (고베타)',
                        '베타 1.2 이상: 1점 (매우 공격적)'
                    ]}
                ]
            },
            policy: {
                title: '정책 수혜 점수 (15점 만점)',
                subtitle: '미국 정부 정책 수혜 (20점→15점 스케일)',
                criteria: [
                    { label: 'CHIPS Act (4.5점)', items: [
                        'INTC: 4.5점 (보조금 $85억)',
                        'TSM: 3.75점 (보조금 $66억)',
                        'MU: 3점 (보조금 $61억)',
                        '반도체 장비 산업: 3.75점'
                    ]},
                    { label: 'IRA 인플레이션 감축법 (4.5점)', items: [
                        'TSLA/GM/F: EV 세액공제 적격',
                        'FSLR: 태양광 제조 세액공제',
                        'NEE: 재생에너지 ITC/PTC',
                        'Electric Utilities: 2.25점'
                    ]},
                    { label: '방산 예산 NDAA (3점)', items: [
                        'LMT: 3점 (DoD 1위 $75B+)',
                        'RTX/GD/BA/NOC: 3점 (DoD Top 5)',
                        'Aerospace & Defense 산업: 2.25점'
                    ]},
                    { label: '인프라법 IIJA (3점)', items: [
                        'CAT: 3점 (건설장비 점유율 40%+)',
                        'VMC/MLM: 골재/시멘트 수혜',
                        'Construction Machinery: 3점',
                        '도로/교량 $110B, 전력망 $65B'
                    ]}
                ]
            }
        };

        function showScoreCriteria(type) {
            const data = scoreCriteria[type];
            if (!data) return;

            document.getElementById('scoreTooltipTitle').innerHTML = data.title + '<div style="font-size: 0.7em; color: #94a3b8; margin-top: 5px;">' + data.subtitle + '</div>';

            let html = '';
            data.criteria.forEach(section => {
                html += '<li class="section-header">' + section.label + '</li>';
                section.items.forEach(item => {
                    html += '<li style="padding-left: 15px;">' + item + '</li>';
                });
            });

            document.getElementById('scoreTooltipContent').innerHTML = html;
            document.getElementById('scoreOverlay').classList.add('show');
            document.getElementById('scoreTooltip').classList.add('show');
        }

        function hideScoreCriteria() {
            document.getElementById('scoreOverlay').classList.remove('show');
            document.getElementById('scoreTooltip').classList.remove('show');
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') hideScoreCriteria();
        });

        function showTab(tabName) {
            var contents = document.getElementsByClassName('tab-content');
            for (var i = 0; i < contents.length; i++) {
                contents[i].classList.remove('active');
            }
            var tabs = document.getElementsByClassName('tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }

        function toggleOtherStocks() {
            var el = document.getElementById('other-stocks');
            var text = document.getElementById('show-more-text');
            if (el.classList.contains('show')) {
                el.classList.remove('show');
                text.textContent = '나머지 종목 보기';
            } else {
                el.classList.add('show');
                text.textContent = '접기';
            }
        }
    </script>
</body>
</html>
"""

    return html


def main():
    """메인 함수"""
    print("가치주/배당주 추천 리포트 생성 중...\n")

    tickers = get_value_tickers()

    if tickers is None:
        print("종목 목록을 불러올 수 없습니다.")
        return

    print(f"분석 대상: {len(tickers)}개 종목\n")

    MAX_WORKERS = 10
    BATCH_SIZE = 25
    BATCH_DELAY = 2.0

    stocks_data = []
    failed_count = 0
    total = len(tickers)

    print(f"병렬 처리: {MAX_WORKERS}개 스레드\n")

    batches = [tickers[i:i + BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]

    processed = 0
    for batch_idx, batch in enumerate(batches):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(analyze_value_stock, ticker): ticker for ticker in batch}

            for future in concurrent.futures.as_completed(futures):
                ticker = futures[future]
                try:
                    result = future.result(timeout=30)
                    if result:
                        stocks_data.append(result)
                    else:
                        failed_count += 1
                except Exception as e:
                    print(f"[ERROR] {ticker}: {e}")
                    failed_count += 1

        processed += len(batch)
        print(f"[배치 {batch_idx + 1}/{len(batches)}] {processed}/{total} (성공: {len(stocks_data)}, 실패: {failed_count})")

        if batch_idx < len(batches) - 1:
            time.sleep(BATCH_DELAY)

    if stocks_data:
        print(f"\n총 {len(stocks_data)}개 종목 분석 완료!")

        # 45점 이상만 포함
        before_filter = len(stocks_data)
        stocks_data = [s for s in stocks_data if s['total_score'] >= 45]
        filtered_out = before_filter - len(stocks_data)
        if filtered_out > 0:
            print(f"[제외] {filtered_out}개 종목 (45점 미만)")
        print(f"[추천 대상] {len(stocks_data)}개 종목")

        html_content = generate_html_report(stocks_data)

        # GitHub Actions용: 고정 파일명 사용
        filename = "value_report.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n리포트 생성 완료: {filename}")
    else:
        print("\n분석된 종목이 없습니다.")


if __name__ == '__main__':
    main()
