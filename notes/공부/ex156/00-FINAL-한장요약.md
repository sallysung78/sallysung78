# 🎯 EX156 FINAL 한 장 요약 (3 챕터 아젠다)

> **Ch3 VM 생성·관리·모니터링 / Ch4 네트워킹 / Ch5 스토리지** — 시험 직전 마지막 한 장.
> 상세는 `합격플랜-약점집중` `5장-스토리지-개념정리` `네트워킹-개념정리` `명령어-정리` 참고.
>
> 🎯 **= 기출** (본인 복기 + 시험 본 분 팁에서 실제 출제 확인된 것)

---

## 📕 Chapter 3 — VM 생성·관리·모니터링
| 섹션 | 핵심 |
| --- | --- |
| 3.1 VM 리소스 | **VM**=정의 / **VMI**=실행 인스턴스 / VM은 **virt-launcher 포드** 안에서 실행 |
| 3.3 생성 | **Template** / **InstanceType + preference** / 부팅소스 4종(URL·Upload·PVC clone·Registry) 🎯 |
| 3.5 웹콘솔 관리 | start/stop/restart, **Console 탭**(Serial/VNC)로 VM 안 접속 |
| 3.7 CLI 생성·접속 | `virtctl create vm` / `virtctl ssh·console·vnc` |
| 3.9 모니터링 | **Metrics 탭**(CPU/Mem), Console **OOM** 확인, 리소스 증설=**InstanceType 변경**(재부팅) |
- 🎯 **cloud-init**: 계정·비번 / **SSH키=Public SSH key 필드** / **부팅 서비스=`runcmd: - systemctl enable --now <svc>`**
- 검증: `virtctl ssh rhel@<vm>` → `sudo systemctl status <svc>` / `journalctl -u <svc> -p notice --since "1m ago"`
> 🔑 VM=정의·VMI=실행 / 🎯부팅소스 4종(URL/gz) / 🎯cloud-init(키+서비스) / 증설=InstanceType

