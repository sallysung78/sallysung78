# 문제 10. 논리 볼륨 생성 (LVM + block/rescue)

> PPT 기출 · 조건부 실패 처리(block/rescue)가 핵심인 LVM 문제.
> 핵심: `lvol` + `filesystem`, 실패 시 rescue에서 **`when`으로 두 경우 분기**.

---

## ⭐ 정답 (완성본)

```yaml
---
- hosts: all
  tasks:
  - block:
      - name: Create a logical volume of 1500m
        lvol:
          vg: research
          lv: data
          size: 1500m
      - name: Create a ext4
        filesystem:
          fstype: ext4
          dev: /dev/research/data
    rescue:
      - debug:
          msg: Could not create logical volume of that size
      - name: Create a logical volume of 800m
        lvol:
          vg: research
          lv: data
          size: 800m
        when: ansible_lvm.vgs.research is defined
        ignore_errors: yes
      - debug:
          msg: Volume group not found
        when: ansible_lvm.vgs.research is undefined
```
> ⚠️ 마지막 debug의 `msg` 는 **문제 원문의 요구 문구와 정확히 일치**시켜야 함
> (원문: `Volume group not found`). 철자/대소문자 그대로.

---

## 1️⃣ 개념

- **LVM**: vg(볼륨그룹) 안에 lv(논리볼륨) 생성 → 파일시스템 포맷.
- **block/rescue** (try/except 같은 구조):
  - `block`: 정상 시도 (1500m 생성 + ext4 포맷)
  - `rescue`: block이 **실패했을 때만** 실행 (대체 처리)
- 이 문제의 rescue는 **`when` 으로 두 상황을 나눠서** 처리:
  1. **vg는 있는데 1500m가 너무 큼** → `is defined` → 800m로 재생성
  2. **vg 자체가 없음** → `is undefined` → "Volume group not found" 메시지
- 그래서 `always` 없이 **rescue 안에서 다 처리**하는 게 이 정답의 포인트.

---

## 2️⃣ 문제 (기출 원문 요약)

> `/home/user/ansible/lv.yml`, `hosts: all`.
- 볼륨그룹(vg) `research`, 논리볼륨(lv) `data`, 크기 **1500 MiB**, **ext4** 포맷 (block)
- 크기 생성 불가 시 → `Could not create logical volume of that size` 출력 후 **800 MiB** 로 생성 (rescue)
- `research` vg 없으면 → `Volume group not found` 출력
- ⚠️ 논리 볼륨은 **마운트하지 않는다** (건드리지 말 것)

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### `/home/user/ansible/lv.yml`
```yaml
---
- hosts: ______                          ← all
  tasks:
  - ______:                              ← block
      - name: Create a logical volume of 1500m
        ______:                          ← lvol
          vg: research
          lv: data
          size: ______                   ← 1500m
      - name: Create a ext4
        ____________:                    ← filesystem
          fstype: ______                 ← ext4
          dev: /dev/research/data
    ______:                              ← rescue
      - ______:                          ← debug
          msg: Could not create logical volume of that size
      - name: Create a logical volume of 800m
        lvol:
          vg: research
          lv: data
          size: ______                   ← 800m
        when: ansible_lvm.vgs.research is ________     ← defined  (vg 있을 때만)
        ignore_errors: yes
      - debug:
          msg: Volume group not found
        when: ansible_lvm.vgs.research is __________   ← undefined  (vg 없을 때만)
```

### 🧠 외우기 포인트 (감점 함정)
- 구조: **block → rescue** (이 정답은 `always` 안 씀 — rescue의 `when`으로 분기)
- rescue 안 3개: **debug(실패메시지) → lvol(800m) → debug(vg없음)**
- 800m 생성: **`when: ...is defined`** + **`ignore_errors: yes`** (vg 있을 때만 시도, 실패해도 무시)
- vg 없음 메시지: **`when: ...is undefined`**
- 조건 변수: **`ansible_lvm.vgs.research`** (짧은 fact 표기), `is defined` / `is undefined`
- 크기: `1500m`, `800m` (MiB)
- ⚠️ **마운트 task 넣지 말 것** (문제에서 마운트 금지)
- ⚠️ debug 메시지 문구는 **문제 원문과 정확히 일치** (`Volume group not found`)

---

## 4️⃣ 중요 명령어
```bash
vim /home/user/ansible/lv.yml
ansible-playbook lv.yml --syntax-check
ansible-playbook lv.yml
```

---

## 5️⃣ 모듈
| 모듈 | 용도 |
|------|------|
| `lvol` (community.general) | 논리 볼륨 생성 (vg/lv/size) |
| `filesystem` (community.general) | 파일시스템 포맷 (fstype/dev) |
| `debug` (ansible.builtin) | 메시지 출력 (rescue) |

> ⚠️ `lvol`·`filesystem` 은 컬렉션 모듈 → `ansible-doc` 볼 땐 FQCN: `ansible-doc community.general.lvol`

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
ansible-doc community.general.lvol         # vg, lv, size 옵션 (짧은 이름은 안 나올 수 있음)
ansible-doc community.general.filesystem   # fstype, dev
ansible all -m setup -a 'filter=ansible_lvm'   # vg 존재 여부/구조 확인 (when 조건용)
```
> block/rescue 문법 자체는 ansible-doc보다 **기존 예제/교재 Task Control** 참고.

---

## 7️⃣ 테스트 후 확인 방법
```bash
ansible-playbook lv.yml
ansible all -m command -a "lvs"        # data lv 확인
ansible all -m command -a "lvdisplay"
ansible all -m command -a "lsblk"
# 마운트 안 됐는지도 확인 (df 에 안 보여야 정상)
```

### ✅ 합격 체크리스트
- [ ] block: lvol(1500m) + filesystem(ext4)
- [ ] rescue: debug(실패메시지) + lvol(800m, `when defined` + `ignore_errors`) + debug(`when undefined`)
- [ ] vg 없을 때 메시지 문구가 문제 원문(`Volume group not found`)과 일치
- [ ] 마운트 task 없음

---

## 💡 로직 이해 (왜 이렇게 되나)
| 상황 | block | rescue 동작 |
|------|------|------|
| vg 있고 1500m OK | ✅ 성공 | rescue 안 탐 |
| vg 있는데 1500m 너무 큼 | ❌ 실패 | "Could not create..." → **800m 생성**(`is defined`) |
| vg `research` 자체가 없음 | ❌ 실패 | "Could not create..." → 800m는 skip → **"Volume group not found"**(`is undefined`) |

> 800m task에 `ignore_errors: yes` 를 둔 이유: 혹시 800m도 실패해도 rescue 전체가 죽지 않고 마지막 debug까지 흐르게 하려는 안전장치.
