# 문제 2. YUM Repository 연결

> PPT 기출 기반 · 모든 노드에 YUM 저장소 2개를 구성하는 **플레이북 작성**
> 핵심 모듈: `yum_repository` — 옵션 이름만 정확하면 끝나는 문제.

---

## 1️⃣ 개념

- **YUM/DNF Repository**: 패키지를 받아오는 저장소. RHEL은 보통 **BaseOS + AppStream** 두 개가 기본.
- `yum_repository` 모듈은 각 관리 노드의 `/etc/yum.repos.d/<name>.repo` 파일을 생성/관리.
  - `name` = **저장소 ID**이자 **파일명**(`.repo` 앞부분). → 저장소마다 **고유해야 함**.
- `gpgcheck`: 패키지 GPG 서명 검증 여부. `gpgkey`: 그 서명을 검증할 공개키 URL.
- 저장소가 **2개**면 → task도 **2개**(또는 loop). 이 문제는 task 2개로 쓰는 게 안전.

---

## 2️⃣ 문제 (기출 원문 요약)

> 모든 노드가 아래 조건의 YUM Repository를 구성하도록
> `/home/user/ansible/yum_repo.yml` 플레이북을 생성하시오.

**리포지토리 1**
- 이름: `EX294_BASE`
- 설명: `EX294 base software`
- 기본 URL: `http://yum.repo.red.hat.com/BaseOS`
- GPG 서명 확인: **yes** (gpgcheck)
- GPG 키 URL: `http://yum.repo.red.hat.com/RHEL/RPM-GPG-KEY-redhat-release`
- 저장소 활성화: `enabled=true`

**리포지토리 2**
- 이름: `EX294_STREAM` ← ⚠️ (슬라이드엔 EX294_BASE로 오타. **name은 겹치면 안 됨** → 시험 원문 이름 사용)
- 설명: `EX294 base software`
- 기본 URL: `http://yum.repo.red.hat.com/AppStream`
- GPG 서명 확인: yes
- GPG 키 URL: `http://yum.repo.red.hat.com/RHEL/RPM-GPG-KEY-redhat-release`
- 저장소 활성화: true

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### `/home/user/ansible/yum_repo.yml`
```yaml
______                                 ← ---  (플레이북 첫 줄!)
- name: configure yum repository
  hosts: ______                        ← all  (모든 노드)
  ______: true                         ← become  (/etc 아래 파일 생성 → 권한 필요)
  ______:                              ← tasks
    - name: EX294 BaseOS repo
      ansible.builtin.________________: ← yum_repository
        name: ____________             ← EX294_BASE
        description: ________________  ← EX294 base software
        baseurl: ____________________  ← http://yum.repo.red.hat.com/BaseOS
        gpgcheck: ______               ← yes  (= true)
        gpgkey: ______________________ ← http://yum.repo.red.hat.com/RHEL/RPM-GPG-KEY-redhat-release
        enabled: ______               ← yes  (= true)

    - name: EX294 AppStream repo
      ansible.builtin.yum_repository:
        name: ____________             ← EX294_STREAM  (1과 다른 이름!)
        description: EX294 base software
        baseurl: ____________________  ← http://yum.repo.red.hat.com/AppStream
        gpgcheck: yes
        gpgkey: http://yum.repo.red.hat.com/RHEL/RPM-GPG-KEY-redhat-release
        enabled: yes
```

### 🧠 외우기 포인트 (감점 함정)
- 옵션 6종 순서로 외우기: **name → description → baseurl → gpgcheck → gpgkey → enabled**
- ⚠️ 두 저장소의 **`name`은 반드시 다르게** (name = 파일명/ID라 같으면 하나가 덮어씀)
- ⚠️ `gpgcheck`/`gpgkey` **붙여쓰기·중복 금지**, gpgkey URL은 **별도 줄**
- `hosts: all` (모든 노드), `become: true` (/etc/yum.repos.d 에 쓰기)
- 플레이북이니 **첫 줄 `---` 있음** (인벤토리와 반대!)
- `yes`/`true` 둘 다 동작하지만 한 가지로 통일

---

## 4️⃣ 중요 명령어

```bash
cd /home/user/ansible
vim yum_repo.yml                       # 위 내용 작성

ansible-playbook yum_repo.yml --syntax-check   # 문법 검사
ansible-playbook yum_repo.yml                  # 실행
```

---

## 5️⃣ 모듈

| 모듈 | 용도 | 핵심 옵션 |
|------|------|------|
| `ansible.builtin.yum_repository` | .repo 파일 생성/관리 | name, description, baseurl, gpgcheck, gpgkey, enabled, file |

> `file:` 옵션을 주면 `/etc/yum.repos.d/<file>.repo` 로 파일명 지정 가능(여러 repo를 한 파일에).
> 문제에서 파일명 지정이 없으면 생략(→ name 기준으로 파일 생성).

---

## 6️⃣ 잊어버렸을 때 검색하는 법

```bash
# 옵션 이름이 기억 안 날 때 → 시험장의 검색엔진
ansible-doc yum_repository             # 전체 문서 + 하단 EXAMPLES
#   문서 열고 /EXAMPLES  또는  /EXAM  으로 검색 → 예제 블록 통째로 긁어서 값만 수정

ansible-doc -s yum_repository          # 옵션만 빠르게 (스니펫)
ansible-doc -l | grep -i repo          # 모듈명이 애매할 때
```
> 💡 시험 팁(슬라이드): `ansible-doc yum_repository` 열고 **`/EXAM`** 검색 → 필요한 모듈 블록 긁어서 붙이고 값만 바꾼다. 옵션 이름을 외우는 것보다 이게 빠르고 정확.

---

## 7️⃣ 테스트 후 확인 방법

```bash
# ① 문법 → 실행
ansible-playbook yum_repo.yml --syntax-check
ansible-playbook yum_repo.yml

# ② 저장소가 실제로 생겼는지 (모든 노드)
ansible all -m command -a "yum repolist"
ansible all -m command -a "ls /etc/yum.repos.d/"

# ③ .repo 파일 내용 직접 확인
ansible all -m command -a "cat /etc/yum.repos.d/EX294_BASE.repo"
```

### ✅ 합격 체크리스트
- [ ] `yum_repo.yml` 첫 줄 `---` 있음
- [ ] `hosts: all`, `become: true`
- [ ] task 2개 (BaseOS / AppStream), **name이 서로 다름**
- [ ] 각 repo: name/description/baseurl/gpgcheck/gpgkey/enabled 6개 모두 채움
- [ ] `ansible-playbook yum_repo.yml` 성공 (에러 없음)
- [ ] `yum repolist` 에 두 저장소가 보임