## 📘 Chapter 4 — 네트워킹 (약점 50%)
| 섹션 | 핵심 |
| --- | --- |
| 4.1 SDN | **Pod network**(클러스터 공용,기본)/Service network, **CNO**=OVN |
| 4.3 Multus CNI | **NAD**로 2차 네트워크, 플러그인: **bridge**(멀티홈 필수)/host-device/ipvlan/macvlan/SR-IOV |
| 4.5 UDN | **프로젝트 전용 격리** 네트워크(서브넷 지정, VM 격리) 🎯 |
| 4.7 외부접근 | 서비스 4종: NodePort/LoadBalancer/Ingress/**Route** → **웹=Route / 비웹=LB·NodePort** 🎯 |
| 4.9 LoadBalancer | **고정 IP**, 온프렘=**MetalLB**(L2-ARP기본/L3-BGP), CR 3종 / SSH over LB 🎯 |
| 4.11 멀티홈 | **NMState(NNCP/NNCE)** → **NAD** → **2차 NIC**(재부팅 / 핫플러그는 `virtctl migrate`) 🎯 |
- 🎯 노출: `virtctl expose vm <vm> --name --type --port --target-port` → `oc expose service/<svc> --name=`(Route)
- 🎯 암호화 Route: `oc create route edge`(edge=라우터종료/passthrough=앱/reencrypt=전구간)
- ⚠️ 🎯 **selector 지정** = Service YAML(+`.spec.template.metadata.labels` 라벨 추가 + **VM 재시작**)
> 🔑 🎯웹=Route/비웹=LB / virtctl expose vm / 라벨전파+재시작 / 🎯UDN=격리 / 🎯2차NIC

## 📗 Chapter 5 — 스토리지 (약점 33%)
| 섹션 | 핵심 |
| --- | --- |
| 5.1 퍼시스턴트 | **SC**(메뉴)→**PVC**(주문)→**PV**(그릇), **DataVolume**=PVC+이미지 채움 / **source 4종**(http·upload·pvc·blank) 🎯 / **RWX=라이브 마이그레이션** / VM디스크=Block 권장 |
| 5.3 디스크 관리 | 인터페이스: **SCSI=핫플러그**(`sdX`)/VirtIO(`vdX`,중지) / **persistent**(Make persistent+재부팅) 🎯 / resize=**확장만**(`xfs_growfs`) |
| 5.5 export/import | 🎯 `virtctl vmexport download`(CLI필수) → `image-upload dv` → `create vm --volume-pvc` |
| 5.7 스냅샷 | 🎯 생성=실행중 OK(게스트에이전트 freeze) / **복원=VM 중지** / 복원=스냅샷 시점 구성 리셋 |
| 5.9 복제 | 🎯 **봉인(`virt-sysprep -a /dev/vda`, CLI필수)** → **Clone**(콘솔) |
> 🔑 🎯**URL=import / gz=upload** / 🎯봉인·export=CLI필수 / 복원·봉인=중지 / 🎯persistent

---

## 🎯 실제 출제 확인 (시험 본 분 팁 — 가장 자주 나옴)
| 기출 문제 | 어떻게 |
| --- | --- |
| 🎯 **Import** (URL로 VM 가져오기) | URL의 yaml `scp` → image url 치환 → `oc apply -f` |
| 🎯 **Route** (8080 서비스 + Route) | Service(selector=주어진 label) → `oc expose service --name` |
| 🎯 **LoadBalancer** (80 서비스) | `type: LoadBalancer`, selector=주어진 label → EXTERNAL-IP |
| 🎯 **Second NIC** | NAD 2차 NIC 등록 → **재부팅** |
| 🎯 **스토리지 persistent** | Add disk → **Make persistent** → **재부팅** |
| 🎯 **골든이미지 봉인 / 클론** | `virtctl guestfs`+`virt-sysprep` → Clone |
| 🎯 **export 다운로드 / 복원** | `vmexport download` → `image-upload` → `create vm` |
| 🎯 **스냅샷 → 변경 → 복원** | 스냅샷 → `touch` → 중지 → 복원 → 파일 사라짐 확인 |
| 🎯 **URL vs gz** (VM 부팅소스) | URL=import / gz=upload (가장 헷갈렸던 것) |

## 🔴 전 영역 공통 함정 (제일 자주 틀림)
- 🎯 **SNO = 바꾸면 재부팅** (NIC·persistent·리소스 변경 → `virtctl restart`)
- **VM 중지 필요**: 복원 / 봉인(virt-sysprep) / export / VirtIO 디스크
- **VM 중지 불필요**: 스냅샷 생성 / SCSI 핫플러그 / PVC 확장
- **핫플러그 = SCSI** / **selector 지정 = Service YAML+재시작** / **RWX = 라이브 마이그레이션**
- **콘솔 불가 = CLI 필수 2개**: ① 봉인 `virtctl guestfs`+`virt-sysprep -a /dev/vda` ② export `virtctl vmexport download`

## ⭐ 무조건 외울 명령 (10줄)
```bash
# 봉인(콘솔불가) 🎯
virtctl guestfs <volume> ; virt-sysprep -a /dev/vda     # VM 중지 → exit → 시작금지
# export(콘솔불가) 🎯
virtctl vmexport download <이름> --vm=<vm> --volume=<vol> --output=disk.img.gz
# 복원(업로드+생성) 🎯
virtctl image-upload dv <dv> --size=10Gi --image-path=x.img.gz [-n <ns>]
virtctl create vm --name=<vm> --volume-pvc=src:<dv> | oc apply -f -
# 핫플러그(영속) 🎯
virtctl addvolume <vm> --volume-name=<dv> --persist
# FS 확장(VM 안)
sudo xfs_growfs /dev/sda
# 노출 + Route 🎯
virtctl expose vm <vm> --name=<svc> --type=ClusterIP --port=80 --target-port=80
oc expose service/<svc> --name=<route>
oc create route edge --service <svc> --hostname <host>   # 암호화
# 마이그레이션(핫플러그/SSH-over-LB 적용)
virtctl migrate <vm>
```

> **한 줄 결론**: 스토리지 **URL=import/gz=upload** + 네트워킹 **웹=Route/비웹=LB** + **봉인·export는 CLI** + **SNO 재부팅** — 이 4개가 합격의 척추. 🔥 (🎯 = 기출)
