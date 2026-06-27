# 01. EX156 3일 합격 플랜 (OpenShift Virtualization)

> 전략: **스토리지 50% · 네트워킹 30% · VM 관리 20%**. 스토리지에서 한 문제만 더 맞아도 합격선이 크게 흔들립니다.

---

## 0. 가장 헷갈리는 핵심 분기 — "URL이냐 gz냐"

시험에서 점수가 갈리는 핵심. **"이미지가 어디에 있느냐"로 방법이 갈립니다.**

| 문제에서 주는 것 | 의미 | 콘솔 | CLI |
| --- | --- | --- | --- |
| **원격 URL** (`https://.../disk.qcow2`) | 클러스터가 그 주소에서 **다운로드(import)** | Boot source: **"URL (creates PVC)"** | DataVolume `source.http.url` |
| **로컬 파일** (`.img.gz`, `.qcow2`, `.iso`) | 내 손의 파일을 **업로드(upload)** | Boot source: **"Upload"** | `virtctl image-upload dv ...` |

### 핵심 암기 문장

- **URL = Import = CDI importer 파드가 받아옴** → DataVolume `http` 소스
- **gz 파일 = Upload = 내가 밀어넣음** → `virtctl image-upload`

### URL → VM 부팅 (DataVolume YAML)

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: imported-rootdisk
spec:
  source:
    http:
      url: "https://content.example.com/rhel9.qcow2"   # 문제에서 준 URL
  storage:
    resources:
      requests:
        storage: 30Gi
```

→ 콘솔에서는 VM 생성 마법사 → **Boot source = "URL (creates PVC)"** 에 URL만 붙여넣으면 동일.

### gz 파일 → VM 만들기

```bash
# 1) 로컬 gz를 새 DataVolume으로 업로드
virtctl image-upload dv fedora-rootdisk \
  --size=30Gi \
  --image-path=fedora-vm-disk.img.gz \
  --storage-class=ocs-external-storagecluster-ceph-rbd-virtualization \
  --insecure          # 라우터 인증서 신뢰 안 될 때 자주 필요

# 2) 생성 확인
oc get dv
oc get pvc

# 3) 이 DataVolume(=PVC)을 부팅 디스크로 VM 생성 (콘솔 또는 YAML)
```

> 팁: 업로드가 `Waiting for PVC upload pod...` 에서 멈추면 `--insecure` 추가, storage-class 정확한지 `oc get sc` 로 확인.

---

## 1. 스토리지 집중 (33% → 목표 80%+)

### 1-1. 객체 관계 (암기)

```
StorageClass ──► PVC ◄── DataVolume(DV) ──(CDI)── import/upload/clone
                  │
                  └─► VM disk
```

- **DataVolume(DV)** = PVC를 만들고 그 안을 채워주는(import/upload/clone) 상위 객체. CDI가 처리.
- **volumeMode**: `Filesystem` vs `Block`
- **accessModes**: `RWO` / `RWX` — **라이브 마이그레이션·일부 작업은 RWX 필요**
- **VolumeSnapshot / VirtualMachineSnapshot / VirtualMachineRestore** = 스냅샷·복원 (CSI 드라이버의 스냅샷 지원 필요)

### 1-2. 골든 이미지 만들기 (sysprep)

> **VM은 반드시 중지(stop) 상태**여야 PVC를 guestfs로 열 수 있습니다.

```bash
# 1) 골든 볼륨 이름 확인
oc get pvc

# 2) libguestfs 컨테이너로 해당 PVC를 마운트해 셸 진입
virtctl guestfs rhel-golden-volume

# 3) 컨테이너 안에서 이미지 일반화(머신ID·SSH키·로그 제거)
virt-sysprep -a /dev/vda

