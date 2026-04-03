# 🍊 제주 감성 맛집 추천 시스템

사용자가 업로드한 이미지의 감성과 분위기를 AI로 분석하여, 어울리는 제주도 맛집을 추천하는 웹 애플리케이션입니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────┐      ┌─────────────┐      ┌─────────────────────────────┐
│   Frontend  │ ───▶ │   Backend   │ ───▶ │     AI/ML Services          │
│  (React)    │      │  (FastAPI)  │      │  - Kimi K2.5 (이미지 분석)   │
│  :3000      │      │   :8000     │      │  - OpenAI (임베딩)          │
└─────────────┘      └──────┬──────┘      │  - Qdrant (벡터 DB)         │
                            │             └─────────────────────────────┘
                            ▼
                     ┌─────────────┐
                     │  Kakao API  │  ← 맛집 데이터 수집
                     └─────────────┘
```

---

## 🚀 실행 방법

### 방법 1: 로컬 개발 환경

순수 로컬에서 개발 및 테스트할 때 사용합니다.

#### 1.1 사전 준비

필요한 API 키 발급:
- [Moonshot AI](https://platform.moonshot.cn/) - Kimi K2.5 API 키
- [OpenAI](https://platform.openai.com/) - Embeddings API 키
- [Qdrant Cloud](https://cloud.qdrant.io/) - 벡터 DB URL 및 API 키
- [Kakao Developers](https://developers.kakao.com/) - REST API 키
- [Langfuse](https://langfuse.com/) - LLM 모니터링 (선택)

#### 1.2 환경 변수 설정

```bash
# 프로젝트 루트의 .env.local 파일 확인
# (이미 설정되어 있다면 무시)
```

**환경별 .env 파일 구성:**

프로젝트 루트에 환경별로 분리된 `.env` 파일들이 있습니다:

```
.env.local              # 로컬 개발용 (PORT=8001)
.env.local.docker       # 로컬 Docker용 (PORT=8000)
.env.server.docker      # 서버 배포용 (PORT=8000)
```

**각 파일의 주요 차이:**

| 파일 | PORT | ENVIRONMENT | 사용 시점 |
|------|------|-------------|-----------|
| `.env.local` | 8001 | local | `python main.py` 직접 실행 |
| `.env.local.docker` | 8000 | local-docker | `docker-compose up` (로컬) |
| `.env.server.docker` | 8000 | server | `docker-compose.prod.yml` (서버) |

> **💡 Tip:** PORT가 다른 이유는 로컬 개발 시(8001)와 로컬 도커(8000)를 동시에 실행핼 때 포트 충돌을 방지하기 위함입니다.

**backend/.env 파일 예시 (.env.local 기준):**
```env

# Embeddings (OpenAI)
OPENAI_API_KEY=your_openai_api_key

# Vector DB (Qdrant)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Kakao API
KAKAO_REST_API_KEY=your_kakao_api_key

# Langfuse (선택)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# 환경 설정 (local, local-docker, server)
ENVIRONMENT=local

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**frontend/.env 파일 생성:**

```bash
cd frontend

# 로컬 개발 시 (포트 8001) - .env.local의 PORT와 일치
echo "VITE_API_URL=http://localhost:8001" > .env
```

> **참고:** 로컬 Docker 테스트 시에는 `docker-compose.yml`의 `VITE_API_URL` build-arg를 사용하므로 별도 설정 불필요

#### 1.3 백엔드 실행

```bash
cd backend

# 가상환경 생성 및 활성화 (Windows)
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행 (방법 1: python main.py - 권장)
# PORT 환경변수 자동 적용 (기본값: 8001)
python main.py

# 서버 실행 (방법 2: uvicorn 직접 실행)
uvicorn main:app --reload --port 8001
```

백엔드 API 문서: http://localhost:8000/docs

#### 1.4 프론트엔드 실행

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드: http://localhost:5173

#### 1.5 데이터 초기화 (최초 1회)

```bash
# 로컬 개발 환경 (.env.local 사용, PORT=8001)
curl -X POST http://localhost:8001/init-data
```

또는 Swagger UI에서 `/init-data` 엔드포인트 실행

---

### 방법 2: 로컬 Docker 환경

Docker로 전체 스택을 로컬에서 테스트할 때 사용합니다.

#### 2.1 환경 변수 설정

별도의 설정 없이 프로젝트 루트의 `.env.local.docker` 파일을 사용합니다.

(이미 설정되어 있다면 무시하고 바로 실행)

#### 2.2 Docker Compose 실행

```bash
# 프로젝트 루트에서 실행
docker-compose up --build
```

#### 2.3 서비스 접속

- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

#### 2.4 데이터 초기화

