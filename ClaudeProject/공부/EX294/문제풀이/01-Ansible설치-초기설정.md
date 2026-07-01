# 문제 1. Ansible 설치 및 초기 설정

> PPT 기출 기반 · control 노드에 Ansible 설치 + 정적 인벤토리 + ansible.cfg 구성
> 시험의 **첫 문제이자 이후 모든 문제의 토대**. 여기서 인벤토리/cfg가 틀리면 뒤 문제 다 흔들림.

---

## 1️⃣ 개념

- **control 노드**: 내가 명령을 실행하는 서버(관리자 PC). 여기에만 Ansible 설치.
- **managed 노드**: 관리 대상 서버들. Ansible 설치 불필요(SSH + Python만 있으면 됨).
- **정적 인벤토리(static inventory)**: 관리 대상 호스트를 그룹으로 묶어 적어둔 텍스트 파일.
  - INI 형식: `[그룹명]` 아래에 호스트를 한 줄씩.
  - `[그룹:children]` → 그룹 안에 다른 그룹을 포함(중첩 그룹).
- **ansible.cfg**: Ansible 동작의 기본값 설정 파일. inventory 위치, roles/collections 경로,
  권한 상승(become) 등을 미리 지정해두면 명령마다 옵션을 안 붙여도 됨.
- **설정 우선순위(낮→높)**: `/etc/ansible/ansible.cfg` < `~/.ansible.cfg` < **작업 디렉토리의 `./ansible.cfg`** < `ANSIBLE_CONFIG` 환경변수
  → 시험에선 보통 **작업 디렉토리(`/home/user/ansible/`)에 만든 ansible.cfg**가 적용됨.

---

## 2️⃣ 문제 (기출 원문 요약)

> control 노드에서 Ansible을 설치하고 아래 조건으로 구성하시오.

- 필요한 패키지 설치 (`ansible-*`)
- `/home/user/ansible/inventory` 파일을 **정적 인벤토리**로 사용하고 아래 그룹 구성:
  - `dev` 그룹 → **node1**
  - `test` 그룹 → **node2**
  - `prod` 그룹 → **node3, node4**
  - `balancers` 그룹 → **node5**
  - `webservers` 그룹 → **prod 그룹 포함** (중첩)
- `/home/user/ansible/ansible.cfg` 작성:
  - `[defaults]` 에 위 inventory 파일 경로 지정
  - role 기본 경로 = `/home/user/ansible/roles`
  - collection 기본 경로 = `/home/user/ansible/collections`

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기

### inventory (`/home/user/ansible/inventory`)
```ini
[dev]
______            ← node1

[test]
______            ← node2

[prod]
______            ← node3
______            ← node4

[balancers]
______            ← node5

[__________]      ← webservers:children   (children = 그룹 안에 그룹!)
______            ← prod
```

### ansible.cfg (`/home/user/ansible/ansible.cfg`)
```ini
[________]                       ← defaults
inventory        = ____________  ← /home/user/ansible/inventory
roles_path       = ____________  ← /home/user/ansible/roles
collections_path = ____________  ← /home/user/ansible/collections

[______________________]         ← privilege_escalation (선택)
become        = true
become_method = sudo
become_user   = root
```

### 🧠 외우기 포인트 (감점 함정)
- ⚠️ **인벤토리 파일 첫 줄에 `---` 없다!** (플레이북과 다름 — 이거 자주 틀림)
- 중첩 그룹 문법은 `[webservers:children]` → 그 아래에 **그룹명**(prod)을 쓴다. 호스트 아님!
- ansible.cfg 섹션명 철자: `[defaults]`, `[privilege_escalation]`
- 키 이름: `roles_path`, `collections_path` (복수형 s, 언더스코어)
- `privilege_escalation` 넣어두면 매 명령/플레이북에 `become` 안 써도 됨 → 편함

---

## 4️⃣ 중요 명령어

```bash
# 설치
sudo dnf install -y ansible-*        # (또는 ansible-core)
ansible --version                    # 버전 + 적용된 cfg/모듈 경로 확인

# 작업 디렉토리 만들고 이동
mkdir -p /home/user/ansible/{roles,collections}
cd /home/user/ansible                # 여기의 ansible.cfg가 우선 적용됨

# 연결 테스트
ansible all -m ping                  # 모든 호스트 ping
ansible dev -m ping                  # 특정 그룹만
```

---

## 5️⃣ 모듈

이 문제는 **파일을 직접 작성**하는 문제라 플레이북 모듈은 안 씀. 대신 검증용 모듈:

| 모듈 | 용도 |
|------|------|
| `ping` | 관리 노드 연결/파이썬 확인 (`ansible all -m ping`) |
| `command` | 임의 명령 실행 확인 (`ansible all -m command -a 'id'`) |
| `setup` | facts 확인 (뒤 문제 대비, `ansible all -m setup`) |

> 참고: 인벤토리/cfg를 플레이북으로 만들라는 변형이 나오면 `copy`(content) 또는 `blockinfile` 사용.

---

## 6️⃣ 잊어버렸을 때 검색하는 법

```bash
# 인벤토리가 제대로 파싱되는지 = 문법 확인의 정석
ansible-inventory --list             # JSON으로 전체 구조 출력
ansible-inventory --graph            # 트리로 그룹/호스트 한눈에

# 어떤 cfg가 적용됐고 경로가 뭔지 헷갈릴 때
ansible --version                    # "config file = ..." 줄 확인
ansible-config dump                  # 현재 적용 설정 전체
ansible-config dump | grep -i -E 'INVENTORY|ROLES|COLLECTIONS'   # 경로만 콕
ansible-config dump --only-changed   # 기본값과 다른 것만 (내가 바꾼 것)

# cfg 옵션 이름/문법이 기억 안 나면
ansible-config list | grep -i roles  # 옵션 이름 검색
```
> 💡 인벤토리 그룹이 의도대로 안 잡히면 **`ansible-inventory --graph`** 가 제일 빠른 진단. `webservers` 밑에 node3/node4가 보이면 children 성공.

---

## 7️⃣ 테스트 후 확인 방법

```bash
# ① cfg가 내 파일을 읽고 있나
cd /home/user/ansible
ansible --version | grep "config file"
#   → config file = /home/user/ansible/ansible.cfg   이어야 함

# ② 인벤토리 그룹 구조 확인
ansible-inventory --graph
#   기대 출력 예:
#   @all:
#     |--@dev:
#     |  |--node1
#     |--@test:
#     |  |--node2
#     |--@prod:
#     |  |--node3
#     |  |--node4
#     |--@balancers:
#     |  |--node5
#     |--@webservers:
#     |  |--@prod:          ← prod가 children으로 들어옴 (핵심!)
#     |  |  |--node3
#     |  |  |--node4

# ③ 경로 설정 확인
ansible-config dump | grep -i -E 'DEFAULT_ROLES_PATH|COLLECTIONS_PATH|INVENTORY'
#   roles_path → /home/user/ansible/roles
#   collections_path → /home/user/ansible/collections

# ④ 실제 통신 확인
ansible all -m ping                  # 전부 SUCCESS / pong
ansible webservers -m ping           # node3, node4 만 응답하면 성공
```

### ✅ 합격 체크리스트
- [ ] `ansible --version` 의 config file 이 `/home/user/ansible/ansible.cfg`
- [ ] `ansible-inventory --graph` 에서 5개 그룹 + webservers 밑에 prod(children) 확인
- [ ] `ansible all -m ping` 전원 SUCCESS
- [ ] inventory 첫 줄에 `---` 없음
- [ ] roles_path / collections_path 두 경로 지정됨
