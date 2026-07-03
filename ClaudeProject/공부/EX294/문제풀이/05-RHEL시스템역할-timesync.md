# 문제 5. RHEL 시스템 역할 사용 - timesync (NTP)

> PPT 기출 · System Role `timesync` 로 NTP 구성. **변수명이 정답**인 문제.
> 핵심: tasks 없이 **vars + roles**. 변수명은 README에서 찾는다.

---

## 1️⃣ 개념

- **RHEL System Roles**: 레드햇이 제공하는 표준 롤 모음(`rhel-system-roles` 패키지).
- System Role은 **직접 task를 쓰지 않고**, 롤을 호출하며 **`vars` 로 요구값만 전달**.
- `timesync` = 시간 동기화(NTP/chrony) 구성 롤.
- 변수명은 **외우지 말고** 롤 `README.md` 의 Example에서 복사 → 값만 수정.

---

## 2️⃣ 문제 (기출 원문 요약)

> `/home/user/ansible/ntp-role.yml` 생성, 모든 노드에서 실행.
- `timesync` 역할 사용
- 활성 NTP 데몬 사용하도록 구성 (`timesync_ntp_servers`)
- 타임 서버 **192.168.0.254** (hostname)
- **iburst** 매개변수 활성화

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### (준비) 롤 설치
```bash
sudo yum -y install ____________________     ← rhel-system-roles  (외우기!)
```

### `/home/user/ansible/ntp-role.yml`
```yaml
---
- name: configure ntp
  hosts: ______                    ← all
  become: true
  ______:                          ← vars   (tasks 아님!)
    timesync_ntp_servers:
      - hostname: ______________   ← 192.168.0.254
        ______: true               ← iburst
  ______:                          ← roles
    - rhel-system-roles.timesync   ← (또는 redhat.rhel_system_roles.timesync)
```

### 🧠 외우기 포인트 (감점 함정)
- System Role은 **`tasks` 가 없다! `vars` + `roles`** 로 구성
- 롤 설치 명령 **`sudo yum -y install rhel-system-roles`** 는 통째로 외우기
- 롤 이름은 설치 방식에 따라 `rhel-system-roles.timesync` 또는 `redhat.rhel_system_roles.timesync` → README에서 확인
- NTP IP는 **문제 원문 값** 사용 (예시 IP와 다를 수 있음)

---

## 4️⃣ 중요 명령어
```bash
sudo yum -y install rhel-system-roles
ls /usr/share/ansible/roles/                         # 설치된 롤 경로
ansible-playbook ntp-role.yml --syntax-check
ansible-playbook ntp-role.yml
```

---

## 5️⃣ 모듈 / 역할
| 역할 | 핵심 변수 |
|------|------|
| `rhel-system-roles.timesync` | `timesync_ntp_servers` (하위: `hostname`, `iburst`) |

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
# 변수명이 정답 → README에서 찾기
find /usr/share/ansible -type d -name "*timesync*"
less /usr/share/ansible/roles/rhel-system-roles.timesync/README.md
#   → README에서 /iburst 또는 /Example 검색해 vars 블록 복사
grep -R "timesync_ntp_servers" /usr/share/ansible/roles/
```
> 💡 System Role 문제는 **README의 Example 복사 → 값만 수정**이 정석.

---

## 7️⃣ 테스트 후 확인 방법
```bash
ansible-playbook ntp-role.yml
ansible all -m command -a "chronyc sources"          # NTP 소스 확인
ansible all -m command -a "cat /etc/chrony.conf"     # server 192.168.0.254 iburst 확인
```

### ✅ 합격 체크리스트
- [ ] `rhel-system-roles` 설치됨
- [ ] `ntp-role.yml` 에 `vars`(timesync_ntp_servers) + `roles` 구조
- [ ] hostname 192.168.0.254, iburst: true
- [ ] `chronyc sources` 에 해당 서버 표시
