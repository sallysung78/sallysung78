# OpenShift AI (RHOAI 3.4) on AWS — 자동 설치

[hyogrin/RHOAI-Toolkit](https://github.com/hyogrin/RHOAI-Toolkit) 의 "Complete Setup" 흐름
(OpenShift 설치 → RHOAI 3.4 → GPU 노드 → MaaS) 을 **비대화형 스크립트 하나**로 실행합니다.

| 파일 | 역할 |
|------|------|
| `install-openshift-ai.sh` | 사전 점검 → 도구 다운로드 → install-config → `openshift-install create cluster` → 툴킷 `install-rhoai-34.sh` → 접속 정보 출력 |
| `destroy-cluster.sh` | `openshift-install destroy cluster` 로 AWS 리소스 전부 삭제 |
| `cluster.env.example` | 설정 템플릿 (`cluster.env` 로 복사해서 사용, 커밋 금지) |

## 준비물 (반드시 필요)

1. **AWS 액세스 키** — 콘솔 로그인 정보(ID/비밀번호)는 API 호출에 사용할 수 없습니다.
   콘솔 → IAM → 사용자 `open-environment-njxfn-admin` → 보안 자격 증명 → **액세스 키 만들기**
2. **Route53 Public Hosted Zone** — 클러스터 도메인(`api.<name>.<domain>`)을 여기에 등록합니다.
   Red Hat Demo Platform(RHDP) 환경이면 제공된 `*.sandboxNNNN.opentlc.com` 을 사용하세요.
3. **Red Hat Pull Secret** — <https://console.redhat.com/openshift/install/pull-secret> (Red Hat 계정 필요)
4. 로컬 도구: `aws`(v1/v2), `jq`, `curl`, `tar`, `git`, `ssh-keygen`. `oc`/`openshift-install` 은 스크립트가 받습니다.

## 실행

```bash
cd openshift-ai
cp cluster.env.example cluster.env
vi cluster.env                      # AWS 키, BASE_DOMAIN, PULL_SECRET_PATH 채우기

./install-openshift-ai.sh --check   # 사전 점검만 (자격증명, Route53, pull secret)
./install-openshift-ai.sh           # 전체 설치 (약 1시간 ~ 1시간 30분)
```

완료되면 `cluster-info.txt` 에 콘솔 URL, kubeadmin 비밀번호, RHOAI 대시보드 URL, `KUBECONFIG` 경로가 저장됩니다.

```bash
export KUBECONFIG=$PWD/rhoai-install/auth/kubeconfig
oc get nodes
oc get datasciencecluster            # Phase: Ready 확인
oc get nodes -l nvidia.com/gpu.present=true
```

- 이미 OpenShift 가 있으면: `./install-openshift-ai.sh --skip-openshift` (`<CLUSTER_NAME>-install/auth/kubeconfig` 필요)
- OpenShift 만 설치: `cluster.env` 에 `INSTALL_RHOAI=false`
- RHOAI 옵션 조정: `RHOAI_EXTRA_ARGS="--skip-maas --no-llmd"` 등 (`install-rhoai-34.sh --help` 참고)

## 기본 구성 (툴킷 권장값)

| 항목 | 값 |
|------|----|
| OpenShift | `stable-4.20` (RHOAI 3.4 는 4.19+, llm-d 는 4.20+) |
| Master | `m6i.xlarge` × 3 |
| Worker | `m6i.2xlarge` × 2 (gp3 200GB) |
| GPU Worker | `g6e.xlarge` (L40S 1장) × 1 — 툴킷이 MachineSet 자동 생성 |
| RHOAI | 채널 `stable-3.x`, admin 사용자 `admin / openshiftai` |
| 네트워크 | 신규 VPC `10.0.0.0/16`, OVN-Kubernetes, 외부 공개 |

## 비용 / 정리

이 구성은 시간당 대략 **$4~5 (GPU 포함)** 입니다. 사용이 끝나면 반드시 삭제하세요.

```bash
./destroy-cluster.sh            # 확인 프롬프트 있음
./destroy-cluster.sh --yes      # 무확인
```

일시 중지만 하려면 툴킷의 `restart-cluster-instances.sh stop|start` 를 `<CLUSTER_NAME>-install` 이 있는 위치에서 실행하세요.

## 문제 해결

| 증상 | 조치 |
|------|------|
| `InvalidClientTokenId` | `cluster.env` 의 액세스 키 확인 (콘솔 비밀번호 아님) |
| `Hosted Zone 이 없습니다` | Route53 에 Public Hosted Zone 생성 후 `BASE_DOMAIN` 지정 |
| `mirror.openshift.com 에 접근할 수 없습니다` | 회사 프록시/방화벽에서 허용 필요 |
| 설치 중단됨 | `./destroy-cluster.sh` 로 정리 후 재시도 (부분 생성 리소스 과금 방지) |
| RHOAI 단계 실패 | `export KUBECONFIG=...` 후 `./install-openshift-ai.sh --skip-openshift` 로 재실행 (멱등) |
| 더 자세한 내용 | 툴킷 `setup-guide_KO.md`, `docs/TROUBLESHOOTING.md` |
