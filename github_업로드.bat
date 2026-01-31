@echo off
chcp 65001
echo ========================================
echo GitHub Pages 자동 업로드
echo ========================================
echo.

set /p USERNAME="GitHub 사용자명 입력: "
set REPO=stock-recommendations

echo.
echo 리포지토리: https://github.com/%USERNAME%/%REPO%
echo.
pause

echo.
echo [1/5] Git 초기화...
git init
git branch -M main

echo.
echo [2/5] 파일 추가...
git add daily_stock_report_*.html
git add index.html
git add README.md
git add .github/

echo.
echo [3/5] 커밋...
git commit -m "First commit: Daily stock recommendations"

echo.
echo [4/5] GitHub 연결...
git remote remove origin 2>nul
git remote add origin https://github.com/%USERNAME%/%REPO%.git

echo.
echo [5/5] 업로드...
git push -u origin main

echo.
echo ========================================
echo 완료!
echo ========================================
echo.
echo 이제 GitHub에서 Settings 클릭하세요:
echo https://github.com/%USERNAME%/%REPO%/settings/pages
echo.
echo Source: Deploy from a branch
echo Branch: main
echo Folder: / (root)
echo Save 클릭!
echo.
echo 몇 분 후 접속:
echo https://%USERNAME%.github.io/%REPO%/
echo.
pause
