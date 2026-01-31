# 🌐 GitHub Pages 활성화 가이드

## 📋 1회만 설정하면 평생 자동 업데이트!

---

## ✅ Step 1: GitHub 저장소 접속

브라우저에서 아래 링크를 열어주세요:

👉 **https://github.com/redchoeng/stock-recommendations**

---

## ✅ Step 2: Settings 메뉴 이동

1. 저장소 페이지 상단의 **"Settings"** 탭 클릭
2. 왼쪽 사이드바에서 **"Pages"** 클릭

---

## ✅ Step 3: GitHub Pages 설정

### Source 섹션:
- **Source**: `Deploy from a branch` 선택

### Branch 섹션:
- **Branch**: `main` 선택
- **Folder**: `/ (root)` 선택
- **Save** 버튼 클릭

---

## ✅ Step 4: 배포 완료 대기

- 1-2분 후 페이지를 새로고침하면 배포 완료!
- 초록색 체크 표시와 함께 링크가 표시됩니다:

```
Your site is live at https://redchoeng.github.io/stock-recommendations/
```

---

## 🎉 완료! 이제 접속하세요

**웹페이지 주소:**
https://redchoeng.github.io/stock-recommendations/

**스마트폰에서도 접속 가능!**
- 위 링크를 북마크하세요
- 매 2시간마다 자동 업데이트됩니다
- PC가 꺼져있어도 GitHub에서 자동 실행

---

## 🔄 자동 업데이트 원리

```
매 2시간마다 (00분, 02시, 04시, ...)
    ↓
GitHub Actions 자동 실행
    ↓
generate_daily_report_v2.py 실행
    ↓
HTML 리포트 생성
    ↓
GitHub에 자동 커밋/푸시
    ↓
GitHub Pages 자동 배포
    ↓
웹페이지 업데이트 완료! 🎉
```

---

## 📱 모바일 접속 방법

### iPhone (Safari):
1. https://redchoeng.github.io/stock-recommendations/ 접속
2. 하단 공유 버튼 → "홈 화면에 추가"
3. 앱처럼 사용 가능!

### Android (Chrome):
1. https://redchoeng.github.io/stock-recommendations/ 접속
2. 메뉴(⋮) → "홈 화면에 추가"
3. 앱처럼 사용 가능!

---

## 🔧 문제 해결

### Q: GitHub Pages 링크가 404 에러
**A:** 2-3분 기다린 후 새로고침. 첫 배포는 시간이 걸립니다.

### Q: 데이터가 업데이트 안돼요
**A:** GitHub Actions 확인:
- https://github.com/redchoeng/stock-recommendations/actions
- 초록색 체크: 성공 / 빨간색 X: 실패

### Q: Actions 실패 시
**A:**
1. Actions 탭에서 실패한 작업 클릭
2. 에러 로그 확인
3. 대부분 yfinance API 제한 → 1-2시간 후 자동 재실행

### Q: 수동으로 실행하고 싶어요
**A:**
1. https://github.com/redchoeng/stock-recommendations/actions
2. 왼쪽 "Daily Stock Report Update" 클릭
3. 오른쪽 "Run workflow" → "Run workflow" 버튼

---

## 📊 실행 상태 모니터링

### Actions 페이지:
https://github.com/redchoeng/stock-recommendations/actions

### 확인 가능한 정보:
- ✅ 마지막 업데이트 시간
- ✅ 성공/실패 여부
- ✅ 실행 로그
- ✅ 다음 예정 시간

---

## 🎯 다음 단계

이제 설정이 완료되었습니다!

1. **북마크 저장**: https://redchoeng.github.io/stock-recommendations/
2. **모바일 홈 화면 추가** (선택사항)
3. **매 2시간마다 자동 업데이트 확인**

---

## 💡 추가 팁

### 카카오톡으로 링크 공유:
```
📊 내 주식 추천 시스템 (자동 업데이트)
https://redchoeng.github.io/stock-recommendations/
```

### 업데이트 주기 변경:
- 파일: `.github/workflows/daily-update.yml`
- `cron: '0 */2 * * *'` 수정
  - `*/2` → `*/3` (3시간마다)
  - `*/2` → `*/4` (4시간마다)

### 즉시 업데이트 원하면:
```bash
cd "c:\Users\niceh\새 폴더\finance-datareader"
python generate_daily_report_v2.py
git add .
git commit -m "Manual update"
git push
```

---

**🎉 설정 완료! 이제 언제 어디서나 최신 주식 추천을 확인하세요!**
