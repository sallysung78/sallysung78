# 문제 13. 웹 컨텐츠 디렉터리 생성 (file 모듈)

> PPT 기출 · `file` 모듈로 디렉터리·권한(특수권한)·심볼릭 링크·SELinux 컨텍스트 처리.
> 핵심: `file` 하나로 directory/link 다 처리, mode 2775, setype.

---

## 1️⃣ 개념

- `file` 모듈: `state` 로 디렉터리(`directory`)·링크(`link`)·빈파일(`touch`)·삭제(`absent`).
- **특수권한 setgid(2)** + rwxrwxr-x = **`2775`**.
- 웹서버(apache)가 읽으려면 **SELinux 타입 `httpd_sys_content_t`** 필요.

---

## 2️⃣ 문제 (기출 원문 요약)

> `/home/user/ansible/webcontent.yml`, **dev 그룹**에서 실행.
- `/webdev` 디렉터리 생성 (`state: directory`)
  - `webdev` 그룹 소유
  - 권한 `2775` (소유자 rwx=7, 그룹 rwx=7, 기타 r-x=5, setgid=2)
- `/var/www/html/webdev` → `/webdev` 심볼릭 링크
- `/webdev/index.html` 에 `Development` 한 줄
- 웹 접근 시 Development 출력 (→ SELinux `httpd_sys_content_t`)

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### `/home/user/ansible/webcontent.yml`
```yaml
---
- name: web content
  hosts: ______                    ← dev
  become: true
  tasks:
    - name: create dir
      ansible.builtin.____:         ← file
        path: /webdev
        state: ____________         ← directory
        group: webdev
        mode: '______'              ← 2775
        setype: __________________  ← httpd_sys_content_t

    - name: symlink
      ansible.builtin.file:
        src: /webdev
        dest: /var/www/html/webdev
        state: ______               ← link

    - name: index
      ansible.builtin.____:         ← copy
        content: "Development\n"
        dest: /webdev/index.html
        setype: httpd_sys_content_t
```

### 🧠 외우기 포인트 (감점 함정)
- 디렉터리·링크 = **`file` 모듈**, `state` 로 구분 (directory / link)
- 권한 **`mode: '2775'`** (따옴표! setgid=2)
- 링크: `src`(원본) → `dest`(링크 위치), `state: link`
- 웹에서 읽으려면 **`setype: httpd_sys_content_t`**
- index.html 내용은 `copy` + `content`

---

## 4️⃣ 중요 명령어
```bash
vim /home/user/ansible/webcontent.yml
ansible-playbook webcontent.yml --syntax-check
ansible-playbook webcontent.yml
```

---

## 5️⃣ 모듈
| 모듈 | 용도 |
|------|------|
| `ansible.builtin.file` | 디렉터리(directory)·링크(link)·권한·setype |
| `ansible.builtin.copy` | index.html 내용 작성 |

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
ansible-doc file           # state(directory/link/touch/absent), mode, setype, group
ansible-doc copy           # content
```

---

## 7️⃣ 테스트 후 확인 방법
```bash
ansible-playbook webcontent.yml
ansible dev -m command -a "ls -ldZ /webdev"           # 권한 2775 + httpd_sys_content_t
ansible dev -m command -a "ls -l /var/www/html/webdev" # 심볼릭 링크 확인
curl http://node1/webdev/                              # Development
```

### ✅ 합격 체크리스트
- [ ] `/webdev` 디렉터리, group=webdev, mode 2775, setype httpd_sys_content_t
- [ ] `/var/www/html/webdev` → `/webdev` 심볼릭 링크
- [ ] `/webdev/index.html` = Development
- [ ] `curl http://node1/webdev/` → Development
