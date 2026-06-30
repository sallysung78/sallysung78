# 5장 스토리지 Lab — 문제 풀이 (시험형 연습)

> 각 문제마다 **CLI 명령 | 콘솔 작업**을 나누고, 맨 아래 **📝 외울 것** 정리.
> 🔴=콘솔 불가(CLI 필수) / 🟢=콘솔 가능. **외울 핵심 = 1번(봉인) + 5번(export)뿐**, 나머지는 콘솔 OK.

---

## 문제 1. rhel-golden → 봉인된 골든 이미지 🔴
> rhel-golden VM을 봉인해 복제용 골든 이미지로 만들기. (시스템별 정보 제거, **`virtctl guestfs` 필수**)

**① VM 중지** (콘솔 또는 CLI)
```bash
virtctl stop rhel-golden            # 또는 콘솔: VM → Actions → Stop
oc get vm rhel-golden               # STATUS: Stopped 확인
```
**② 봉인 (CLI 필수 — 콘솔 불가)**
```bash
oc login -u admin -p redhatocp https://api.ocp4.example.com:6443
oc project <프로젝트>
oc get pvc                          # 볼륨 이름 확인 → rhel-golden-volume
virtctl guestfs rhel-golden-volume  # PVC 디스크 열기
  virt-sysprep -a /dev/vda          # 고유정보 제거
  exit
```
**📝 외울 것**: 🔴 **콘솔 불가**. **VM 중지 → `virtctl guestfs <볼륨>` → `virt-sysprep -a /dev/vda` → exit**. 봉인 후 **VM 시작 금지!**

---

## 문제 2. rhel-golden 복제 → file-server VM 생성 + 시작 🟢
> 봉인된 rhel-golden을 **웹 콘솔로 복제**해 file-server 생성, 완료되면 시작.

**🌐 콘솔 (지정됨)**
```
Virtualization → VirtualMachines → rhel-golden 선택
   → Actions → Clone
   → 이름: file-server
   → "Start this VirtualMachine after creation" 체크 (또는 생성 후 수동 start)
   → Clone
```
**🖥️ CLI 대안**
```bash
virtctl create clone --source-name rhel-golden --target-name file-server | oc apply -f -
oc get virtualmachineclone          # PHASE: Succeeded
virtctl start file-server           # ★CLI 복제는 자동시작 없음 → 수동 start
```
**📝 외울 것**: 🟢 **복제=콘솔 Actions→Clone**. 콘솔은 "생성 후 시작" 체크박스 있음. **CLI 복제는 자동시작 X → `virtctl start`**.

---

## 문제 3. webapp 스냅샷 pre-update-backup 생성 🟢
> webapp 업데이트 **전에** pre-update-backup 스냅샷 생성. 완료까지 대기. (VM 안 죽여도 됨)

**🌐 콘솔**
```
VM webapp → Snapshots 탭 → Take snapshot
   → 이름: pre-update-backup → Save  (READYTOUSE: true 까지 대기)
```
**🖥️ CLI 대안**
```bash
oc apply -f - <<EOF
apiVersion: snapshot.kubevirt.io/v1beta1
kind: VirtualMachineSnapshot
metadata:
  name: pre-update-backup
spec:
  source: { apiGroup: kubevirt.io, kind: VirtualMachine, name: webapp }
EOF
oc get virtualmachinesnapshot       # READYTOUSE: true 확인
```
**📝 외울 것**: 🟢 **스냅샷 생성 = VM 중지 불필요**(실행 중 OK). 게스트에이전트가 FS freeze로 일관성.

---

## 문제 4. webapp 변경 시뮬레이션 → 스냅샷 복원 → 시작 🟢
> webapp에 `~/update_failed.txt` 생성(실패 시뮬레이션) → pre-update-backup 복원 → 시작.

**① VM 안에서 파일 생성** (CLI 접속 또는 콘솔 Console 탭)
```bash
virtctl console webapp              # 로그인 후
  touch ~/update_failed.txt         # 변경 흔적 만들기
  exit (Ctrl+])
```
**② VM 중지** (복원은 중지 필수!)
```bash
virtctl stop webapp
```
**③ 복원 (콘솔)**
```
VM webapp → Snapshots → pre-update-backup ⋮ → Restore VirtualMachine from snapshot → Restore
```
**④ 시작 + 검증**
```bash
virtctl start webapp
virtctl console webapp → ls ~/update_failed.txt   # 사라졌으면 복원 성공 ✅
```
**📝 외울 것**: 🔴 **복원 = VM 중지 필수!** (생성은 실행 중, 복원만 중지) / `touch`로 변경 → 복원 후 **파일 사라짐**으로 검증.

