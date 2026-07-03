# 문제 7. Ansible Galaxy로 역할 설치 (requirements.yml)

> PPT 기출 · URL에서 롤 2개를 받아 설치하는 **requirements.yml** 작성 + 설치.
> 핵심: 롤은 **`- name/src` 리스트**, 설치는 **`install -r`** (콜렉션과 구분!).

---

## 1️⃣ 개념

- **requirements.yml**: 설치할 롤/콜렉션 목록을 적는 파일.
- **롤 설치**: `ansible-galaxy install -r requirements.yml`
- **콜렉션 설치**: `ansible-galaxy collection install -r requirements.yml` (3번 문제)
- 롤 항목은 `- name:`(설치될 이름) + `src:`(다운로드 URL) 형태.

---

## 2️⃣ 문제 (기출 원문 요약)

> `/home/user/ansible/roles/requirements.yml` 로 Galaxy 역할 다운로드 구성.
- 역할 1: 이름 `balancer`, URL `http://ansible.galaxy.com/materials/haproxy.tar`
- 역할 2: 이름 `phpinfo`, URL `http://ansible.galaxy.com/materials/phpinfo.tar`

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### `/home/user/ansible/roles/requirements.yml`
```yaml
- ______: balancer                                       ← name
  ______: http://ansible.galaxy.com/materials/haproxy.tar ← src
- name: phpinfo
  src: http://ansible.galaxy.com/materials/phpinfo.tar
```
> ℹ️ requirements.yml 은 **첫 줄 `---` 없이** 바로 `- name:` 부터 시작해도 됨 (실제 정답도 없음).
> `---`는 YAML 문서 시작 표시라 있어도 동작은 하지만, 관례상 안 붙임.

### 설치 명령
```bash
ansible-galaxy ________ -r /home/user/ansible/roles/requirements.yml     ← install
#   (롤 = install -r,  콜렉션 = collection install -r)
#   경로 지정 필요 시:  ____ roles/                                       ← -p
```

### 🧠 외우기 포인트 (감점 함정)
- 롤 항목 = **`- name` + `src`** (콜렉션은 `collections:` 리스트라 다름!)
- 설치: **롤 = `ansible-galaxy install -r`**, 콜렉션 = `collection install -r` ← ⭐ 최대 함정
- `src` 는 다운로드 URL, `name` 은 설치 후 롤 디렉토리 이름
- 설치 경로는 ansible.cfg 의 `roles_path` 와 맞게 (또는 `-p`)

---

## 4️⃣ 중요 명령어
```bash
vim /home/user/ansible/roles/requirements.yml
ansible-galaxy install -r /home/user/ansible/roles/requirements.yml
ansible-galaxy install -r requirements.yml -p roles/     # 경로 지정
```

---

## 5️⃣ 모듈 / 도구
- 모듈 아님 → **`ansible-galaxy` CLI** (`install` 하위 명령).

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
ansible-galaxy install --help      # -r, -p 옵션 확인
ansible-galaxy role list           # 설치된 롤 목록
```

---

## 7️⃣ 테스트 후 확인 방법
```bash
ansible-galaxy role list           # balancer, phpinfo 표시
ls /home/user/ansible/roles/       # balancer/ phpinfo/ 디렉토리 확인
```

### ✅ 합격 체크리스트
- [ ] requirements.yml 에 롤 2개 (`- name`/`src`)
- [ ] `ansible-galaxy install -r` 로 설치 (collection install 아님)
- [ ] `roles/` 에 balancer, phpinfo 디렉토리 생성됨
