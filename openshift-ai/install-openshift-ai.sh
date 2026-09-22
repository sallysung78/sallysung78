#!/usr/bin/env bash
################################################################################
# install-openshift-ai.sh
#   AWS 위에 OpenShift 클러스터를 만들고 RHOAI 3.4 를 설치하는 비대화형 스크립트
#   (hyogrin/RHOAI-Toolkit 의 "1) Complete Setup" 흐름을 그대로 자동화)
#
# 단계:
#   1. 사전 점검   : AWS 자격증명, Route53 도메인, pull secret, SSH 키
#   2. 도구 준비   : openshift-install / oc 다운로드 (mirror.openshift.com)
#   3. install-config.yaml 생성
#   4. openshift-install create cluster   (30~45분)
#   5. RHOAI-Toolkit clone → scripts/install-rhoai-34.sh   (20~30분, GPU 노드 포함)
#   6. 접속 정보 출력 (cluster-info.txt)
#
# 사용법:
#   cp cluster.env.example cluster.env   # 값 채우기
#   ./install-openshift-ai.sh            # 전체
#   ./install-openshift-ai.sh --skip-openshift   # 기존 클러스터에 RHOAI 만
#   ./install-openshift-ai.sh --check            # 사전 점검만
################################################################################
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()      { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()     { echo -e "${RED}[ERROR]${NC} $*" >&2; }
header()  { echo; echo -e "${CYAN}══════════════════════════════════════════════${NC}"; echo -e "${CYAN}  $*${NC}"; echo -e "${CYAN}══════════════════════════════════════════════${NC}"; }
die()     { err "$*"; exit 1; }

SKIP_OPENSHIFT=false
CHECK_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --skip-openshift) SKIP_OPENSHIFT=true ;;
    --check)          CHECK_ONLY=true ;;
    -h|--help) sed -n 2,20p "$0"; exit 0 ;;
    *) die "알 수 없는 옵션: $arg" ;;
  esac
done

# ── 설정 로드 ──────────────────────────────────────────────────
if [ -f "$SCRIPT_DIR/cluster.env" ]; then
  set -a; # shellcheck disable=SC1091
  source "$SCRIPT_DIR/cluster.env"; set +a
else
  warn "cluster.env 가 없습니다. 환경변수만으로 진행합니다. (cp cluster.env.example cluster.env 권장)"
fi

AWS_REGION="${AWS_REGION:-us-east-2}"
CLUSTER_NAME="${CLUSTER_NAME:-rhoai}"
OCP_VERSION="${OCP_VERSION:-stable-4.20}"
MASTER_INSTANCE_TYPE="${MASTER_INSTANCE_TYPE:-m6i.xlarge}"
MASTER_REPLICAS="${MASTER_REPLICAS:-3}"
WORKER_INSTANCE_TYPE="${WORKER_INSTANCE_TYPE:-m6i.2xlarge}"
WORKER_REPLICAS="${WORKER_REPLICAS:-2}"
PULL_SECRET_PATH="${PULL_SECRET_PATH:-$HOME/pull-secret.txt}"
SSH_KEY_PATH="${SSH_KEY_PATH:-$HOME/.ssh/id_ed25519}"
RHOAI_CHANNEL="${RHOAI_CHANNEL:-stable-3.x}"
RHOAI_TOOLKIT_REF="${RHOAI_TOOLKIT_REF:-main}"
INSTALL_RHOAI="${INSTALL_RHOAI:-true}"
RHOAI_EXTRA_ARGS="${RHOAI_EXTRA_ARGS:-}"
BASE_DOMAIN="${BASE_DOMAIN:-}"
SINGLE_AZ="${SINGLE_AZ:-false}"

export AWS_REGION AWS_DEFAULT_REGION="$AWS_REGION"
[ -n "${AWS_ACCESS_KEY_ID:-}" ] && export AWS_ACCESS_KEY_ID
[ -n "${AWS_SECRET_ACCESS_KEY:-}" ] && export AWS_SECRET_ACCESS_KEY

BIN_DIR="$SCRIPT_DIR/bin"
INSTALL_DIR="$SCRIPT_DIR/${CLUSTER_NAME}-install"
TOOLKIT_DIR="$SCRIPT_DIR/RHOAI-Toolkit"
export PATH="$BIN_DIR:$PATH"

OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"
case "$OS-$ARCH" in
  linux-x86_64)  INSTALLER_PKG="openshift-install-linux.tar.gz"; OC_PKG="openshift-client-linux.tar.gz" ;;
  linux-aarch64) INSTALLER_PKG="openshift-install-linux-arm64.tar.gz"; OC_PKG="openshift-client-linux-arm64.tar.gz" ;;
  darwin-x86_64) INSTALLER_PKG="openshift-install-mac.tar.gz"; OC_PKG="openshift-client-mac.tar.gz" ;;
  darwin-arm64)  INSTALLER_PKG="openshift-install-mac-arm64.tar.gz"; OC_PKG="openshift-client-mac-arm64.tar.gz" ;;
  *) die "지원하지 않는 플랫폼: $OS-$ARCH" ;;
esac

# ── 1. 사전 점검 ───────────────────────────────────────────────
preflight() {
  header "1/6 사전 점검"
  local missing=()
  for t in aws jq curl tar ssh-keygen; do command -v "$t" >/dev/null || missing+=("$t"); done
  [ ${#missing[@]} -eq 0 ] || die "필수 도구 없음: ${missing[*]}  (aws: pip install awscli / jq: apt|yum|brew install jq)"

  info "AWS 자격증명 확인..."
  local ident
  ident="$(aws sts get-caller-identity 2>&1)" || die "AWS 자격증명이 유효하지 않습니다.\n$ident\n→ cluster.env 의 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY 를 IAM 액세스 키로 채우세요 (콘솔 비밀번호는 사용 불가)."
  ok "AWS 계정: $(echo "$ident" | jq -r .Account)  /  $(echo "$ident" | jq -r .Arn)"

  info "Route53 Hosted Zone 확인..."
  local zones
  zones="$(aws route53 list-hosted-zones --query 'HostedZones[?Config.PrivateZone==`false`].Name' --output text | tr '\t' '\n' | sed 's/\.$//' | sed '/^$/d')"
  if [ -z "$BASE_DOMAIN" ]; then
    local n; n="$(echo "$zones" | grep -c . || true)"
    if [ "$n" = "1" ]; then BASE_DOMAIN="$zones"; ok "BASE_DOMAIN 자동 선택: $BASE_DOMAIN"
    else die "BASE_DOMAIN 이 비어 있고 자동 선택할 수 없습니다. 계정의 Public Hosted Zone:\n${zones:-(없음)}\n→ cluster.env 의 BASE_DOMAIN 을 지정하세요 (없으면 Route53 에 Public Hosted Zone 을 먼저 만드세요)."; fi
  else
    echo "$zones" | grep -qx "$BASE_DOMAIN" && ok "Hosted Zone 존재: $BASE_DOMAIN" \
      || die "Route53 에 '$BASE_DOMAIN' Public Hosted Zone 이 없습니다. 현재 존:\n${zones:-(없음)}"
  fi

  if [ "$SKIP_OPENSHIFT" = false ]; then
    # 이름 충돌 방지: 같은 도메인에 이미 api.<name> 레코드/클러스터가 있으면 중단
    info "클러스터 이름 충돌 확인: ${CLUSTER_NAME}.${BASE_DOMAIN}"
    local existing_clusters
    existing_clusters="$(aws ec2 describe-instances \
      --filters "Name=instance-state-name,Values=pending,running,stopping,stopped" \
      --query 'Reservations[].Instances[].Tags[?starts_with(Key, `kubernetes.io/cluster/`)].Key' \
      --output text 2>/dev/null | tr '\t' '\n' | sed 's#kubernetes.io/cluster/##' | sort -u | sed '/^$/d')"
    if [ -n "$existing_clusters" ]; then
      info "이 계정에 이미 존재하는 클러스터: $(echo "$existing_clusters" | tr '\n' ' ')"
    fi
    if echo "$existing_clusters" | grep -q "^${CLUSTER_NAME}-"; then
      die "이미 '${CLUSTER_NAME}' 로 시작하는 클러스터가 이 계정에 있습니다.\n→ cluster.env 의 CLUSTER_NAME 을 다른 값으로 바꾸세요 (기존 클러스터와 도메인/리소스 충돌 방지)."
    fi
    local zone_id
    zone_id="$(aws route53 list-hosted-zones --query "HostedZones[?Name=='${BASE_DOMAIN}.' && Config.PrivateZone==\`false\`].Id" --output text | head -1)"
    if [ -n "$zone_id" ] && aws route53 list-resource-record-sets --hosted-zone-id "$zone_id" \
         --query "ResourceRecordSets[?Name=='api.${CLUSTER_NAME}.${BASE_DOMAIN}.'].Name" --output text 2>/dev/null | grep -q .; then
      die "Route53 에 이미 api.${CLUSTER_NAME}.${BASE_DOMAIN} 레코드가 있습니다.\n→ CLUSTER_NAME 을 다른 값으로 바꾸세요."
    fi
    ok "이름 충돌 없음: ${CLUSTER_NAME}.${BASE_DOMAIN}"

    # EIP 쿼터 확인: 멀티 AZ 는 AZ 당 NAT(=EIP) 1개 필요. 부족하면 SINGLE_AZ 권장
    local eip_q eip_used eip_free az_count need
    eip_q="$(aws service-quotas get-service-quota --service-code ec2 --quota-code L-0263D0A3 --query 'Quota.Value' --output text 2>/dev/null | cut -d. -f1)"
    eip_used="$(aws ec2 describe-addresses --query 'length(Addresses)' --output text 2>/dev/null)"
    if [ -n "$eip_q" ] && [ -n "$eip_used" ]; then
      eip_free=$(( eip_q - eip_used ))
      [ "$SINGLE_AZ" = "true" ] && az_count=1 || az_count=3
      need=$az_count
      info "EIP: 쿼터 ${eip_q}, 사용중 ${eip_used}, 여유 ${eip_free}, 필요(신규 NAT) ${need}"
      if [ "$eip_free" -lt "$need" ]; then
        if [ "$SINGLE_AZ" = "true" ]; then
          die "EIP 여유(${eip_free})가 부족합니다. 미사용 EIP 를 해제하거나 쿼터 상향이 필요합니다."
        else
          die "EIP 여유(${eip_free})가 멀티 AZ 필요치(${need})보다 부족합니다.\n→ cluster.env 에 SINGLE_AZ=true (NAT/EIP 1개) 를 설정하거나, 미사용 EIP 해제/쿼터 상향 하세요."
        fi
      fi
    fi

    info "Pull secret 확인: $PULL_SECRET_PATH"
    [ -s "$PULL_SECRET_PATH" ] || die "Pull secret 파일이 없습니다: $PULL_SECRET_PATH\n→ https://console.redhat.com/openshift/install/pull-secret 에서 받아 저장하세요."
    jq -e '.auths' "$PULL_SECRET_PATH" >/dev/null 2>&1 || die "Pull secret 형식이 올바르지 않습니다 (JSON .auths 필요)."
    ok "Pull secret OK ($(wc -c <"$PULL_SECRET_PATH" | tr -d ' ') bytes)"

    if [ ! -f "${SSH_KEY_PATH}.pub" ]; then
      warn "SSH 키가 없어 새로 생성합니다: $SSH_KEY_PATH"
      mkdir -p "$(dirname "$SSH_KEY_PATH")"
      ssh-keygen -t ed25519 -f "$SSH_KEY_PATH" -N "" -q
    fi
    ok "SSH 공개키: ${SSH_KEY_PATH}.pub"

    info "리전 $AWS_REGION 가용영역 / 인스턴스 타입 확인..."
    aws ec2 describe-instance-type-offerings --location-type region --region "$AWS_REGION" \
      --filters "Name=instance-type,Values=$MASTER_INSTANCE_TYPE,$WORKER_INSTANCE_TYPE" \
      --query 'InstanceTypeOfferings[].InstanceType' --output text | tr '\t' ' ' | sed 's/^/  제공 타입: /'
    aws ec2 describe-instance-type-offerings --location-type region --region "$AWS_REGION" \
      --filters "Name=instance-type,Values=${GPU_INSTANCE_TYPE:-g6e.xlarge}" --query 'InstanceTypeOfferings[].InstanceType' --output text \
      | grep -q . || warn "GPU 타입 ${GPU_INSTANCE_TYPE:-g6e.xlarge} 가 $AWS_REGION 에 없습니다. RHOAI 단계에서 GPU 노드 생성이 실패할 수 있습니다."
  fi
  ok "사전 점검 통과"
}

# ── 2. 도구 준비 ───────────────────────────────────────────────
fetch_tools() {
  header "2/6 openshift-install / oc 준비 ($OCP_VERSION)"
  mkdir -p "$BIN_DIR"
  local base="https://mirror.openshift.com/pub/openshift-v4/clients/ocp/$OCP_VERSION"
  local ver
  ver="$(curl -fsSL "$base/release.txt" | awk '/^Name:/{print $2}')" || die "mirror.openshift.com 에 접근할 수 없습니다 (프록시/방화벽 확인)."
  info "해당 채널 최신 버전: $ver"
  if [ -x "$BIN_DIR/openshift-install" ] && "$BIN_DIR/openshift-install" version 2>/dev/null | grep -q "$ver"; then
    ok "openshift-install $ver 이미 존재"
  else
    curl -fsSL "$base/$INSTALLER_PKG" | tar -xz -C "$BIN_DIR" openshift-install
    chmod +x "$BIN_DIR/openshift-install"
  fi
  if ! command -v oc >/dev/null 2>&1 || [ ! -x "$BIN_DIR/oc" ]; then
    curl -fsSL "$base/$OC_PKG" | tar -xz -C "$BIN_DIR" oc kubectl 2>/dev/null || curl -fsSL "$base/$OC_PKG" | tar -xz -C "$BIN_DIR" oc
    chmod +x "$BIN_DIR/oc" "$BIN_DIR/kubectl" 2>/dev/null || true
  fi
  "$BIN_DIR/openshift-install" version | head -1
  oc version --client | head -1
}

# ── 3. install-config.yaml ─────────────────────────────────────
generate_install_config() {
  header "3/6 install-config.yaml 생성"
  if [ -f "$INSTALL_DIR/metadata.json" ]; then
    die "이미 설치된 클러스터 디렉터리가 있습니다: $INSTALL_DIR\n→ 재사용하려면 --skip-openshift, 지우려면 ./destroy-cluster.sh 를 먼저 실행하세요."
  fi
  mkdir -p "$INSTALL_DIR"
  local pull_secret ssh_key zones_block=""
  pull_secret="$(jq -c . "$PULL_SECRET_PATH")"
  ssh_key="$(cat "${SSH_KEY_PATH}.pub")"

  # SINGLE_AZ=true → NAT/EIP 1개만 쓰도록 단일 가용영역으로 제한 (EIP 쿼터 절약)
  local az_yaml_compute="" az_yaml_master=""
  if [ "$SINGLE_AZ" = "true" ]; then
    local az
    az="$(aws ec2 describe-instance-type-offerings --location-type availability-zone --region "$AWS_REGION" \
      --filters "Name=instance-type,Values=${WORKER_INSTANCE_TYPE}" \
      --query 'InstanceTypeOfferings[0].Location' --output text 2>/dev/null)"
    [ -n "$az" ] && [ "$az" != "None" ] || az="${AWS_REGION}a"
    ok "SINGLE_AZ 모드: 가용영역 $az 하나만 사용 (NAT/EIP 1개)"
    az_yaml_compute=$'\n      zones:\n      - '"$az"
    az_yaml_master=$'\n      zones:\n      - '"$az"
  fi

  cat >"$INSTALL_DIR/install-config.yaml" <<YAML
apiVersion: v1
baseDomain: ${BASE_DOMAIN}
metadata:
  name: ${CLUSTER_NAME}
platform:
  aws:
    region: ${AWS_REGION}
    userTags:
      owner: ${CLUSTER_NAME}
      purpose: openshift-ai
compute:
- name: worker
  platform:
    aws:
      type: ${WORKER_INSTANCE_TYPE}
      rootVolume:
        size: 200
        type: gp3${az_yaml_compute}
  replicas: ${WORKER_REPLICAS}
controlPlane:
  name: master
  platform:
    aws:
      type: ${MASTER_INSTANCE_TYPE}${az_yaml_master}
  replicas: ${MASTER_REPLICAS}
networking:
  clusterNetwork:
  - cidr: 10.128.0.0/14
    hostPrefix: 23
  machineNetwork:
  - cidr: 10.0.0.0/16
  networkType: OVNKubernetes
  serviceNetwork:
  - 172.30.0.0/16
publish: External
pullSecret: '${pull_secret}'
sshKey: '${ssh_key}'
YAML
  cp "$INSTALL_DIR/install-config.yaml" "$INSTALL_DIR/install-config.yaml.backup"
  ok "$INSTALL_DIR/install-config.yaml (백업: install-config.yaml.backup)"
}

# ── 4. 클러스터 생성 ───────────────────────────────────────────
create_cluster() {
  header "4/6 OpenShift 클러스터 생성 (30~45분, 중단하지 마세요)"
  "$BIN_DIR/openshift-install" create cluster --dir="$INSTALL_DIR" --log-level=info
  ok "OpenShift 설치 완료"
}

# ── 5. RHOAI 3.4 ───────────────────────────────────────────────
install_rhoai() {
  header "5/6 RHOAI 3.4 설치 (RHOAI-Toolkit @ $RHOAI_TOOLKIT_REF)"
  export KUBECONFIG="$INSTALL_DIR/auth/kubeconfig"
  [ -f "$KUBECONFIG" ] || die "kubeconfig 가 없습니다: $KUBECONFIG"
  oc whoami >/dev/null || die "클러스터에 접속할 수 없습니다 (KUBECONFIG=$KUBECONFIG)"
  info "접속 확인: $(oc whoami) @ $(oc whoami --show-server)"

  if [ ! -d "$TOOLKIT_DIR/.git" ]; then
    git clone https://github.com/hyogrin/RHOAI-Toolkit "$TOOLKIT_DIR"
  fi
  git -C "$TOOLKIT_DIR" fetch -q origin
  git -C "$TOOLKIT_DIR" checkout -q "$RHOAI_TOOLKIT_REF"
  chmod +x "$TOOLKIT_DIR"/scripts/*.sh

  local domain
  domain="$(oc get ingresses.config.openshift.io cluster -o jsonpath='{.spec.domain}' | sed 's/^apps\.//')"
  # 툴킷 install-rhoai-34.sh: 노드 스케일(worker 2 + GPU g6e.xlarge 1) → NFD/GPU/Kueue/cert-manager/LWS/RHCL
  #   → RHOAI Operator → DataScienceCluster → 대시보드 기능 → MaaS → 관측성
  # shellcheck disable=SC2086
  "$TOOLKIT_DIR/scripts/install-rhoai-34.sh" \
    --create-admin-user \
    --channel "$RHOAI_CHANNEL" \
    --domain "$domain" \
    $RHOAI_EXTRA_ARGS
  ok "RHOAI 설치 스크립트 완료"
}

# ── 6. 요약 ────────────────────────────────────────────────────
summary() {
  header "6/6 접속 정보"
  export KUBECONFIG="$INSTALL_DIR/auth/kubeconfig"
  local console api pw dash
  console="$(oc whoami --show-console 2>/dev/null || echo '-')"
  api="$(oc whoami --show-server 2>/dev/null || echo '-')"
  pw="$(cat "$INSTALL_DIR/auth/kubeadmin-password" 2>/dev/null || echo '-')"
  dash="$(oc get route -n redhat-ods-applications -o jsonpath='{.items[?(@.metadata.name=="rhods-dashboard")].spec.host}' 2>/dev/null || true)"
  [ -z "$dash" ] && dash="$(oc get gateway -A -o jsonpath='{.items[?(@.metadata.name=="data-science-gateway")].spec.listeners[0].hostname}' 2>/dev/null || true)"
  cat >"$SCRIPT_DIR/cluster-info.txt" <<TXT
OpenShift AI 클러스터 정보 ($(date))
─────────────────────────────────────────────
클러스터:      ${CLUSTER_NAME}.${BASE_DOMAIN}  (${AWS_REGION})
Web Console:   ${console}
API:           ${api}
kubeadmin PW:  ${pw}
RHOAI 관리자:  admin / openshiftai   (htpasswd, 툴킷 --create-admin-user)
RHOAI 대시보드: https://${dash:-<oc get route -n redhat-ods-applications 로 확인>}
KUBECONFIG:    ${KUBECONFIG}

oc login ${api} -u kubeadmin -p '${pw}'
삭제:          ./destroy-cluster.sh
TXT
  cat "$SCRIPT_DIR/cluster-info.txt"
  warn "cluster-info.txt 와 ${INSTALL_DIR}/ 에는 비밀정보가 있습니다 (.gitignore 처리됨). 안전하게 보관하세요."
}

main() {
  preflight
  [ "$CHECK_ONLY" = true ] && { ok "--check: 사전 점검만 수행했습니다."; exit 0; }
  fetch_tools
  if [ "$SKIP_OPENSHIFT" = false ]; then
    generate_install_config
    create_cluster
  else
    info "--skip-openshift: 기존 클러스터($INSTALL_DIR) 사용"
  fi
  if [ "$INSTALL_RHOAI" = "true" ]; then install_rhoai; else info "INSTALL_RHOAI=false: RHOAI 단계 생략"; fi
  summary
}
main
