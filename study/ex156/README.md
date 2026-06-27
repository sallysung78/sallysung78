# EX156 — Red Hat Certified Specialist in OpenShift Virtualization

EX156 (OpenShift Virtualization) 시험 준비 정리 폴더입니다.

## 📂 문서 구성

| 파일 | 내용 |
| --- | --- |
| [`00-cluster-access-and-cli.md`](./00-cluster-access-and-cli.md) | 클러스터 접속·상태 점검, kubectl CLI 설치, 토큰/웹 로그인(Lab1) |
| [`01-3day-plan.md`](./01-3day-plan.md) | 3일 합격 플랜 — VM 스토리지/네트워킹/관리 핵심 정리 + 치트시트 |

## 🎯 시험 개요

- **시험명**: Red Hat Certified Specialist in OpenShift Virtualization exam (EX156)
- **버전 기준**: OpenShift 4.18
- **출제 영역**: 가상 시스템(VM) 생성·관리·모니터링 / VM 네트워킹 / VM 스토리지 / 골든 이미지

## 📊 직전 시험 결과 & 전략

| 영역 | 점수 | 전략 |
| --- | --- | --- |
| VM 생성·관리 | **75%** | 유지·보강 (시간 20%) |
| VM 네트워킹 | **50%** | 보강 (시간 30%) |
| VM 스토리지 | **33%** | ⭐ **최우선 집중** (시간 50%) |

**핵심 한 줄**: 스토리지에서 `URL = import / gz = upload` 분기만 몸에 배면 합격선은 거의 확정.

## ✅ 시험 직전 체크리스트

- [ ] `oc login` (토큰/웹) 으로 접속, `oc get node/csr/co` 로 클러스터 상태 확인
- [ ] URL vs gz 분기 (import vs image-upload) 손으로 재현
- [ ] 골든 이미지: `virtctl guestfs` + `virt-sysprep`
- [ ] 스냅샷 → 변경 → 복원 (파일 존재로 검증)
- [ ] export download → image-upload 로 새 VM 복원
- [ ] 핫플러그 `--persist` (영속화)
- [ ] cloud-init 계정·SSH키·runcmd → 로그인 검증
- [ ] `virtctl expose` LoadBalancer → `curl`/`ssh` 검증
- [ ] storage class 지정 → `oc get pvc` Bound 검증
