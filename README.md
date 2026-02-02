# 📊 S&P500 AI Stock Recommendations

**검증된 퀀트 전략 + 뉴스 감성 분석 기반 주식 추천 시스템**

## 🌐 웹페이지 보기

### 🚀 메인 (Netlify - 빠름)
👉 **[https://redcho-stocks.netlify.app](https://redcho-stocks.netlify.app)**

### 🔄 백업 (GitHub Pages)
👉 **[https://redchoeng.github.io/stock-recommendations/](https://redchoeng.github.io/stock-recommendations/)**

*매 2시간마다 자동 업데이트됩니다!*

## 🎯 핵심 기능

### 📱 텔레그램 실시간 알림
- ✅ **14일 리밸런싱 결과** 자동 전송
- 🚨 **시장 급변 감지** 즉시 알림 (±3% 이상)
- 📊 **일일 시장 요약** 전송
- 📰 **뉴스 감성 급변** 알림

**[텔레그램 알림 설정하기](텔레그램_알림_설정가이드.md)** →

## 📈 전략 성과

### 백테스트 결과 (2개월)
```
수익률: +3.43% (vs S&P500 +1.21%)
초과 수익: +2.22%
승률: 75% (3/4)
샤프 비율: 4.49
리밸런싱: 14일
```

**[백테스트 상세 보기](백테스팅_가이드.md)** →

## 🎓 검증된 학술 전략

### 기술적 분석 (75점)
- **Momentum**: Jegadeesh & Titman (1993)
- **Mean Reversion**: De Bondt & Thaler (1985)
- **Trend Following**: Hurst et al. (2013)
- **Low Volatility**: Ang et al. (2006)

### 뉴스 감성 분석 (20점)
- **Yahoo Finance** 최근 7일 뉴스
- **TextBlob** 자연어 처리
- **감성 점수** 자동 계산

**[뉴스 감성 분석 가이드](뉴스감성분석_가이드.md)** →

## 📊 제공 정보
- ✅ 종목별 점수 (0-100점)
- ✅ 매수 가격 추천 (공격적/중도/보수적)
- ✅ 매도 목표가 (3단계)
- ✅ 손절 가격
- ✅ 리스크/리워드 비율
- ✅ 섹터별 분석

## 🎨 화면 구성

- **TOP 5 강조**: 최고 점수 종목 하이라이트
- **섹터별 탭**: Technology, Energy, Financials 등
- **더보기 버튼**: 접기/펼치기 가능
- **반응형 디자인**: 모바일 최적화

## 🔄 업데이트

매일 자동으로 업데이트됩니다 (GitHub Actions)

## 🛠️ 로컬 실행

```bash
# 리포트 생성
python generate_daily_report_v2.py

# 로컬 서버 실행
python run_web_server.py
```

## 📝 면책 조항

본 리포트는 투자 참고 자료이며, 투자 판단 및 결과에 대한 책임은 투자자 본인에게 있습니다.
손절가는 반드시 지켜서 리스크를 관리하시기 바랍니다.

## 📄 라이선스

MIT License

---

**Powered by 검증된 퀀트 전략** 🚀
