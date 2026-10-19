# RHOAI 제품 요청/공유 — MaaS · DB · Gateway LB (AI Product Engineering)

> **대상**: Red Hat AI Product Engineering 팀
> **작성 배경**: 한국 주요 금융 고객(은행) RHOAI 3.5 / OpenShift 4.22 도입·검토 과정에서 도출
> **요약**: 아래 3개 주제의 제품 요구/개선 사항을 공유하고 우선순위 검토를 요청드립니다.
> **최종 업데이트**: 2026-10-19

---

## 0. 한눈 요약

| # | 주제 (제안 타이틀) | 핵심 요청 | 성격 |
|---|---|---|---|
| 1 | **MaaS 기능 고도화 요구사항** | 금융 운영 수준의 키/쿼터/사용량·멀티테넌시 기능 강화 | 기능 요구 |
| 2 | **제품 내장 DB 통합 및 DB 엔진 단일화** | 다수 DB 엔진 혼재 해소, 단일 엔진 지향 + 번들 옵션 | 아키텍처 개선 |
| 3 | **MaaS Gateway LoadBalancer 구성 가이드** (MetalLB 미사용/미경험 고객용) | 공식 가이드 문서화 + ClusterIP 정식 지원(RFE) 우선순위 상향 | 문서화 + RFE |

---

## 1. MaaS 기능 고도화 요구사항

> **제안 타이틀**: "MaaS 기능 고도화 요구사항" *(원안 "MaaS 기능 요구" → 범위를 명확히 하기 위해 '고도화 요구사항'으로 제안)*

### 배경
- 금융 고객은 MaaS를 **사내 LLM API 게이트웨이**로 도입하려 하며, 운영·감사·과금 관점의 기능 성숙도를 중요하게 봄.
- RHOAI 3.5의 MaaS 멀티테넌시 컨트롤러는 현재 **Technology Preview** 상태로 확인됨 → GA화 요구.

### 세부 요청 항목 (후보 — 고객별 우선순위 확정 필요)
| 항목 | 내용 | 비고 |
|---|---|---|
| **API Key 라이프사이클** | 셀프서비스 발급·회수·로테이션, 만료 정책, 감사 로그 | Authorino 연계 |
| **쿼터/Rate Limit 세분화** | 테넌트·모델·사용자·시간대별 정책, 초과 시 동작 정의 | Limitador(Redis) |
| **사용량 측정/과금(Metering)** | 토큰·요청 수 집계, 테넌트별 리포트/내보내기 | 과금 연동 |
| **멀티테넌시 GA** | 테넌트 격리·온보딩 워크플로 정식 지원 | 현재 TP |
| **관측성(Observability)** | 토큰 사용량·지연·에러율 대시보드 기본 제공 | |
| **모델 카탈로그/온보딩** | 모델 등록→정책→노출까지 표준 워크플로 | |
| **폐쇄망(Disconnected) 지원** | 금융 폐쇄망에서 전 기능 동작 보장 | 금융 필수 |

### Product 팀에 드리는 질문
- 멀티테넌시 **GA 목표 버전/시점**은?
- Metering/과금은 제품 기본 기능인지, 외부 연동 전제인지?

---

## 2. 제품 내장 DB 통합 및 DB 엔진 단일화

> **제안 타이틀**: "제품 내장 DB 통합 및 DB 엔진 단일화" *(원안 "제품에 DB 통합 및 DB종류 단일화" → 동일 의미, 표현만 정리)*

### 현황 — DB 엔진이 여러 종류로 혼재
| 구성요소 | DB 엔진 |
|---|---|
| Model Registry | PostgreSQL |
| MaaS (API Key 관리) | PostgreSQL |
| Limitador (Rate Limit) | Redis |
| TrustyAI | MariaDB / MySQL |
| Pipelines | MariaDB |

### 문제점 (특히 금융/클라우드 환경)
- **운영 관리 포인트 증가**: 엔진이 많을수록 백업·패치·HA·보안심의 부담↑.
- **클라우드 관리형 서비스 매핑 복잡**: 각 엔진을 별도 관리형 서비스로 매핑해야 함.
- **MariaDB EOL 리스크**: Azure Database for MariaDB 서비스 종료(2025-09-19) → MySQL Flexible Server 등으로 대체 필요. 엔진 종속이 운영 리스크로 직결.

### 요청
1. **DB 엔진 단일화 지향** — 가능한 범위에서 **PostgreSQL 기준**으로 통합 (Redis 등 캐시성 저장소는 성격상 예외 검토).
2. **제품 내장(번들) DB 옵션 제공** — 외부 관리형 DB를 못/안 쓰는 환경을 위한 기본 내장 옵션.
3. **지원 DB/버전 매트릭스 명확화** — 구성요소별 지원 엔진·버전·관리형 서비스 매핑 가이드.

