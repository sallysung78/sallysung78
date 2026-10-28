#!/usr/bin/env bash
# lab-up.sh — EX294 연습랩 "원클릭" (AWS CloudShell에서 실행)
# ───────────────────────────────────────────────────────────
# 하는 일: RHEL9 6대 생성 → control에 ansible/컬렉션/시스템롤 설치
#          → inventory 자동작성 → ansible all -m ping → node3에 vg research
# 끝나면: ssh -i ~/ex294-key.pem ec2-user@<control_IP>  하고 cd ~/ansible 에서 문제풀이
#
# 사용법(콘솔 CloudShell): 이 파일 통째로 붙여넣고  bash lab-up.sh
# 정리: teardown-aws.sh
set -uo pipefail

REGION="${AWS_REGION:-$(aws configure get region 2>/dev/null || echo us-east-1)}"
KEY=ex294-key ; SG_NAME=ex294-sg ; ITYPE=t3.micro
NODES=(control node1 node2 node3 node4 node5)
MANAGED=(node1 node2 node3 node4 node5)     # 추가 디스크(LVM/vdb)
PEM="$HOME/${KEY}.pem"
echo "== Region=$REGION =="

# 1) 키페어
if ! aws ec2 describe-key-pairs --key-names $KEY --region $REGION >/dev/null 2>&1; then
  aws ec2 create-key-pair --key-name $KEY --region $REGION --query KeyMaterial --output text > "$PEM"
  chmod 600 "$PEM"; echo "키 생성: $PEM"
else echo "키 이미 있음: $KEY (기존 $PEM 사용)"; fi

# 2) VPC/서브넷/SG/AMI
VPC=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --region $REGION --query 'Vpcs[0].VpcId' --output text)
SUBNET=$(aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC --region $REGION --query 'Subnets[0].SubnetId' --output text)
SG=$(aws ec2 describe-security-groups --filters Name=group-name,Values=$SG_NAME Name=vpc-id,Values=$VPC --region $REGION --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo None)
if [ "$SG" = "None" ] || [ -z "$SG" ]; then
  SG=$(aws ec2 create-security-group --group-name $SG_NAME --description "EX294 lab" --vpc-id $VPC --region $REGION --query GroupId --output text)
  aws ec2 authorize-security-group-ingress --group-id $SG --region $REGION --ip-permissions \
    IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges='[{CidrIp=0.0.0.0/0}]' \
    IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges='[{CidrIp=0.0.0.0/0}]' \
    IpProtocol=icmp,FromPort=-1,ToPort=-1,IpRanges='[{CidrIp=0.0.0.0/0}]' >/dev/null
  aws ec2 authorize-security-group-ingress --group-id $SG --region $REGION --protocol -1 --source-group $SG >/dev/null
fi
echo "VPC=$VPC SUBNET=$SUBNET SG=$SG"
AMI=$(aws ec2 describe-images --owners 309956199498 --region $REGION \
  --filters "Name=name,Values=RHEL-9.*_HVM-*-x86_64-*" "Name=state,Values=available" \
  --query 'sort_by(Images,&CreationDate)[-1].ImageId' --output text)
echo "RHEL9 AMI=$AMI"

# 3) 인스턴스 기동
declare -A IID
for n in "${NODES[@]}"; do
  BDM=""
  [[ " ${MANAGED[*]} " == *" $n "* ]] && BDM="--block-device-mappings DeviceName=/dev/sdb,Ebs={VolumeSize=2,VolumeType=gp3,DeleteOnTermination=true}"
  IID[$n]=$(aws ec2 run-instances --image-id $AMI --instance-type $ITYPE --key-name $KEY \
    --security-group-ids $SG --subnet-id $SUBNET --region $REGION $BDM \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$n},{Key=Project,Value=ex294}]" \
    --user-data "#!/bin/bash
hostnamectl set-hostname $n" \
    --query 'Instances[0].InstanceId' --output text)
  echo "  $n -> ${IID[$n]}"
done

echo "== running 대기 =="
aws ec2 wait instance-running --instance-ids "${IID[@]}" --region $REGION

# 4) IP 수집 + inventory 작성
declare -A PUB PRIV
for n in "${NODES[@]}"; do
  PUB[$n]=$(aws ec2 describe-instances --instance-ids ${IID[$n]} --region $REGION --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
  PRIV[$n]=$(aws ec2 describe-instances --instance-ids ${IID[$n]} --region $REGION --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text)
done
CTRL=${PUB[control]}
cat > /tmp/inventory <<EOF
[dev]
node1 ansible_host=${PRIV[node1]}

[test]
node2 ansible_host=${PRIV[node2]}

[prod]
node3 ansible_host=${PRIV[node3]}
node4 ansible_host=${PRIV[node4]}

[balancers]
node5 ansible_host=${PRIV[node5]}

[webservers:children]
prod
EOF
echo "control PublicIP = $CTRL"

# 5) control SSH 대기
echo "== control SSH 대기 =="
for i in $(seq 1 40); do
  ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i "$PEM" ec2-user@$CTRL true 2>/dev/null && break || sleep 10
done

# 6) 키 + inventory 전송
scp -o StrictHostKeyChecking=no -i "$PEM" "$PEM" ec2-user@$CTRL:~/.ssh/id_rsa
scp -o StrictHostKeyChecking=no -i "$PEM" /tmp/inventory ec2-user@$CTRL:~/inventory

# 7) control 원격 설정
ssh -o StrictHostKeyChecking=no -i "$PEM" ec2-user@$CTRL 'bash -s' <<'REMOTE'
set -e
chmod 600 ~/.ssh/id_rsa
echo "[control] ansible 설치..."
sudo dnf install -y ansible-core rhel-system-roles yamllint 2>/dev/null || sudo dnf install -y ansible-core
ansible-galaxy collection install ansible.posix community.general 2>/dev/null || true
mkdir -p ~/ansible/roles ~/ansible/collections
mv ~/inventory ~/ansible/inventory
cat > ~/ansible/ansible.cfg <<CFG
[defaults]
inventory = ./inventory
roles_path = ./roles
collections_path = ./collections
remote_user = ec2-user
host_key_checking = False
private_key_file = ~/.ssh/id_rsa

[privilege_escalation]
become = True
become_method = sudo
become_user = root
CFG
cat > ~/.vimrc <<VIM
set expandtab shiftwidth=2 softtabstop=2 autoindent number
set list listchars=tab:>-,trail:.
autocmd FileType yaml setlocal ts=2 sts=2 sw=2 expandtab
VIM
cd ~/ansible
echo "[control] 연결 테스트..."
ansible all -m ping || true
echo "[control] node3에 vg research 생성(문제10 defined 분기용)..."
ansible node3 -b -m shell -a 'pvcreate -y /dev/nvme1n1 2>/dev/null; vgcreate research /dev/nvme1n1 2>/dev/null || true; vgs' || true
echo "[control] 준비 완료."
REMOTE

echo ""
echo "============================================================"
echo " 랩 준비 완료!"
echo " 접속:  ssh -i $PEM ec2-user@$CTRL"
echo " 그다음: cd ~/ansible  →  ansible all -m ping  →  문제풀이 시작"
echo " (pem 다운로드: CloudShell 우상단 Actions > Download file > $PEM)"
echo "============================================================"
aws ec2 describe-instances --region $REGION \
  --filters Name=tag:Project,Values=ex294 Name=instance-state-name,Values=running \
  --query 'Reservations[].Instances[].[Tags[?Key==`Name`]|[0].Value,PublicIpAddress,PrivateIpAddress]' --output table
