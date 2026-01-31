# 주식 추천 웹페이지 호스팅 가이드

## 질문: 내 컴퓨터가 켜져있을 때만 접속 가능한가요?

**네, 맞습니다!** 현재 `run_web_server.py`는 당신의 컴퓨터에서 실행되므로:
- ✅ 컴퓨터 **켜져 있을 때**: 접속 가능
- ❌ 컴퓨터 **꺼져 있을 때**: 접속 불가능

---

## 해결 방법: 24시간 접속 가능하게 만들기

### 옵션 1: 무료 호스팅 (추천!) ⭐

#### A. **GitHub Pages** (완전 무료, 가장 쉬움)
```bash
# 1. GitHub에 리포지토리 생성
# 2. HTML 파일 업로드
git add daily_stock_report_20260131.html
git commit -m "Add daily report"
git push

# 3. Settings > Pages에서 활성화
# 접속 주소: https://[username].github.io/[repo-name]/daily_stock_report_20260131.html
```

**장점**:
- 완전 무료
- 설정 간단
- HTTPS 자동 제공

**단점**:
- 정적 파일만 가능 (HTML만)
- 매일 수동으로 업데이트 필요

---

#### B. **Vercel** (무료, 자동 배포)
```bash
# 1. Vercel 가입: https://vercel.com
# 2. GitHub 연결
# 3. 자동 배포 설정

# 매일 자동 업데이트 설정 (GitHub Actions)
# .github/workflows/daily-update.yml 생성
name: Daily Update
on:
  schedule:
    - cron: '0 0 * * *'  # 매일 자정
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: python generate_daily_report_v2.py
      - run: git add . && git commit -m "Daily update" && git push
```

**장점**:
- 완전 무료
- 자동 배포
- 빠른 속도

---

#### C. **Netlify** (무료)
```bash
# 1. Netlify 가입
# 2. 프로젝트 연결
# 3. 자동 배포
```

---

### 옵션 2: 저렴한 VPS 호스팅 (월 $5~$10)

#### A. **DigitalOcean / Linode / Vultr**
```bash
# Ubuntu 서버 생성
# SSH 접속 후:
sudo apt update
sudo apt install python3 python3-pip

# 파일 업로드
scp *.py user@your-server-ip:/home/user/

# 서버 실행
cd /home/user
python3 run_web_server.py

# 백그라운드 실행 (서버 재시작해도 유지)
nohup python3 run_web_server.py &
```

**접속**: `http://서버IP:8000`

---

#### B. **AWS EC2 Free Tier** (1년 무료)
```bash
# 프리티어 계정 생성
# EC2 인스턴스 시작
# 위와 동일하게 설정
```

---

### 옵션 3: 클라우드 서비스 (무료 티어 있음)

#### A. **Python Anywhere** (무료 플랜)
```python
# 1. PythonAnywhere 가입
# 2. Web 탭에서 Flask 앱 생성
# 3. 코드 업로드
# 4. 자동으로 https://[username].pythonanywhere.com 생성됨
```

**장점**:
- 완전 무료 플랜 있음
- Python 환경 기본 제공
- 설정 간단

**단점**:
- 무료는 속도 제한 있음

---

#### B. **Render** (무료)
```bash
# 1. Render 가입
# 2. GitHub 연결
# 3. Web Service 생성
# 4. 자동 배포
```

---

### 옵션 4: 집 서버로 24시간 운영

#### 필요 사항:
1. **공유기 설정**:
   - 포트 포워딩: 외부 8000번 → 내부 PC IP:8000

2. **DDNS 설정** (IP 주소 고정):
   ```
   무료 DDNS 서비스:
   - NoIP (https://www.noip.com)
   - DuckDNS (https://www.duckdns.org)

   설정 후: http://yourname.ddns.net:8000
   ```

3. **방화벽 설정**:
   ```bash
   # Windows 방화벽에서 8000번 포트 허용
   ```

4. **자동 시작 설정**:
   ```
   Windows 작업 스케줄러:
   - 시작 프로그램: python run_web_server.py
   - 트리거: 시스템 시작 시
   ```

**장점**:
- 무료 (전기세만)
- 완전한 제어권

**단점**:
- 컴퓨터 24시간 켜둬야 함
- 전기세 발생
- 보안 위험

---

## 추천 순서 (상황별)

### 😀 초보자 / 무료로 시작:
1. **GitHub Pages** (가장 쉬움)
2. **Vercel** (자동화)
3. **Netlify**

### 💼 비즈니스 / 안정성 필요:
1. **DigitalOcean** ($5/월)
2. **AWS EC2**
3. **Google Cloud Run**

### 🏠 집에서 운영:
1. DDNS 설정
2. 포트 포워딩
3. 오래된 노트북 활용

---

## 빠른 시작: GitHub Pages로 배포하기

```bash
# 1. GitHub 계정 생성
# 2. 새 리포지토리 생성: stock-recommendations

# 3. 로컬에서 git 초기화
cd "c:\Users\niceh\새 폴더\finance-datareader"
git init
git add daily_stock_report_20260131.html
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/[username]/stock-recommendations.git
git push -u origin main

# 4. GitHub에서 Settings > Pages > Source를 main 브랜치로 설정

# 5. 완료! 접속 주소:
# https://[username].github.io/stock-recommendations/daily_stock_report_20260131.html
```

---

## 매일 자동 업데이트 (GitHub Actions)

`.github/workflows/daily-report.yml` 파일 생성:

```yaml
name: Daily Stock Report

on:
  schedule:
    - cron: '0 15 * * 1-5'  # 매일 오전 0시 (UTC+9 = 오전 9시)
  workflow_dispatch:  # 수동 실행 가능

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install yfinance pandas numpy

      - name: Generate report
        run: |
          python generate_daily_report_v2.py

      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add daily_stock_report_*.html
          git commit -m "Daily report update" || exit 0
          git push
```

이제 **매일 자동으로** 새 리포트가 생성되고 웹페이지가 업데이트됩니다! 🎉

---

## 요약

| 방법 | 비용 | 난이도 | 24시간 | 자동화 |
|------|------|--------|--------|--------|
| 로컬 서버 | 무료 | 쉬움 | ❌ | ❌ |
| GitHub Pages | 무료 | 쉬움 | ✅ | ⭐ |
| Vercel | 무료 | 쉬움 | ✅ | ✅ |
| VPS | $5/월 | 중간 | ✅ | ✅ |
| 집 서버 | 전기세 | 어려움 | ✅ | ✅ |

**가장 추천**: GitHub Pages + GitHub Actions = 무료 + 자동화! 🚀
