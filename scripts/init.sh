#!/usr/bin/env bash
# init.sh — 폐쇄망 Claude-like 스택 초기화 스크립트
set -euo pipefail

BOLD='\033[1m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "\n${BOLD}========== 폐쇄망 AI 스택 초기화 ==========${NC}\n"

# 1. .env 파일 확인
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    warn ".env 파일이 없습니다. .env.example 을 복사합니다."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    warn "⚠  $PROJECT_DIR/.env 를 편집하여 비밀번호/키를 변경하세요."
    warn "   변경 후 다시 init.sh 를 실행하거나 docker compose up -d 를 실행하세요."
    exit 1
fi

# 2. 필수 환경변수 검증
source "$PROJECT_DIR/.env"
REQUIRED_VARS=(POSTGRES_PASSWORD LITELLM_MASTER_KEY WEBUI_SECRET_KEY)
for var in "${REQUIRED_VARS[@]}"; do
    val="${!var:-}"
    if [[ -z "$val" || "$val" == *"CHANGE_ME"* ]]; then
        error "$var 가 설정되지 않았거나 기본값입니다. .env 파일을 편집하세요."
    fi
done
info "환경변수 검증 완료"

# 3. TLS 인증서 생성 (자체 서명, 프로덕션에서는 내부 CA 인증서로 교체)
CERT_DIR="$PROJECT_DIR/nginx/certs"
mkdir -p "$CERT_DIR"
if [[ ! -f "$CERT_DIR/server.crt" ]]; then
    info "자체 서명 TLS 인증서 생성 중 (개발용)..."
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -keyout "$CERT_DIR/server.key" \
        -out    "$CERT_DIR/server.crt" \
        -subj   "/C=KR/ST=Seoul/O=Internal/CN=ai.internal" \
        2>/dev/null
    chmod 600 "$CERT_DIR/server.key"
    info "인증서 생성 완료: $CERT_DIR/"
    warn "프로덕션에서는 내부 CA 인증서를 nginx/certs/ 에 배치하세요."
else
    info "기존 TLS 인증서 사용: $CERT_DIR/"
fi

# 4. Ollama 모델 사전 다운로드 (선택)
PULL_OLLAMA_MODELS="${PULL_OLLAMA_MODELS:-false}"
if [[ "$PULL_OLLAMA_MODELS" == "true" ]]; then
    info "Ollama 모델 다운로드 중..."
    docker compose -f "$PROJECT_DIR/docker-compose.yml" up -d ollama
    sleep 5
    docker compose -f "$PROJECT_DIR/docker-compose.yml" exec ollama \
        ollama pull "${OLLAMA_DEFAULT_MODEL:-llama3:8b}"
    info "Ollama 모델 다운로드 완료"
fi

# 5. 스택 시작
info "Docker Compose 스택 시작 중..."
docker compose -f "$PROJECT_DIR/docker-compose.yml" --env-file "$PROJECT_DIR/.env" up -d

# 6. 헬스체크 대기
info "서비스 기동 대기 중 (최대 120초)..."
TIMEOUT=120
ELAPSED=0
while [[ $ELAPSED -lt $TIMEOUT ]]; do
    if docker compose -f "$PROJECT_DIR/docker-compose.yml" ps --format json 2>/dev/null \
        | grep -q '"Health":"healthy"'; then
        break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    echo -n "."
done
echo ""

echo -e "\n${BOLD}========== 접속 정보 ==========${NC}"
echo -e "  채팅 UI  : ${GREEN}https://localhost${NC}"
echo -e "  LiteLLM  : ${GREEN}http://localhost:4000/ui${NC}  (내부망 전용)"
echo -e "  관리자 키: LITELLM_MASTER_KEY (.env 파일 참조)"
echo -e "\n${BOLD}초기 관리자 계정은 Open WebUI 첫 접속 시 생성됩니다.${NC}\n"
