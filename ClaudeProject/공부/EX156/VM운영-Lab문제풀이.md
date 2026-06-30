# VM 운영 Lab — 문제 풀이 (시험형 연습)

> "Operating Virtual Machines" 첫 Lab. **VM 생성·cloud-init·SSH·모니터링·리소스 증설**.
> 포맷: 문제별 **🖥️ CLI | 🌐 콘솔** + **📝 외울 것**. 🟢=콘솔 / 🔴=CLI 필수.
> 이 Lab은 **대부분 콘솔 주도**(생성·메트릭·인스턴스타입), 검증만 CLI(`virtctl ssh`).

> **시나리오**: developer로 accessing-review 프로젝트에 `rhel10-mariadb` 부팅볼륨으로 `mariadb-perf` VM 생성.
> cloud-init로 **부팅 시 perftest 서비스 시작** + **SSH 공개키(lab_rsa.pub) 주입**. 이후 리소스 경합 확인 → 증설.

---

## 문제 1. mariadb-perf VM 생성 (instance type + cloud-init) 🟢
> accessing-review에 VM 생성: rhel10-mariadb 부팅볼륨 + **u1.small**, 디스크 **10GiB**, **SSH 공개키**(lab_rsa.pub), cloud-init로 **`systemctl enable --now perftest`**.

**🌐 콘솔 (지정됨)**
```
웹 콘솔 developer/developer 로그인
Virtualization → VirtualMachines → Create → From InstanceType
 ① 부팅 볼륨: rhel10-mariadb 선택
 ② Instance type: u1.small
 ③ Disk size: 10GiB
 ④ Public SSH key → "Not configured" → Add new
      → 로컬 pub 파일 /home/student/.ssh/lab_rsa.pub 등록 (이름: lab-key)
 ⑤ Customize VirtualMachine → Scripts(또는 Initial run) → Cloud-init → Edit
      → #cloud-config 아래에 추가:
        runcmd:
          - systemctl enable --now perftest
 ⑥ Create VirtualMachine
```
**📝 외울 것**: 🟢 콘솔. **From InstanceType**(부팅볼륨+타입). **SSH키 = Public SSH key 필드**(별도, cloud-init 아님). **서비스 시작 = cloud-init `runcmd`**. `#cloud-config` 헤더 필수.

> ❓ "runcmd 주어지나?" → **아니요, 직접 입력**. 두 문법 다 OK:
> `runcmd:` 줄 아래 `- systemctl enable --now perftest` (블록), 또는 `- [ systemctl, enable, --now, perftest ]` (인라인).

---

## 문제 2. SSH 접속 + perftest 서비스 확인 🔴(접속은 CLI)
> 암호 없이 `virtctl ssh`로 rhel 사용자 접속 → `sudo systemctl status perftest`로 실행 확인.

**🖥️ CLI**
```bash
oc login -u developer -p developer https://api.ocp4.example.com:6443
oc project accessing-review
virtctl ssh rhel@mariadb-perf          # 암호 없이(주입한 SSH키로)
  sudo systemctl status perftest       # active(running) 확인
```
**📝 외울 것**: `virtctl ssh <user>@<vm>` = **주입한 SSH키로 암호 없이** 접속. 키가 제대로 들어갔으면 비번 안 물음(=문제1 검증). `virtctl console`은 암호 필요, `ssh`는 키.

---

## 문제 3. 리소스 제약 오류(OOM) 확인 🟢
> VM 콘솔에서 리소스 제약 오류 메시지 확인.

**🌐 콘솔**
```
VM mariadb-perf → Console 탭 (Open web console)
   → OOM(Out Of Memory) / "Out of memory: Killed process" 등 메시지 확인
```
**📝 외울 것**: 🟢 콘솔. **메모리 부족 = OOM 메시지**가 VM 콘솔/로그에 뜸. "리소스 경합 = OOM" 연결.

---

## 문제 4. 리소스 사용량 검사 🟢
> 지표로 리소스 경합 발생 여부 확인.

**🌐 콘솔**
```
VM mariadb-perf → Metrics 탭
   → CPU / Memory 사용률(Utilization) 그래프 확인 (한계 근접/초과?)
```
**📝 외울 것**: 🟢 콘솔 **Metrics 탭** = CPU/메모리 사용률 그래프. 경합 = 사용률이 한계에 붙음.

---

## 문제 5. VM 리소스 증설 🟢
> 리소스 늘리기 → 다시 확인.

**🌐 콘솔**
```
VM mariadb-perf → Configuration → Instance type
   → u1.small → u1.medium 으로 변경 (저장 시 재시작 필요할 수 있음)
   → Utilization(또는 Metrics)에서 CPU/Memory 늘어난 것 확인
```
**🖥️ CLI 검증**
```bash
virtctl ssh rhel@mariadb-perf
  sudo journalctl -u perftest -p notice --since "1m ago"   # perftest 로그 확인
```
**📝 외울 것**: 🟢 **리소스 증설 = Instance type 변경**(small→medium). 적용에 **재시작** 필요. 검증: Metrics + `journalctl -u perftest -p notice --since "1m ago"`.

> ❓ 맨 위 `journalctl` 명령 = 시나리오가 준 **검증용 명령**. `-u perftest`=해당 서비스, `-p notice`=notice 이상 우선순위, `--since "1m ago"`=최근 1분 로그.

---

## 🎯 Lab 전체 요점 (콘솔 vs CLI)
| 문제 | 작업 | 콘솔 | CLI |
| --- | --- | --- | --- |
| 1 | VM 생성(타입+cloud-init+SSH키) | ✅ **지정** | |
| 2 | SSH 접속 + 서비스 확인 | | 🔴 `virtctl ssh` |
| 3 | OOM 메시지 확인 | ✅ Console 탭 | |
| 4 | 리소스 사용량 | ✅ Metrics | |
| 5 | 리소스 증설 | ✅ Instance type 변경 | 검증 ssh |

## 📝 이 Lab 핵심 암기
- **VM 생성** = From InstanceType (부팅볼륨 + 인스턴스타입 + 디스크크기)
- **SSH 공개키** = 콘솔 "Public SSH key" 필드 → Add new (cloud-init 스크립트와 별개)
- **부팅 시 서비스 시작** = cloud-init **`runcmd: - systemctl enable --now <svc>`** (`#cloud-config` 헤더 필수, 첫 부팅만 적용)
- **접속** = `virtctl ssh rhel@<vm>` (키로 암호 없이) / `virtctl console`=암호 필요
- **모니터링** = Console 탭(OOM) / **Metrics 탭**(CPU·메모리 사용률)
- **리소스 증설** = Configuration → **Instance type 변경**(재시작 필요)
- **서비스 로그** = `sudo journalctl -u <svc> -p notice --since "1m ago"`
