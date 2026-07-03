# 문제 17. Ansible Vault 키 다시 입력 (rekey)

> 🔴 취약 분야 "Manage content" · **가장 쉬운 Vault 문제** (슬라이드: "제일 쉬워").
> 핵심: 파일 다운로드 → `ansible-vault rekey` 로 암호만 교체.

---

## 1️⃣ 개념

- **rekey**: 이미 암호화된 Vault 파일의 **비밀번호만 변경** (내용은 암호화 상태 유지).
- 옛 암호로 풀고 → 새 암호로 다시 잠금. 한 줄 명령이면 끝.

---

## 2️⃣ 문제 (기출 원문 요약)

> - `http://materials.classroom.com/salaries.yml` → `/home/user/ansible` 다운로드
> - 현재 Vault 암호: `insecure`
> - 새 Vault 암호: `bbe2de9838b`
> - 파일은 **암호화된 상태 유지** (새 암호로)

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

```bash
cd /home/user/ansible
______ http://materials.classroom.com/salaries.yml     ← wget

ansible-vault ______ salaries.yml       ← rekey
#   Vault password (old): ____________  ← insecure
#   New Vault password:   ____________  ← bbe2de9838b
#   Confirm New Vault password: bbe2de9838b
```

### (대안) 비밀번호 프롬프트 방식
```bash
ansible-vault rekey --ask-vault-pass salaries.yml
```

### 🧠 외우기 포인트 (감점 함정)
- 명령: **`ansible-vault rekey <파일>`**
- old = `insecure`, new = `bbe2de9838b`
- ⚠️ 비밀번호 **철자 정확히** (슬라이드/문제 원문 값이 다를 수 있음 → 문제 원문 우선)
- 끝나도 파일은 **암호화 상태 유지** (decrypt 하면 안 됨!)

---

## 4️⃣ 중요 명령어
```bash
wget http://materials.classroom.com/salaries.yml
ansible-vault rekey salaries.yml
```

---

## 5️⃣ 모듈 / 도구
- 모듈 아님 → **`ansible-vault rekey`** CLI.

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
ansible-vault --help          # rekey 하위 명령 확인
ansible-vault rekey --help    # --ask-vault-pass / --vault-password-file 옵션
```

---

## 7️⃣ 테스트 후 확인 방법
```bash
# 새 암호로 열리는지 확인 (내용 보이면 성공)
ansible-vault view salaries.yml         # → New Vault password: bbe2de9838b 입력
head -1 salaries.yml                     # $ANSIBLE_VAULT;1.1;AES256 (여전히 암호화)
```

### ✅ 합격 체크리스트
- [ ] `salaries.yml` 다운로드됨
- [ ] `ansible-vault rekey` 로 암호 변경 (insecure → bbe2de9838b)
- [ ] 파일이 여전히 암호화 상태 (`$ANSIBLE_VAULT` 헤더)
- [ ] 새 암호로 `view` 시 내용 정상 표시
