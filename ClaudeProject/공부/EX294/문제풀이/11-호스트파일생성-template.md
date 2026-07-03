# 문제 11. 호스트 파일 생성 (Jinja2 Template)

> 🔴 취약 분야 "Manage content" · 템플릿 + facts + for 반복.
> 핵심: `hosts.j2` 작성(외우기) → `template` 모듈로 dev 그룹에 배포.

---

## 1️⃣ 개념

- **템플릿(Jinja2)**: 각 노드에 맞게 값이 채워지는 설정 파일 생성.
- `groups['all']` 로 모든 인벤토리 호스트를 돌며 `hostvars` 에서 IP/FQDN/hostname 추출.
- `template` 모듈: `src`(*.j2) → `dest`(생성 위치).
- `/etc/hosts` 형식 = `IP FQDN shortname` 한 줄.

---

## 2️⃣ 문제 (기출 원문 요약)

> - `http://materials.classroom.com/hosts.j2` 를 `/home/user/ansible` 로 다운로드(wget)
> - `/etc/hosts` 형식으로 각 인벤토리 호스트 줄이 들어가게 템플릿 작성
> - `/home/user/ansible/hosts.yml` 로 **dev 그룹**의 `/etc/myhosts` 생성

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### `hosts.j2` (템플릿 — 외우기!)
```jinja
{% ______ host in groups['all'] %}        ← for
{{ hostvars[host]['ansible_facts']['default_ipv4']['address'] }} {{ hostvars[host]['ansible_facts']['fqdn'] }} {{ hostvars[host]['ansible_facts']['hostname'] }}
{% ______ %}                              ← endfor
```

### `/home/user/ansible/hosts.yml`
```yaml
---
- name: gen hosts
  hosts: ______                    ← all   (facts 수집 위해 all에서 실행)
  become: true
  tasks:
    - name: deploy myhosts
      ansible.builtin.____________: ← template
        src: hosts.j2
        dest: /etc/myhosts
      when: inventory_hostname in groups['____']    ← dev
```

### 🧠 외우기 포인트 (감점 함정)
- **`{% for host in groups['all'] %}` … `{% endfor %}`** 통째로 외우기
- 한 호스트 = **한 줄** (IP FQDN shortname)
- facts 경로: `hostvars[host]['ansible_facts']['default_ipv4']['address']`
- `template` 은 `templates/` 폴더 없이 현재 경로의 `hosts.j2` 도 가능 (플레이북과 같은 위치)
- `when: inventory_hostname in groups['dev']` 로 dev만 생성

---

## 4️⃣ 중요 명령어
```bash
cd /home/user/ansible
wget http://materials.classroom.com/hosts.j2
vim hosts.j2                        # for 루프 작성
vim hosts.yml
ansible-playbook hosts.yml --syntax-check
ansible-playbook hosts.yml
```

---

## 5️⃣ 모듈
| 모듈 | 용도 |
|------|------|
| `ansible.builtin.template` | j2 → 대상 파일 생성 (src/dest) |

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
ansible-doc template                          # src, dest
ansible all -m setup | less                   # facts 이름 확인
ansible localhost -m setup -a 'filter=ansible_default_ipv4'
ansible localhost -m setup -a 'filter=ansible_fqdn'
```
> 💡 fact 이름은 외우지 말고 `setup` 결과에서 확인.

---

## 7️⃣ 테스트 후 확인 방법
```bash
ansible-playbook hosts.yml
ansible dev -m command -a "cat /etc/myhosts"
#   → 각 관리 호스트마다 한 줄 (IP FQDN hostname)
```
> 참고: 호스트가 나오는 순서는 중요하지 않음.

### ✅ 합격 체크리스트
- [ ] `hosts.j2` 에 for/endfor 루프 + IP/FQDN/hostname
- [ ] `hosts.yml` 이 template 모듈로 `/etc/myhosts` 생성
- [ ] `when: inventory_hostname in groups['dev']`
- [ ] dev 노드의 `/etc/myhosts` 에 모든 호스트 줄 존재
