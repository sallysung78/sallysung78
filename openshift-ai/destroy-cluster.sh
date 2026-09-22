#!/usr/bin/env bash
# 클러스터와 AWS 리소스(VPC, EC2, ELB, Route53 레코드, IAM 등)를 모두 삭제합니다.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
[ -f cluster.env ] && { set -a; source cluster.env; set +a; }
CLUSTER_NAME="${CLUSTER_NAME:-rhoai}"
INSTALL_DIR="$SCRIPT_DIR/${CLUSTER_NAME}-install"
export PATH="$SCRIPT_DIR/bin:$PATH" AWS_REGION="${AWS_REGION:-us-east-2}" AWS_DEFAULT_REGION="${AWS_REGION:-us-east-2}"
[ -f "$INSTALL_DIR/metadata.json" ] || { echo "metadata.json 이 없습니다: $INSTALL_DIR (삭제할 클러스터 없음)"; exit 1; }
echo "삭제 대상: $(jq -r '.clusterName + " (" + .infraID + ", " + .aws.region + ")"' "$INSTALL_DIR/metadata.json")"
if [ "${1:-}" != "--yes" ]; then read -r -p "정말 삭제하시겠습니까? (yes 입력): " a; [ "$a" = "yes" ] || exit 0; fi
openshift-install destroy cluster --dir="$INSTALL_DIR" --log-level=info
echo "완료. 로컬 디렉터리 $INSTALL_DIR 는 남겨두었습니다 (필요 시 rm -rf)."
