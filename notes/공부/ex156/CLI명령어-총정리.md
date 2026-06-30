# virtctl 명령어 정리 (ex156)

> OpenShift Virtualization CLI(`virtctl`) 명령어 모음. ex156 노트 전체에서 추출·중복 제거.
> 표기: `<vm>` VM 이름 / `<dv>` DataVolume / `<svc>` Service 이름 / `<vol>` 볼륨 이름

---

## 1. VM 전원·상태 제어

```bash
virtctl start <vm>
virtctl stop <vm>
virtctl restart <vm>
virtctl pause <vm>
virtctl unpause <vm>
# 묶음 표기: virtctl start|stop|restart|pause|unpause <vm>
```

## 2. 접속 (콘솔 / SSH / VNC)

```bash
virtctl ssh <user>@<vm>                       # 주입한 SSH키로 암호 없이
virtctl ssh -i ~/.ssh/id_rsa cloud-user@<vm>  # 키 지정
virtctl console <vm>                          # 시리얼 콘솔 (Ctrl+] 로 빠져나옴, 암호 필요)
virtctl vnc <vm>                              # 그래픽(VNC) 콘솔
```

## 3. 노출 (Service 생성)

```bash
virtctl expose vm <vm> --name=<svc> --port=8080 --target-port=8080
virtctl expose vm <vm> --name=<svc> --type=ClusterIP    --port=80 --target-port=80
virtctl expose vm <vm> --name=<svc> --type=LoadBalancer --port=80                  # target-port 생략 = port와 동일
virtctl expose vm <vm> --name=<svc> --type=LoadBalancer --port=22 --target-port=22
virtctl expose vm <vm> --name=<svc> --type=NodePort     --port=22 --target-port=22
```

## 4. 볼륨 핫플러그 (add / remove)

```bash
virtctl addvolume    <vm> --volume-name=<dv-or-pvc>            # 임시(재부팅 시 사라짐)
virtctl addvolume    <vm> --volume-name=<dv-or-pvc> --persist  # 영구(재부팅 후에도 유지)
virtctl removevolume <vm> --volume-name=<dv-or-pvc>
```

## 5. 이미지 업로드 / 게스트 디스크

```bash
virtctl image-upload dv <name> --size=NGi --image-path=FILE [--storage-class=SC] [--insecure]
virtctl guestfs <volume>                              # PVC 디스크 열기 (콘솔 불가, CLI만)
virtctl guestfs <volume>; virt-sysprep -a /dev/vda    # 게스트 봉인(sysprep)
```

## 6. Export (백업 / 다운로드)

```bash
virtctl vmexport create   --vm=<vm> <export>
virtctl vmexport create   --snapshot=<snap> <export>
virtctl vmexport download <export> --vm=<vm> --volume=<vol> --output=disk.img.gz
virtctl vmexport download <export> --keep-vme --manifest --include-secret --output <file>.yml
virtctl vmexport delete   <export>
```

## 7. VM 생성 / 복제

```bash
virtctl create vm    --name=<vm> --volume-pvc=src:<dv>          | oc apply -f -
virtctl create clone --source-name <src> --target-name <tgt>   | oc apply -f -   # 복제는 자동시작 안 됨 → 수동 start
```

## 8. 마이그레이션

```bash
virtctl migrate <vm>          # 또는 콘솔 Actions → Migration → Compute
```

## 9. 도움말 / 기타

```bash
virtctl version              # virtctl 사용 가능 여부 확인
virtctl <키워드> --help      # 예: virtctl vmexport --help
virtctl --help               # 하위명령 전체 목록 (키워드 자체가 기억 안 날 때)
```

---

# oc 명령어 정리 (ex156)

> OpenShift CLI(`oc`) 명령어 모음. ex156 노트 전체에서 추출·중복 제거.

## 1. 로그인 / 프로젝트 / 사용자

```bash
oc login -u <user> -p <pw> https://api.ocp4.example.com:6443
oc login --token=sha256~... --server=https://api.ocp4.example.com:6443
oc login --web
oc whoami --show-console
oc new-project <project>
oc project <project>                  # 현재 프로젝트 전환
```

## 2. 조회 (get)

```bash
oc get vm                              # vm / vmi / dv / pvc / svc / route / nad ...
oc get vm,vmi,dv,pvc
oc get vm,vmi,dv,pvc,snapshot,nad,svc
oc get vmi
oc get dv,pvc -n <ns>
oc get pvc <name> -o jsonpath='{.spec.storageClassName}{"\n"}'
oc get sc                              # StorageClass
oc get svc <svc> -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
oc get route -A
oc get nad                             # NetworkAttachmentDefinition (net-attach-def)
oc get nncp,nnce                       # NodeNetworkConfigurationPolicy/Enactment
oc get metallb,ipaddresspool,l2advertisement -n metallb-system
oc get endpoints
oc get virtualmachinesnapshot          # vmsnapshot
oc get virtualmachineclone
oc get vmexport / vmrestore / volumesnapshots
oc get events --sort-by=.lastTimestamp -n <ns>
oc get node && oc get csr && oc get co # 노드/인증서/클러스터오퍼레이터
oc get network/cluster -o yaml
```

## 3. 생성 / 적용 (apply / create)

