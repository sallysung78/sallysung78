# 문제 10. 논리 볼륨 생성 (LVM + block/rescue/always)

> PPT 기출 · 조건부 실패 처리(block/rescue/always)가 핵심인 LVM 문제.
> 핵심: `lvol` + `filesystem`, 실패 시 대체 크기, vg 없으면 메시지.

---

## 1️⃣ 개념

- **LVM**: vg(볼륨그룹) 안에 lv(논리볼륨) 생성 → 파일시스템 포맷.
- **block/rescue/always** (try/except/finally 같은 구조):
  - `block`: 정상 시도
  - `rescue`: block 실패 시 실행 (대체 작업)
  - `always`: 성공/실패 상관없이 항상 실행
- `lvol` 로 크기 초과 요청 시 실패 → rescue에서 작은 크기로 재생성.

---

## 2️⃣ 문제 (기출 원문 요약)

> `/home/user/ansible/lv.yml`, `hosts: all`.
- 볼륨그룹(vg) `research`, 논리볼륨(lv) `data`, 크기 **1500 MiB**, **ext4** 포맷 (block)
- 크기 생성 불가 시 → `Could not create logical volume of that size` 출력 후 **800 MiB** 로 생성 (rescue)
- `research` vg 없으면 → `Volume group not found` 출력 (always 또는 조건)
- ⚠️ 논리 볼륨은 **마운트하지 않는다** (건드리지 말 것)

---

## 3️⃣ 빈칸 (외울 것) — 손으로 채워보기 ⭐

### `/home/user/ansible/lv.yml`
```yaml
---
- name: create lv
  hosts: ______                      ← all
  become: true
  tasks:
    - ______:                        ← block
        - name: create data lv
          community.general.______:  ← lvol
            vg: research
            lv: data
            size: ______             ← 1500m
        - name: format ext4
          community.general.____________:  ← filesystem
            fstype: ______           ← ext4
            dev: /dev/research/data
      ______:                        ← rescue
        - name: msg size
          ansible.builtin.______:    ← debug
            msg: "Could not create logical volume of that size"
        - name: create smaller
          community.general.lvol:
            vg: research
            lv: data
            size: ______             ← 800m
      ______:                        ← always
        - name: msg no vg
          ansible.builtin.debug:
            msg: "Volume group not found"
          when: ansible_facts['lvm']['vgs']['research'] is ____________  ← undefined
```

### 🧠 외우기 포인트 (감점 함정)
- 구조 순서: **block → rescue → always**
- rescue 안에 **debug(메시지) + lvol(작은 크기)** 두 개
- 크기 표기: `1500m`, `800m` (MiB)
- ⚠️ **마운트 task 넣지 말 것** (문제에서 마운트 금지)
- vg 존재 여부: `ansible_lvm.vgs.research is defined / undefined`

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
| `community.general.lvol` | 논리 볼륨 생성 (vg/lv/size) |
| `community.general.filesystem` | 파일시스템 포맷 (fstype/dev) |
| `ansible.builtin.debug` | 메시지 출력 (rescue/always) |

---

## 6️⃣ 잊어버렸을 때 검색하는 법
```bash
ansible-doc lvol           # vg, lv, size 옵션
ansible-doc filesystem     # fstype, dev
ansible all -m setup -a 'filter=ansible_lvm'   # vg 존재 여부/구조 확인
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
- [ ] block/rescue/always 구조
- [ ] block: lvol(1500m) + filesystem(ext4)
- [ ] rescue: debug 메시지 + lvol(800m)
- [ ] always/조건: vg 없을 때 "Volume group not found"
- [ ] 마운트 task 없음
