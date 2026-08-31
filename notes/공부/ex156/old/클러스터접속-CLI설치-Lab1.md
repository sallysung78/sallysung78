# 00. 클러스터 접속 · 상태 점검 · CLI 설치 (사전 준비)

시험 시작 직후 가장 먼저 하는 작업들. 여기서 막히면 본 문제를 못 푸니 손에 익혀두기.

---

## 1. 클러스터 로그인

### 1-1. ID/PW 로그인

```bash
oc login -u admin -p redhatocp \
  https://api.ocp4.example.com:6443
```

**계정 정보**

| 용도 | 사용자 | 비밀번호 |
| --- | --- | --- |
| 관리자 | `admin` | `redhatocp` |
| 개발자 | `developer` | `developer` |

- 웹 콘솔: `https://console-openshift-console.apps.ocp4.example.com`

### 1-2. 토큰 로그인 (Lab1 — 권한 부여 토큰 검색)

웹 콘솔에서 토큰을 받아 CLI 로그인:

1. 웹 콘솔 우측 상단 **Help(?) → Command line tools** 클릭
2. 첫 줄 **"Copy login command"** 클릭
3. **Display Token** 클릭 → `oc login --token=...` 명령 복사
4. 터미널에 붙여넣기:

```bash
oc login --token=sha256~fypX...Ot6A \
  --server=https://api.ocp4.example.com:6443
```

### 1-3. 웹 로그인 (브라우저 인증)

```bash
oc login --web
```

- 브라우저가 열리면 `admin` 으로 로그인 → access token 자동 수신.

### 1-4. 콘솔 URL 확인

```bash
oc whoami --show-console
```

---

## 2. 클러스터 상태 점검 (로그인 직후 필수)

```bash
oc get node      # 모든 노드가 Ready 인지 확인
oc get csr       # 승인 안 된 보류(Pending) CSR 있는지 확인
oc get co        # 사용 불가/성능 저하/롤아웃 중인 ClusterOperator 확인
```

| 명령 | 확인 포인트 |
| --- | --- |
| `oc get node` | 클러스터 노드가 모두 `Ready` 인지 |
| `oc get csr` | 승인되지 않은 채 **Pending** 상태인 CSR 있는지 (있으면 승인) |
| `oc get co` | `AVAILABLE=False`, `DEGRADED=True`, `PROGRESSING=True` 인 Operator 있는지 |

> **OpenShift Virtualization Operator** 가 설치되면 웹 콘솔에서 **Virtualization** 관점(perspective)도 사용 가능.
> 추가로 **프로젝트 만들기**, **Route 확인** 등 기본 작업도 함께 점검.

---

## 3. kubectl CLI 설치 (체크섬 검증 포함)

> 순서: **체크섬 파일 받기 → 검증(OK) → 압축 해제 → root 권한으로 설치 → 버전 확인**

```bash
# 1) 클라이언트 + sha256sum.txt 다운로드
curl -LO "https://mirror.openshift.com/pub/openshift-v4/amd64/clients/ocp/stable-4.18/openshift-client-linux-4.18.19.tar.gz"
#   (sha256sum.txt 도 같은 경로에서 함께 받기)

# 2) 체크섬 검증 → OK 확인
sha256sum -c --ignore-missing sha256sum.txt

# 3) tar.gz 압축 해제
tar -xvf openshift-client-linux-4.18.19.tar.gz

# 4) root 권한으로 /usr/local/bin 에 설치
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 5) 버전 확인
kubectl version --client
```

- `sudo` 비밀번호: root / root
- `install -o root -g root -m 0755` = 소유자·그룹 root, 실행권한 부여하며 복사.

---

## 4. kubectl vs oc 명령 비교 (Lab1)

```bash
kubectl help     # kubectl 사용 가능한 명령 목록
oc help          # oc 사용 가능한 명령 목록 (oc = kubectl 상위호환)
```

- `oc` 는 `kubectl` 기능을 모두 포함 + OpenShift 전용 명령(`oc login`, `oc new-project`, `oc expose route`, `oc adm` 등) 추가.
- 시험에서 일반 k8s 리소스 조작은 `kubectl`/`oc` 둘 다 가능, OpenShift 전용(Route·로그인·프로젝트)은 `oc` 사용.

---

## 5. 빠른 점검 한 줄 모음

```bash
# 로그인
oc login -u admin -p redhatocp https://api.ocp4.example.com:6443
oc login --web                      # 브라우저 인증
oc login --token=sha256~... --server=https://api.ocp4.example.com:6443

# 상태
oc get node && oc get csr && oc get co
oc whoami --show-console

# 프로젝트/라우트
oc new-project <name>
oc get route -A
```