```bash
# 로컬 Docker 환경 (.env.local.docker 사용, PORT=8000)
curl -X POST http://localhost:8000/init-data
```

#### 2.5 종료

```bash
# 터미널에서 Ctrl+C 후
docker-compose down

# 완전 정리 (볼륨 포함)
docker-compose down -v
```

---

### 방법 3: 서버 배포 환경 (OCI + CI/CD)

Oracle Cloud Infrastructure (OCI)에 Docker Compose로 배포합니다.

#### 3.1 서버 준비 (OCI)

```bash
# OCI 인스턴스 생성 후 SSH 접속
ssh -i ~/.ssh/oci_key ubuntu@your-server-ip

# Docker & Docker Compose 설치
sudo apt update
sudo apt install -y docker.io docker-compose

# Docker 권한 설정
sudo usermod -aG docker $USER
newgrp docker

# 프로젝트 디렉토리 생성
mkdir -p ~/vibe-restaurant-recommender
cd ~/vibe-restaurant-recommender
```

#### 3.2 환경 변수 설정

서버에서는 프로젝트 루트의 `.env.server.docker` 파일을 사용합니다.

```bash
# 서버에 .env.server.docker 파일이 없는 경우에만 생성
# (보통 GitHub Secrets나 안전한 방법으로 미리 전송)

# 서버에서 파일 확인
ls -la ~/vibe-restaurant-recommender/.env.server.docker
```

**서버용 .env.server.docker 예시:**
```env
PORT=8000
ENVIRONMENT=server
MOONSHOT_API_KEY=your_moonshot_api_key
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
KAKAO_REST_API_KEY=your_kakao_api_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
CORS_ORIGINS=http://YOUR_SERVER_IP:3000
```

#### 3.3 docker-compose.prod.yml 배포

```bash
# docker-compose.prod.yml 파일 생성 (YOUR_GITHUB_USERNAME을 실제 사용자명으로 변경)
cat > docker-compose.prod.yml << 'EOF'
services:
  backend:
    image: ghcr.io/YOUR_GITHUB_USERNAME/vibe-restaurant-recommender-backend:latest
    container_name: vibe-backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    environment:
      - CORS_ORIGINS=http://YOUR_SERVER_IP:3000
      - ENVIRONMENT=server
      - PORT=8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: ghcr.io/YOUR_GITHUB_USERNAME/vibe-restaurant-recommender-frontend:latest
    container_name: vibe-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
EOF
```

**⚠️ 주의:** `YOUR_GITHUB_USERNAME`과 `YOUR_SERVER_IP`를 실제 값으로 변경하세요!

예시:
- `ghcr.io/devmigi619/vibe-restaurant-recommender-backend:latest`
- `CORS_ORIGINS=http://123.456.789.0:3000`

#### 3.4 CI/CD 설정 (GitHub Actions)

GitHub Actions로 자동 빌드 및 배포를 설정합니다.

**GitHub Secrets 설정:**

Repository → Settings → Secrets and variables → Actions → New repository secret

| Secret 이름 | 설명 | 예시 값 |
|------------|------|---------|
| `VITE_API_URL` | 프론트엔드에서 호출할 API URL | `http://123.456.789.0:8000` |
| `SERVER_HOST` | 서버 IP 주소 | `123.456.789.0` |
| `SERVER_SSH_KEY` | 서버 SSH 프라이빗 키 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `GITHUB_TOKEN` | GitHub 자동 생성 (설정 불필요) | 자동 생성됨 |

**SSH 키 생성 및 등록:**

```bash
# 로컬에서 SSH 키 생성 (없는 경우)
ssh-keygen -t ed25519 -C "deploy@github-actions" -f ~/.ssh/github_actions

# 퍼블릭 키를 서버에 등록
cat ~/.ssh/github_actions.pub | ssh -i ~/.ssh/oci_key ubuntu@your-server-ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# 프라이빗 키를 GitHub Secrets에 복사
# (Windows: cat ~/.ssh/github_actions | clip)
# (Mac: cat ~/.ssh/github_actions | pbcopy)
```

#### 3.5 자동 배포 (GitHub Actions)

`.github/workflows/deploy.yml`이 이미 설정되어 있습니다.

**배포 과정:**

```bash
# 1. 코드 수정
git add .
git commit -m "feat: add new feature"
git push origin main

# 2. GitHub Actions 자동 실행
# - Docker 이미지 빌드
# - GitHub Container Registry (GHCR)에 푸시
# - 서버에 SSH 접속
# - docker-compose.prod.yml pull & up -d
```

**배포 상태 확인:**

GitHub Repository → Actions 탭에서 워크플로우 상태 확인

#### 3.6 수동 배포 (GitHub Actions 없이)

비상 상황 또는 GitHub Actions 없이 수동으로 배포할 때:

