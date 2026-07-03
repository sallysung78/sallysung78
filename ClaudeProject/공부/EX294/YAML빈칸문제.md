# ✍️ EX294 YAML 빈칸 문제 (정답 숨김)

> 완성해야 하는 YAML만 모음. **빈칸을 손으로 채운 뒤 `▶ 정답 보기` 클릭해 대조.**
> `____` = 빈칸. GitHub에서 정답은 접혀 있음(눌러야 펼쳐짐).
> ⭐ 재부팅 유지: 서비스 `enabled:true` / 방화벽 `permanent:true` / 마운트 `state:mounted`

---

## 2. `yum_repo.yml` — 모든 노드에 BaseOS·AppStream 저장소 2개

```yaml
___                                    # 첫 줄
- name: configure yum repository
  hosts: ___
  ___: true
  tasks:
    - name: BaseOS repo
      ansible.builtin.________________:
        name: ___________
        description: EX294 base software
        baseurl: http://yum.repo.red.hat.com/BaseOS
        ________: true                 # gpg 서명 확인
        gpgkey: http://yum.repo.red.hat.com/RHEL/RPM-GPG-KEY-redhat-release
        _______: true                  # 활성화
    - name: AppStream repo
      ansible.builtin.yum_repository:
        name: ___________              # 1번과 다른 이름!
        description: EX294 base software
        baseurl: http://yum.repo.red.hat.com/AppStream
        gpgcheck: true
        gpgkey: http://yum.repo.red.hat.com/RHEL/RPM-GPG-KEY-redhat-release
        enabled: true
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: configure yum repository
  hosts: all
  become: true
  tasks:
    - name: BaseOS repo
      ansible.builtin.yum_repository:
        name: EX294_BASE
        description: EX294 base software
        baseurl: http://yum.repo.red.hat.com/BaseOS
        gpgcheck: true
        gpgkey: http://yum.repo.red.hat.com/RHEL/RPM-GPG-KEY-redhat-release
        enabled: true
    - name: AppStream repo
      ansible.builtin.yum_repository:
        name: EX294_STREAM
        description: EX294 base software
        baseurl: http://yum.repo.red.hat.com/AppStream
        gpgcheck: true
        gpgkey: http://yum.repo.red.hat.com/RHEL/RPM-GPG-KEY-redhat-release
        enabled: true
```
</details>

---

## 4. `install-pkg.yml` — 그룹별 패키지 설치/그룹/업데이트

```yaml
---
- name: install php mariadb
  hosts: ______________              # dev,test,prod
  become: true
  tasks:
    - name: packages
      ansible.builtin.___:
        name:
          - ___
          - ________
        state: _______

- name: dev only
  hosts: ___
  become: true
  tasks:
    - name: dev tools group
      ansible.builtin.dnf:
        name: "____________________"  # 패키지 그룹
        state: present
    - name: update all
      ansible.builtin.dnf:
        name: "___"                   # 전체
        state: ______
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: install php mariadb
  hosts: dev,test,prod
  become: true
  tasks:
    - name: packages
      ansible.builtin.dnf:
        name:
          - php
          - mariadb
        state: present

- name: dev only
  hosts: dev
  become: true
  tasks:
    - name: dev tools group
      ansible.builtin.dnf:
        name: "@RPM Development Tools"
        state: present
    - name: update all
      ansible.builtin.dnf:
        name: "*"
        state: latest
```
> dnf=yum 동일. 어느 쪽 써도 정답.
</details>

---

## 5. `ntp-role.yml` — timesync 시스템 롤 (tasks 없음!)

```yaml
---
- name: configure ntp
  hosts: ___
  become: true
  ____:                              # tasks 아님!
    timesync_ntp_servers:
      - hostname: _____________      # 192.168.0.254
        ______: true                 # iburst
  ____:
    - rhel-system-roles.timesync
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: configure ntp
  hosts: all
  become: true
  vars:
    timesync_ntp_servers:
      - hostname: 192.168.0.254
        iburst: true
  roles:
    - rhel-system-roles.timesync
```
> 사전: `sudo yum -y install rhel-system-roles`. 변수명은 README에서 확인.
</details>

