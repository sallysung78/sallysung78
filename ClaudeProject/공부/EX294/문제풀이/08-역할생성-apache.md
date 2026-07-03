# 문제 8. 역할 생성 (Custom Role - apache)

> PPT 기출 · `apache` 커스텀 롤을 직접 만들고 플레이북으로 호출.
> 핵심: `ansible-galaxy init` + tasks(yum/service/firewalld/template) + templates/*.j2.

---

## 1️⃣ 개념

- **Custom Role**: 내가 직접 만드는 롤. `ansible-galaxy init` 으로 뼈대 생성.
- 롤 구조: `tasks/main.yml`(핵심), `templates/`(*.j2), `handlers/`, `files/` ...
- **롤은 호출당하는 쪽** → 롤 내부 YAML에 **`hosts` 없음**. `tasks/main.yml` 부터 실행.
- 호출은 별도 플레이북에서 `roles:` 로.

---

## 2️⃣ 문제 (기출 원문 요약)

> `/home/user/ansible/roles/apache` 역할 생성:
- `httpd` 패키지 설치
- 서비스: 부팅 시 실행(`enabled: true`) + 실행 중(`state: started`)
- 방화벽: 외부에서 httpd 접근 가능하게 (firewalld http 허용)
- 템플릿 `index.html.j2` → 배포 시 `/var/www/html/index.html` 로 저장
  - 출력: `Hello Apache from HOSTNAME on IPADDR`
- `/home/user/ansible/run-role.yml` 로 **webservers** 그룹에 이 역할 실행

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### (준비) 롤 뼈대 생성
```bash
cd /home/user/ansible
ansible-galaxy ______ roles/apache        ← init   (roles/apache 디렉토리 생성)
```

### `roles/apache/tasks/main.yml` (hosts 없음!)
```yaml
---
- name: install httpd
  ansible.builtin.____:              ← yum
    name: httpd
    state: latest

- name: start httpd
  ansible.builtin.service:
    name: httpd
    state: ______                    ← started
    enabled: ______                  ← true

- name: start firewalld
  ansible.builtin.service:
    name: firewalld
    state: started
    enabled: true

- name: allow http
  ansible.posix.____________:        ← firewalld
    service: http
    state: ______                    ← enabled
    permanent: true
    immediate: true

- name: deploy index
  ansible.builtin.____________:      ← template
    src: index.html.j2               ← templates/ 안의 파일
    dest: /var/www/html/index.html
```

### `roles/apache/templates/index.html.j2`
```jinja
Hello Apache from {{ ansible_facts['hostname'] }} on {{ ansible_facts['default_ipv4']['address'] }}
```

### `/home/user/ansible/run-role.yml` (호출 플레이북)
```yaml
---
- hosts: ______                      ← webservers
  become: true
  ______:                            ← roles   (tasks 아님!)
    - apache
```

### 🧠 외우기 포인트 (감점 함정)
- 롤 내부 tasks에는 **`hosts` 없음** (호출 플레이북에만 있음)
- 호출 플레이북은 **`roles:` - apache** (tasks 아님)
- 4가지: **설치(yum) → 서비스(service) → 방화벽(firewalld) → 템플릿(template)**
- 템플릿은 `templates/` 폴더에 `.j2` 로, `src:` 엔 파일명만
- firewalld: `permanent: true` + `immediate: true` (재부팅 후에도 유지)

---

## 4️⃣ 중요 명령어
```bash
ansible-galaxy init roles/apache
vim roles/apache/tasks/main.yml
vim roles/apache/templates/index.html.j2
vim run-role.yml
ansible-playbook run-role.yml --syntax-check
ansible-playbook run-role.yml
```

---

## 5️⃣ 모듈
| 모듈 | 용도 |
|------|------|
| `yum` | httpd 설치 |
| `service` | httpd/firewalld 시작 + enabled |
| `ansible.posix.firewalld` | http 서비스 허용 |
| `template` | index.html.j2 배포 |

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
ansible-doc yum
ansible-doc service
ansible-doc firewalld       # service/port, permanent, immediate, state
ansible-doc template        # src, dest
ansible localhost -m setup -a 'filter=ansible_fqdn'          # 템플릿 변수명 확인
ansible localhost -m setup -a 'filter=ansible_default_ipv4'
```

---

## 7️⃣ 테스트 후 확인 방법
```bash
ansible-playbook run-role.yml
curl http://<webserver-IP>          # → Hello Apache from node3 on 172.x.x.x
ansible webservers -m command -a "systemctl is-enabled httpd"
```

### ✅ 합격 체크리스트
- [ ] `roles/apache/` 구조 생성 (init)
- [ ] tasks: yum → service(httpd,firewalld) → firewalld(http) → template
- [ ] `templates/index.html.j2` 에 Hello Apache 출력
- [ ] `run-role.yml` 이 webservers 에 `roles: - apache`
- [ ] `curl` 로 각 노드 hostname/IP 출력 확인