---

## 문제 5. dev-server export → 아카이빙 후 VM 삭제 🔴
> dev-server-volume PVC를 `/home/student/dev-server-disk.img.gz`로 내보내기 → 완료 후 VM 삭제.

**① export 다운로드 (CLI 필수 — 콘솔 불가)**
```bash
cd /home/student
virtctl vmexport download dev-server --vm=dev-server --volume=dev-server-volume --output=dev-server-disk.img.gz
ls -lh dev-server-disk.img.gz       # 파일 확인 (몇 분 걸림)
```
**② VM 삭제**
```bash
oc delete vm dev-server             # 또는 콘솔: VM → Actions → Delete
```
**📝 외울 것**: 🔴 **콘솔 불가**. `virtctl vmexport download <이름> --vm --volume --output=<파일.img.gz>`. 첫 인자=만들 export 이름.

---

## 문제 6. 아카이브 복원 → 업로드 + VM 생성 (legacy-apps) 🟢
> dev-server-disk.img.gz를 **legacy-apps** 프로젝트의 10Gi DV(dev-server-restored-disk)로 업로드 → 그 DV를 부팅소스로 dev-server-restored VM 생성.

**① gz 업로드 (한 줄로! `\` 뒤 공백 주의)**
```bash
oc project legacy-apps              # 또는 명령에 -n legacy-apps
virtctl image-upload dv dev-server-restored-disk --size=10Gi --image-path=dev-server-disk.img.gz -n legacy-apps
# 실패 시: oc delete dv dev-server-restored-disk -n legacy-apps → 재시도
oc get dv,pvc -n legacy-apps        # Succeeded / Bound 확인
```
**② DV에서 VM 생성 (한 줄!)**
```bash
virtctl create vm --name=dev-server-restored --volume-pvc=src:dev-server-restored-disk -n legacy-apps | oc apply -f -
virtctl start dev-server-restored -n legacy-apps
```
**🌐 콘솔 대안**: 업로드=Bootable volumes→Add volume→With form→Upload / VM생성=Create→From InstanceType(볼륨 선택) 또는 With YAML.
**📝 외울 것**: 🟢 둘 다 콘솔 가능. **한 줄로** 치기(`\ ` 깨짐 주의) / **`-n legacy-apps` 네임스페이스** / 실패 시 `oc delete dv` 후 재시도 / SC는 기본이면 생략.

---

## 문제 7. webapp 실행 중 빈 5GiB 디스크 핫플러그 🟢
> 실행 중인 webapp에 **빈 5GiB 디스크 핫플러그**. (실행 중 = SCSI 인터페이스!)

**🌐 콘솔 (가장 쉬움)**
```
VM webapp → Configuration → Storage → Add disk
   → Source: Blank (빈 디스크)
   → Size: 5 GiB
   → Interface: SCSI   ★실행 중 핫플러그는 SCSI만!
   → (필요시) Storage class 지정 → Save
```
**🖥️ CLI 대안** (빈 DV 만들고 핫플러그)
```bash
# 빈 5Gi DataVolume 생성 후
virtctl addvolume webapp --volume-name=<빈-dv>          # 실행 중 핫플러그
# 재부팅 후에도 유지하려면: --persist
```
**📝 외울 것**: 🟢 콘솔 OK. 🚨 **실행 중 핫플러그 = SCSI 인터페이스만!** (VirtIO면 VM 중지 필요) / Source=Blank, 5Gi / 영구하려면 `--persist`.

---

## 🎯 Lab 전체 요점 (콘솔 vs CLI)
| 문제 | 작업 | 콘솔 | 외울 |
| --- | --- | --- | --- |
| 1 | 봉인(guestfs+sysprep) | ❌ | 🔴 |
| 2 | 복제(Clone) | ✅ | |
| 3 | 스냅샷 생성 | ✅ | |
| 4 | 스냅샷 복원 | ✅ | (복원=중지) |
| 5 | export download | ❌ | 🔴 |
| 6 | upload + VM 생성 | ✅ | |
| 7 | 핫플러그(blank) | ✅ | (SCSI) |

> **외울 CLI 2대 = ① 봉인(문제1) ② export(문제5).** 나머지는 콘솔로 충분.
> 자주 나오는 함정: **복원=VM 중지 / 핫플러그=SCSI / 한 줄로 치기 / 네임스페이스**.