```bash
# 서버에서 실행

# 1. GitHub Container Registry 로그인
# GitHub Personal Access Token 필요 (ghp_...)
docker login ghcr.io -u YOUR_GITHUB_USERNAME
# Password: ghp_YOUR_PERSONAL_ACCESS_TOKEN

# 2. 최신 이미지 Pull
cd ~/vibe-restaurant-recommender
docker compose -f docker-compose.prod.yml pull

# 3. 실행
docker compose -f docker-compose.prod.yml up -d

# 4. 로그 확인
docker compose -f docker-compose.prod.yml logs -f

# 5. 컨테이너 상태 확인
docker ps
```

**수동 배포 vs 자동 배포:**

| 방식 | 장점 | 단점 | 사용 시점 |
|------|------|------|-----------|
| **자동 배포** | 편리함, 실수 방지 | GitHub 의존 | 일상적인 배포 |
| **수동 배포** | 제어 가능 | 번거로움 | 비상 상황, GitHub Actions 장애 시 |

---

## 📊 환경 구분 및 모니터링

### 화면 표시

모든 환경에서 화면 우측 상단에 현재 환경이 표시됩니다:

| 환경 | 색상 | 설명 |
|------|------|------|
| 🟢 로컬 | 녹색 | `npm run dev`로 실행한 개발 서버 |
| 🔵 로컬도커 | 파란색 | `docker-compose up`으로 실행한 로컬 Docker |
| 🟠 서버 | 주황색 | OCI 등 실제 서버 배포 환경 |
| 🔴 오프라인 | 빨간색 | 백엔드 연결 불가 |

### Langfuse 트레이싱

모든 LLM 호출은 Langfuse에 기록되며, 환경별로 태그가 붙습니다:

```python
# 트레이스 필터링 예시
tags: ["local"]        # 로컬 개발
tags: ["local-docker"] # 로컬 Docker
tags: ["server"]       # 서버 배포
```

---

## 🔧 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/health` | GET | 서버 상태 및 환경 확인 |
| `/init-data` | POST | 카카오 API로 맛집 데이터 초기화 |
| `/reset-data` | POST | DB 초기화 후 데이터 재수집 |
| `/recommend` | POST | 이미지 업로드 후 맛집 추천 |

---

## 📁 프로젝트 구조

```
vibe-restaurant-recommender/
├── backend/                      # FastAPI 백엔드
│   ├── main.py                   # API 엔트리포인트
│   ├── agent.py                  # LangChain ReAct Agent
│   ├── tools.py                  # AI 도구 (이미지 분석, 검색)
│   ├── vector_store.py           # Qdrant 벡터 DB 연동
│   ├── data_pipeline.py          # 카카오 API 데이터 수집
│   ├── requirements.txt          # Python 의존성
│   ├── Dockerfile                # 백엔드 Docker 이미지
│   └── .env                      # 환경 변수 (Git 제외)
├── frontend/                     # React 프론트엔드
│   ├── src/
│   │   ├── App.jsx               # 메인 컴포넌트
│   │   ├── components/
│   │   │   ├── ImageUpload.jsx   # 이미지 업로드
│   │   │   ├── RecommendationResult.jsx  # 추천 결과
│   │   │   └── EnvironmentBadge.jsx      # 환경 표시
│   │   └── ...
│   ├── package.json
│   ├── Dockerfile                # 프론트엔드 Docker 이미지
│   └── .env                      # 환경 변수 (Git 제외)
├── docker-compose.yml            # 로컬 Docker Compose
├── docker-compose.prod.yml       # 서버 배포용 Compose
├── .github/workflows/deploy.yml  # CI/CD 파이프라인
└── README.md                     # 이 파일
```

---

## 🐛 문제 해결

### Q: `/init-data` 실행 시 "맛집 데이터가 없습니다" 오류

**A:** 데이터 파이프라인을 먼저 실행해야 합니다.

```bash
curl -X POST http://localhost:8000/init-data
```

### Q: Langfuse 트레이스가 보이지 않음

**A:** 환경 변수 확인

```bash
# backend/.env에 Langfuse 키가 설정되어 있는지 확인
echo $LANGFUSE_PUBLIC_KEY
```

### Q: CORS 오류 발생

**A:** CORS_ORIGINS 환경 변수 확인

```bash
# backend/.env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Q: Docker에서 환경이 "local"로 표시됨

**A:** docker-compose.yml의 ENVIRONMENT 설정 확인

```yaml
environment:
  - ENVIRONMENT=local-docker  # 이 값이 설정되어야 함
```

---

## 📄 라이선스

MIT License

---

## 🙋 문의

프로젝트 관련 문의는 GitHub Issues를 통해 부탁드립니다.