# 4) 셸 빠져나오면 → 깨끗한 골든 이미지
exit
```

- `virt-sysprep` = "이 디스크를 템플릿용으로 깨끗하게 청소" (복제 VM마다 고유 ID 생성되게).
- 디스크 경로 확인: guestfs 안에서 `virt-filesystems -a /dev/vda` 또는 `lsblk`.

### 1-3. 스냅샷 / 클론 / 복원

| 작업 | 위치 | 핵심 |
| --- | --- | --- |
| **클론(Clone)** | 콘솔 | VM → Actions → Clone. 새 VM 복사본 생성 |
| **스냅샷 생성** | 콘솔 | VM → Snapshots → Take snapshot. **오프라인이 안전**(guest agent 있으면 온라인 가능) |
| **복원(Restore)** | 콘솔 + CLI | **VM 중지 후** Restore. CLI는 `VirtualMachineRestore` CR |

복원 검증용 빈 파일 패턴 — **문제 지시 순서를 정확히**:

```bash
# 시나리오: 스냅샷 → 변경 → 복원하면 변경이 사라져야 함
# VM 안에서 (업데이트 실패 흔적 파일을 미리 만들어 두라고 할 때)
touch update_failed.txt
```

> 함정: "스냅샷 찍기 **전에** 만들 파일"인지 "복원 **후에** 있어야/없어야 할 파일"인지 지문 두 번 읽기. 채점은 파일 존재 여부로 판정.

### 1-4. 내보내기(Export) / 다운로드

```bash
# VM 볼륨을 gz로 내려받기 (export 생성 + 다운로드 한 번에)
virtctl vmexport download dev-server \
  --vm=dev-server \
  --volume=dev-server-volume \
  --output=dev-server-disk.img.gz

# 이미 만들어진 export 이름으로 다운로드만
virtctl vmexport download <EXPORT_NAME> --output=disk.img.gz
```

- 첫 인자 `dev-server` = **새로 만들 VirtualMachineExport 이름** (VM 이름과 같아도 됨, 헷갈리지 말 것)
- 소스 선택 플래그: `--vm=` / `--pvc=` / `--snapshot=` 중 하나
- 기본 포맷 gzip → 보통 `--output` 만 주면 됨

### 1-5. 아카이브 디스크 → 새 볼륨 → 새 VM (복원/이관)

```bash
# 1) 받아둔 gz를 새 DataVolume으로 업로드
virtctl image-upload dv dev-server-restored-disk \
  --size=10Gi \
  --image-path=dev-server-disk.img.gz \
  --insecure

# 2) 새 DataVolume(PVC)에서 VM 생성
virtctl create vm --name=dev-server-restored \
  --volume-pvc=src:dev-server-restored-disk | oc apply -f -
```

> **전체 흐름**: `vmexport download`(gz로 빼냄) → `image-upload`(gz를 새 DV로 넣음) → VM 생성. 시험에서 자주 묶여 나옴.

### 1-6. 디스크 핫플러그 + 블랭크 디스크 + ★persistent(영속화)★

```bash
# 핫플러그 (실행 중 VM에 디스크 붙였다 뗐다)
virtctl addvolume <vm> --volume-name=<dv-or-pvc>
virtctl removevolume <vm> --volume-name=<dv-or-pvc>
```

**블랭크(빈) 디스크 만들기**

- 콘솔: VM → **Disks 탭 → Add disk** → **Source: Blank** → Name·Size·Type·Interface·**Storage Class** 지정
  - 옵션: **Preallocation(사전 할당)** = 최대 쓰기 성능 필요 시 체크
- YAML:

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: blank-disk
spec:
  source:
    blank: {}                 # ★ 빈 디스크
  storage:
    storageClassName: <sc>
    resources:
      requests:
        storage: 10Gi
```

**★ persistent = 핫플러그 디스크 영속화 ★**

- 실행 중 VM에 핫플러그한 디스크는 **기본적으로 VMI(실행 인스턴스)에만 임시로** 붙음 → **stop/start 하면 사라짐.**
- VM 사양에 **영구 마운트**로 박으려면:
  - **CLI**: `--persist` 플래그

```bash
virtctl addvolume <vm> --volume-name=<dv-or-pvc> --persist
# 이후 stop/restart 해야 영구 반영
```

  - **콘솔**: 디스크 추가 후 → 디스크 옆 **⋮ 메뉴 → "Make persistent"** → **VM 재부팅**

```bash
# 검증: VM stop/start 후에도 디스크가 남아있는지
oc get vm <vm> -o jsonpath='{.spec.template.spec.domain.devices.disks[*].name}{"\n"}'
# VM 안에서 블록 장치 보이는지
lsblk
```

