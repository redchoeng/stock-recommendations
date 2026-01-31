# 🚀 Netlify 배포 가이드 (5분 완료)

## 📊 현재 구조

```
GitHub Actions (매 2시간)
    ↓
Python으로 주식 분석
    ↓
HTML 리포트 생성
    ↓
GitHub에 자동 푸시
    ↓
Netlify 자동 배포 ⚡
```

---

## ✅ Step 1: Netlify 계정 생성 (1분)

1. **https://www.netlify.com/** 접속
2. **Sign up** 클릭
3. **GitHub 계정으로 로그인** (추천)
   - "Authorize netlify" 클릭
4. 완료!

---

## ✅ Step 2: GitHub 저장소 연결 (2분)

### 방법 A: Netlify 웹사이트에서 설정

1. Netlify 대시보드 → **Add new site** → **Import an existing project**

2. **Deploy with GitHub** 선택

3. GitHub 저장소 선택:
   - `redchoeng/stock-recommendations` 검색 및 선택

4. 배포 설정:
   ```
   Branch to deploy: main
   Build command: (비워두기)
   Publish directory: .
   ```

5. **Deploy site** 클릭!

6. 🎉 배포 완료! (30초 소요)

---

## 🌐 생성된 URL

배포 완료 후 자동으로 URL이 생성됩니다:

```
https://[랜덤이름].netlify.app
```

예시:
- `https://sparkling-unicorn-123456.netlify.app`
- `https://cosmic-dolphin-abcdef.netlify.app`

### URL 커스터마이징 (선택사항)

1. Site settings → Domain management → Options
2. **Edit site name** 클릭
3. 원하는 이름 입력 (예: `redcho-stocks`)
4. Save

최종 URL:
```
https://redcho-stocks.netlify.app
```

---

## ⚡ Step 3: 자동 배포 확인

이제 자동으로 작동합니다:

1. **GitHub Actions**가 2시간마다 실행
2. Python 스크립트가 새 HTML 생성
3. GitHub에 자동 커밋/푸시
4. **Netlify가 변경사항 감지** → 자동 배포!
5. 10-30초 후 웹사이트 업데이트 완료 ✅

### 배포 상태 확인:
- Netlify 대시보드 → Deploys 탭
- 초록색 "Published" 확인

---

## 🎯 Netlify 장점

### ✅ GitHub Pages보다 나은 점:

1. **더 빠른 속도**
   - 글로벌 CDN (전세계 서버)
   - 한국에서도 빠름

2. **즉시 배포**
   - GitHub Pages: 1-2분
   - Netlify: 10-30초

3. **커스텀 도메인 무료**
   - `.netlify.app` 서브도메인
   - 자체 도메인 연결도 무료

4. **배포 미리보기**
   - Pull Request마다 미리보기 URL 생성

5. **HTTPS 자동**
   - Let's Encrypt 인증서 자동 갱신

6. **Form 처리**
   - 정적 사이트에서도 폼 제출 가능

7. **분석 기능**
   - 트래픽 통계 확인 가능

---

## 🔧 고급 설정 (선택사항)

### 1. 커스텀 도메인 연결

**무료 도메인 서비스 (Freenom 등) 사용:**

1. Site settings → Domain management
2. **Add custom domain** 클릭
3. 도메인 입력 (예: `mystocks.tk`)
4. DNS 설정:
   ```
   Type: CNAME
   Name: www
   Value: [your-site].netlify.app
   ```
5. Netlify에서 자동으로 HTTPS 설정

**유료 도메인:**
- 가비아, Namecheap 등에서 구매 (연 1-2만원)
- 동일한 방식으로 연결

### 2. 환경 변수 설정

API 키 등이 필요한 경우:

1. Site settings → Environment variables
2. **Add a variable** 클릭
3. Key/Value 입력
4. Python 코드에서 `os.environ['KEY_NAME']`으로 사용

### 3. 배포 알림 설정

