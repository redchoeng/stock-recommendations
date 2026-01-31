"""
퀀트 트레이딩 시스템 간단한 데모
pandas-ta 없이 기본 pandas로 작동하는 버전
"""

import yfinance as yf
import pandas as pd
from datetime import datetime


def simple_technical_score(df):
    """
    간단한 기술적 분석 점수 (pandas-ta 없이)
    """
    score = 0
    signals = []

    # 이동평균선 계산
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_60'] = df['Close'].rolling(window=60).mean()

    # 최근 데이터
    recent = df.iloc[-1]
    prev = df.iloc[-2]

    # 골든크로스 확인
    if prev['SMA_20'] <= prev['SMA_60'] and recent['SMA_20'] > recent['SMA_60']:
        score += 10
        signals.append("골든크로스")

    # RSI 계산 (14일)
    try:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # RSI 과매도 탈출
        if not pd.isna(prev.get('RSI')) and not pd.isna(recent.get('RSI')):
            if prev['RSI'] <= 30 and recent['RSI'] > 30:
                score += 10
                signals.append("RSI Oversold Exit")
    except Exception as e:
        pass  # RSI 계산 실패 시 무시

    # 상승 추세 확인 (최근 5일)
    if df['Close'].iloc[-5:].is_monotonic_increasing:
        score += 5
        signals.append("상승 추세")

    return score, ' + '.join(signals) if signals else '시그널 없음'


def analyze_stock(ticker):
    """
    개별 종목 간단 분석
    """
    print(f"\n{'='*60}")
    print(f"종목 분석: {ticker}")
    print(f"{'='*60}\n")

    try:
        # 데이터 다운로드
        stock = yf.Ticker(ticker)
        df = stock.history(period='6mo')

        if df.empty:
            print(f"[ERROR] {ticker} 데이터를 가져올 수 없습니다.")
            return None

        # 종목 정보
        info = stock.info
        name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')

        print(f"종목명: {name}")
        print(f"섹터: {sector}")
        print(f"산업: {industry}")
        print(f"현재가: ${df['Close'].iloc[-1]:.2f}")

        # 기술적 분석
        tech_score, signals = simple_technical_score(df)

        print(f"\n기술적 점수: {tech_score}점")
        print(f"시그널: {signals}")

        # 테마 점수 (간단히)
        theme_score = 0
        if any(keyword in sector for keyword in ['Energy', 'Technology', 'Defense']):
            theme_score = 25
            print(f"테마 점수: {theme_score}점 (트럼프 수혜 섹터)")

        total = tech_score + theme_score
        print(f"\n총점: {total}점")

        if total >= 80:
            print("[BUY] Strong Buy Recommendation!")
        elif total >= 70:
            print("[WATCH] Watch List")
        else:
            print("[PASS] Pass")

        return {
            'Ticker': ticker,
            'Name': name,
            'Sector': sector,
            'Total_Score': total,
            'Tech_Score': tech_score,
            'Theme_Score': theme_score,
            'Signals': signals
        }

    except Exception as e:
        print(f"[ERROR] 분석 실패: {e}")
        return None


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("Quant Trading System - Simple Demo")
    print("="*60)

    # 분석할 종목 리스트
    tickers = ['AAPL', 'NVDA', 'TSLA', 'XOM', 'LMT']

    results = []

    for ticker in tickers:
        result = analyze_stock(ticker)
        if result:
            results.append(result)

    # 결과 요약
    if results:
        print(f"\n\n{'='*60}")
        print("Analysis Results Summary")
        print(f"{'='*60}\n")

        df = pd.DataFrame(results)
        df = df.sort_values('Total_Score', ascending=False)

        print(df[['Ticker', 'Name', 'Total_Score', 'Tech_Score', 'Theme_Score']].to_string(index=False))

        # 추천 종목
        recommendations = df[df['Total_Score'] >= 70]

        if not recommendations.empty:
            print(f"\n\n{'='*60}")
            print(f"[RECOMMENDATIONS] (70+ points): {len(recommendations)} stocks")
            print(f"{'='*60}\n")

            print(recommendations[['Ticker', 'Name', 'Total_Score', 'Signals']].to_string(index=False))

    print("\n" + "="*60)
    print("[SUCCESS] Demo Completed!")
    print("="*60 + "\n")

    print("[NOTE] To use full features:")
    print("   1. pandas-ta 라이브러리 설치 필요")
    print("   2. Python 3.10-3.13 버전 권장")
    print("   3. run_stock_recommender.py 실행")


if __name__ == '__main__':
    main()
