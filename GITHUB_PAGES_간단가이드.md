# 🚀 GitHub Pages 초간단 설정 가이드

## 준비물
- ✅ GitHub 계정 (없으면 https://github.com 에서 가입)
- ✅ Git 설치 (https://git-scm.com/download/win)

---

## 📝 3단계로 완료하기

### ✨ 1단계: GitHub에서 리포지토리 생성 (2분)

1. **GitHub 접속**: https://github.com/new

2. **리포지토리 정보 입력**:
   ```
   Repository name: stock-recommendations
   Description: Daily Stock Recommendations
   ```

3. **Public 선택** (중요! Private는 유료)

4. **Create repository 클릭**

---

### 💻 2단계: 로컬에서 업로드 (3분)

**명령 프롬프트(CMD) 또는 PowerShell 열기**

```bash
# 1. 프로젝트 폴더로 이동
cd "c:\Users\niceh\새 폴더\finance-datareader"

# 2. Git 초기화 (처음 한 번만)
git init
git branch -M main

# 3. 파일 추가
git add daily_stock_report_20260131.html
git add README.md
git add .github/

# 4. 커밋
git commit -m "First commit: Daily stock recommendations"

# 5. GitHub 연결 (본인 username으로 변경!)
git remote add origin https://github.com/[본인username]/stock-recommendations.git

# 6. 업로드
git push -u origin main
```

**⚠️ 주의**: `[본인username]` 부분을 본인 GitHub 사용자명으로 바꾸세요!

**예시**:
```bash
git remote add origin https://github.com/johndoe/stock-recommendations.git
```

---

### 🌐 3단계: GitHub Pages 활성화 (1분)

1. **GitHub 리포지토리로 이동**:
   ```
   https://github.com/[본인username]/stock-recommendations
   ```

2. **Settings 클릭** (오른쪽 상단)

3. **왼쪽 메뉴에서 Pages 클릭**

4. **설정**:
   ```
   Source: Deploy from a branch
   Branch: main
   Folder: / (root)
   ```

5. **Save 클릭**

6. **완료!** 🎉

---

## ✅ 접속하기

**1-2분 후** 다음 주소로 접속:

```
https://[본인username].github.io/stock-recommendations/daily_stock_report_20260131.html
```

**또는 간단히**:
```
https://[본인username].github.io/stock-recommendations/
```

---

## 🔄 매일 자동 업데이트 설정 (선택사항)

위 3단계까지만 해도 웹페이지가 만들어집니다!

매일 자동으로 최신 리포트를 생성하려면:

1. **GitHub 리포지토리 > Actions 탭**

2. **"I understand my workflows, go ahead and enable them" 클릭**

3. **완료!** 매일 자동으로 새 리포트 생성됨

---

## 🆘 문제 해결

### Git이 없다고 나올 때
```bash
# Git 설치 확인
git --version

# 없으면 다운로드: https://git-scm.com/download/win
```

### Push할 때 인증 오류
```bash
# GitHub Personal Access Token 필요
# 1. GitHub > Settings > Developer settings > Personal access tokens
# 2. Generate new token (classic)
# 3. repo 권한 체크
# 4. 생성된 토큰을 비밀번호 대신 사용
```

### 파일이 보이지 않을 때
```bash
# 1-2분 기다리기
# 브라우저 새로고침 (Ctrl+F5)
```

---

## 📱 최종 결과

✅ **24시간 접속 가능**
✅ **무료**
✅ **모바일에서도 접속 가능**
✅ **HTTPS 보안 연결**
✅ **매일 자동 업데이트** (GitHub Actions 활성화 시)

---

## 🎯 요약 (30초 버전)

```bash
# 1. GitHub에서 리포지토리 생성 (stock-recommendations)

# 2. CMD에서 실행
cd "c:\Users\niceh\새 폴더\finance-datareader"
git init
git add .
git commit -m "First commit"
git remote add origin https://github.com/[username]/stock-recommendations.git
git push -u origin main

# 3. GitHub > Settings > Pages > Branch: main > Save

# 완료!
```

---

## 💡 다음 번 업데이트 방법

새 리포트를 만들었을 때:

```bash
cd "c:\Users\niceh\새 폴더\finance-datareader"
git add daily_stock_report_*.html
git commit -m "Update report"
git push
```

1-2분 후 웹페이지에 자동 반영됨!

---

**문제가 있으면 언제든지 물어보세요!** 🙋‍♂️
