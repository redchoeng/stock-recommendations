# FMP API 사용 결과 및 대안

## 결론

**FMP 무료 플랜은 뉴스 API를 지원하지 않습니다.**

대신 **Yahoo Finance API (무료)**를 사용하여 뉴스 감성 분석을 구현했습니다.

---

## FMP API 테스트 결과

### 가입 정보
- API 키: `DNkdgbD5DhfuAsO0OF1d5XfumWJFIfVB`
- 플랜: 무료 (250 calls/day)

### 테스트 결과 (2026-02-02)
```
[1] API 상태 확인
  [ERROR] 403 Forbidden - 엔드포인트 사용 불가

[2] 뉴스 API 테스트
  [ERROR] 403 Forbidden - 뉴스 API는 무료 플랜에서 제한됨
```

### 원인
FMP는 2025년 8월 31일부터 레거시 엔드포인트를 중단했고, 무료 플랜에서는 뉴스 API 접근이 차단됩니다.

---

## 해결 방법: Yahoo Finance 사용 (채택)

### 장점
- ✅ **완전 무료**
- ✅ **충분한 뉴스 데이터** (종목당 10~20개)
- ✅ **이미 구현 완료** (news_sentiment_analyzer.py)
- ✅ **yfinance 라이브러리 기반** (안정적)

### 단점 및 해결
| 문제 | 해결책 |
|-----|--------|
| 하루 2000 calls 제한 | 14일 리밸런싱 (50종목 × 26주 = 1,300 calls) |
| 속도 제한 | 0.5초 딜레이 추가 |
| 뉴스 개수 적음 | TextBlob으로 충분히 분석 가능 |

---

## 구현된 파일

### 1. news_sentiment_analyzer.py
Yahoo Finance 기반 뉴스 감성 분석 엔진

```python
from quant_trading.news_sentiment_analyzer import NewsSentimentAnalyzer

analyzer = NewsSentimentAnalyzer('AAPL')
result = analyzer.calculate_news_score()
# {
#   'total_score': 14.8,  # 20점 만점
#   'news_count': 8,
#   'avg_sentiment': 0.42,
#   'positive_ratio': 0.75
# }
```

### 2. backtest_news_quick.py (실행 중)
2개월, 20종목 빠른 테스트

**설정**:
- 기간: 2개월
- 종목: 20개
- 리밸런싱: 14일
- API 호출: ~80 calls (안전)

**실행**:
```bash
python backtest_news_quick.py
```

### 3. backtest_with_news.py
1년, 50종목 전체 백테스팅

**설정**:
- 기간: 1년
- 종목: 50개
- 리밸런싱: 7일 (또는 14일 권장)

---

## 다른 무료 뉴스 API 옵션

### NewsAPI.org
```
무료: 100 calls/day
가입: https://newsapi.org/register
장점: 다양한 소스, 실시간
단점: 상업용 제한, 적은 무료 한도
```

### Alpha Vantage
```
무료: 25 calls/day
가입: https://www.alphavantage.co/
장점: 금융 데이터 특화
단점: 매우 적은 무료 한도
```

### Finnhub
```
무료: 60 calls/minute
가입: https://finnhub.io/
장점: 실시간 뉴스, WebSocket 지원
단점: 기본 뉴스만 무료
```

---

## 비용 비교

| API | 무료 한도 | 뉴스 지원 | 유료 비용 | 추천도 |
|-----|----------|---------|---------|--------|
| **Yahoo Finance** | **~2000/day** | **✅** | **무료** | **★★★** |
| FMP | 250/day | ❌ (유료만) | $14/month | ★☆☆ |
| NewsAPI | 100/day | ✅ | $449/month | ★★☆ |
| Alpha Vantage | 25/day | ✅ | $49.99/month | ★☆☆ |
| Finnhub | 60/min | ✅ (제한) | $39.99/month | ★★☆ |

---

## 최종 권장 사항

### 현재 상황
1. ✅ Yahoo Finance 구현 완료
2. ✅ TextBlob 감성 분석 설치 완료
3. ✅ 백테스트 스크립트 준비 완료
4. 🚀 **소규모 테스트 실행 중**

### 추천 순서
1. **지금**: 2개월 테스트 결과 확인 (backtest_news_quick.py)
2. **결과 좋으면**: 1년 전체 백테스팅 (backtest_with_news.py)
3. **실전 적용**: GitHub Actions에 뉴스 감성 통합

### API 제한 대응
```python
# 14일 리밸런싱으로 설정 (권장)
rebalance_days = 14

# 필요 API 호출: 50종목 × 26주 = 1,300 calls
# Yahoo Finance 한도: ~2,000 calls/day
# 결과: ✅ 안전하게 실행 가능
```

---

## FMP API 키 활용 방안

비록 뉴스는 안 되지만, FMP API는 다른 용도로 활용 가능:

### 1. 가격 데이터 (무료)
```python
import requests

url = f"https://financialmodelingprep.com/api/v3/quote/AAPL?apikey={FMP_API_KEY}"
response = requests.get(url)
price = response.json()[0]['price']
```

### 2. 재무 제표 (무료, 제한적)
```python
url = f"https://financialmodelingprep.com/api/v3/income-statement/AAPL?apikey={FMP_API_KEY}"
```

### 3. 향후 업그레이드 옵션
만약 전략이 성공하면 $14/month 유료 플랜 고려:
- 뉴스 API 무제한
- 더 많은 뉴스 소스
- 본문 전체 분석 가능

---

## 결론

**Yahoo Finance API가 최선의 무료 옵션입니다.**

- ✅ 무료
- ✅ 안정적
- ✅ 충분한 데이터
- ✅ 이미 구현 완료

**지금 진행 중인 백테스트로 성과를 확인하고, 좋으면 전체 시스템에 통합하면 됩니다!**