---

## 6. `selinux.yml` — selinux 시스템 롤

```yaml
---
- name: configure selinux
  hosts: ___
  become: true
  ____:
    selinux_policy: ____________     # targeted
    selinux_state: ____________      # enforcing
  ____:
    - rhel-system-roles.selinux
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: configure selinux
  hosts: all
  become: true
  vars:
    selinux_policy: targeted
    selinux_state: enforcing
  roles:
    - rhel-system-roles.selinux
```
</details>

---

## 7. `roles/requirements.yml` — 갤럭시 롤 설치 (--- 없음!)

```yaml
- ____: balancer
  ___: http://ansible.galaxy.com/materials/haproxy.tar
- name: phpinfo
  src: http://ansible.galaxy.com/materials/phpinfo.tar
```
설치 명령: `ansible-galaxy ________ -r roles/requirements.yml`
<details><summary>▶ 정답 보기</summary>

```yaml
- name: balancer
  src: http://ansible.galaxy.com/materials/haproxy.tar
- name: phpinfo
  src: http://ansible.galaxy.com/materials/phpinfo.tar
```
설치: `ansible-galaxy install -r roles/requirements.yml`
> 롤=`install -r`, 콜렉션=`collection install -p`. requirements.yml엔 `---` 안 붙임.
</details>

---

## 8-a. `roles/apache/tasks/main.yml` — 커스텀 롤 (hosts 없음!)

```yaml
---
- name: install httpd
  ansible.builtin.___:
    name: httpd
    state: latest
- name: start httpd
  ansible.builtin.________:
    name: httpd
    state: _______
    _______: true                    # 재부팅 후에도
- name: start firewalld
  ansible.builtin.service:
    name: firewalld
    state: started
    enabled: true
- name: allow http
  ansible.posix.__________:
    service: http
    state: _______
    _________: true                  # 재부팅 유지 (★놓치기 쉬움)
    _________: true                  # 지금도 적용
- name: deploy index
  ansible.builtin.________:
    src: index.html.j2
    dest: /var/www/html/index.html
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: install httpd
  ansible.builtin.dnf:
    name: httpd
    state: latest
- name: start httpd
  ansible.builtin.service:
    name: httpd
    state: started
    enabled: true
- name: start firewalld
  ansible.builtin.service:
    name: firewalld
    state: started
    enabled: true
- name: allow http
  ansible.posix.firewalld:
    service: http
    state: enabled
    permanent: true
    immediate: true
- name: deploy index
  ansible.builtin.template:
    src: index.html.j2
    dest: /var/www/html/index.html
```
</details>

## 8-b. `roles/apache/templates/index.html.j2`

```jinja
Hello Apache from {{ ____________ }} on {{ _____________________ }}
```
<details><summary>▶ 정답 보기</summary>

```jinja
Hello Apache from {{ ansible_hostname }} on {{ ansible_default_ipv4.address }}
```
> setup에 보이는 `ansible_xxx` 이름 그대로. `ansible_facts['ansible_hostname']` ❌
</details>

## 8-c. `run-role.yml` — 롤 호출

```yaml
---
- hosts: __________
  become: true
  ____:                              # tasks 아님!
    - apache
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- hosts: webservers
  become: true
  roles:
    - apache
```
</details>

---

## 9. `roles.yml` — balancer/phpinfo 롤 사용

```yaml
---
- name: load balancer
  hosts: __________                  # balancers
  become: true
  ____:
    - balancer
- name: php info
  hosts: __________                  # webservers
  become: true
  roles:
    - ________
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: load balancer
  hosts: balancers
  become: true
  roles:
    - balancer
- name: php info
  hosts: webservers
  become: true
  roles:
    - phpinfo
```
</details>

---

## 10. `lv.yml` — 논리 볼륨 (block/rescue)

