# 🔴 콘텐츠 관리: Vault · Jinja2 템플릿 · 변수 (약점 33% — 1순위)

> 가장 약한 영역. Vault·템플릿은 절차가 정해져 있으니 손에 익히면 점수가 보임.

## 🔐 Ansible Vault (암호화)
```bash
# 새 암호화 파일 생성
ansible-vault create secret.yml

# 기존 파일 암호화 / 복호화
ansible-vault encrypt vars/secret.yml
ansible-vault decrypt vars/secret.yml

# 내용 보기 / 편집 / 비밀번호 변경
ansible-vault view secret.yml
ansible-vault edit secret.yml
ansible-vault rekey secret.yml
```

### 플레이북에서 Vault 사용
```bash
# 실행 시 비밀번호 입력
ansible-playbook site.yml --ask-vault-pass

# 비밀번호 파일 사용 (시험 빈출)
echo 'mypassword' > vault-pass.txt
chmod 600 vault-pass.txt
ansible-playbook site.yml --vault-password-file vault-pass.txt
```
> ansible.cfg에 `vault_password_file = vault-pass.txt` 넣으면 자동 적용.

### 단일 변수만 암호화 (encrypt_string)
```bash
ansible-vault encrypt_string 'S3cr3t!' --name 'db_password'
# 출력된 블록을 vars에 붙여넣기
```

## 🧩 Jinja2 템플릿 (template 모듈)
```yaml
- ansible.builtin.template:
    src: index.html.j2        # roles/x/templates/ 또는 templates/
    dest: /var/www/html/index.html
    owner: apache
    mode: '0644'
```

### templates/index.html.j2 예시
```jinja
Welcome to {{ ansible_facts['hostname'] }}
IP: {{ ansible_facts['default_ipv4']['address'] }}

{# 조건 #}
{% if ansible_facts['os_family'] == "RedHat" %}
RHEL 계열 서버
{% endif %}

{# 반복 #}
{% for host in groups['webservers'] %}
server {{ host }};
{% endfor %}
```
> `{{ }}` 출력, `{% %}` 로직, `{# #}` 주석.
> `/etc/hosts` 만들기, `httpd.conf` 만들기가 단골 문제.

### 자주 쓰는 필터
```jinja
{{ name | upper }}          {{ name | default('none') }}
{{ list | join(',') }}      {{ password | password_hash('sha512') }}
{{ num | int }}             {{ path | basename }}
```

## 📊 변수 우선순위 (낮음 → 높음, 시험 단골 개념)
1. role `defaults/main.yml`
2. inventory file / group_vars `all`
3. inventory group_vars / host_vars
4. play `vars`, `vars_files`, `vars_prompt`
5. role `vars/main.yml`, block/task vars
6. **`-e` extra vars (가장 강함, 항상 이김)**

## group_vars / host_vars (자동 로드)
```
inventory
group_vars/
  all.yml            # 모든 호스트
  webservers.yml     # webservers 그룹
host_vars/
  servera.yml        # servera 호스트
```
> 디렉터리/파일명이 그룹·호스트명과 일치하면 **자동으로 변수 로드**.
> 암호화된 group_vars도 가능 (Vault).

## 매직 변수 (자주 씀)
- `hostvars['servera']['ansible_facts']` — 다른 호스트의 변수/팩트
- `groups['webservers']` — 그룹의 호스트 리스트
- `group_names` — 현재 호스트가 속한 그룹
- `inventory_hostname` — 인벤토리상 호스트명