> 함정: `--persist` 없이 붙이면 "지금은 보이는데 재시작하니 없어졌다". 문제에 "영구적으로/재부팅 후에도" 있으면 **무조건 persist**.

---

## 2. 네트워킹 보강 (50% → 목표 80%)

### 2-1. 바인딩/네트워크 종류

- **기본 파드 네트워크** = `masquerade` 바인딩 (NAT). 별도 설정 없이 붙음.
- **2차 네트워크(Secondary)** = **Multus + NetworkAttachmentDefinition(NAD)**
  - **Linux bridge** (bridge 바인딩)
  - **OVN-Kubernetes** (localnet / layer2)
  - **SR-IOV**

### 2-2. 자주 나오는 작업 흐름

```bash
# 외부 SSH 접근: 서비스로 노출
virtctl expose vm <vm> --name=<svc> --type=LoadBalancer --port=22 --target-port=22
# 또는 NodePort
virtctl expose vm <vm> --name=<svc> --type=NodePort --port=22 --target-port=22

# 웹 80 → 80 길 만들기 (ClusterIP 예)
virtctl expose vm hello-web --name=hello-web \
  --type=ClusterIP --port=80 --target-port=80

# 간단 접속
virtctl ssh <user>@<vm>
virtctl console <vm>
```

- **외부 접근 객체**: Service(ClusterIP/NodePort/LoadBalancer), Route(HTTP/S), `virtctl expose`
- **멀티홈 VM** = 파드 네트워크 + 2차 NAD 동시 연결 → VM YAML의 `networks`/`interfaces` 에 NAD 추가
- 호스트 브리지 구성은 **NMState**(NodeNetworkConfigurationPolicy)로

### 2-3. VM에 2차 네트워크 붙이는 YAML (개념)

```yaml
spec:
  template:
    spec:
      domain:
        devices:
          interfaces:
          - name: default
            masquerade: {}
          - name: bridge-net          # 2차 네트워크
            bridge: {}
      networks:
      - name: default
        pod: {}
      - name: bridge-net
        multus:
          networkName: my-bridge-nad  # NAD 이름
```

> 체크: `interface name` 과 `network name` 이 **짝이 맞아야** 함. masquerade는 파드 네트워크에만.

---

## 3. VM 생성·관리 유지 (75% → 90%)

```bash
virtctl start <vm> / stop <vm> / restart <vm>
virtctl pause <vm> / unpause <vm>
virtctl console <vm>        # 시리얼 콘솔 (Ctrl+] 로 나옴)
virtctl vnc <vm>
virtctl ssh user@<vm>
oc get vm,vmi,dv,pvc
```

- **생성 방식**: Template / **instance type + preference** / 커스텀 이미지(URL·Upload·Clone)
- **cloud-init**: 사용자/비밀번호/SSH 키 주입 (`userData`)
- **guest agent**: 설치돼 있어야 IP·게스트 정보·정상 종료가 콘솔에 보임
- **RunStrategy**: `Always` / `RerunOnFailure` / `Manual` / `Halted`

---

## 3.5 자주 막히는 3가지 — "만들기 + 검증"까지

> 시험은 "만들었나"가 아니라 **"동작하나"**로 채점. 검증 명령까지 손에 익히기.

### A. cloud-init — 계정 · SSH 키 · 초기 스크립트

```yaml
spec:
  template:
    spec:
      volumes:
      - name: rootdisk
        dataVolume:
          name: my-rootdisk
      - name: cloudinitdisk
        cloudInitNoCloud:
          userData: |-
            #cloud-config
            user: cloud-user                 # 사용자 계정
            password: redhat123              # 비밀번호
            chpasswd:
              expire: false                  # 첫 로그인 시 변경 강제 안 함
            ssh_authorized_keys:             # SSH 공개키 (인라인)
              - ssh-rsa AAAAB3Nza... user@host
            runcmd:                          # 초기 스크립트(부팅 후 1회)
              - touch /etc/created-by-cloud-init
              - systemctl enable --now httpd
```

**SSH 키를 Secret으로 주입 (4.18 권장, `accessCredentials`)** — "키를 Secret으로"라고 하면 이것:

```bash
# 1) 공개키로 Secret 생성
oc create secret generic authorized-keys --from-file=key1=~/.ssh/id_rsa.pub
```

