# 📗 EX294 (RHCE - Ansible) 시험 준비

> 기반: 구글 슬라이드 공부노트 ([원본](https://docs.google.com/presentation/d/1NJUD3s0FF6vP7wa4S-ze8WrRtt5ZfuLIQkYHYalS5BA/edit))
> 참고 풀이: aingface.tistory.com/103
> 여기 정리된 문제들이 **기출문제** 기준

## 📂 파일 구성 (요청한 4분류)

1. **[01-개념.md](01-개념.md)** — 시험 전체를 관통하는 핵심 개념 (인벤토리·플레이북 뼈대·facts·롤·vault·block/rescue·when 등)
2. **[02-외워야할-명령어.md](02-외워야할-명령어.md)** — 무조건 손에 익혀야 하는 명령어 (설치·galaxy·vault·검증)
3. **[03-모듈과-역할.md](03-모듈과-역할.md)** — 외워야 할 모듈 + 시스템 역할(role) + 기출 18문제 매핑
4. **[04-시험중-참고-리스트.md](04-시험중-참고-리스트.md)** — `ansible-doc`·`setup`(facts) 등 시험장에서 **찾아 쓰는** 것들

## 🧪 문제별 상세 풀이 ([문제풀이/](문제풀이/))

각 기출문제를 **개념 → 문제 → 빈칸(외울것) → 명령어 → 모듈 → 검색법 → 확인법** 7단계로 정리.

- [문제 1. Ansible 설치 및 초기 설정](문제풀이/01-Ansible설치-초기설정.md)
- [문제 2. YUM Repository 연결](문제풀이/02-YUM-Repository연결.md)

## 🎯 핵심 전략 (슬라이드 정리)

> 문제를 보면 **"완성 YAML"을 외우려 하지 말고**, 먼저 **"어떤 module/role 문서를 열지"** 를 잡는다.
> `ansible-doc` 은 시험장의 검색 엔진. 변수명은 README에서 찾는다.

| 단계 | 행동 |
|---|---|
| 1 | 문제 키워드 → 모듈명/역할명 떠올리기 |
| 2 | `ansible-doc <module>` 또는 role `README.md` 열기 |
| 3 | EXAMPLE 복사 → 문제 요구 값만 수정 |
| 4 | `ansible-playbook <file>.yml --syntax-check` → 실행 → `ansible all -m command -a` 검증 |
