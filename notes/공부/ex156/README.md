# 📘 EX156 (OpenShift Virtualization) 재시험 자료

> 재시험 마감: 6/30 · 약점: 스토리지 33% → 네트워킹 50% → VM관리 75%

## 파일 목록
- **[합격플랜-약점집중.md](합격플랜-약점집중.md)** ⭐ — 시험 직전 이거 하나만 보면 됨. 실제 출제 복기 + URL/gz 분기 + 스토리지/네트워킹 집중 + 3일 일정 + 치트시트
- [시험정보-상세정리.md](시험정보-상세정리.md) — 전 영역 상세 레퍼런스 (명령어·manifest 모음)
- [3일플랜-상세.md](3일플랜-상세.md) — 상세 3일 플랜 (전체 설명 버전)
- [클러스터접속-CLI설치-Lab1.md](클러스터접속-CLI설치-Lab1.md) — 시험 시작 직후 사전 준비: 클러스터 접속(토큰/웹 로그인), 상태 점검(node/csr/co), kubectl CLI 설치(체크섬), oc vs kubectl(Lab1)
- [5장-스토리지-개념정리.md](5장-스토리지-개념정리.md) 🔰 — 스토리지 약점(33%) 기초: SC/PVC/PV/DataVolume 비유로 이해, source 4종(URL/upload/clone/blank), 골든이미지, 콘솔 vs CLI 전략
- [5장-스토리지-Lab문제풀이.md](5장-스토리지-Lab문제풀이.md) 🧪 — 스토리지 Lab 7문제 풀이: 문제별 CLI/콘솔 + 외울 것 (봉인·복제·스냅샷·export·복원·핫플러그)
- [VM운영-Lab문제풀이.md](VM운영-Lab문제풀이.md) 🧪 — VM 운영 Lab 5문제: VM생성(instance type)·cloud-init(SSH키/서비스)·virtctl ssh·Metrics·리소스 증설

## 핵심 한 줄
스토리지 **"URL=import / gz=upload"** 분기만 몸에 배면 33% → 70%대 거의 확정.
