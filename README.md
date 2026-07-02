https://github.com/sallysung78/sallysung78/tree/claude/github-project-folders-lg9ms6/ClaudeProject


# 폐쇄망 Claude-like AI 인터페이스

인터넷이 차단된 내부망에서 Claude와 유사한 채팅 경험을 제공하는 스택입니다.

```
[사용자 브라우저]
      ↓ HTTPS
[Nginx 리버스 프록시]
      ↓
[Open WebUI]        ← Claude 유사 채팅 인터페이스
      ↓ OpenAI-compatible API
[LiteLLM Proxy]     ← 라우팅 / 인증 / 폴백 / 사용량 추적
      ↓
[vLLM / Ollama]     ← 내부 LLM 서버 (GPU 또는 CPU)
```

## 구성 요소

| 서비스 | 역할 | 포트 |
|---|---|---|
| **Open WebUI** | 채팅 UI (Claude 유사) | 내부 8080 |
| **LiteLLM** | OpenAI-compatible 프록시 | 내부 4000 |
| **vLLM** | GPU 기반 고성능 LLM 서빙 | 내부 8000 |
| **Ollama** | CPU/GPU 경량 LLM 서빙 | 내부 11434 |
| **PostgreSQL** | 사용량·키·팀 관리 DB | 내부 5432 |
| **Nginx** | TLS termination, 리버스 프록시 | 80, 443 |

## 빠른 시작

### 1. 환경변수 설정

```bash
cp .env.example .env
# .env 파일에서 CHANGE_ME 값을 모두 교체
vim .env
```

필수 변경 항목:
- `POSTGRES_PASSWORD` — PostgreSQL 비밀번호
- `LITELLM_MASTER_KEY` — LiteLLM API 마스터 키 (`openssl rand -hex 32`)
- `WEBUI_SECRET_KEY` — Open WebUI 세션 키 (`openssl rand -hex 32`)

### 2. 초기화 및 시작

```bash
bash scripts/init.sh
```

스크립트가 자동으로:
- 환경변수 유효성 검사
- 자체 서명 TLS 인증서 생성 (개발용)
- Docker Compose 스택 기동

### 3. 접속

| 서비스 | URL |
|---|---|
| 채팅 UI | `https://localhost` |
| LiteLLM 관리 UI | `http://localhost:4000/ui` (내부망) |

첫 접속 시 Open WebUI에서 관리자 계정을 생성합니다.

---

## 모델 서버 구성

### vLLM (GPU, 프로덕션 권장)

`.env`에서 설정:
```env
MODEL_PATH=/path/to/your/models    # 모델 가중치 디렉토리
VLLM_MODEL_NAME=gptoss-120b        # 모델 디렉토리명
TENSOR_PARALLEL_SIZE=2             # GPU 수
```

### Ollama (CPU/GPU, PoC·소규모)

컨테이너 기동 후 모델 다운로드:
```bash
docker compose exec ollama ollama pull llama3:70b
```

### Rebellions ATOM 연결

ATOM 서버가 OpenAI-compatible API를 노출하는 경우:

1. `litellm/config.yaml`에서 ATOM 블록 주석 해제
2. `.env`에 추가:
   ```env
   REBEL_ATOM_API_BASE=http://rebel-atom-server:8080/v1
   REBEL_ATOM_API_KEY=your-key
   ```
3. `docker-compose.yml` litellm 서비스의 environment 블록에서 주석 해제

---

## 팀별 API 키 관리 (LiteLLM Virtual Keys)

```bash
# 팀 생성
curl -X POST http://localhost:4000/team/new \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"team_alias": "dev-team", "max_budget": 100}'

# 팀 키 발급
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"team_id": "<team_id>", "key_alias": "dev-team-key", "models": ["gptoss-120b"]}'
```

---

## 보안 체크리스트

- [ ] `.env`의 모든 `CHANGE_ME` 값 교체 완료
- [ ] `nginx/certs/` 에 내부 CA 서명 인증서 배치 (프로덕션)
- [ ] `ENABLE_SIGNUP=false` 유지 → 관리자가 계정 직접 생성
- [ ] Docker network `internal: true` 으로 컨테이너간 통신이 외부망 차단 확인
- [ ] LiteLLM 포트(4000)는 내부망 접근만 허용 (방화벽)
- [ ] AD/LDAP SSO 연동 후 OAUTH 설정 활성화 (선택)

---

## 디렉토리 구조

```
.
├── docker-compose.yml          # 전체 스택 정의
├── .env.example                # 환경변수 템플릿
├── litellm/
│   └── config.yaml             # LiteLLM 모델·라우팅 설정
├── nginx/
│   ├── conf.d/default.conf     # Nginx 리버스 프록시 설정
│   └── certs/                  # TLS 인증서 (init.sh가 생성)
└── scripts/
    └── init.sh                 # 초기화 스크립트
```
