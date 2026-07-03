# 📗 EX294 (RHCE - Ansible) 시험 준비

> 기반: 구글 슬라이드 공부노트 ([원본](https://docs.google.com/presentation/d/1NJUD3s0FF6vP7wa4S-ze8WrRtt5ZfuLIQkYHYalS5BA/edit))
> 참고 풀이: aingface.tistory.com/103
> 여기 정리된 문제들이 **기출문제** 기준

## 📂 파일 구성 (요청한 4분류)

1. **[01-개념.md](01-개념.md)** — 시험 전체를 관통하는 핵심 개념 (인벤토리·플레이북 뼈대·facts·롤·vault·block/rescue·when 등)
2. **[02-외워야할-명령어.md](02-외워야할-명령어.md)** — 무조건 손에 익혀야 하는 명령어 (설치·galaxy·vault·검증)
3. **[03-모듈과-역할.md](03-모듈과-역할.md)** — 외워야 할 모듈 + 시스템 역할(role) + 기출 18문제 매핑
4. **[04-시험중-참고-리스트.md](04-시험중-참고-리스트.md)** — `ansible-doc`·`setup`(facts) 등 시험장에서 **찾아 쓰는** 것들

## ⭐ [핵심문제.md](핵심문제.md) — 약점 집중 암기 (시험 직전 필독)
> 지난번 시간 오래 걸린 5곳(7 Galaxy설치 · 8 j2변수 · 10 볼륨msg · 11 호스트파일 · 14 vda/vdb)만 압축.

## 🧪 문제별 상세 풀이 ([문제풀이/](문제풀이/))

각 기출문제를 **개념 → 문제 → 빈칸(외울것) → 명령어 → 모듈 → 검색법 → 확인법** 7단계로 정리.

| # | 문제 | 핵심 | 취약분야 |
|:--:|------|------|:--:|
| 1 | [Ansible 설치·초기설정](문제풀이/01-Ansible설치-초기설정.md) | inventory, ansible.cfg | |
| 2 | [YUM Repository 연결](문제풀이/02-YUM-Repository연결.md) | yum_repository | |
| 3 | [콜렉션 설치](문제풀이/03-콜렉션설치.md) | galaxy collection install | |
| 4 | [패키지 설치](문제풀이/04-패키지설치.md) | yum (list/@/*) | |
| 5 | [RHEL 역할-timesync](문제풀이/05-RHEL시스템역할-timesync.md) | System Role (vars) | 🟠 롤 |
| 6 | [SELinux 역할](문제풀이/06-SELinux역할.md) | System Role (vars) | 🟠 롤 |
| 7 | [Galaxy 역할 설치](문제풀이/07-Galaxy역할설치-requirements.md) | requirements.yml + install -r | 🟠 롤 |
| 8 | [역할 생성-apache](문제풀이/08-역할생성-apache.md) | init + yum/service/firewalld/template | 🟠 롤 |
| 9 | [Galaxy 역할 사용](문제풀이/09-Galaxy역할사용-balancer-phpinfo.md) | roles: 호출 | 🟠 롤 |
| 10 | [논리 볼륨 생성](문제풀이/10-논리볼륨생성-block-rescue.md) | lvol + block/rescue | |
| 11 | [호스트 파일 생성](문제풀이/11-호스트파일생성-template.md) | template + facts | 🔴 콘텐츠 |
| 12 | [파일 내용 수정](문제풀이/12-파일내용수정-issue.md) | copy content + when | |
| 13 | [웹 컨텐츠 디렉터리](문제풀이/13-웹컨텐츠디렉터리생성-file.md) | file (link/mode/setype) | |
| 14 | [하드웨어 보고서](문제풀이/14-하드웨어보고서생성.md) | get_url+lineinfile+facts | 🔴 콘텐츠 |
| 15 | [암호 자격증명 모음 생성](문제풀이/15-암호자격증명모음생성.md) | ansible-vault encrypt | 🔴 콘텐츠 |
| 16 | [사용자 계정 생성](문제풀이/16-사용자계정생성.md) | user+group+password_hash+vault | 🔴 콘텐츠 |
| 17 | [Vault 키 재입력](문제풀이/17-Vault키재입력-rekey.md) | ansible-vault rekey | 🔴 콘텐츠 |
| 18 | [cron 설정](문제풀이/18-cron설정.md) | cron | |

> 🔴 콘텐츠(Manage content, 지난시험 33% 최약점) · 🟠 롤(Roles & Collections, 39%) 우선 반복 권장

## 🎯 핵심 전략 (슬라이드 정리)

> 문제를 보면 **"완성 YAML"을 외우려 하지 말고**, 먼저 **"어떤 module/role 문서를 열지"** 를 잡는다.
> `ansible-doc` 은 시험장의 검색 엔진. 변수명은 README에서 찾는다.

| 단계 | 행동 |
|---|---|
| 1 | 문제 키워드 → 모듈명/역할명 떠올리기 |
| 2 | `ansible-doc <module>` 또는 role `README.md` 열기 |
| 3 | EXAMPLE 복사 → 문제 요구 값만 수정 |
| 4 | `ansible-playbook <file>.yml --syntax-check` → 실행 → `ansible all -m command -a` 검증 |
