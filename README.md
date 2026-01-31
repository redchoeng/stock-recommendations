# 📊 Daily Stock Recommendations

검증된 퀀트 전략 기반 주식 추천 시스템

## 🌐 웹페이지 보기

👉 [최신 리포트 보기](https://[username].github.io/stock-recommendations/)

*(username을 본인 GitHub 사용자명으로 변경)*

## 📈 특징

### 검증된 학술 전략
- **Momentum**: Jegadeesh & Titman (1993)
- **Mean Reversion**: De Bondt & Thaler (1985)
- **Trend Following**: Hurst et al. (2013)
- **Low Volatility**: Ang et al. (2006)

### 제공 정보
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
