#!/usr/bin/env bash
# control-setup.sh — EX294 control 노드 초기 설치 (RHEL 9)
# 사용: bash control-setup.sh
set -euo pipefail

echo "== [1/4] 기본 패키지 =="
sudo dnf install -y ansible-core git vim bash-completion tar

echo "== [2/4] 문법/오타 검증 도구 =="
# RHEL9 repo에 있으면 dnf, 없으면 pip로
sudo dnf install -y yamllint ansible-lint 2>/dev/null || pip3 install --user yamllint ansible-lint

echo "== [3/4] 컬렉션 (8·10번 모듈 / posix·general) =="
# 인터넷 되면 Galaxy에서, 오프라인이면 미리 받아둔 tar.gz를 -p 로 설치
ansible-galaxy collection install ansible.posix community.general || \
  echo "  (인터넷 안되면: ansible-galaxy collection install <파일>.tar.gz -p ~/ansible/collections)"

echo "== [4/4] RHEL 시스템 롤 (5·6번 timesync/selinux) =="
sudo dnf install -y rhel-system-roles || \
  echo "  (repo 구독 필요. BYOS면 subscription-manager register 먼저)"

echo ""
echo "== 설치 확인 =="
ansible --version | head -1
yamllint --version 2>/dev/null || true
ansible-lint --version 2>/dev/null || true
ansible-galaxy collection list 2>/dev/null | grep -Ei 'posix|general' || true
ls /usr/share/ansible/roles/ 2>/dev/null | grep -i system || true

echo ""
echo "완료. 다음: ~/ansible 디렉토리 만들고 ansible.cfg·inventory 복사 → bootstrap.yml 실행"