```bash
oc apply -f <file>.yaml
oc apply -f -                          # virtctl create ... | oc apply -f -
oc create route edge --service <svc> --hostname <host>   # 암호화(HTTPS), edge|passthrough|reencrypt
oc create service clusterip <name> ...
oc create secret generic <name> --from-file=key1=~/.ssh/id_rsa.pub
# create -f = 새로 생성(이미 있으면 에러) / apply -f = 없으면 생성·있으면 업데이트(재실행 안전)
```

## 4. 노출 (expose / route)

```bash
oc expose service/<svc> --name=<name> --port=8080 --hostname=<host>
oc expose service/<svc> --path=/static --hostname=<host>
oc expose svc/<svc>
# 주의: oc expose = 평문(HTTP)만. 암호화는 oc create route edge 사용
```

## 5. 수정 / 삭제 (edit / delete / set)

```bash
oc edit vm <vm>
oc edit pvc <pvc>                      # spec.resources.requests.storage 증설
oc edit service <svc>
oc set selector svc/<svc> <key>=<val>
oc delete vm <vm>
oc delete dv <dv> -n <ns>
oc delete datavolume/<dv>
oc delete virtualmachinesnapshot <snap>
```

## 6. 디버그 / 설명 (describe / explain / adm)

```bash
oc describe vm <vm>
oc describe vmexport/<export>
oc explain dv.spec                     # 리소스 스펙 필드 설명
oc label pod virt-launcher-<...> <key>=<val>
oc adm ...                             # 클러스터 관리(adm)
oc get csr                             # 인증서 승인 대기 확인
oc run mypod -it --rm --image=rhel8/toolbox   # 임시 테스트 포드(DNS 확인 등)
```

## 7. 도움말

```bash
oc <명령> --help                       # 예: oc expose --help, oc create route --help
oc help
```

---

# 기타 CLI 명령어 정리 (ex156)

> `virtctl`·`oc` 외에 시험에서 쓰는 CLI. **대부분 "VM 안(게스트)" 또는 "guestfs 컨테이너 안"** 에서 실행.

## 1. 게스트(VM 안) 명령 — `virtctl ssh/console`로 접속 후

```bash
# 파일/검증
touch ~/update_failed.txt              # 빈 파일 생성(스냅샷 복원 시뮬레이션)
ls -l ~/update_failed.txt              # 존재 확인

# 디스크/FS
lsblk                                  # 블록 장치(디스크·파티션) 확인
df -h /dev/sda                         # 파일시스템 용량/사용률
sudo xfs_growfs /dev/sda               # XFS 파일시스템 확장
sudo resize2fs /dev/sda                # ext4 파일시스템 확장

# 네트워크
ip address                             # VM 인터페이스/IP 확인 (enp1s0=primary 등)

# 서비스 / 시스템 정보
sudo systemctl enable --now <svc>      # 서비스 부팅 시 시작+즉시 실행 (cloud-init runcmd에도)
sudo systemctl status <svc>            # 서비스 상태
sudo journalctl -u <svc> -p notice --since "1m ago"   # 서비스 로그
hostnamectl                            # 호스트명·Machine ID 확인 (골든이미지 전후 비교)
last                                   # 로그인 기록
```

## 2. libguestfs 도구 — `virtctl guestfs <volume>` 진입 후 (VM 중지 상태)

```bash
virt-sysprep -a /dev/vda                       # 고유정보 제거(봉인). 디스크는 항상 /dev/vda
virt-sysprep --list-operations                 # 봉인 작업 40+종 보기
virt-sysprep -a /dev/vda --enable ca-certificates,user-account --remove-user-accounts cloud-user
virt-filesystems -a /dev/vda                   # 디스크 파일시스템 확인
virt-edit                                      # 이미지 안 파일 편집
virt-customize                                 # SSH키 주입·패키지 설치 등
guestfish                                      # 대화형 libguestfs 셸
exit                                           # 컨테이너 나가기 (봉인 후 VM 시작 금지!)
```

## 3. 검증 / 접속 / 전송

```bash
nc -vz <EXTERNAL-IP> 22                 # TCP 연결 확인(LoadBalancer 검증)
curl http://<EXTERNAL-IP>:80            # HTTP 응답 확인
ssh <user>@<EXTERNAL-IP>                # 외부에서 VM 접속(LB IP 등)
scp <user>@<host>:/path/file.yaml .     # 파일 복사(Import 시 yaml 가져오기)
getent hosts <svc>.<ns>.svc.cluster.local   # 포드 안에서 서비스 DNS 확인
```

## 4. kubectl (= oc 하위호환) + CLI 설치

```bash
kubectl version --client               # 버전 확인
kubectl help                           # oc help와 비교 (oc = kubectl 상위호환)
# kubectl CLI 설치 (체크섬 검증 흐름)
curl -LO "https://mirror.openshift.com/.../openshift-client-linux-<ver>.tar.gz"
sha256sum -c --ignore-missing sha256sum.txt    # 체크섬 검증(OK)
tar -xvf <file>.tar.gz                          # 압축 해제
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl   # 설치
```

> 💡 **명령 실행 위치 구분** (제일 헷갈림):
> - `virtctl`/`oc`/`kubectl` = **워크스테이션(클러스터 제어)**
> - `touch`/`lsblk`/`xfs_growfs`/`systemctl`/`ip` = **VM 안**(ssh/console로 접속 후)
> - `virt-sysprep`/`virt-edit`/`guestfish` = **guestfs 컨테이너 안**(VM 중지 상태)
> - `getent` = **클러스터 내 포드 안**(oc run 테스트 포드 등)