```yaml
---
- hosts: ___
  tasks:
  - _____:
      - name: 1500m
        community.general.____:
          vg: research
          lv: data
          size: ______
      - name: ext4
        community.general.__________:
          fstype: ____
          dev: /dev/research/data
    ______:
      - debug:
          msg: Could not create logical volume of that size
      - name: 800m
        community.general.lvol:
          vg: research
          lv: data
          size: _____
        when: ansible_lvm.vgs.research is _______
        ______________: yes
      - debug:
          msg: Volume group not found
        when: ansible_lvm.vgs.research is _________
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- hosts: all
  tasks:
  - block:
      - name: 1500m
        community.general.lvol:
          vg: research
          lv: data
          size: 1500m
      - name: ext4
        community.general.filesystem:
          fstype: ext4
          dev: /dev/research/data
    rescue:
      - debug:
          msg: Could not create logical volume of that size
      - name: 800m
        community.general.lvol:
          vg: research
          lv: data
          size: 800m
        when: ansible_lvm.vgs.research is defined
        ignore_errors: yes
      - debug:
          msg: Volume group not found
        when: ansible_lvm.vgs.research is undefined
```
> 마운트 task 금지. 메시지 문구는 문제 원문과 정확히 일치.
</details>

---

## 11-a. `hosts.j2` — 템플릿 (for 반복)

```jinja
{% ___ host in groups['___'] %}
{{ hostvars[host]['ansible_facts']['____________']['address'] }} {{ hostvars[host]['ansible_facts']['____'] }} {{ hostvars[host]['ansible_facts']['________'] }}
{% ______ %}
```
<details><summary>▶ 정답 보기</summary>

```jinja
{% for host in groups['all'] %}
{{ hostvars[host]['ansible_facts']['default_ipv4']['address'] }} {{ hostvars[host]['ansible_facts']['fqdn'] }} {{ hostvars[host]['ansible_facts']['hostname'] }}
{% endfor %}
```
> 남의 호스트 정보라 `hostvars[host]` 필수. 순서: IP·FQDN·hostname.
</details>

## 11-b. `hosts.yml` — 템플릿 배포

```yaml
---
- name: gen hosts
  hosts: ___
  become: true
  tasks:
    - name: deploy myhosts
      ansible.builtin.________:
        src: hosts.j2
        dest: /etc/myhosts
      when: ________________ in groups['___']
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: gen hosts
  hosts: all
  become: true
  tasks:
    - name: deploy myhosts
      ansible.builtin.template:
        src: hosts.j2
        dest: /etc/myhosts
      when: inventory_hostname in groups['dev']
```
</details>

---

## 12. `issue.yml` — 그룹별 /etc/issue 내용

```yaml
---
- name: set issue
  hosts: ___
  become: true
  tasks:
    - name: dev
      ansible.builtin.____:
        content: "___________\n"     # Development
        dest: /etc/issue
      when: ________________ in groups['dev']
    - name: test
      ansible.builtin.copy:
        content: "Test\n"
        dest: /etc/issue
      when: inventory_hostname in groups['test']
    - name: prod
      ansible.builtin.copy:
        content: "Production\n"
        dest: /etc/issue
      when: inventory_hostname in groups['prod']
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: set issue
  hosts: all
  become: true
  tasks:
    - name: dev
      ansible.builtin.copy:
        content: "Development\n"
        dest: /etc/issue
      when: inventory_hostname in groups['dev']
    - name: test
      ansible.builtin.copy:
        content: "Test\n"
        dest: /etc/issue
      when: inventory_hostname in groups['test']
    - name: prod
      ansible.builtin.copy:
        content: "Production\n"
        dest: /etc/issue
      when: inventory_hostname in groups['prod']
```
</details>

---

## 13. `webcontent.yml` — 디렉터리/링크/권한/setype

