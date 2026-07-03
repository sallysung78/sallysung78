# 문제 18. cron 설정

> PPT 기출 · `cron` 모듈로 사용자 crontab 등록. 짧고 확실한 득점 문제.
> 핵심: `cron` 모듈의 name/minute/user/job.

---

## 1️⃣ 개념

- `cron` 모듈: 특정 사용자의 crontab(예약 작업)을 관리.
- `name` = 항목 식별자(주석으로 들어감, **멱등성 키**). `minute/hour/...` = 스케줄.
- `user` = 어느 사용자의 crontab. `job` = 실행할 명령.
- 시스템 crontab(`/etc/cron.d/`)이 필요하면 `cron_file:` 옵션 사용.

---

## 2️⃣ 문제 (기출 원문 요약)

> `/home/user/ansible/cron.yml`, `hosts: all`.
- 사용자 `natasha` 의 crontab에 작업 추가
- **2분마다** (`*/2`) 실행
- 명령: `logger "EX294 in progress"`

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### `/home/user/ansible/cron.yml`
```yaml
---
- name: cron
  hosts: ______                    ← all
  become: true
  tasks:
    - name: add cron
      ansible.builtin.____:         ← cron
        name: add cron natasha
        minute: "______"            ← */2   (2분마다)
        user: ____________          ← natasha
        job: logger "EX294 in progress"
```

### 🧠 외우기 포인트 (감점 함정)
- 모듈 = **`cron`**, 필수: `name`, `minute`, `user`, `job`
- **2분마다 = `minute: "*/2"`** (따옴표)
- `name` 은 crontab에 주석으로 남고 중복 방지 키 → 의미 있게
- 시스템 cron(`/etc/cron.d`) 요구 시 → **`cron_file:`** + `user:` 추가

---

## 4️⃣ 중요 명령어
```bash
vim /home/user/ansible/cron.yml
ansible-playbook cron.yml --syntax-check
ansible-playbook cron.yml
```

---

## 5️⃣ 모듈
| 모듈 | 핵심 옵션 |
|------|------|
| `ansible.builtin.cron` | name, minute/hour/day/weekday, user, job, cron_file |

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
ansible-doc cron           # minute/hour/weekday/user/job/cron_file 예제
```
> "/etc/cron.d 파일 생성" 요구면 `cron_file` 옵션이 핵심.

---

## 7️⃣ 테스트 후 확인 방법
```bash
ansible-playbook cron.yml
ansible all -m command -a "crontab -u natasha -l"     # 등록된 작업 확인
ansible all -m command -a "grep CRON /var/log/cron"   # 실제 실행 로그
# 2분 기다린 뒤 logger 메시지가 뜨는지도 확인
```

### ✅ 합격 체크리스트
- [ ] `cron` 모듈, user=natasha
- [ ] `minute: "*/2"`
- [ ] job = `logger "EX294 in progress"`
- [ ] `crontab -u natasha -l` 에 항목 표시
