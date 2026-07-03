# 문제 12. 파일 내용 수정 (/etc/issue, 그룹별 다른 내용)

> PPT 기출 · 그룹마다 다른 텍스트를 파일에 넣는 문제.
> 핵심: `copy` 의 `content` + `when` 으로 그룹 분기.

---

## 1️⃣ 개념

- `copy` 모듈은 파일 복사뿐 아니라 **`content:` 로 인라인 텍스트**를 파일에 쓸 수 있음.
- `when: inventory_hostname in groups['<그룹>']` 로 호스트 그룹별 분기.
- 같은 파일이지만 그룹마다 다른 내용 → task 3개 (또는 변수).

---

## 2️⃣ 문제 (기출 원문 요약)

> `/home/user/ansible/issue.yml`, 모든 호스트에서 실행.
> `/etc/issue` 내용을 한 줄 텍스트로 교체:
- dev 그룹 → `Development`
- test 그룹 → `Test`
- prod 그룹 → `Production`

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### `/home/user/ansible/issue.yml`
```yaml
---
- name: set issue
  hosts: ______                    ← all
  become: true
  tasks:
    - name: dev
      ansible.builtin.____:         ← copy
        content: "____________\n"   ← Development
        dest: /etc/issue
      when: inventory_hostname in groups['____']   ← dev

    - name: test
      ansible.builtin.copy:
        content: "Test\n"
        dest: /etc/issue
      when: inventory_hostname in groups['test']

    - name: prod
      ansible.builtin.copy:
        content: "Production\n"
        dest: /etc/issue
      when: inventory_hostname in groups['prod']
```

### 🧠 외우기 포인트 (감점 함정)
- 파일에 인라인 텍스트 → **`copy` + `content`** (파일 복사 아님)
- 그룹 분기: **`when: inventory_hostname in groups['dev']`** (외우기)
- `content` 끝에 `\n` 붙여 줄바꿈 (한 줄 텍스트)
- ⚠️ `inventory_hostname`(인벤토리상 이름) vs `ansible_hostname`(팩트) 구분

---

## 4️⃣ 중요 명령어
```bash
vim /home/user/ansible/issue.yml
ansible-playbook issue.yml --syntax-check
ansible-playbook issue.yml
```

---

## 5️⃣ 모듈
| 모듈 | 용도 |
|------|------|
| `ansible.builtin.copy` | `content` 로 파일 내용 작성 |

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
ansible-doc copy           # 열고 /content 검색 → content 옵션 예제
```
> "파일 내용을 인라인으로" = `copy` 의 `content`.

---

## 7️⃣ 테스트 후 확인 방법
```bash
ansible-playbook issue.yml
ansible dev  -m command -a "cat /etc/issue"   # Development
ansible test -m command -a "cat /etc/issue"   # Test
ansible prod -m command -a "cat /etc/issue"   # Production
```

### ✅ 합격 체크리스트
- [ ] `copy` + `content` 사용
- [ ] task 3개, 각각 `when: inventory_hostname in groups[...]`
- [ ] dev/test/prod 별로 올바른 텍스트 출력
