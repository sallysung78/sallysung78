#!/usr/bin/env bash
# teardown-aws.sh — EX294 연습랩 정리 (AWS CloudShell에서 실행)
# 과금 방지: 연습 끝나면 인스턴스 종료. (샌드박스는 보통 자동 만료되지만 확실히)
set -euo pipefail
REGION="${AWS_REGION:-$(aws configure get region 2>/dev/null || echo us-east-1)}"

echo "== Project=ex294 인스턴스 종료 ($REGION) =="
IDS=$(aws ec2 describe-instances --region "$REGION" \
  --filters Name=tag:Project,Values=ex294 Name=instance-state-name,Values=running,stopped,pending \
  --query 'Reservations[].Instances[].InstanceId' --output text)

if [ -n "$IDS" ]; then
  echo "종료 대상: $IDS"
  aws ec2 terminate-instances --region "$REGION" --instance-ids $IDS \
    --query 'TerminatingInstances[].[InstanceId,CurrentState.Name]' --output table
else
  echo "실행 중인 ex294 인스턴스 없음"
fi

echo ""
echo "참고: 보안그룹(ex294-sg)·키페어(ex294-key)는 남아있음(과금 X)."
echo "완전 삭제하려면:"
echo "  aws ec2 delete-security-group --group-name ex294-sg --region $REGION"
echo "  aws ec2 delete-key-pair --key-name ex294-key --region $REGION"