```yaml
---
- name: web content
  hosts: ___
  become: true
  tasks:
    - name: create dir
      ansible.builtin.____:
        path: /webdev
        state: ____________          # directory
        group: webdev
        mode: '______'               # 2775
        setype: __________________   # httpd_sys_content_t
    - name: symlink
      ansible.builtin.file:
        src: /webdev
        dest: /var/www/html/webdev
        state: ____                  # link
    - name: index
      ansible.builtin.____:
        content: "Development\n"
        dest: /webdev/index.html
        setype: httpd_sys_content_t
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: web content
  hosts: dev
  become: true
  tasks:
    - name: create dir
      ansible.builtin.file:
        path: /webdev
        state: directory
        group: webdev
        mode: '2775'
        setype: httpd_sys_content_t
    - name: symlink
      ansible.builtin.file:
        src: /webdev
        dest: /var/www/html/webdev
        state: link
    - name: index
      ansible.builtin.copy:
        content: "Development\n"
        dest: /webdev/index.html
        setype: httpd_sys_content_t
```
</details>

---

## 14. `hwreport.yml` — 다운로드 후 값 치환 (없으면 NONE)

```yaml
---
- name: Create Report
  hosts: ___
  become: true
  tasks:
    - name: Download Empty File
      ansible.builtin.________:
        url: http://materials.classroom.com/hwreport.empty
        dest: /root/hwreport.txt
    - name: HOST
      ansible.builtin.__________:
        path: /root/hwreport.txt
        ______: "^HOST="             # regexp (철자!)
        line: "HOST={{ ________________ }}"   # inventory_hostname
    - name: MEM
      ansible.builtin.lineinfile:
        path: /root/hwreport.txt
        regexp: "^MEM="
        line: "MEM={{ ansible_memtotal_mb | ________________ }}"   # default('NONE', true)
    - name: BIOS
      ansible.builtin.lineinfile:
        path: /root/hwreport.txt
        regexp: "^BIOS="
        line: "BIOS={{ ansible_bios_version | default('NONE', true) }}"
    - name: VDA
      ansible.builtin.lineinfile:
        path: /root/hwreport.txt
        regexp: "^DISK_VDA_SIZE="
        line: "DISK_VDA_SIZE={{ ______________________ | default('NONE', true) }}"
    - name: VDB
      ansible.builtin.lineinfile:
        path: /root/hwreport.txt
        regexp: "^DISK_VDB_SIZE="
        line: "DISK_VDB_SIZE={{ ansible_devices.vdb.size | default('NONE', true) }}"
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: Create Report
  hosts: all
  become: true
  tasks:
    - name: Download Empty File
      ansible.builtin.get_url:
        url: http://materials.classroom.com/hwreport.empty
        dest: /root/hwreport.txt
    - name: HOST
      ansible.builtin.lineinfile:
        path: /root/hwreport.txt
        regexp: "^HOST="
        line: "HOST={{ inventory_hostname }}"
    - name: MEM
      ansible.builtin.lineinfile:
        path: /root/hwreport.txt
        regexp: "^MEM="
        line: "MEM={{ ansible_memtotal_mb | default('NONE', true) }}"
    - name: BIOS
      ansible.builtin.lineinfile:
        path: /root/hwreport.txt
        regexp: "^BIOS="
        line: "BIOS={{ ansible_bios_version | default('NONE', true) }}"
    - name: VDA
      ansible.builtin.lineinfile:
        path: /root/hwreport.txt
        regexp: "^DISK_VDA_SIZE="
        line: "DISK_VDA_SIZE={{ ansible_devices.vda.size | default('NONE', true) }}"
    - name: VDB
      ansible.builtin.lineinfile:
        path: /root/hwreport.txt
        regexp: "^DISK_VDB_SIZE="
        line: "DISK_VDB_SIZE={{ ansible_devices.vdb.size | default('NONE', true) }}"
```
> 라벨은 받은 파일(`cat`)에 맞춤. `default('NONE', true)` — vdb 없어도 에러 안 남.
</details>

---

## 15. `locker.yml` — Vault 변수 파일 (암호화 전 평문)

```yaml
____________: ______                 # pw_developer: Imadev
____________: ______                 # pw_manager: Imamgr
```
암호화: `ansible-vault ________ --vault-password-file=________ locker.yml`
<details><summary>▶ 정답 보기</summary>