```yaml
# 2) VM에 연결
spec:
  template:
    spec:
      accessCredentials:
      - sshPublicKey:
          source:
            secret:
              secretName: authorized-keys
          propagationMethod:
            noCloud: {}        # cloud-init 주입 (또는 qemuGuestAgent: {} = 런타임 주입)
```

**검증 (이게 점수)**

```bash
virtctl console <vm>                        # 또는
virtctl ssh -i ~/.ssh/id_rsa cloud-user@<vm>
# VM 안에서:
id cloud-user                              # 계정 생성 확인
cat ~/.ssh/authorized_keys                 # SSH 키 주입 확인
ls -l /etc/created-by-cloud-init           # runcmd 실행 결과
sudo cloud-init status                     # status: done 이어야 정상
sudo cat /var/log/cloud-init-output.log    # 스크립트 로그 (에러 추적)
```

> 함정: `userData` 는 **첫 부팅에만** 적용. 바꿔 적용하려면 VM **재생성/디스크 초기화** 필요. `#cloud-config` 헤더 빠지면 통째로 무시됨.

### B. virtctl expose — 포트 안 줄 때 + LoadBalancer 검증

```bash
virtctl expose vm <vm> \
  --name=<svc-name> \         # 만들 Service 이름
  --type=LoadBalancer \       # LoadBalancer / NodePort / ClusterIP(기본)
  --port=80 \                 # Service가 받는 포트
  --target-port=80            # VM 안 실제 포트 (생략 시 --port 값과 동일)
```

**"포트 안 주고 URL/서비스만 줬을 때"**

- `--target-port` 생략 시 **`--port` 와 같은 값** 자동 설정.
- **앱 기본 포트 추론**: 웹 80, HTTPS 443, SSH 22, RDP 3389. URL 스킴으로 판단(`http://` = 80).

```bash
# 예: 웹서버 VM을 LoadBalancer로 (target-port 생략)
virtctl expose vm webvm --name=webvm-lb --type=LoadBalancer --port=80
```

**LoadBalancer 외부 접근 검증**

```bash
# 1) EXTERNAL-IP가 <pending>이 아니라 IP가 떠야 함
oc get svc webvm-lb
# 2) 외부 IP 추출
oc get svc webvm-lb -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
# 3) 실제 접속 검증
curl http://<EXTERNAL-IP>:80          # 웹
ssh cloud-user@<EXTERNAL-IP>          # SSH
```

> 함정 3가지: ① `EXTERNAL-IP <pending>` → LB(MetalLB) 없음, NodePort로 `<노드IP>:<3xxxx>` 접속. ② expose 대상 VM은 **masquerade 파드 네트워크 + 실행 중**이어야(SR-IOV/bridge 불가). ③ `--target-port` 틀리면 서비스는 생기는데 연결 안 됨 → `curl`/`ssh` 로 꼭 확인.

### C. 스토리지 클래스 지정 + 검증

```bash
# 0) 사용 가능한 SC 확인 (이름 정확히 복붙)
oc get sc
#   ocs-external-storagecluster-ceph-rbd-virtualization ...
```

**방법 1 — image-upload 시 SC 지정 (gz)**

```bash
virtctl image-upload dv my-dv \
  --size=30Gi \
  --image-path=disk.img.gz \
  --storage-class=ocs-external-storagecluster-ceph-rbd-virtualization \
  --insecure
```

**방법 2 — DataVolume YAML에 SC 지정 (URL import)**

```yaml
spec:
  source:
    http:
      url: "https://.../rhel9.qcow2"
  storage:
    storageClassName: ocs-external-storagecluster-ceph-rbd-virtualization   # ★
    resources:
      requests:
        storage: 30Gi
```

**검증**

```bash
oc get pvc                                              # STATUS Bound + STORAGECLASS 확인
oc get pvc my-dv -o jsonpath='{.spec.storageClassName}{"\n"}'
oc get dv my-dv                                         # Succeeded 떠야 함
```

> 함정: SC 이름 **오타 = PVC 영원히 Pending**. SC **생략 = 클러스터 default SC** (특정 SC 요구 시 오답). 라이브 마이그레이션/RWX 필요하면 그걸 지원하는 SC(보통 ceph-rbd-virtualization)인지 확인.

