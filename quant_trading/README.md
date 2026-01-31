# 퀀트 트레이딩 주식 추천 시스템

기술적 분석과 테마 분석을 결합하여 미국 주식(S&P500/NASDAQ)을 자동으로 분석하고 점수화하여 매수 추천 종목을 제공하는 시스템입니다.

## 특징

### 점수 체계 (총 100점)

**1. 기술적 분석 (75점)**
- 이동평균선 및 추세 (15점): 골든크로스, 정배열
- 일목균형표 (20점): 구름대 돌파, 눌림목
- 채널 및 변동성 (10점): 볼린저/켈트너 채널
- 스토캐스틱 (15점): 멀티 타임프레임 바닥 매수
- RSI (15점): 다이버전스, 과매도 탈출

**2. 테마 분석 (25점)**
- 트럼프 정책 수혜 섹터: 원전, 에너지, 방산, AI, 금융
- 뉴스 센티먼트: 최근 3일 긍정 뉴스

### 추천 기준
- **80점 이상**: 강력 매수 추천
- **70-79점**: 매수 관심 종목
- **70점 미만**: 관망

## 설치

### 필수 라이브러리
```bash
pip install yfinance pandas-ta beautifulsoup4 lxml pandas numpy
```

## 사용법

### 1. 메인 추천 시스템 실행

```bash
# S&P500 종목 30개 분석 (기본)
python run_stock_recommender.py

# NASDAQ 종목 50개 분석
python run_stock_recommender.py --market nasdaq --max-stocks 50

# 최소 점수 70점으로 설정
python run_stock_recommender.py --min-score 70

# 결과 파일명 지정
python run_stock_recommender.py --output my_recommendations.csv
```

### 2. Python 코드에서 사용

```python
from quant_trading import StockRecommender

# 추천 시스템 생성 (최소 80점)
recommender = StockRecommender(min_score=80)

# S&P500 종목 가져오기
tickers = recommender.get_sp500_tickers()

# 상위 30개 종목 분석
df = recommender.analyze_stocks(tickers, max_stocks=30)

# 추천 종목 필터링
recommendations = recommender.get_recommendations(df)

# 결과 출력
print(recommendations)

# CSV 저장
recommender.export_to_csv(recommendations, 'my_stocks.csv')
```

### 3. 개별 종목 분석

```python
from quant_trading import StockScorer

# Apple 분석
scorer = StockScorer('AAPL', period='6mo')
scorer.fetch_data()
result = scorer.calculate_score()

print(f"총점: {result['Total_Score']}점")
print(f"시그널: {result['Signal_Type']}")
```

## 클래스 구조

### 1. TechnicalAnalyzer
기술적 지표 계산 및 점수화
- pandas-ta 라이브러리 활용
- 5가지 핵심 지표 분석

### 2. ThemeAnalyzer
테마 및 뉴스 분석
- yfinance를 통한 종목 정보/뉴스 수집
- 섹터/산업 키워드 매칭
- 뉴스 센티먼트 분석

### 3. StockScorer
개별 종목 점수 계산
- 기술적 + 테마 점수 통합
- 시그널 생성

### 4. StockRecommender
대량 종목 분석 및 추천
- S&P500/NASDAQ 종목 리스트
- 병렬 분석 처리
- 결과 필터링 및 export

## 출력 예시

```
============================================================
📊 분석 결과 요약
============================================================
총 분석 종목 수: 30
평균 점수: 52.3점
최고 점수: 87점 (NVDA)
최저 점수: 23점

점수 분포:
  90점 이상: 0개
  80-89점: 3개
  70-79점: 7개
  70점 미만: 20개
============================================================

📊 추천 종목: 3개 (최소 80점 이상)
============================================================

📌 추천 종목 상세:
------------------------------------------------------------
Ticker  Total_Score  Tech_Score  Theme_Score  Matched_Theme  Signal_Type
NVDA    87           62          25           AI/Data Center RSI 과매도 탈출 + 테마: AI/Data Center
LMT     84           59          25           Defense        골든크로스 + 일목 눌림목 + 테마: Defense
XOM     82           57          25           Oil/Gas        채널 하단 반등 + 테마: Oil/Gas
------------------------------------------------------------
```

## 알고리즘 상세

### 기술적 분석 로직

#### 1. 이동평균선 (15점)
```python
# 골든크로스: SMA20 > SMA60 돌파 (+10점)
if 20일선 상향돌파 60일선:
    score += 10

# 정배열: SMA5 > SMA20 > SMA60 > SMA120 (+5점)
if 정배열 상태:
    score += 5
```

#### 2. 일목균형표 (20점)
```python
# 강력 돌파: 주가가 구름대 상단 돌파 + 거래량 150% 이상 (+10점)
if (Close > 선행스팬B) and (Volume >= 전일*1.5):
    score += 10

# 눌림목: 구름대 위 + 전환선/기준선 지지 + 양봉 (+10점)
if 구름대_위 and (전환선_터치 or 기준선_터치) and 양봉:
    score += 10
```

#### 3. 스토캐스틱 (15점)
```python
# 바닥 잡기: 중기&장기 침체권 + 단기 골든크로스 (+15점)
if (중기%K <= 20) and (장기%K <= 20) and (단기골든크로스):
    score += 15
```

#### 4. RSI (15점)
```python
# 상승 다이버전스: 주가 신저가 + RSI 저점 상승 (+15점)
if (주가저점 < 이전저점) and (RSI저점 > 이전RSI저점):
    score += 15

# 과매도 탈출: RSI 30 이하 → 30 초과 (+10점)
if (이전RSI <= 30) and (현재RSI > 30):
    score += 10
```

### 테마 분석 로직

```python
# 트럼프 수혜 섹터 매칭 (+25점)
if 종목.섹터 in ['Energy', 'Defense', 'Nuclear', ...]:
    score += 25

# 긍정 뉴스 가산점 (최대 +5점)
if 긍정뉴스 >= 3:
    score += 5
```

## 주의사항

1. **API 호출 제한**: yfinance는 무료 API이므로 과도한 호출 시 차단될 수 있음
2. **데이터 품질**: 일부 종목은 데이터가 부족하거나 부정확할 수 있음
3. **투자 판단**: 본 시스템은 참고용이며, 최종 투자 판단은 본인 책임
4. **실시간 데이터 아님**: 15-20분 지연된 데이터 사용

## 라이선스

MIT License

## 기여

버그 리포트 및 기능 제안은 이슈 트래커로 제출해주세요.
