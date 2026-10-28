# 🖥️ EX294 연습환경 세팅 (AWS RHEL 9)

> AWS에 RHEL 9 인스턴스를 받으면 **이 폴더 파일들을 복붙**해서 빠르게 연습환경을 만든다.
> 구성: control 1대 + managed 5대 (node1~5). node3·4는 webservers(부하분산용).

## ⭐ 원클릭 (추천): AWS CloudShell에서 `lab-up.sh`
> 콘솔 로그인 → CloudShell(`>_`) → 아래 한 줄 → 기다리면 끝.
> 인스턴스 6대 생성 + control에 ansible/컬렉션 설치 + inventory 자동작성 + ping + node3 vg까지 자동.
```bash
curl -sL "https://raw.githubusercontent.com/sallysung78/sallysung78/claude/github-project-folders-lg9ms6/ClaudeProject/%EA%B3%B5%EB%B6%80/EX294/%EC%8B%9C%ED%97%98%ED%99%98%EA%B2%BD/lab-up.sh" -o lab-up.sh
bash lab-up.sh
```
끝나면 출력된 명령으로 접속: `ssh -i ~/ex294-key.pem ec2-user@<control_IP>` → `cd ~/ansible` → 문제풀이.

## 📂 파일
- `lab-up.sh` — ⭐ **원클릭**: 생성+control설정+inventory+ping 전부
- `provision-aws.sh` — (수동 변형) 인스턴스 6대+SG+키만 생성
- `teardown-aws.sh` — **AWS CloudShell에서** 인스턴스 정리(과금 방지)
- `control-setup.sh` — control 노드에 Ansible·검증도구·컬렉션·시스템롤 설치
- `bootstrap.yml` — 모든 노드에 devops 유저·SSH키·/etc/hosts 세팅 (+ node3에 LVM용 vg)
- `ansible.cfg` — 작업 디렉토리용 설정 템플릿
- `inventory` — 그룹(dev/test/prod/balancers/webservers) 템플릿 (IP만 채우면 됨)
- `vimrc` — 탭 실수 예방용 vim 설정

---

## ▶️ 실행 순서 (AWS 뜨면)

### 0) 사전
- RHEL 9 인스턴스 6대 (control, node1~5), 같은 VPC
- 보안그룹: SSH 22 / HTTP 80 / ICMP
- managed(특히 node3)에 **빈 EBS 디스크** 1개 추가 (→ LVM 10번 / vdb 14번)
- (BYOS면) 각 노드 `sudo subscription-manager register ...` 로 repo 활성화

### 0.5) 인스턴스 생성 — AWS CloudShell에서 (가장 쉬움)
> 로컬/세션에서 키 쓰지 말고 **콘솔 CloudShell**에서. 키·권한 이미 있고 바로 됨.
```bash
# 웹 콘솔 로그인 → 우상단 CloudShell(>_) 아이콘 클릭 → 아래 실행
curl -O <provision-aws.sh 내용 붙여넣기 or 업로드>   # 또는 내용 복붙
bash provision-aws.sh          # 6대 생성 + IP 출력
# 끝나면 정리: bash teardown-aws.sh
```
- 출력된 **control PublicIP** 로 접속, **각 노드 PrivateIP** 를 inventory에 기입
- 생성된 `~/ex294-key.pem` 은 CloudShell **Actions > Download file** 로 받아 보관

### 1) control 노드에서
```bash
# 이 폴더 파일들을 control의 ~/ 에 복사한 뒤
bash control-setup.sh                      # ansible 등 설치
mkdir -p ~/ansible && cd ~/ansible
cp ~/ansible.cfg ~/inventory .             # 템플릿 복사
cp ~/vimrc ~/.vimrc

# inventory 파일 열어서 각 node의 실제 사설 IP 입력
vim inventory
```

### 2) 최초 접속용 키 배포 (ec2-user 기준)
```bash
# EC2 키페어(.pem)로 먼저 접속되는 상태에서, 공용키를 각 노드에 심기
ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519      # 없으면 생성
# 각 노드에 ec2-user로 키 복사 (pem 사용)
for ip in <node1_ip> <node2_ip> ... ; do
  ssh-copy-id -i ~/.ssh/id_ed25519.pub -o StrictHostKeyChecking=no ec2-user@$ip
done
```

### 3) 부트스트랩 (devops 유저·키·hosts·vg 자동 세팅)
```bash
# 처음엔 ec2-user로 연결해 devops를 만든다
ansible-playbook bootstrap.yml -u ec2-user --key-file ~/.ssh/id_ed25519 -b
```

### 4) 검증
```bash
cd ~/ansible
ansible all -m ping                        # 전부 SUCCESS면 준비 완료
ansible all -m command -a id -b
```

### 5) 연습 시작
- [YAML빈칸문제](../YAML빈칸문제.md) / [핵심문제](../핵심문제.md) 보며 18문제
- 매 파일: **`yamllint x.yml` → `ansible-playbook x.yml --syntax-check` → `-C` → 실행**

---

## 💰 끝나면
- 연습 안 할 땐 인스턴스 **Stop** (컴퓨팅 과금 0)
- 완전히 끝나면 **Terminate + EBS/EIP 정리** (안 하면 계속 과금)
