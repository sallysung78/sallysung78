#!/usr/bin/env bash
# finish-setup.sh — provision-aws.sh 로 인스턴스를 만든 뒤 실행 (AWS CloudShell)
# 하는 일: 기존 ex294 인스턴스 IP 수집 → inventory 작성 → control에 ansible/컬렉션 설치
#          → 키/인벤토리 전송 → ansible all -m ping → node3 vg research
# 사용: bash finish-setup.sh
set -uo pipefail
REGION="${AWS_REGION:-$(aws configure get region 2>/dev/null || echo us-east-1)}"
KEY=ex294-key; PEM="$HOME/${KEY}.pem"

get(){ aws ec2 describe-instances --region "$REGION" \
  --filters "Name=tag:Name,Values=$1" "Name=tag:Project,Values=ex294" "Name=instance-state-name,Values=running" \
  --query "Reservations[0].Instances[0].$2" --output text; }

CTRL=$(get control PublicIpAddress)
echo "control PublicIP = $CTRL"
if [ -z "$CTRL" ] || [ "$CTRL" = "None" ]; then
  echo "ERROR: control 인스턴스를 못 찾음. provision-aws.sh 가 성공했는지 확인."
  exit 1
fi

cat > /tmp/inventory <<EOF
[dev]
node1 ansible_host=$(get node1 PrivateIpAddress)

[test]
node2 ansible_host=$(get node2 PrivateIpAddress)

[prod]
node3 ansible_host=$(get node3 PrivateIpAddress)
node4 ansible_host=$(get node4 PrivateIpAddress)

[balancers]
node5 ansible_host=$(get node5 PrivateIpAddress)

[webservers:children]
prod
EOF
echo "== inventory =="; cat /tmp/inventory

echo "== control SSH 대기 =="
for i in $(seq 1 40); do
  ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i "$PEM" ec2-user@"$CTRL" true 2>/dev/null && break || sleep 10
done

scp -o StrictHostKeyChecking=no -i "$PEM" "$PEM" ec2-user@"$CTRL":~/.ssh/id_rsa
scp -o StrictHostKeyChecking=no -i "$PEM" /tmp/inventory ec2-user@"$CTRL":~/inventory

ssh -o StrictHostKeyChecking=no -i "$PEM" ec2-user@"$CTRL" 'bash -s' <<'REMOTE'
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
echo "[control] 연결 테스트..."; ansible all -m ping || true
echo "[control] node3 vg research..."; ansible node3 -b -m shell -a 'pvcreate -y /dev/nvme1n1 2>/dev/null; vgcreate research /dev/nvme1n1 2>/dev/null || true; vgs' || true
echo "[control] 완료."
REMOTE

echo ""
echo "============================================================"
echo " 준비 완료!  접속:  ssh -i $PEM ec2-user@$CTRL"
echo " 그다음: cd ~/ansible && ansible all -m ping"
echo "============================================================"
