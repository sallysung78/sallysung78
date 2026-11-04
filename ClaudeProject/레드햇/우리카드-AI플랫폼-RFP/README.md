# 우리카드 AI 플랫폼 RFP — Day1 / Day2 요건 정리 및 Red Hat 지원 범위

> **대상**: 우리카드 AI 플랫폼(Kubernetes 기반 GPU 통합·MLOps) 제안요청사항 **41건**  
> **원본**: [우리카드_AI_플랫폼_요구사항_지원분석_v0_4](https://docs.google.com/spreadsheets/d/1HdjXSlA_d3ECMl-INQWbLe_lg_grl6z85R5Lko9mdtk/edit) (2026-10-29), [AI_플랫폼_요구사항_검토_Red_Hat_AI_기능_비교](https://docs.google.com/spreadsheets/d/1MoZ5Qk-yEzmBHkxVWCH_rcHNXPMk7UTSGEHVAis0k9c/edit) (2026-10-21)  
> **판단 기준 버전**: OpenShift 4.22 · OpenShift AI 3.5 — 제안 버전 확정 시 GA/TP 상태 재확인  
> **엑셀**: [`우리카드_AI플랫폼_Day1-Day2_요건매트릭스.xlsx`](./우리카드_AI플랫폼_Day1-Day2_요건매트릭스.xlsx) — 필터 가능한 전체 매트릭스(원문·Day1·Day2·구성요소·확인사항)  
> **작성일**: 2026-11-04

---

## 0. 한눈 요약

### 단계 × 제공 영역 (건수)

| 단계 | 🐳 컨테이너 플랫폼<br>(OpenShift) | 🧠 AI<br>(OpenShift AI) | 🔗 공통 | 합계 |
|---|:-:|:-:|:-:|:-:|
| **Day1** | 5 | 9 | 2 | **16** |
| **Day1→Day2** | 5 | 14 | 0 | **19** |
| **Day2** | 2 | 0 | 4 | **6** |
| **합계** | **12** | **23** | **6** | **41** |

### Red Hat 지원 수준 (건수)

| ● 제품 기능으로 충족 | ◐ 제품 기능 + 보완 | ○ 제품 범위 외 | ◇ 서비스 |
|:-:|:-:|:-:|:-:|
| **17** | **18** | **2** | **4** |

### 핵심 메시지

1. **AI 요건이 23건으로 과반**이지만, 그중 **14건은 Day1→Day2**입니다. OpenShift AI가 기능(학습·평가·Registry·서빙·MaaS)은 제공하고, 고객 정책·데이터 반영(업무 평가지표, 승격 게이트, 이력 자동화, MaaS 정책)은 Day2 개발·컨설팅입니다. → 제안서에 **"Day1 = 제품 기능 구성·샘플 1건 검증 / Day2 = 정책 반영·개발"**을 명시해 범위 분쟁을 막습니다.
2. **Day1 단독 16건 중 15건은 제품 기능(●)만으로 충족**됩니다. GPU 인프라(MIG·스케줄링·DCGM)와 추론(vLLM·API·Continuous Batching)이 중심이며, 나머지 1건(R29 부하분산·장애 격리)은 GPU 1노드 제약으로 ◐입니다.
3. **컨테이너 플랫폼 영역은 Day1 인프라 결정이 전체를 좌우합니다.** 서버 4대로는 개발/운영 2클러스터가 불가(R35)하고, 운영 GPU 1노드라 GPU HA가 없습니다(R29). 제안 전 토폴로지 합의가 1순위입니다.
4. **제품 범위 외(○) 2건** — 기존 AI 서비스 이전(R33), PCMS 연동(R41)은 SI 개발·마이그레이션 범위로 분리합니다.
5. **별도 구독 확인**: MaaS 정책용 **Red Hat Connectivity Link**, 데이터셋·모델용 **S3 스토리지(ODF 또는 고객 보유)**, 보안·SBOM용 RHACS·Quay·Trusted Profile Analyzer(선택).

---

## 1. 분류 기준

### 1-1. Day1 / Day2

기존 v0.4 시트의 **"1단계(예제제공) / 2단계(정책반영)"** 및 **"1차 / 2차"** 구분을 Day1/Day2로 매핑했습니다.

| 단계 | 의미 |
|---|---|
| **Day1** | 구축(1차) 시점에 제품 기능 구성·예제 검증으로 요건 충족. 이후는 일상 운영만 필요 |
| **Day1→Day2** | Day1에 제품 기반·예제 구성, Day2에 고객 정책·데이터 반영 및 개발·연동으로 완성 |
| **Day2** | 운영 데이터·프로세스·유지관리 성격. Day1에는 준비(분석·예제·기준 합의)만 수행 |

### 1-2. AI vs 컨테이너 플랫폼 구분 원칙

| 영역 | 제공 제품 | 판단 기준 |
|---|---|---|
| 🐳 컨테이너 플랫폼 | Red Hat OpenShift (OCP) | 클러스터·GPU 인프라 활성화·네트워크·보안·인증·모니터링 기반·CI/CD·라이프사이클 — AI가 없어도 필요한 플랫폼 기능 |
| 🧠 AI | Red Hat OpenShift AI (RHOAI) | 데이터셋→학습→평가→등록→서빙→API(MaaS)까지 모델 라이프사이클과 AI 특화 자원 추상화(Hardware Profile)·AI 지표 |
| 🔗 공통 | OpenShift + OpenShift AI | 두 제품이 함께 맞물려야 성립 (GPU Pool·스케줄링, 운영 프로세스, 라이프사이클 관리) |

계층으로 보면 아래와 같습니다. 위로 갈수록 OpenShift AI, 아래로 갈수록 OpenShift가 담당합니다.

| 계층 | 제공 | 주요 구성요소 | 관련 요건 |
|---|---|---|---|
| AI 서비스 접점 (API·Gateway) | 🧠 OpenShift AI | MaaS(API Key·Rate/Token Limit), OpenAI 호환 API | R22, R24–R26, R28 |
| 모델 라이프사이클 (MLOps) | 🧠 OpenShift AI | Workbench, Data Science Pipelines, Training Hub·Kubeflow Trainer, TrustyAI LM-Eval, Model Registry, KServe·vLLM·llm-d | R06–R08, R10–R21, R23, R32 |
| AI 자원 추상화 | 🔗 공통 | Hardware Profile(AI) + Red Hat build of Kueue·ResourceQuota(OpenShift) | R02, R05, R15 |
| GPU 인프라 | 🐳 OpenShift + NVIDIA | NVIDIA GPU Operator(MIG·DCGM), Node Feature Discovery | R02, R04, R31 |
| 컨테이너 플랫폼 | 🐳 OpenShift | 클러스터(폐쇄망), Project·RBAC·NetworkPolicy, OAuth/IdP, Monitoring·Logging, GitOps·Pipelines, Gateway API·MetalLB | R01, R27, R29–R30, R33–R36, R41 |
| 별도 구독·타사·SI | — | RHCL, ODF/S3, RHACS·Quay·TPA, 고객 IdP·SIEM·DLP·PCMS | R24, R27, R36, R40, R41 |

### 1-3. 지원 수준

| 표시 | 의미 | 설명 |
|:-:|---|---|
| ● | 제품 기능으로 충족 | Red Hat 제품을 구성·설정하면 요건 충족 |
| ◐ | 제품 기능 + 보완 | 제품이 핵심 기능을 제공하고, 컨설팅·개발·연동으로 보완 |
| ○ | 제품 범위 외 | 개발·연동·마이그레이션(SI/고객) 중심, Red Hat은 실행 기반만 제공 |
| ◇ | 서비스 | 교육·컨설팅·기술지원(구독)으로 제공 |

---

## 2. 한 장 요약 — 단계 × 영역 매트릭스

| 단계 | 🐳 컨테이너 플랫폼 (OpenShift) | 🧠 AI (OpenShift AI) | 🔗 공통 |
|---|---|---|---|
| **Day1** | ● R01 컨테이너 실행환경 구축·개발/운영 분리<br>● R04 MIG 기반 GPU 분할·격리<br>◐ R29 부하분산·장애 격리<br>● R31 GPU 상태·성능 지표<br>● R35 4노드 GPU 클러스터 구축 | ● R07 학습/운영 환경 논리 분할<br>● R10 외부 Base Model 등록·관리<br>● R12 SFT 수행<br>● R14 학습 파라미터 설정<br>● R15 학습 Job별 GPU 지정·정책 할당<br>● R20 승인 모델 추론 배포<br>● R21 vLLM 기반 추론 서비스<br>● R22 표준 API 호출<br>● R23 Continuous Batching 동시 처리 | ● R02 공용 GPU Pool 통합관리<br>● R05 GPU 요청·할당·회수 스케줄링 |
| **Day1→Day2** | ◐ R27 보안정책·감사로그 통합<br>◐ R30 통합 모니터링<br>● R34 SSO·2차 인증<br>◐ R36 데이터 유출 방지 확장 구조<br>◇ R37 운영자 기술이전·교육 | ◐ R06 데이터셋→학습→평가→등록 표준화<br>◐ R08 검증 모델 배포·서비스 연계<br>◐ R11 모델 버전·학습·성능·배포 이력<br>◐ R13 LoRA/QLoRA(PEFT)<br>◐ R16 평가 데이터셋 등록·버전관리<br>● R17 평가 데이터셋 기반 평가 수행<br>◐ R18 정량 메트릭(정확성·관련성)<br>◐ R19 평가 통과 모델 서빙 전환<br>◐ R24 단일 AI API Gateway<br>◐ R25 등록·배포·버전·라우팅 통합관리<br>◐ R26 API 인증·인가·접근통제<br>◐ R28 호출량·동시 요청 제어<br>◐ R32 AI 서비스 TPS·TTFT·Latency<br>◇ R38 내부 개발자 AI 플랫폼 교육 | — |
| **Day2** | ○ R33 기존 AI 서비스 3종 이전<br>○ R41 PCMS 변경관리 연계 | — | ◐ R03 사용률 기반 GPU 할당 기준<br>◇ R09 공통 운영 프로세스(배포·변경·장애)<br>◇ R39 오픈소스 최신성<br>◐ R40 OSS 자산·취약점·EOL 관리 |

---

## 3. Day1 요건 — 구축 (1차)

Day1 단독 16건 + Day1→Day2 19건의 Day1 범위입니다. (Day2 단독 항목의 Day1 준비 작업은 엑셀 참조)

### 3-1. 🐳 컨테이너 플랫폼 — OpenShift로 제공 (10건)

| ID | 요건 | 단계 | Day1 제공 내용 | Red Hat 구성요소 | 지원 |
|---|---|---|---|---|:-:|
| R01 | 컨테이너 실행환경 구축·개발/운영 분리 | Day1 | 폐쇄망 OpenShift 설치, 개발/운영 분리 방식(물리 클러스터 vs 논리 분리) 설계, Project·RBAC·NetworkPolicy·ResourceQuota 기본 구성 | OpenShift(Project·RBAC·NetworkPolicy·ResourceQuota), oc-mirror(폐쇄망 미러링)<br>↔ AI 연계: Data Science Project로 AI 작업 공간 분리(보조) | ● |
| R04 | MIG 기반 GPU 분할·격리 | Day1 | MIG 전략(single/mixed)·프로파일 설계 및 적용, MIG 리소스를 Hardware Profile로 노출 | NVIDIA GPU Operator(MIG Manager), 노드 label 기반 MIG 구성<br>↔ AI 연계: Hardware Profile에 MIG 리소스(nvidia.com/mig-*) 매핑<br>＋ 별도·타사: NVIDIA GPU Operator(기술지원 주체 NVIDIA) | ● |
| R27 | 보안정책·감사로그 통합 | Day1→Day2 | RBAC·NetworkPolicy·Gateway 정책 기본 구성, 감사로그 항목·조회 방법 정리, 로그 포워딩 기본 구성 | API 감사로그, OpenShift Logging(LokiStack·로그 포워딩), RBAC, NetworkPolicy<br>↔ AI 연계: MaaS·Gateway 호출 로그<br>＋ 별도·타사: RHACS(보안정책 통합, 별도 구독), 고객 SIEM | ◐ |
| R29 | 부하분산·장애 격리 | Day1 | Service·Gateway 부하분산, 복제본·Health Probe·PDB, 프로젝트 격리, HA 설계 | Service·Route·Gateway, Deployment 복제본, Probe, PodDisruptionBudget<br>↔ AI 연계: KServe 복제본·오토스케일링 | ◐ |
| R30 | 통합 모니터링 | Day1→Day2 | OpenShift 기본 모니터링 + 사용자 워크로드 모니터링 활성화, 대시보드 예제 | OpenShift Monitoring(Prometheus·Alertmanager·Thanos), 콘솔 대시보드, Cluster Observability Operator<br>↔ AI 연계: 모델 서빙 메트릭<br>＋ 별도·타사: Grafana(커뮤니티 오퍼레이터 — Red Hat 지원 대상 아님) | ◐ |
| R31 | GPU 상태·성능 지표 | Day1 | DCGM Exporter 지표 수집, OpenShift 콘솔(Observe) GPU 대시보드 구성 | NVIDIA GPU Operator DCGM Exporter, OpenShift Monitoring<br>＋ 별도·타사: NVIDIA GPU Operator(기술지원 주체 NVIDIA) | ● |
| R34 | SSO·2차 인증 | Day1→Day2 | OpenShift OAuth–사내 IdP(OIDC·LDAP) 연동 → 콘솔·OpenShift AI 대시보드 SSO | OpenShift OAuth(IdP 연동), Red Hat build of Keycloak(IdP 브로커 필요 시)<br>↔ AI 연계: OpenShift AI 대시보드(OpenShift 인증 연동)<br>＋ 별도·타사: 고객 IdP(MFA 기능) | ● |
| R35 | 4노드 GPU 클러스터 구축 | Day1 | 폐쇄망 OpenShift 설치·GPU 노드 구성, Control Plane 배치 재설계 | OpenShift 설치(폐쇄망), NVIDIA GPU Operator | ● |
| R36 | 데이터 유출 방지 확장 구조 | Day1→Day2 | NetworkPolicy·Egress 통제(EgressFirewall·Egress IP) 기본 구성, 폐쇄망 구조 설계 | NetworkPolicy, AdminNetworkPolicy, EgressFirewall, Egress IP<br>↔ AI 연계: TrustyAI Guardrails(PII 탐지·마스킹)<br>＋ 별도·타사: DLP·망연계 솔루션 | ◐ |
| R37 | 운영자 기술이전·교육 | Day1→Day2 | 구축 완료 시 구축·운영·장애대응·배포 교육 및 인수인계(교재·실습·산출물) | Red Hat Training(DO180·DO280 등 OpenShift 운영 과정)<br>↔ AI 연계: AI 서비스 배포 실습<br>＋ 별도·타사: Red Hat Consulting 기술이전 | ◇ |

### 3-2. 🧠 AI — OpenShift AI로 제공 (23건)

| ID | 요건 | 단계 | Day1 제공 내용 | Red Hat 구성요소 | 지원 |
|---|---|---|---|---|:-:|
| R06 | 데이터셋→학습→평가→등록 표준화 | Day1→Day2 | 샘플 모델 1건으로 데이터셋 저장·학습·평가·등록 E2E 파이프라인 예제 + 표준 절차서 | Data Science Pipelines, Connections(S3), Training Hub·Kubeflow Trainer, TrustyAI LM-Eval, Model Registry<br>↔ OpenShift 기반: OpenShift Pipelines·GitOps(배포 자동화 연계 시)<br>＋ 별도·타사: S3 호환 오브젝트 스토리지(고객 보유 또는 ODF 별도 구독) | ◐ |
| R07 | 학습/운영 환경 논리 분할 | Day1 | 학습·운영 프로젝트 각 1개 구성 — 권한·자원 한도·스토리지·접속정보 분리, 기본 NetworkPolicy, 동작 검증 | Data Science Project, 프로젝트별 Hardware Profile·Connection 분리<br>↔ OpenShift 기반: Namespace·RBAC·ResourceQuota·NetworkPolicy | ● |
| R08 | 검증 모델 배포·서비스 연계 | Day1→Day2 | Red Hat 검증 모델 1건 추론 배포, API 호출 검증, 배포·연계 절차 문서화 | Model Registry → KServe 배포, Red Hat AI 검증 모델(ModelCar)<br>↔ OpenShift 기반: OpenShift GitOps·Pipelines(배포 자동화)<br>＋ 별도·타사: 업무 서비스 연계·승인 체계 개발 | ◐ |
| R10 | 외부 Base Model 등록·관리 | Day1 | Model Registry 구성, 외부 모델 등록(버전·메타정보·접근권한), 폐쇄망 모델 반입 절차 설계 | Model Registry, Model Catalog, ModelCar(OCI 이미지) 또는 S3 저장<br>↔ OpenShift 기반: 내부 미러 레지스트리(oc-mirror)<br>＋ 별도·타사: 가중치 저장소(S3·레지스트리), Registry DB | ● |
| R11 | 모델 버전·학습·성능·배포 이력 | Day1→Day2 | Registry 버전·메타정보·배포 연계 예제 | Model Registry(custom properties), 실험 추적(MLflow)<br>＋ 별도·타사: 이력 자동 기록 코드 개발 | ◐ |
| R12 | SFT 수행 | Day1 | Training Hub·Kubeflow Trainer로 SFT 실행 방법 및 예제 노트북 제공 | Training Hub, Kubeflow Trainer, Workbench, Kueue 연동 | ● |
| R13 | LoRA/QLoRA(PEFT) | Day1→Day2 | LoRA/QLoRA 학습 예제 제공 | Training Hub(LoRA/QLoRA), vLLM LoRA 어댑터 서빙 | ◐ |
| R14 | 학습 파라미터 설정 | Day1 | 노트북·SDK 파라미터로 배치 크기·최대 입력 길이·학습률·Epoch 지정 | Training Hub·Kubeflow Trainer SDK | ● |
| R15 | 학습 Job별 GPU 지정·정책 할당 | Day1 | Trainer 자원 요청 + Hardware Profile + Kueue ResourceFlavor(GPU 종류별)·Quota 정책 구성 | Kubeflow Trainer, Hardware Profile<br>↔ OpenShift 기반: Red Hat build of Kueue, 노드 선택 조건 | ● |
| R16 | 평가 데이터셋 등록·버전관리 | Day1→Day2 | 학습·평가 버킷 분리, Connection 등록, 폴더 기반 버전 규칙 예제 | Connections(S3)<br>＋ 별도·타사: S3 버전관리 기능, 카탈로그 화면 개발 | ◐ |
| R17 | 평가 데이터셋 기반 평가 수행 | Day1→Day2 | TrustyAI LM-Eval로 샘플 데이터셋 평가 실행(Workbench·Pipeline) | TrustyAI LM-Eval, EvalHub, Data Science Pipelines | ● |
| R18 | 정량 메트릭(정확성·관련성) | Day1→Day2 | 표준 벤치마크 메트릭 평가 예제 | TrustyAI LM-Eval(표준 메트릭)<br>＋ 별도·타사: 업무 지표 정의·평가 로직 개발 | ◐ |
| R19 | 평가 통과 모델 서빙 전환 | Day1→Day2 | 평가 결과를 Registry 속성에 기록 → 서빙 배포 예제 | Model Registry, KServe, Data Science Pipelines<br>↔ OpenShift 기반: OpenShift GitOps·Pipelines<br>＋ 별도·타사: 승격 게이트 개발 | ◐ |
| R20 | 승인 모델 추론 배포 | Day1 | Registry 등록 모델 → 추론환경 배포 | Model Registry → KServe 배포 | ● |
| R21 | vLLM 기반 추론 서비스 | Day1 | KServe + vLLM 런타임 구성, 모델 배포 | KServe, vLLM(Red Hat AI Inference Server), llm-d | ● |
| R22 | 표준 API 호출 | Day1 | OpenAI 호환 API 엔드포인트 제공·호출 검증 | vLLM OpenAI 호환 API, KServe 엔드포인트<br>↔ OpenShift 기반: Route·Gateway 노출 | ● |
| R23 | Continuous Batching 동시 처리 | Day1 | vLLM continuous batching 기본 제공 | vLLM, KServe 오토스케일링 | ● |
| R24 | 단일 AI API Gateway | Day1→Day2 | Gateway API + MaaS 구성, 대표 LLM 공통 진입점 제공 | Models-as-a-Service(MaaS)<br>↔ OpenShift 기반: Gateway API, MetalLB(LoadBalancer)<br>＋ 별도·타사: Red Hat Connectivity Link(RHCL) — 구독 범위 확인 / 비 LLM 통합 시 기존·별도 API GW | ◐ |
| R25 | 등록·배포·버전·라우팅 통합관리 | Day1→Day2 | 대표 모델 등록(Registry)→배포(Serving)→Gateway 연결을 제품 화면·설정으로 수행 | Model Registry, Model Serving, MaaS<br>＋ 별도·타사: 통합 관리 화면 연동 개발 | ◐ |
| R26 | API 인증·인가·접근통제 | Day1→Day2 | MaaS API Key·인가 정책으로 대표 모델 허용/거부 정책 적용·검증 | MaaS(API Key·티어 정책), 모델 엔드포인트 토큰 인증<br>↔ OpenShift 기반: OpenShift OAuth·RBAC<br>＋ 별도·타사: RHCL(AuthPolicy·Authorino) | ◐ |
| R28 | 호출량·동시 요청 제어 | Day1→Day2 | 대표 모델 요청·토큰 사용량 제한 + vLLM 동시성 설정, 초과 동작 확인 | MaaS Rate·Token Limit, vLLM 동시 처리 설정<br>＋ 별도·타사: RHCL(Limitador) | ◐ |
| R32 | AI 서비스 TPS·TTFT·Latency | Day1→Day2 | vLLM 지표(TTFT·토큰 처리량·지연) 대시보드 구성 | vLLM 메트릭, OpenShift AI 모델 메트릭<br>↔ OpenShift 기반: 사용자 워크로드 모니터링<br>＋ 별도·타사: 비 LLM 앱 계측 개발 | ◐ |
| R38 | 내부 개발자 AI 플랫폼 교육 | Day1→Day2 | AI267 등 OpenShift AI 공식 교육 | Red Hat Training AI267<br>＋ 별도·타사: 워크숍은 컨설팅 범위 | ◇ |

### 3-3. 🔗 공통 — OpenShift + OpenShift AI로 제공 (2건)

| ID | 요건 | 단계 | Day1 제공 내용 | Red Hat 구성요소 | 지원 |
|---|---|---|---|---|:-:|
| R02 | 공용 GPU Pool 통합관리 | Day1 | GPU Operator·NFD 설치, GPU 노드 Pool(label/taint) 구성, Hardware Profile 정의, 프로젝트별 GPU 사용 한도(Quota) 설정 | **OpenShift**: NVIDIA GPU Operator, Node Feature Discovery, ResourceQuota, Red Hat build of Kueue(ClusterQueue)<br>**OpenShift AI**: Hardware Profile(GPU 유형·수량 프리셋), 프로젝트별 프로파일 노출<br>＋ 별도·타사: NVIDIA GPU Operator(NVIDIA 인증 오퍼레이터, 기술지원 주체 NVIDIA) | ● |
| R05 | GPU 요청·할당·회수 스케줄링 | Day1 | Kueue(ClusterQueue·LocalQueue·ResourceFlavor) 구성, 작업 종료·정지 시 GPU 반환 검증 | **OpenShift**: Red Hat build of Kueue, OpenShift 스케줄러(nodeSelector·taint·toleration)<br>**OpenShift AI**: Hardware Profile, 워크벤치 정지 시 자원 반환, 분산 워크로드 Kueue 연동 | ● |

---

## 4. Day2 요건 — 운영·고도화 (2차)

Day1→Day2 19건 + Day2 단독 6건입니다. Day1 단독 16건은 Day2에 일상 운영(정책 조정·업그레이드)만 필요합니다(엑셀 'Day2' 열 참조).

### 4-1. 🐳 컨테이너 플랫폼 — OpenShift (7건)

| ID | 요건 | 단계 | Day2 수행 내용 | 수행 주체 | 지원 |
|---|---|---|---|---|:-:|
| R27 | 보안정책·감사로그 통합 | Day1→Day2 | SIEM·기존 로그 수집계 연동, 통합 관리 화면 개발 | SI/고객 연동 | ◐ |
| R30 | 통합 모니터링 | Day1→Day2 | 통합 화면·알림 체계 구성, 기존 관제 시스템 연동 | SI/고객 연동 + Red Hat 컨설팅 | ◐ |
| R33 | 기존 AI 서비스 3종 이전 | Day2 | 3개 서비스 실제 이전(컨테이너화·API 이전·테스트) | SI 마이그레이션·테스트 | ○ |
| R34 | SSO·2차 인증 | Day1→Day2 | IdP 기반 MFA 강제, 자체 포털 적용 | 고객 IdP + SI(자체 포털) | ● |
| R36 | 데이터 유출 방지 확장 구조 | Day1→Day2 | DLP·반출/마스킹 정책, 망연계 설계, LLM 입출력 Guardrails 적용 | 고객 보안정책 + SI 연동 | ◐ |
| R37 | 운영자 기술이전·교육 | Day1→Day2 | 운영 중 심화 교육, 기술 내재화 지원 | Red Hat Training·Consulting | ◇ |
| R41 | PCMS 변경관리 연계 | Day2 | PCMS 연동 개발(승인 후 배포 강제) | SI 개발·연동 | ○ |

### 4-2. 🧠 AI — OpenShift AI (14건)

| ID | 요건 | 단계 | Day2 수행 내용 | 수행 주체 | 지원 |
|---|---|---|---|---|:-:|
| R06 | 데이터셋→학습→평가→등록 표준화 | Day1→Day2 | 고객 데이터 처리 컴포넌트·표준 파이프라인 템플릿 개발, 서비스별 확대 적용 | SI/고객 개발 + Red Hat 컨설팅 | ◐ |
| R08 | 검증 모델 배포·서비스 연계 | Day1→Day2 | 승인 게이트(평가 통과 판정)·업무 서비스 연계 개발, PCMS 연동(R41) | SI/고객 개발·연동 | ◐ |
| R11 | 모델 버전·학습·성능·배포 이력 | Day1→Day2 | 학습·평가·배포 이력 자동 기록(파이프라인 연동 개발, 공통 식별자) | SI/고객 개발 | ◐ |
| R13 | LoRA/QLoRA(PEFT) | Day1→Day2 | 어댑터 병합·멀티 LoRA 서빙 구성 표준, 모델·백엔드별 검증 | Red Hat 컨설팅 + SI/고객 개발 | ◐ |
| R16 | 평가 데이터셋 등록·버전관리 | Day1→Day2 | 데이터셋 카탈로그·메타정보 관리 화면 개발, S3 버전관리 정책 | SI/고객 개발 | ◐ |
| R17 | 평가 데이터셋 기반 평가 수행 | Day1→Day2 | 우리카드 자체 평가 코드·custom task 연동 | SI/고객 연동 | ● |
| R18 | 정량 메트릭(정확성·관련성) | Day1→Day2 | 업무 기준 한국어 관련성·답변품질 지표 custom task 개발 | SI/고객 개발 + Red Hat 컨설팅 | ◐ |
| R19 | 평가 통과 모델 서빙 전환 | Day1→Day2 | 기준 충족 시 자동 승인·전환(승격 게이트) 개발 | SI/고객 개발 | ◐ |
| R24 | 단일 AI API Gateway | Day1→Day2 | OCR·KMS 등 비 LLM 서비스 편입, 라우팅 정책 확장 | Red Hat 컨설팅(MaaS 정책) + SI/고객 연동 | ◐ |
| R25 | 등록·배포·버전·라우팅 통합관리 | Day1→Day2 | 단일 통합관리 화면·이력 연결 개발 | SI/고객 개발·연동 | ◐ |
| R26 | API 인증·인가·접근통제 | Day1→Day2 | API Key 발급·회수·로테이션 운영, 사내 IAM/OIDC 연동 확장 | 고객 운영 + Red Hat 컨설팅 | ◐ |
| R28 | 호출량·동시 요청 제어 | Day1→Day2 | 테넌트·모델·사용자별 쿼터 정책 운영, 사용량 리포트 | 고객 운영 + Red Hat 컨설팅 | ◐ |
| R32 | AI 서비스 TPS·TTFT·Latency | Day1→Day2 | 비 LLM 서비스(OCR 등) 계측 개발, TPS 정의·측정 위치·집계식 합의 | SI/고객 개발 | ◐ |
| R38 | 내부 개발자 AI 플랫폼 교육 | Day1→Day2 | 고객 환경 실습 워크숍(Workbench·Pipelines·Training Hub·평가·모델 배포), 독립 수행 검증 | Red Hat Training·Consulting | ◇ |

### 4-3. 🔗 공통 — OpenShift + OpenShift AI (4건)

| ID | 요건 | 단계 | Day2 수행 내용 | 수행 주체 | 지원 |
|---|---|---|---|---|:-:|
| R03 | 사용률 기반 GPU 할당 기준 | Day2 | 운영 데이터 기반 서비스별 할당 기준 정례화·주기적 재조정 | Red Hat 컨설팅 (자동 조정은 개발) | ◐ |
| R09 | 공통 운영 프로세스(배포·변경·장애) | Day2 | 운영 프로세스 적용·개선, 장애 대응 체계와 Red Hat 기술지원 에스컬레이션 연계 | Red Hat 컨설팅·기술지원 + 고객 운영 | ◇ |
| R39 | 오픈소스 최신성 | Day2 | 정기 릴리스·업그레이드로 최신성 유지(업스트림을 하드닝한 제품 형태) | Red Hat 구독(기술지원) | ◇ |
| R40 | OSS 자산·취약점·EOL 관리 | Day2 | 정기 패치·업그레이드 운영, SCA/SBOM 운영 체계 | Red Hat 구독 + 고객 운영(별도 도구) | ◐ |

---

## 5. 확인 필요 사항 / 리스크 (제안 전 합의)

| # | 항목 | 관련 요건 | 영향 | 권장 대응 |
|:-:|---|---|---|---|
| 1 | **서버 4대 클러스터 구성** | R01, R35 | Control Plane 3노드가 기본이라 서버 4대로 개발/운영 2클러스터를 만들 수 없음 | ① 단일 클러스터(Control Plane 3대는 소형 서버·VM으로 확보) + 프로젝트 기반 개발/운영 논리 분리 ② 환경별 2노드+Arbiter 토폴로지(지원 버전·HW 요건 확인) ③ 환경별 SNO(HA 없음, 운영 비권장) — 제안 전 고객 합의 |
| 2 | **운영 GPU 1노드** | R29, R35 | GPU 노드 장애 시 운영 추론 중단(GPU HA 불가) | GPU 노드 추가 또는 장애 시 개발 GPU 전환 절차·SLA를 제안서에 명시 |
| 3 | **B300 GPU 지원 매트릭스** | R04, R21, R31 | 최신 세대 GPU — GPU Operator·드라이버·vLLM·OpenShift AI 지원 버전 의존 | 제안 버전 확정 전 지원 매트릭스 검증, 폐쇄망 드라이버 이미지 반입 계획 수립 |
| 4 | **MaaS 구독·성숙도** | R24, R26, R28 | MaaS 정책(인증·Rate Limit)은 RHCL 구성요소 사용, 멀티테넌시·외부 OIDC는 TP(3.5) | RHCL 구독 포함 여부 확인, TP 기능은 제안서에 '기술 검토' 수준으로 표기 |
| 5 | **MaaS Gateway LoadBalancer** | R24 | MaaS Gateway는 LoadBalancer 서비스 전제 — 온프렘은 MetalLB 필요 | MetalLB(OCP 포함) L2/BGP 구성 협의. 미사용 시 ClusterIP+Route 우회는 공식 가이드 아님(RFE OCPSTRAT-3781) |
| 6 | **스토리지·DB 선행 조건** | R06, R10, R11, R16, R27 | 데이터셋·모델·파이프라인 아티팩트·LokiStack용 S3, Registry·Pipelines·MaaS용 DB 필요 | 고객 보유 S3 활용 또는 ODF(별도 구독) 산정, 구성요소별 DB 엔진·외부 DB 정책 확정 |
| 7 | **모델 폐쇄망 반입** | R10 | 대용량 가중치는 기존 컨테이너 이미지 반입 절차로 처리하기 어려움 | ModelCar(OCI)·S3 반입 경로를 보안팀과 사전 협의 |
| 8 | **Grafana 지원 범위** | R30 | Grafana는 커뮤니티 오퍼레이터로 Red Hat 지원 대상 아님 | OpenShift 콘솔 대시보드·COO를 기본으로 제안, Grafana는 지원 범위 외로 명시 |
| 9 | **신규 기능 GA/TP 상태** | R11, R13, R17, R21 | MLflow·EvalHub·Training Hub(LoRA)·llm-d 등은 버전에 따라 지원 상태가 다름 | 제안 버전(OpenShift AI 3.x) 기준 GA/TP 확인 후 지원 수준 표기 확정 |
| 10 | **오픈소스 최신성 해석** | R39, R40 | '최신 업스트림 상시 보장'은 제품 구독으로 약속 불가 | 'Red Hat 지원 버전·보안 패치 기준'으로 합의, 비제품 OSS·고객 앱 의존성은 별도 관리 |
| 11 | **NVIDIA GPU Operator 지원 주체** | R02, R04, R31 | GPU Operator는 NVIDIA 인증 오퍼레이터 — 기술지원 주체 NVIDIA | NVIDIA 기술지원 체계(예: NVIDIA AI Enterprise) 포함 여부 확인 |

---

## 6. 필요 구독·서비스 구성

| 구분 | 제품/서비스 | 내용 | 관련 요건 |
|---|---|---|---|
| 컨테이너 플랫폼 | **Red Hat OpenShift Container Platform** | GitOps·Pipelines·Logging·Monitoring·MetalLB·Gateway API·Red Hat build of Kueue·MTA 포함 | R01, R02, R03, R04, R05, R09, R27, R29, R30, R31, R33, R34, R35, R36, R37, R39, R40, R41 |
| AI | **Red Hat OpenShift AI** | MaaS·Model Registry·KServe/vLLM·llm-d·Training Hub·Kubeflow Trainer·TrustyAI·Pipelines 포함 | R02, R03, R05, R06, R07, R08, R09, R10, R11, R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23, R24, R25, R26, R28, R32, R38, R39, R40 |
| 파트너 | **NVIDIA GPU Operator** | NVIDIA 인증 오퍼레이터(GPU 드라이버·MIG·DCGM) | R02, R04, R31, R35 |
| 별도 구독(확인) | **Red Hat Connectivity Link** | MaaS 인증·Rate Limit 정책 구성요소 | R24, R26, R28 |
| 별도 구독(선택) | **OpenShift Data Foundation** | 고객 S3 보유 시 불필요 | R06, R10, R16, R27 |
| 별도 구독(선택) | **RHACS · Quay · Trusted Profile Analyzer** | 보안정책·이미지 취약점·SBOM 관리 | R27, R40 |
| 서비스 | **Red Hat Consulting** | 설계·정책 수립·튜닝·기술이전 | R03, R09, R24, R35, R37, R38 |
| 서비스 | **Red Hat Training** | DO180·DO280(OpenShift), AI267(OpenShift AI) | R37, R38 |
| 서비스 | **기술지원·TAM** | 구독 기술지원, 라이프사이클·패치 | R09, R39, R40 |
| 고객/SI | **개발·연동·마이그레이션** | 제품 범위 외 개발 항목 | R33, R41 + Day2 개발 항목 |

> OpenShift·OpenShift AI 행의 관련 요건은 **주 제공 영역 기준**입니다(공통 포함). 구독 SKU·GPU 노드 산정 기준은 영업/파트너와 확인이 필요합니다.

---

## 7. 전체 요건 매트릭스 (41건, 원문 대비)

| ID | 구분 | 세부 구분 | 제안 요청 사항 (원문) | 단계 | 영역 | 지원 | 별도·타사·SI / 확인 사항 |
|---|---|---|---|---|---|:-:|---|
| R01 | GPU 통합관리 | Kubernetes 기반 AI 플랫폼 구축 | 컨테이너 기반 AI 서비스 실행환경 구축 및 개발/운영 환경 분리 | Day1 | 🐳 컨테이너 플랫폼 | ● | 서버 4대로는 개발/운영 물리 2클러스터 구성 불가 → R35 참조 |
| R02 | GPU 통합관리 | GPU 자원 통합 관리 | AI 서비스별 GPU 전용 운영 방식에서 공용 GPU Pool 기반 통합관리 체계로 전환 | Day1 | 🔗 공통 | ● | NVIDIA GPU Operator(NVIDIA 인증 오퍼레이터, 기술지원 주체 NVIDIA) / GPU 메모리 통합·실행 중 워크로드 이동 기능이 아님 — 요건 해석 합의 |
| R03 | GPU 통합관리 | GPU 스케줄링 및 동적 할당 | AI서비스 및 GPU 자원 사용률 모니터링에 기반한 GPU할당 기준 마련 | Day2 | 🔗 공통 | ◐ | 사용률 기반 자동 조정은 별도 개발 / 기준 수립은 컨설팅 산출물로 명시 |
| R04 | GPU 통합관리 | GPU 스케줄링 및 동적 할당 | MIG 등 GPU 분할 기술을 활용하여 서비스별 요구량에 따른 GPU 할당 및 격리 | Day1 | 🐳 컨테이너 플랫폼 | ● | NVIDIA GPU Operator(기술지원 주체 NVIDIA) / B300 MIG 지원 — GPU Operator·드라이버·vLLM·OpenShift AI 지원 버전과 폐쇄망 드라이버 반입 확인 |
| R05 | GPU 통합관리 | GPU 스케줄링 및 동적 할당 | 워크로드별 GPU 요청·할당·회수 및 가용자원 기반 스케줄링 체계 구현 | Day1 | 🔗 공통 | ● | 실행 중 GPU를 무중단 축소·이동하는 기능이 아님 |
| R06 | AI 모델관리 | AI 서비스 운영 표준화 | 데이터 셋 관리 → 학습 → 평가 → 모델 등록까지 일련의 프로세스 표준화 | Day1→Day2 | 🧠 AI | ◐ | S3 호환 오브젝트 스토리지(고객 보유 또는 ODF 별도 구독) / 파이프라인·Registry용 DB와 S3 사전 준비 |
| R07 | AI 모델관리 | AI 서비스 운영 표준화 | AI 서비스 학습, 운영 환경 논리적 분할 관리 | Day1 | 🧠 AI | ● | 공유 클러스터의 장애·자원 영향은 설계로 통제 |
| R08 | AI 모델관리 | AI 서비스 운영 표준화 | 검증 완료 모델의 추론환경 배포 및 서비스 연계 프로세스 구축 | Day1→Day2 | 🧠 AI | ◐ | 업무 서비스 연계·승인 체계 개발 |
| R09 | AI 모델관리 | AI 서비스 운영 표준화 | AI 서비스 배포·변경·장애·모니터링 등 공통 운영 프로세스 마련 | Day2 | 🔗 공통 | ◇ | Red Hat Consulting(운영 프로세스 수립), 기술지원/TAM |
| R10 | AI 모델관리 | 모델 관리체계 | 외부 Base Model 등록 및 관리 | Day1 | 🧠 AI | ● | 가중치 저장소(S3·레지스트리), Registry DB / 대용량 가중치 폐쇄망 반입 절차 — 보안팀 협의 필요 |
| R11 | AI 모델관리 | 모델 관리체계 | AI모델별 버전, 메타정보, 학습이력, 성능 및 배포이력 관리 | Day1→Day2 | 🧠 AI | ◐ | 이력 자동 기록 코드 개발 / MLflow 등 신규 기능은 제안 버전 기준 GA/TP 상태 확인 |
| R12 | AI 모델관리 | 학습 | 등록된 데이터셋을 사용하여 외부 Base Model기반 SFT(Supervised Fine Tuning) 수행 가능 | Day1 | 🧠 AI | ● | 고객 데이터 전처리는 개발 범위 |
| R13 | AI 모델관리 | 학습 | GPU자원을 효율적으로 사용할 수 있도록 LoRA, QLoRA등 Parameter-Efficient Fine-Tuning 방식 지원 | Day1→Day2 | 🧠 AI | ◐ | 지원 모델·백엔드 확인 |
| R14 | AI 모델관리 | 학습 | Batch Size, Max Sequence Length등 주요 학습 Parameter 설정 가능 | Day1 | 🧠 AI | ● | — |
| R15 | AI 모델관리 | 학습 | 학습 Job별 GPU 종류, 수량 등 필요한 자원을 지정, 정책에 따라 할당 할 수 있어야 함 | Day1 | 🧠 AI | ● | — |
| R16 | AI 모델관리 | 평가 | 학습 데이터셋과 구분된 평가용 데이터셋을 등록, 선택하고 버전을 관리할 수 있어야 함 | Day1→Day2 | 🧠 AI | ◐ | S3 버전관리 기능, 카탈로그 화면 개발 / 평가 데이터셋 전용 등록·버전관리 화면은 제품에 없음 |
| R17 | AI 모델관리 | 평가 | 등록된 평가 Dataset을 기반으로 평가 수행 가능 | Day1→Day2 | 🧠 AI | ● | EvalHub 등 신규 평가 기능은 버전별 GA/TP 상태 확인 |
| R18 | AI 모델관리 | 평가 | 정량평가 메트릭을 설정하여 답변 정확성, 관련성 등 평가를 수행해야 함 | Day1→Day2 | 🧠 AI | ◐ | 업무 지표 정의·평가 로직 개발 |
| R19 | AI 모델관리 | 추론 | 평가 기준을 충족한 모델을 관리하고 서빙 단계로 전환할 수 있어야 함 | Day1→Day2 | 🧠 AI | ◐ | 승격 게이트 개발 |
| R20 | AI 모델관리 | 추론 | 모델 저장소에 등록, 승인된 모델을 추론환경에 배포할 수 있어야 함 | Day1 | 🧠 AI | ● | 승인 강제 통제는 R41(PCMS)로 분리 |
| R21 | AI 모델관리 | 추론 | vLLM등 표준화된 서빙엔진 기반 모델 추론 서비스를 구성할 수 있어야 함 | Day1 | 🧠 AI | ● | 모델 형식·B300 호환 vLLM 버전, llm-d 사용 조건 확인 |
| R22 | AI 모델관리 | 추론 | 배포된 모델을 표준 인터페이스(API)를 통해 호출 할 수 있어야 함 | Day1 | 🧠 AI | ● | — |
| R23 | AI 모델관리 | 추론 | Continuous Batching등 다수의 동시 추론 요청을 효율적으로 처리할 수 있어야 함 | Day1 | 🧠 AI | ● | 목표 TPS 달성 튜닝은 컨설팅/기술지원 범위로 명시 |
| R24 | API Gateway | AI API 통합관리 | AI서비스 및 모델 호출을 위한 단일 API Gateway 구성 | Day1→Day2 | 🧠 AI | ◐ | Red Hat Connectivity Link(RHCL) — 구독 범위 확인 / 비 LLM 통합 시 기존·별도 API GW / MaaS Gateway는 LoadBalancer 전제 → MetalLB 필요(미사용 시 Route 우회는 공식 가이드 아님, RFE OCPSTRAT-3781) / MaaS 멀티테넌시 TP(3.5) |
| R25 | API Gateway | AI API 통합관리 | AI서비스 및 모델 등록, 배포, 버전 및 라우팅 통합 관리 | Day1→Day2 | 🧠 AI | ◐ | 통합 관리 화면 연동 개발 |
| R26 | API Gateway | 인증 및 보안관리 | API 호출 주체에 대한 인증, 인가 및 접근 통제 수행 | Day1→Day2 | 🧠 AI | ◐ | RHCL(AuthPolicy·Authorino) / MaaS 외부 OIDC 연동은 TP — 버전 확인 |
| R27 | API Gateway | 인증 및 보안관리 | 서비스별 보안정책과 감사로그 통합 관리 | Day1→Day2 | 🐳 컨테이너 플랫폼 | ◐ | RHACS(보안정책 통합, 별도 구독), 고객 SIEM / 플랫폼 감사로그와 모델 호출 로그는 별도 — 통합 범위 합의 |
| R28 | API Gateway | 트래픽 및 서비스 제어 | AI서비스 및 모델별 처리용량을 고려하여 호출량, 동시 요청 제어 | Day1→Day2 | 🧠 AI | ◐ | RHCL(Limitador) / 전역 동시성 제어는 Gateway 정책 별도 구성·검증 |
| R29 | API Gateway | 트래픽 및 서비스 제어 | 부하분산 및 장애 격리를 통해 안정적인 서비스 제공 가능 | Day1 | 🐳 컨테이너 플랫폼 | ◐ | 운영 GPU 1노드 → GPU 노드 장애 시 HA 불가, 여유 자원 필요(사전 합의) |
| R30 | 모니터링 | 통합 모니터링 체계 구축 | GPU·서버·K8s·AI 서비스의 상태 및 성능을 통합적으로 모니터링 | Day1→Day2 | 🐳 컨테이너 플랫폼 | ◐ | Grafana(커뮤니티 오퍼레이터 — Red Hat 지원 대상 아님) / Grafana 사용 시 지원 범위 명시 |
| R31 | 모니터링 | 통합 모니터링 체계 구축 | GPU Utilization, VRAM, 온도, 전력, ECC Error 등 주요 GPU 상태 및 성능지표 모니터링 | Day1 | 🐳 컨테이너 플랫폼 | ● | NVIDIA GPU Operator(기술지원 주체 NVIDIA) / B300 ECC·전력·MIG 지표 collector 설정 확인 |
| R32 | 모니터링 | 통합 모니터링 체계 구축 | AI서비스별 TPS, TTFT, Latency 등의 정보를 수집 및 모니터링 | Day1→Day2 | 🧠 AI | ◐ | 비 LLM 앱 계측 개발 |
| R33 | 기존 AI 서비스 이전 | 서비스 이전 | 기 구축(혹은 구축 진행 中) AI 서비스(코드어시스턴트, KMS, AI OCR)의 GPU클러스터 이전을 지원하여야 함 | Day2 | 🐳 컨테이너 플랫폼 | ○ | 마이그레이션·테스트 인력 / 이전 범위·수량 파악 필요 |
| R34 | 인증 | SSO연동 | 관리자 페이지나 기타 포털에 대해 SSO나 2차인증을 지원하여야 함 | Day1→Day2 | 🐳 컨테이너 플랫폼 | ● | 고객 IdP(MFA 기능) / MFA는 IdP에서 강제 / Keycloak 구독 포함 범위 확인 |
| R35 | 인프라구성 | GPU 클러스터 구축 | GPU 서버 운영 1노드, 개발 1노드 및 CPU영역 서버 운영 1노드, 개발 1노드의 클러스터를 구축하여야 함 | Day1 | 🐳 컨테이너 플랫폼 | ● | Control Plane 3노드 기본 → 서버 4대로 개발/운영 2클러스터 불가. 단일 클러스터+논리 분리 또는 Control Plane 추가 확보 재협의 / 운영 GPU 1노드 HA 부재 |
| R36 | 인프라구성 | GPU 클러스터 구축 | 향후 외부 시스템 연계 시, 내부 데이터의 유출이 발생하지 않도록 확장성을 고려한 구조로 설계 | Day1→Day2 | 🐳 컨테이너 플랫폼 | ◐ | DLP·망연계 솔루션 |
| R37 | 기술이전 | 기술이전 및 운영자 교육 | 플랫폼 구축·운영·장애대응 및 AI 서비스 배포 등에 대한 기술이전 및 교육 수행 | Day1→Day2 | 🐳 컨테이너 플랫폼 | ◇ | Red Hat Consulting 기술이전 |
| R38 | 기술이전 | 기술이전 및 운영자 교육 | 내부개발 인력들이 자체적으로 AI모델을 개발/운영 할 수 있도록 플랫폼 교육 실시 | Day1→Day2 | 🧠 AI | ◇ | 워크숍은 컨설팅 범위 |
| R39 | 오픈소스 | 패치 및 업그레이드 | 프로젝트에 적용되는 오픈소스의 최신성을 보장하여야 함 | Day2 | 🔗 공통 | ◇ | 비제품 OSS는 별도 유지관리 / '최신 업스트림 상시 보장'이 아닌 'Red Hat 지원 버전 기준'으로 합의 |
| R40 | 오픈소스 | 패치 및 업그레이드 | 플랫폼에 적용되는 오픈소스의 구성, 버전, 라이선스, 취약점, EoS/EoL 정보를 체계적으로 관리하고, 보안 패치 및 버전 업그레이드 등 지속적인 유지관리 체계를 제공 | Day2 | 🔗 공통 | ◐ | RHACS·Quay(취약점 스캔), Trusted Profile Analyzer(SBOM) — 별도 구독 / 구독 제품 유지관리와 전체 OSS 자산 관리를 구분 |
| R41 | 기타 | 변경관리 | 당사 변경관리 프로세스를 준용하여 PCMS(변경관리 시스템)와 연계하여야 함(쿠버네티스 컨테이너 및 AI모델 전반) | Day2 | 🐳 컨테이너 플랫폼 | ○ | PCMS API·EAI 연동 개발 / PCMS 표준 커넥터 없음 |

---

### 참고

- 기존 MaaS·DB·Gateway LB 제품 요청 정리: `openshift-ai/product-requests-maas-db-lb.md` (branch `claude/admiring-fermat-mqr4q4`)
- RFE OCPSTRAT-3781 (MaaS Gateway ClusterIP 정식 지원): https://issues.redhat.com/browse/OCPSTRAT-3781
- OpenShift AI 3.5 MaaS 문서: https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/html/govern_llm_access_with_models-as-a-service/deploy-and-manage-models-as-a-service
- 재생성: `src/rfp_data.py`(요건 41건 단일 데이터)를 수정한 뒤 `cd src && python3 build.py ..` 실행 → README.md·엑셀 동시 갱신