```yaml
pw_developer: Imadev
pw_manager: Imamgr
```
```bash
echo 'thisissecert' > secret.txt && chmod 0600 secret.txt
ansible-vault encrypt --vault-password-file=secret.txt locker.yml
```
</details>

---

## 16. `users.yml` — Vault + loop + password_hash

```yaml
---
- name: developers
  hosts: dev,test
  become: true
  __________:                        # 외부 변수 파일
    - locker.yml
    - user_list.yml
  tasks:
    - name: devops group
      ansible.builtin.____:
        name: devops
        state: present
    - name: dev users
      ansible.builtin.____:
        name: "{{ item.name }}"
        groups: devops
        ______: true                 # 기존 그룹 유지
        password: "{{ pw_developer | ____________('sha512') }}"
      ____: "{{ users }}"
      when: item.job == "____________"   # developer
- name: managers
  hosts: prod
  become: true
  vars_files:
    - locker.yml
    - user_list.yml
  tasks:
    - name: opsmgr group
      ansible.builtin.group:
        name: opsmgr
        state: present
    - name: mgr users
      ansible.builtin.user:
        name: "{{ item.name }}"
        groups: opsmgr
        append: true
        password: "{{ pw_manager | password_hash('sha512') }}"
      loop: "{{ users }}"
      when: item.job == "manager"
```
실행: `ansible-playbook users.yml --vault-password-file=secret.txt`
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: developers
  hosts: dev,test
  become: true
  vars_files:
    - locker.yml
    - user_list.yml
  tasks:
    - name: devops group
      ansible.builtin.group:
        name: devops
        state: present
    - name: dev users
      ansible.builtin.user:
        name: "{{ item.name }}"
        groups: devops
        append: true
        password: "{{ pw_developer | password_hash('sha512') }}"
      loop: "{{ users }}"
      when: item.job == "developer"
- name: managers
  hosts: prod
  become: true
  vars_files:
    - locker.yml
    - user_list.yml
  tasks:
    - name: opsmgr group
      ansible.builtin.group:
        name: opsmgr
        state: present
    - name: mgr users
      ansible.builtin.user:
        name: "{{ item.name }}"
        groups: opsmgr
        append: true
        password: "{{ pw_manager | password_hash('sha512') }}"
      loop: "{{ users }}"
      when: item.job == "manager"
```
> 외부 파일 변수명(`users`, `item.name/job`)은 `cat user_list.yml`로 확인.
</details>

---

## 18. `cron.yml` — natasha 2분마다

```yaml
---
- name: cron
  hosts: ___
  become: true
  tasks:
    - name: add cron
      ansible.builtin.____:
        name: add cron natasha
        minute: "______"             # 2분마다
        user: ____________           # natasha (빠지면 root로 감!)
        job: logger "EX294 in progress"
```
<details><summary>▶ 정답 보기</summary>

```yaml
---
- name: cron
  hosts: all
  become: true
  tasks:
    - name: add cron
      ansible.builtin.cron:
        name: add cron natasha
        minute: "*/2"
        user: natasha
        job: logger "EX294 in progress"
```
</details>

---

## ✅ 채운 뒤 검증 (결과가 채점 대상!)
```bash
# 공통
ansible-playbook <파일>.yml --syntax-check && ansible-playbook <파일>.yml
# 문제별
ansible all -m command -a "yum repolist"                 # 2
ansible dev -m command -a "rpm -q php mariadb"           # 4
ansible all -m command -a "chronyc sources"              # 5
ansible all -m command -a "sestatus"                     # 6
curl http://node3   ;  curl http://node3/hello.php        # 8·9
ansible all -m command -a "lvs"                          # 10
ansible dev -m command -a "cat /etc/myhosts"             # 11
ansible all -m command -a "cat /etc/issue"               # 12
curl http://node1/webdev/                                # 13
ansible all -m command -a "cat /root/hwreport.txt"       # 14
ansible dev -m command -a "id developer"                 # 16
ansible all -m command -a "crontab -u natasha -l"        # 18
```
> ⭐ 방화벽/마운트 문제는 **재부팅 후에도** 되는지가 진짜 채점 기준.
