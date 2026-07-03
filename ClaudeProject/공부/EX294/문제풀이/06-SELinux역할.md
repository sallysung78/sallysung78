# 문제 6. SELinux 역할 사용

> PPT 기출 · System Role `selinux` 로 정책/모드 구성. 5번과 형제 문제.
> 핵심: tasks 없이 **vars + roles**, 변수는 README에서.

---

## 1️⃣ 개념

- `selinux` System Role: SELinux 정책(policy)과 모드(state)를 선언적으로 설정.
- `selinux_policy: targeted` (정책), `selinux_state: enforcing` (모드).
- enforcing 모드 전환 시 재부팅이 필요할 수 있어 롤이 알아서 처리.
- 5번(timesync)과 **구조가 완전히 동일** → vars + roles.

---

## 2️⃣ 문제 (기출 원문 요약)

> 모든 호스트에서 실행하는 `/home/user/ansible/selinux.yml` 생성.
- `selinux_type` (정책) = **targeted**
- `selinux_mode` (모드) = **enforcing**
- selinux 역할 사용

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### `/home/user/ansible/selinux.yml`
```yaml
---
- name: configure selinux
  hosts: ______                 ← all
  become: true
  ______:                       ← vars
    selinux_policy: ____________ ← targeted
    selinux_state: ____________  ← enforcing
  ______:                       ← roles
    - rhel-system-roles.selinux
```

### 🧠 외우기 포인트 (감점 함정)
- 변수명: **`selinux_policy`**(정책=targeted), **`selinux_state`**(모드=enforcing)
  → 문제의 "type/mode" 표현과 실제 변수명이 다름! README에서 확인
- 역시 **tasks 없이 vars + roles**
- 롤 이름 `rhel-system-roles.selinux` (설치 방식 따라 `redhat.rhel_system_roles.selinux`)

---

## 4️⃣ 중요 명령어
```bash
sudo yum -y install rhel-system-roles     # (5번에서 이미 설치했으면 생략)
ansible-playbook selinux.yml --syntax-check
ansible-playbook selinux.yml
```

---

## 5️⃣ 모듈 / 역할
| 역할 | 핵심 변수 |
|------|------|
| `rhel-system-roles.selinux` | `selinux_policy`, `selinux_state` |

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
find /usr/share/ansible -type d -name "*selinux*"
less /usr/share/ansible/roles/rhel-system-roles.selinux/README.md
#   → /enforcing 또는 /Example 검색해 vars 블록 복사
```

---

## 7️⃣ 테스트 후 확인 방법
```bash
ansible-playbook selinux.yml
ansible all -m command -a "sestatus"     # Current mode: enforcing / policy: targeted
ansible all -m command -a "getenforce"   # Enforcing
```

### ✅ 합격 체크리스트
- [ ] `selinux.yml` 에 vars(selinux_policy/selinux_state) + roles 구조
- [ ] policy=targeted, state=enforcing
- [ ] `sestatus` 결과: enforcing + targeted