---

## 4. 3일 일정표

### Day 1 — 스토리지 올인 (가장 약한 33%)

- 오전: 0·1번 정독 + URL/gz 분기 손으로 적으며 암기
- 실습: ① URL import→부팅 ② gz image-upload→부팅 ③ guestfs + virt-sysprep ④ 스냅샷→변경→복원(파일 검증) ⑤ vmexport download→image-upload로 새 VM ⑥ addvolume/removevolume 핫플러그
- 저녁: 위 6개를 **아무것도 안 보고** 재현

### Day 2 — 네트워킹 + 만들기/검증 3종

- 오전: 2번 + 3.5번 (NAD/Multus, cloud-init, expose, storage class)
- 실습: ① cloud-init 계정·SSH키·runcmd → 로그인 검증 ② expose LoadBalancer(target-port 생략) → curl/ssh ③ SC 지정 DV → pvc Bound 검증 ④ Linux bridge NAD 멀티홈 VM → ping
- 저녁: Day 1 스토리지 6종 **1회 더 반복**

### Day 3 — 모의 + 약점 굳히기

- 오전: 챕터 퀴즈 + 개방 실습 전부 다시
- 오후: **타이머 켜고 풀 모의시험** (콘솔/CLI 섞어서)
- 저녁: 틀린 것 + "URL vs gz" 마지막 점검, 일찍 자기

---

## 5. 시험장 전술

- **지문 두 번 읽기**: VM 이름·볼륨·네임스페이스·storage-class 그대로 복붙. 오타가 0점 1위.
- **검증까지**: `oc get vm,vmi,dv,pvc` 로 Running/Bound 확인. 부팅 끝까지 대기.
- **콘솔 vs CLI 자유**: 명시 없으면 빠른 쪽. 클론·스냅샷은 콘솔이 빠름.
- **시간 배분**: 스토리지 → 네트워킹 → VM 관리. 막히면 다음으로.
- **안전장치**: image-upload 안 되면 `--insecure`, SC는 `oc get sc` 로 정확히.
- **삭제 신중히**: 이름 확인 후 실행.

---

## 6. 막판 1분 치트시트

```bash
# 이미지 들여오기
URL  → DataVolume http source  (콘솔: "URL (creates PVC)")
gz   → virtctl image-upload dv <name> --size=NGi --image-path=FILE --storage-class=SC --insecure

# 골든 이미지
oc get pvc
virtctl guestfs <golden-vol>
virt-sysprep -a /dev/vda

# 내보내기/복원
virtctl vmexport download <export> --vm=<vm> --volume=<vol> --output=disk.img.gz
virtctl image-upload dv <restored> --size=NGi --image-path=disk.img.gz --insecure
virtctl create vm --name=<new> --volume-pvc=src:<restored> | oc apply -f -

# 핫플러그 (+영속화)
virtctl addvolume <vm> --volume-name=<dv> --persist   # --persist=재부팅 후 유지, 빼면 임시
virtctl removevolume <vm> --volume-name=<dv>
# 블랭크 디스크: 콘솔 Add disk→Source:Blank, 또는 DV source: blank: {}

# 네트워크 외부 노출 + 검증
virtctl expose vm <vm> --name=<svc> --type=LoadBalancer --port=80   # target-port 생략=port와 동일
oc get svc <svc>                                                    # EXTERNAL-IP 확인
oc get svc <svc> -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
curl http://<EXTERNAL-IP>:80   # 또는 ssh <user>@<EXTERNAL-IP>

# cloud-init 검증 (로그인 후 VM 안에서)
id <user>; cat ~/.ssh/authorized_keys; sudo cloud-init status

# storage class 지정 + 검증
oc get sc                                                # 이름 확인(복붙)
oc get pvc <dv> -o jsonpath='{.spec.storageClassName}'   # 지정 SC / STATUS Bound 확인

# VM 제어
virtctl start|stop|restart|console|ssh|vnc <vm>
oc get vm,vmi,dv,pvc,snapshot,nad,svc
```

> **핵심 한 줄**: 스토리지에서 "URL=import / gz=upload" 분기만 몸에 배면 33% → 70%대는 거의 확정. 3일이면 충분합니다. 화이팅!