### Product 팀에 드리는 질문
- 구성요소별 DB 엔진을 **단일 엔진으로 수렴**하는 로드맵이 있는지?
- 각 DB의 **내장 제공 vs 외부 연동** 기본 전략은?

---

## 3. MaaS Gateway LoadBalancer 구성 가이드 (MetalLB 미사용/미경험 고객용)

> **제안 타이틀**: "MaaS Gateway LoadBalancer 구성 가이드 — MetalLB 미사용/미경험 고객용" *(원안 유지, 대상 명시)*

### 배경
- MaaS Gateway 기본 구성은 **LoadBalancer 서비스** → 온프렘은 **MetalLB** 필요.
- 다수 금융 고객이 **MetalLB 미경험/구성 제약**(예: 공유 IP 대역에 VM 배치로 BGP 곤란)으로 대안을 찾는 상황.
- 상세 분석: [`openshift-ai/maas-gateway-no-loadbalancer.md`](./maas-gateway-no-loadbalancer.md)

### 3가지 구성 요약
| | Gateway 서비스 | pending | 지원 여부 |
|---|---|---|---|
| **① MetalLB (BGP/L2)** | LoadBalancer | 없음 | ✅ **공식 가이드·기본 지원** |
| **② 우리은행 현재** (L4→Router→Route) | ClusterIP (gw-options 수동) | 없음 | ⚠️ 우회 방법 (공식 가이드 아님) → Support 확인 |
| **③ RFE 후** | ClusterIP (네이티브) | 없음 | ✅ 정식 지원 (추진 중) |

### 요청
1. **공식 가이드 문서화** — "LoadBalancer(MetalLB)를 쓸 수 없는 환경"을 위한 **지원되는 구성 절차**를 공식 문서로 제공.
   - 현재 공식 문서는 "LB 없으면 OpenShift Route 사용"만 명시 → pending 처리, Route 수동/자동 여부 등 **구체 절차·지원 범위가 불명확**.
2. **ClusterIP 정식 지원 ([RFE OCPSTRAT-3781](https://issues.redhat.com/browse/OCPSTRAT-3781)) 우선순위 상향** — 이 RFE의 목적은 **MetalLB를 쓸 수 없는 고객의 우회 방법(ClusterIP 전환)을 제품 기본 기능으로 끌어올려 정식 지원되게** 하는 것. 다수 금융 고객이 대기 중 → GA 목표 시점 공유 요청.
3. **MetalLB L2 모드 가이드 보강** — BGP가 어려운 고객을 위한 L2(ARP) 모드 구성 가이드.

### Product 팀에 드리는 질문
- 베어메탈에서 **LB pending 상태 + Route 노출**이 **정식 지원 구성**인지 공식 입장은?
- RFE OCPSTRAT-3781의 **GA 목표 버전/시점**은? (현재 ~OCP 5.1로 파악)

---

## 4. 추가 제안 (Field → Product)

| 제안 | 내용 | 기대효과 |
|---|---|---|
| **A. 금융 온프렘 레퍼런스 아키텍처** | MaaS + DB + Gateway(LB/Route) 표준 구성 레퍼런스 | 반복 수주 시 설계 시간 단축, 심의 근거 |
| **B. Confidential Computing 연계 (Confidential AI)** | 민감데이터 위 추론을 TEE로 보호 (CoCo + Trustee) | 금융 규제 내 AI 도입 명분, 차별화. GPU TEE는 TP → 로드맵 |
| **C. 한국 금융 규제 매핑 문서** | 전자금융감독규정·망분리 완화·개인정보/신용정보법 ↔ 제품 기능 매핑 | 보안심의 대응 자료 |
| **D. 설치 자동화 연계** | 온프렘/클라우드 설치 스크립트에 위 구성 반영 | PoC·배포 가속 |

---

## 5. 요청 정리 (Product 팀 액션)

1. **MaaS**: 멀티테넌시 GA 시점 + Metering/과금 전략 공유
2. **DB**: 엔진 단일화 로드맵 + 내장/외부 전략 공유
3. **Gateway LB**: 무(無)LoadBalancer 환경 **지원 구성 공식화** + RFE OCPSTRAT-3781 **우선순위/시점** 공유

---

## 참고 자료
- RHOAI 3.5 MaaS 공식 문서: https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/html/govern_llm_access_with_models-as-a-service/deploy-and-manage-models-as-a-service
- opendatahub-io/models-as-a-service Issue #331: https://github.com/opendatahub-io/models-as-a-service/issues/331
- RFE: OCPSTRAT-3781 — https://issues.redhat.com/browse/OCPSTRAT-3781
- 내부 분석: `openshift-ai/maas-gateway-no-loadbalancer.md`
- Red Hat Support Case: 07767086
