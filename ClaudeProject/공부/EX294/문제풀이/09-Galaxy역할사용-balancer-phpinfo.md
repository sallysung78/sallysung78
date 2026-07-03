# 문제 9. Ansible Galaxy에서 역할 사용 (balancer / phpinfo)

> PPT 기출 · 7번에서 설치한 롤(balancer, phpinfo)을 **호출**하는 플레이북.
> 핵심: 그룹별로 다른 롤 실행. tasks 대신 `roles:`.

---

## 1️⃣ 개념

- 이미 설치된 롤(7번의 balancer/phpinfo)을 **호출**만 하는 문제.
- **balancer**: webservers 요청을 여러 웹서버로 **부하 분산**(HAProxy).
- **phpinfo**: webservers에 `/hello.php` 배포 → `Hello PHP from FQDN` 출력.
- 그룹마다 다른 롤 → **play를 2개**로 나눔.

---

## 2️⃣ 문제 (기출 원문 요약)

> `/home/user/ansible/roles.yml` 생성.
- `balancers` 그룹 → `balancer` 역할 (webservers로 부하 분산)
  - `http://node5` 접속 시 새로고침마다 `Hello node3` / `Hello node4` 번갈아 출력
- `webservers` 그룹 → `phpinfo` 역할
  - `http://node3/hello.php` → `Hello PHP from node3.redfaceh.com`

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### `/home/user/ansible/roles.yml`
```yaml
---
- name: load balancer
  hosts: ____________          ← balancers
  become: true
  ______:                      ← roles
    - balancer

- name: php info
  hosts: ____________          ← webservers
  become: true
  roles:
    - ________                 ← phpinfo
```

### 🧠 외우기 포인트 (감점 함정)
- **7번(설치)이 먼저 되어야 9번(사용)이 됨** — 롤이 `roles/` 에 있어야 호출 가능
- 그룹별로 다른 롤 → **play 2개** (balancers용 / webservers용)
- 호출은 `tasks` 가 아니라 **`roles:`**
- balancer는 `balancers` 그룹에서, phpinfo는 `webservers` 그룹에서 실행

---

## 4️⃣ 중요 명령어
```bash
vim /home/user/ansible/roles.yml
ansible-playbook roles.yml --syntax-check
ansible-playbook roles.yml
```

---

## 5️⃣ 모듈 / 역할
- 설치된 롤 `balancer`, `phpinfo` 를 `roles:` 로 호출 (별도 모듈 없음).

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
ansible-galaxy role list                       # balancer, phpinfo 설치 확인
ls roles/balancer/tasks/ roles/phpinfo/tasks/  # 롤 내용 참고
cat roles/phpinfo/README.md                    # 롤 사용법/변수 확인
```

---

## 7️⃣ 테스트 후 확인 방법
```bash
ansible-playbook roles.yml

# 부하 분산 확인 (여러 번 호출 → node3/node4 번갈아)
curl http://node5     # Hello node3
curl http://node5     # Hello node4

# phpinfo 확인
curl http://node3/hello.php    # Hello PHP from node3.redfaceh.com
curl http://node4/hello.php    # Hello PHP from node4.redfaceh.com
```
> ⚠️ 함정: `/hello.php/hello.php` 처럼 경로 중복 입력 금지.

### ✅ 합격 체크리스트
- [ ] `roles.yml` 에 play 2개 (balancers→balancer, webservers→phpinfo)
- [ ] `roles:` 로 호출 (tasks 아님)
- [ ] curl node5 새로고침 → node3/node4 번갈아 출력
- [ ] curl node3/hello.php → Hello PHP from FQDN