1. Site settings → Build & deploy → Deploy notifications
2. Email, Slack, Discord 등 알림 설정 가능

---

## 📊 비용

### 무료 플랜 (Starter):
- ✅ 100GB 대역폭/월
- ✅ 300분 빌드 시간/월
- ✅ 무제한 사이트
- ✅ HTTPS 포함
- ✅ 충분함! (현재 프로젝트에 적합)

### 유료 플랜:
- 필요 없음 (무료로 충분)

---

## 🔄 배포 흐름 상세

### GitHub Actions (변경 없음):
```yaml
# .github/workflows/daily-update.yml
# 2시간마다 실행 → HTML 생성 → GitHub 푸시
```

### Netlify 자동 감지:
```
GitHub main 브랜치 업데이트 감지
    ↓
Netlify 빌드 트리거
    ↓
파일 복사 (HTML, CSS, JS)
    ↓
글로벌 CDN에 배포
    ↓
캐시 업데이트
    ↓
완료! (10-30초)
```

---

## 🐛 문제 해결

### Q: 배포가 실패했어요
**A:** Netlify 대시보드 → Deploys → 실패한 배포 클릭 → 로그 확인

### Q: HTML 파일이 안보여요
**A:** `netlify.toml`의 `publish = "."` 확인

### Q: 이전 버전이 보여요
**A:** 브라우저 캐시 삭제 (Ctrl+Shift+R)

### Q: GitHub Pages와 충돌하나요?
**A:** 아니요, 동시에 사용 가능합니다
- GitHub Pages: `redchoeng.github.io/stock-recommendations/`
- Netlify: `redcho-stocks.netlify.app`

---

## 📱 모바일 앱처럼 사용

Netlify URL을 스마트폰 홈 화면에 추가:

### iPhone:
1. Safari에서 접속
2. 공유 버튼 → "홈 화면에 추가"

### Android:
1. Chrome에서 접속
2. 메뉴 → "홈 화면에 추가"

---

## 🎨 Netlify 기능 활용

### 1. 분기별 배포 (미리보기)

개발 중인 기능 테스트:

```bash
# 새 브랜치 생성
git checkout -b feature/new-design

# 수정 후 푸시
git push origin feature/new-design
```

Netlify가 자동으로 미리보기 URL 생성:
```
https://[branch-name]--[site-name].netlify.app
```

### 2. 폼 제출 처리

HTML 폼 추가 시 Netlify가 자동 처리:

```html
<form name="contact" method="POST" data-netlify="true">
  <input type="text" name="name" />
  <input type="email" name="email" />
  <button type="submit">Send</button>
</form>
```

제출된 데이터는 Netlify 대시보드에서 확인 가능!

---

## 🔗 최종 링크 정리

### 배포 후 사용할 링크들:

1. **Netlify 기본 URL**
   ```
   https://redcho-stocks.netlify.app
   ```

2. **Bitly로 축약** (선택사항)
   ```
   https://bit.ly/redcho
   ```

3. **커스텀 도메인** (선택사항)
   ```
   https://stocks.yourdomain.com
   ```

---

## ✅ 체크리스트

- [ ] Netlify 계정 생성
- [ ] GitHub 저장소 연결
- [ ] 배포 완료 확인
- [ ] 사이트 이름 커스터마이징
- [ ] URL 북마크 저장
- [ ] 모바일 홈 화면 추가
- [ ] 2시간 후 자동 업데이트 확인

---

## 🎉 완료 후

이제 두 개의 URL을 사용할 수 있습니다:

1. **GitHub Pages**: `https://redchoeng.github.io/stock-recommendations/`
   - 백업용, GitHub 공식

2. **Netlify**: `https://redcho-stocks.netlify.app`
   - 메인 사용, 빠른 속도

원하는 쪽을 메인으로 사용하세요!

---

**💡 추천: Netlify를 메인으로 사용하고, GitHub Pages는 백업으로!**
