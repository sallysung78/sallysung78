#!/usr/bin/env bash
# provision-aws.sh — EX294 연습랩 프로비저닝 (AWS CloudShell에서 실행)
# 콘솔 로그인 → 우상단 CloudShell(>_) 열기 → 이 스크립트 붙여넣고 실행
# (CloudShell은 로그인한 계정 권한을 그대로 씀. 키 입력 불필요)
set -euo pipefail

# ===== 설정 (필요시 수정) =====
REGION="${AWS_REGION:-$(aws configure get region 2>/dev/null || echo us-east-1)}"
KEY_NAME="ex294-key"
SG_NAME="ex294-sg"
ITYPE="t3.micro"           # vCPU 쿼터 빠듯하면 유지, 여유되면 control만 t3.small
NODES=(control node1 node2 node3 node4 node5)
MANAGED=(node1 node2 node3 node4 node5)   # 추가 디스크 붙일 노드(LVM/vdb용)
EXTRA_DISK_GB=2
# ==============================

echo "== Region: $REGION =="

# 1) 키페어 (없으면 생성 → .pem 저장)
if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$REGION" >/dev/null 2>&1; then
  aws ec2 create-key-pair --key-name "$KEY_NAME" --region "$REGION" \
    --query 'KeyMaterial' --output text > ~/${KEY_NAME}.pem
  chmod 600 ~/${KEY_NAME}.pem
  echo "키 생성: ~/${KEY_NAME}.pem (★ 다운로드해서 보관: CloudShell Actions > Download file)"
else
  echo "키페어 이미 있음: $KEY_NAME (기존 .pem 사용)"
fi

# 2) 기본 VPC / 서브넷
VPC=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true \
  --region "$REGION" --query 'Vpcs[0].VpcId' --output text)
SUBNET=$(aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC \
  --region "$REGION" --query 'Subnets[0].SubnetId' --output text)
echo "VPC=$VPC SUBNET=$SUBNET"

# 3) 보안그룹 (SSH/HTTP/ICMP + SG 내부 전체 허용)
SG=$(aws ec2 describe-security-groups --filters Name=group-name,Values=$SG_NAME Name=vpc-id,Values=$VPC \
  --region "$REGION" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "None")
if [ "$SG" = "None" ] || [ -z "$SG" ]; then
  SG=$(aws ec2 create-security-group --group-name "$SG_NAME" --description "EX294 lab" \
    --vpc-id "$VPC" --region "$REGION" --query 'GroupId' --output text)
  aws ec2 authorize-security-group-ingress --group-id "$SG" --region "$REGION" \
    --ip-permissions \
      IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges='[{CidrIp=0.0.0.0/0}]' \
      IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges='[{CidrIp=0.0.0.0/0}]' \
      IpProtocol=icmp,FromPort=-1,ToPort=-1,IpRanges='[{CidrIp=0.0.0.0/0}]' >/dev/null
  # SG 내부 노드끼리 전체 통신 허용
  aws ec2 authorize-security-group-ingress --group-id "$SG" --region "$REGION" \
    --protocol -1 --source-group "$SG" >/dev/null
  echo "보안그룹 생성: $SG"
else
  echo "보안그룹 이미 있음: $SG"
fi

# 4) RHEL 9 AMI (Red Hat 공식, owner 309956199498)
AMI=$(aws ec2 describe-images --owners 309956199498 --region "$REGION" \
  --filters "Name=name,Values=RHEL-9.*_HVM-*-x86_64-*" "Name=architecture,Values=x86_64" "Name=state,Values=available" \
  --query 'sort_by(Images,&CreationDate)[-1].ImageId' --output text)
echo "RHEL9 AMI=$AMI"

# 5) 인스턴스 기동
launch () {
  local NAME=$1 BDM=""
  # 관리노드면 추가 디스크(/dev/sdb) 붙이기
  for m in "${MANAGED[@]}"; do
    if [ "$m" = "$NAME" ]; then
      BDM="--block-device-mappings DeviceName=/dev/sdb,Ebs={VolumeSize=${EXTRA_DISK_GB},VolumeType=gp3,DeleteOnTermination=true}"
    fi
  done
  aws ec2 run-instances --image-id "$AMI" --instance-type "$ITYPE" \
    --key-name "$KEY_NAME" --security-group-ids "$SG" --subnet-id "$SUBNET" \
    --region "$REGION" $BDM \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME},{Key=Project,Value=ex294}]" \
    --user-data "#!/bin/bash
hostnamectl set-hostname $NAME" \
    --query 'Instances[0].InstanceId' --output text
}

echo "== 인스턴스 기동 =="
for n in "${NODES[@]}"; do
  ID=$(launch "$n"); echo "  $n -> $ID"
done

echo ""
echo "== 30초 후 IP 확인 =="; sleep 30
aws ec2 describe-instances --region "$REGION" \
  --filters Name=tag:Project,Values=ex294 Name=instance-state-name,Values=running,pending \
  --query 'Reservations[].Instances[].[Tags[?Key==`Name`]|[0].Value, InstanceId, PublicIpAddress, PrivateIpAddress]' \
  --output table

echo ""
echo "완료. control에 SSH:  ssh -i ~/${KEY_NAME}.pem ec2-user@<control_PublicIP>"
echo "각 노드 PrivateIP를 inventory에 넣으세요."
