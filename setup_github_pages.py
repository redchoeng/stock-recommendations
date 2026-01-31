"""
GitHub Pages 자동 설정 스크립트
"""

import os
import subprocess
import webbrowser


def run_command(command, description=""):
    """명령어 실행"""
    if description:
        print(f"\n[단계] {description}")
    print(f"실행: {command}")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"[오류] {result.stderr}")
        return False


def setup_github_pages():
    """GitHub Pages 설정"""

    print("\n" + "="*70)
    print("GitHub Pages 자동 설정")
    print("="*70 + "\n")

    # 1. 사용자 정보 입력
    print("GitHub 정보를 입력하세요:\n")
    github_username = input("GitHub 사용자명: ").strip()
    repo_name = input("리포지토리 이름 (예: stock-recommendations): ").strip() or "stock-recommendations"

    print(f"\n리포지토리: https://github.com/{github_username}/{repo_name}")
    confirm = input("계속하시겠습니까? (y/n): ").strip().lower()

    if confirm != 'y':
        print("취소되었습니다.")
        return

    print("\n" + "="*70)
    print("설정 시작...")
    print("="*70)

    # 2. Git 초기화
    if not os.path.exists('.git'):
        run_command('git init', 'Git 초기화')
        run_command('git branch -M main', 'Main 브랜치 생성')
    else:
        print("\n[정보] Git이 이미 초기화되어 있습니다.")

    # 3. .gitignore 생성
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Data
*.csv
*.xlsx
*.pkl

# Logs
*.log

# 임시 파일
*.tmp
*.bak
"""

    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content.strip())

    print("\n[완료] .gitignore 생성")

    # 4. README.md 생성
    readme_content = f"""# 📊 Daily Stock Recommendations

검증된 퀀트 전략 기반 주식 추천 시스템

## 🌐 웹페이지 보기

👉 [최신 리포트 보기](https://{github_username}.github.io/{repo_name}/daily_stock_report_20260131.html)

## 📈 특징

- **검증된 전략**: 학술 논문 기반 퀀트 전략
  - Momentum (Jegadeesh & Titman 1993)
  - Mean Reversion (De Bondt & Thaler 1985)
  - Trend Following (Hurst et al. 2013)

- **매수/매도 가격 추천**
- **섹터별 분석**
- **리스크/리워드 비율**

## 🔄 업데이트

매일 자동으로 업데이트됩니다.

## 📝 면책 조항

본 리포트는 투자 참고 자료이며, 투자 판단 및 결과에 대한 책임은 투자자 본인에게 있습니다.
"""

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("[완료] README.md 생성")

    # 5. index.html 생성 (리다이렉트)
    index_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=./daily_stock_report_20260131.html">
    <title>Redirecting...</title>
</head>
<body>
    <p>리다이렉트 중... <a href="./daily_stock_report_20260131.html">여기를 클릭하세요</a></p>
</body>
</html>
"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)

    print("[완료] index.html 생성")

    # 6. 파일 추가
    run_command('git add .', '파일 스테이징')

    # 7. 커밋
    run_command('git commit -m "Initial commit: Daily stock recommendations"', '첫 커밋')

    # 8. 원격 저장소 추가
    remote_url = f"https://github.com/{github_username}/{repo_name}.git"

    # 기존 원격 저장소 확인
    result = subprocess.run('git remote', shell=True, capture_output=True, text=True)
    if 'origin' in result.stdout:
        run_command('git remote remove origin', '기존 원격 저장소 제거')

    run_command(f'git remote add origin {remote_url}', '원격 저장소 추가')

    print("\n" + "="*70)
    print("다음 단계:")
    print("="*70)
    print(f"\n1. GitHub에서 리포지토리 생성:")
    print(f"   https://github.com/new")
    print(f"   리포지토리 이름: {repo_name}")
    print(f"   Public으로 설정!")
    print(f"\n2. 생성 후 아래 명령 실행:")
    print(f"\n   git push -u origin main")
    print(f"\n3. GitHub에서 Settings > Pages 설정:")
    print(f"   - Source: Deploy from a branch")
    print(f"   - Branch: main")
    print(f"   - Folder: / (root)")
    print(f"\n4. 완료! 몇 분 후 접속 가능:")
    print(f"   https://{github_username}.github.io/{repo_name}/")

    print("\n" + "="*70)

    # GitHub 새 리포지토리 페이지 열기
    open_github = input("\nGitHub 리포지토리 생성 페이지를 여시겠습니까? (y/n): ").strip().lower()
    if open_github == 'y':
        webbrowser.open("https://github.com/new")

    print("\n[완료] 설정이 완료되었습니다!")
    print("\n다음 명령어를 실행하세요:")
    print("\n  git push -u origin main\n")


if __name__ == '__main__':
    try:
        setup_github_pages()
    except KeyboardInterrupt:
        print("\n\n[취소] 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n[오류] {e}")
        import traceback
        traceback.print_exc()
