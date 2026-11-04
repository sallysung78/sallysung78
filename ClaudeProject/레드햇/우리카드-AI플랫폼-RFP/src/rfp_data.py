# -*- coding: utf-8 -*-
"""우리카드 AI 플랫폼 RFP 요건 41건 — Day1/Day2 · 제공영역 · Red Hat 지원 분석 (단일 데이터 소스).

원본: Google Sheets「우리카드_AI_플랫폼_요구사항_지원분석_v0_4」(2026-10-29)
      Google Sheets「AI_플랫폼_요구사항_검토_Red_Hat_AI_기능_비교」(2026-10-21)
"""

SOURCE_V04 = "https://docs.google.com/spreadsheets/d/1HdjXSlA_d3ECMl-INQWbLe_lg_grl6z85R5Lko9mdtk/edit"
SOURCE_1021 = "https://docs.google.com/spreadsheets/d/1MoZ5Qk-yEzmBHkxVWCH_rcHNXPMk7UTSGEHVAis0k9c/edit"

# 단계
D1 = "Day1"
D12 = "Day1→Day2"
D2 = "Day2"

# 주 제공 영역
OCP = "컨테이너 플랫폼"
AI = "AI"
COM = "공통"

# 지원 수준
FULL = "●"     # 제품 기능으로 충족 (구성·설정)
PART = "◐"     # 제품 기능 + 보완 (컨설팅·개발·연동)
OUT = "○"      # 제품 범위 외 — 개발·연동(SI) 중심, Red Hat은 기반 제공
SVC = "◇"      # 서비스 — 교육·컨설팅·기술지원(구독)

LEGEND_SUPPORT = [
    (FULL, "제품 기능으로 충족", "Red Hat 제품을 구성·설정하면 요건 충족"),
    (PART, "제품 기능 + 보완", "제품이 핵심 기능을 제공하고, 컨설팅·개발·연동으로 보완"),
    (OUT, "제품 범위 외", "개발·연동·마이그레이션(SI/고객) 중심, Red Hat은 실행 기반만 제공"),
    (SVC, "서비스", "교육·컨설팅·기술지원(구독)으로 제공"),
]

LEGEND_PHASE = [
    (D1, "구축(1차) 시점에 제품 기능 구성·예제 검증으로 요건 충족. 이후는 일상 운영만 필요"),
    (D12, "Day1에 제품 기반·예제 구성, Day2에 고객 정책·데이터 반영 및 개발·연동으로 완성"),
    (D2, "운영 데이터·프로세스·유지관리 성격. Day1에는 준비(분석·예제·기준 합의)만 수행"),
]

LEGEND_AREA = [
    (OCP, "Red Hat OpenShift (OCP)", "클러스터·GPU 인프라 활성화·네트워크·보안·인증·모니터링 기반·CI/CD·라이프사이클 — AI가 없어도 필요한 플랫폼 기능"),
    (AI, "Red Hat OpenShift AI (RHOAI)", "데이터셋→학습→평가→등록→서빙→API(MaaS)까지 모델 라이프사이클과 AI 특화 자원 추상화(Hardware Profile)·AI 지표"),
    (COM, "OpenShift + OpenShift AI", "두 제품이 함께 맞물려야 성립 (GPU Pool·스케줄링, 운영 프로세스, 라이프사이클 관리)"),
]

# fields: id, 구분, 세부구분, 원문, 요약, 단계, 영역, 지원, day1, day2, day2_owner, ai_part, ocp_part, extra, check
R = []


def add(**kw):
    kw.setdefault("ai_part", "")
    kw.setdefault("ocp_part", "")
    kw.setdefault("extra", "")
    kw.setdefault("check", "")
    kw.setdefault("day2_owner", "")
    R.append(kw)


# ── GPU 통합관리 ────────────────────────────────────────────────────────────
add(id="R01", cat="GPU 통합관리", sub="Kubernetes 기반 AI 플랫폼 구축",
    req="컨테이너 기반 AI 서비스 실행환경 구축 및 개발/운영 환경 분리",
    short="컨테이너 실행환경 구축·개발/운영 분리",
    phase=D1, area=OCP, sup=FULL,
    day1="폐쇄망 OpenShift 설치, 개발/운영 분리 방식(물리 클러스터 vs 논리 분리) 설계, Project·RBAC·NetworkPolicy·ResourceQuota 기본 구성",
    day2="개발→운영 승격(이미지·모델 반입) 절차 운영, 환경별 정책 정비",
    day2_owner="고객 운영 + Red Hat 기술지원",
    ocp_part="OpenShift(Project·RBAC·NetworkPolicy·ResourceQuota), oc-mirror(폐쇄망 미러링)",
    ai_part="Data Science Project로 AI 작업 공간 분리(보조)",
    check="서버 4대로는 개발/운영 물리 2클러스터 구성 불가 → R35 참조")

add(id="R02", cat="GPU 통합관리", sub="GPU 자원 통합 관리",
    req="AI 서비스별 GPU 전용 운영 방식에서 공용 GPU Pool 기반 통합관리 체계로 전환",
    short="공용 GPU Pool 통합관리",
    phase=D1, area=COM, sup=FULL,
    day1="GPU Operator·NFD 설치, GPU 노드 Pool(label/taint) 구성, Hardware Profile 정의, 프로젝트별 GPU 사용 한도(Quota) 설정",
    day2="사용 현황 기반 Pool·한도 재조정, 신규 서비스 GPU 온보딩",
    day2_owner="고객 운영",
    ocp_part="NVIDIA GPU Operator, Node Feature Discovery, ResourceQuota, Red Hat build of Kueue(ClusterQueue)",
    ai_part="Hardware Profile(GPU 유형·수량 프리셋), 프로젝트별 프로파일 노출",
    extra="NVIDIA GPU Operator(NVIDIA 인증 오퍼레이터, 기술지원 주체 NVIDIA)",
    check="GPU 메모리 통합·실행 중 워크로드 이동 기능이 아님 — 요건 해석 합의")

add(id="R03", cat="GPU 통합관리", sub="GPU 스케줄링 및 동적 할당",
    req="AI서비스 및 GPU 자원 사용률 모니터링에 기반한 GPU할당 기준 마련",
    short="사용률 기반 GPU 할당 기준",
    phase=D2, area=COM, sup=PART,
    day1="DCGM·서빙 지표 수집 체계 구성, 대표 서비스 1개 초기 할당 기준 수립",
    day2="운영 데이터 기반 서비스별 할당 기준 정례화·주기적 재조정",
    day2_owner="Red Hat 컨설팅 (자동 조정은 개발)",
    ocp_part="OpenShift Monitoring + DCGM Exporter 지표",
    ai_part="모델 서빙(vLLM) 지표, Hardware Profile에 기준 반영",
    extra="사용률 기반 자동 조정은 별도 개발",
    check="기준 수립은 컨설팅 산출물로 명시")

add(id="R04", cat="GPU 통합관리", sub="GPU 스케줄링 및 동적 할당",
    req="MIG 등 GPU 분할 기술을 활용하여 서비스별 요구량에 따른 GPU 할당 및 격리",
    short="MIG 기반 GPU 분할·격리",
    phase=D1, area=OCP, sup=FULL,
    day1="MIG 전략(single/mixed)·프로파일 설계 및 적용, MIG 리소스를 Hardware Profile로 노출",
    day2="서비스 수요 변화에 따른 MIG 재구성(재구성 시 해당 GPU 워크로드 중단)",
    day2_owner="고객 운영",
    ocp_part="NVIDIA GPU Operator(MIG Manager), 노드 label 기반 MIG 구성",
    ai_part="Hardware Profile에 MIG 리소스(nvidia.com/mig-*) 매핑",
    extra="NVIDIA GPU Operator(기술지원 주체 NVIDIA)",
    check="B300 MIG 지원 — GPU Operator·드라이버·vLLM·OpenShift AI 지원 버전과 폐쇄망 드라이버 반입 확인")

add(id="R05", cat="GPU 통합관리", sub="GPU 스케줄링 및 동적 할당",
    req="워크로드별 GPU 요청·할당·회수 및 가용자원 기반 스케줄링 체계 구현",
    short="GPU 요청·할당·회수 스케줄링",
    phase=D1, area=COM, sup=FULL,
    day1="Kueue(ClusterQueue·LocalQueue·ResourceFlavor) 구성, 작업 종료·정지 시 GPU 반환 검증",
    day2="우선순위·선점(preemption)·공정 분배 정책 튜닝, 유휴 워크벤치 정지 정책",
    day2_owner="고객 운영 + Red Hat 컨설팅",
    ocp_part="Red Hat build of Kueue, OpenShift 스케줄러(nodeSelector·taint·toleration)",
    ai_part="Hardware Profile, 워크벤치 정지 시 자원 반환, 분산 워크로드 Kueue 연동",
    check="실행 중 GPU를 무중단 축소·이동하는 기능이 아님")

# ── AI 모델관리 / AI 서비스 운영 표준화 ─────────────────────────────────────
add(id="R06", cat="AI 모델관리", sub="AI 서비스 운영 표준화",
    req="데이터 셋 관리 → 학습 → 평가 → 모델 등록까지 일련의 프로세스 표준화",
    short="데이터셋→학습→평가→등록 표준화",
    phase=D12, area=AI, sup=PART,
    day1="샘플 모델 1건으로 데이터셋 저장·학습·평가·등록 E2E 파이프라인 예제 + 표준 절차서",
    day2="고객 데이터 처리 컴포넌트·표준 파이프라인 템플릿 개발, 서비스별 확대 적용",
    day2_owner="SI/고객 개발 + Red Hat 컨설팅",
    ai_part="Data Science Pipelines, Connections(S3), Training Hub·Kubeflow Trainer, TrustyAI LM-Eval, Model Registry",
    ocp_part="OpenShift Pipelines·GitOps(배포 자동화 연계 시)",
    extra="S3 호환 오브젝트 스토리지(고객 보유 또는 ODF 별도 구독)",
    check="파이프라인·Registry용 DB와 S3 사전 준비")

add(id="R07", cat="AI 모델관리", sub="AI 서비스 운영 표준화",
    req="AI 서비스 학습, 운영 환경 논리적 분할 관리",
    short="학습/운영 환경 논리 분할",
    phase=D1, area=AI, sup=FULL,
    day1="학습·운영 프로젝트 각 1개 구성 — 권한·자원 한도·스토리지·접속정보 분리, 기본 NetworkPolicy, 동작 검증",
    day2="서비스 추가 시 프로젝트 템플릿(GitOps)으로 온보딩 표준화",
    day2_owner="고객 운영",
    ai_part="Data Science Project, 프로젝트별 Hardware Profile·Connection 분리",
    ocp_part="Namespace·RBAC·ResourceQuota·NetworkPolicy",
    check="공유 클러스터의 장애·자원 영향은 설계로 통제")

add(id="R08", cat="AI 모델관리", sub="AI 서비스 운영 표준화",
    req="검증 완료 모델의 추론환경 배포 및 서비스 연계 프로세스 구축",
    short="검증 모델 배포·서비스 연계",
    phase=D12, area=AI, sup=PART,
    day1="Red Hat 검증 모델 1건 추론 배포, API 호출 검증, 배포·연계 절차 문서화",
    day2="승인 게이트(평가 통과 판정)·업무 서비스 연계 개발, PCMS 연동(R41)",
    day2_owner="SI/고객 개발·연동",
    ai_part="Model Registry → KServe 배포, Red Hat AI 검증 모델(ModelCar)",
    ocp_part="OpenShift GitOps·Pipelines(배포 자동화)",
    extra="업무 서비스 연계·승인 체계 개발")

add(id="R09", cat="AI 모델관리", sub="AI 서비스 운영 표준화",
    req="AI 서비스 배포·변경·장애·모니터링 등 공통 운영 프로세스 마련",
    short="공통 운영 프로세스(배포·변경·장애)",
    phase=D2, area=COM, sup=SVC,
    day1="파일럿 서비스 기준 운영 절차서·점검표 작성 및 인계",
    day2="운영 프로세스 적용·개선, 장애 대응 체계와 Red Hat 기술지원 에스컬레이션 연계",
    day2_owner="Red Hat 컨설팅·기술지원 + 고객 운영",
    ocp_part="플랫폼 운영 기능(모니터링·로깅·알림·업그레이드)",
    ai_part="모델 배포·관측 기능",
    extra="Red Hat Consulting(운영 프로세스 수립), 기술지원/TAM")

# ── AI 모델관리 / 모델 관리체계 ─────────────────────────────────────────────
add(id="R10", cat="AI 모델관리", sub="모델 관리체계",
    req="외부 Base Model 등록 및 관리",
    short="외부 Base Model 등록·관리",
    phase=D1, area=AI, sup=FULL,
    day1="Model Registry 구성, 외부 모델 등록(버전·메타정보·접근권한), 폐쇄망 모델 반입 절차 설계",
    day2="모델 반입·버전 관리 운영",
    day2_owner="고객 운영",
    ai_part="Model Registry, Model Catalog, ModelCar(OCI 이미지) 또는 S3 저장",
    ocp_part="내부 미러 레지스트리(oc-mirror)",
    extra="가중치 저장소(S3·레지스트리), Registry DB",
    check="대용량 가중치 폐쇄망 반입 절차 — 보안팀 협의 필요")

add(id="R11", cat="AI 모델관리", sub="모델 관리체계",
    req="AI모델별 버전, 메타정보, 학습이력, 성능 및 배포이력 관리",
    short="모델 버전·학습·성능·배포 이력",
    phase=D12, area=AI, sup=PART,
    day1="Registry 버전·메타정보·배포 연계 예제",
    day2="학습·평가·배포 이력 자동 기록(파이프라인 연동 개발, 공통 식별자)",
    day2_owner="SI/고객 개발",
    ai_part="Model Registry(custom properties), 실험 추적(MLflow)",
    extra="이력 자동 기록 코드 개발",
    check="MLflow 등 신규 기능은 제안 버전 기준 GA/TP 상태 확인")

# ── AI 모델관리 / 학습 ──────────────────────────────────────────────────────
add(id="R12", cat="AI 모델관리", sub="학습",
    req="등록된 데이터셋을 사용하여 외부 Base Model기반 SFT(Supervised Fine Tuning) 수행 가능",
    short="SFT 수행",
    phase=D1, area=AI, sup=FULL,
    day1="Training Hub·Kubeflow Trainer로 SFT 실행 방법 및 예제 노트북 제공",
    day2="고객 데이터 전처리·학습 스크립트·모델별 설정 개발, 정례 학습 파이프라인화",
    day2_owner="SI/고객 개발",
    ai_part="Training Hub, Kubeflow Trainer, Workbench, Kueue 연동",
    check="고객 데이터 전처리는 개발 범위")

add(id="R13", cat="AI 모델관리", sub="학습",
    req="GPU자원을 효율적으로 사용할 수 있도록 LoRA, QLoRA등 Parameter-Efficient Fine-Tuning 방식 지원",
    short="LoRA/QLoRA(PEFT)",
    phase=D12, area=AI, sup=PART,
    day1="LoRA/QLoRA 학습 예제 제공",
    day2="어댑터 병합·멀티 LoRA 서빙 구성 표준, 모델·백엔드별 검증",
    day2_owner="Red Hat 컨설팅 + SI/고객 개발",
    ai_part="Training Hub(LoRA/QLoRA), vLLM LoRA 어댑터 서빙",
    check="지원 모델·백엔드 확인")

add(id="R14", cat="AI 모델관리", sub="학습",
    req="Batch Size, Max Sequence Length등 주요 학습 Parameter 설정 가능",
    short="학습 파라미터 설정",
    phase=D1, area=AI, sup=FULL,
    day1="노트북·SDK 파라미터로 배치 크기·최대 입력 길이·학습률·Epoch 지정",
    day2="하이퍼파라미터 튜닝(컨설팅), 통일 입력 UI는 요구 시 개발",
    day2_owner="Red Hat 컨설팅",
    ai_part="Training Hub·Kubeflow Trainer SDK")

add(id="R15", cat="AI 모델관리", sub="학습",
    req="학습 Job별 GPU 종류, 수량 등 필요한 자원을 지정, 정책에 따라 할당 할 수 있어야 함",
    short="학습 Job별 GPU 지정·정책 할당",
    phase=D1, area=AI, sup=FULL,
    day1="Trainer 자원 요청 + Hardware Profile + Kueue ResourceFlavor(GPU 종류별)·Quota 정책 구성",
    day2="정책 튜닝, 분산학습 호환성 검증",
    day2_owner="고객 운영 + Red Hat 컨설팅",
    ai_part="Kubeflow Trainer, Hardware Profile",
    ocp_part="Red Hat build of Kueue, 노드 선택 조건")

# ── AI 모델관리 / 평가 ──────────────────────────────────────────────────────
add(id="R16", cat="AI 모델관리", sub="평가",
    req="학습 데이터셋과 구분된 평가용 데이터셋을 등록, 선택하고 버전을 관리할 수 있어야 함",
    short="평가 데이터셋 등록·버전관리",
    phase=D12, area=AI, sup=PART,
    day1="학습·평가 버킷 분리, Connection 등록, 폴더 기반 버전 규칙 예제",
    day2="데이터셋 카탈로그·메타정보 관리 화면 개발, S3 버전관리 정책",
    day2_owner="SI/고객 개발",
    ai_part="Connections(S3)",
    extra="S3 버전관리 기능, 카탈로그 화면 개발",
    check="평가 데이터셋 전용 등록·버전관리 화면은 제품에 없음")

add(id="R17", cat="AI 모델관리", sub="평가",
    req="등록된 평가 Dataset을 기반으로 평가 수행 가능",
    short="평가 데이터셋 기반 평가 수행",
    phase=D12, area=AI, sup=FULL,
    day1="TrustyAI LM-Eval로 샘플 데이터셋 평가 실행(Workbench·Pipeline)",
    day2="우리카드 자체 평가 코드·custom task 연동",
    day2_owner="SI/고객 연동",
    ai_part="TrustyAI LM-Eval, EvalHub, Data Science Pipelines",
    check="EvalHub 등 신규 평가 기능은 버전별 GA/TP 상태 확인")

add(id="R18", cat="AI 모델관리", sub="평가",
    req="정량평가 메트릭을 설정하여 답변 정확성, 관련성 등 평가를 수행해야 함",
    short="정량 메트릭(정확성·관련성)",
    phase=D12, area=AI, sup=PART,
    day1="표준 벤치마크 메트릭 평가 예제",
    day2="업무 기준 한국어 관련성·답변품질 지표 custom task 개발",
    day2_owner="SI/고객 개발 + Red Hat 컨설팅",
    ai_part="TrustyAI LM-Eval(표준 메트릭)",
    extra="업무 지표 정의·평가 로직 개발")

# ── AI 모델관리 / 추론 ──────────────────────────────────────────────────────
add(id="R19", cat="AI 모델관리", sub="추론",
    req="평가 기준을 충족한 모델을 관리하고 서빙 단계로 전환할 수 있어야 함",
    short="평가 통과 모델 서빙 전환",
    phase=D12, area=AI, sup=PART,
    day1="평가 결과를 Registry 속성에 기록 → 서빙 배포 예제",
    day2="기준 충족 시 자동 승인·전환(승격 게이트) 개발",
    day2_owner="SI/고객 개발",
    ai_part="Model Registry, KServe, Data Science Pipelines",
    ocp_part="OpenShift GitOps·Pipelines",
    extra="승격 게이트 개발")

add(id="R20", cat="AI 모델관리", sub="추론",
    req="모델 저장소에 등록, 승인된 모델을 추론환경에 배포할 수 있어야 함",
    short="승인 모델 추론 배포",
    phase=D1, area=AI, sup=FULL,
    day1="Registry 등록 모델 → 추론환경 배포",
    day2="승인 판정·강제는 운영 정책 / PCMS 연동(R41)",
    day2_owner="고객 운영",
    ai_part="Model Registry → KServe 배포",
    check="승인 강제 통제는 R41(PCMS)로 분리")

add(id="R21", cat="AI 모델관리", sub="추론",
    req="vLLM등 표준화된 서빙엔진 기반 모델 추론 서비스를 구성할 수 있어야 함",
    short="vLLM 기반 추론 서비스",
    phase=D1, area=AI, sup=FULL,
    day1="KServe + vLLM 런타임 구성, 모델 배포",
    day2="llm-d 분산 추론·양자화(LLM Compressor) 등 성능 최적화",
    day2_owner="Red Hat 컨설팅",
    ai_part="KServe, vLLM(Red Hat AI Inference Server), llm-d",
    check="모델 형식·B300 호환 vLLM 버전, llm-d 사용 조건 확인")

add(id="R22", cat="AI 모델관리", sub="추론",
    req="배포된 모델을 표준 인터페이스(API)를 통해 호출 할 수 있어야 함",
    short="표준 API 호출",
    phase=D1, area=AI, sup=FULL,
    day1="OpenAI 호환 API 엔드포인트 제공·호출 검증",
    day2="호출 시스템 인증·timeout 연동",
    day2_owner="SI/고객 연동",
    ai_part="vLLM OpenAI 호환 API, KServe 엔드포인트",
    ocp_part="Route·Gateway 노출")

add(id="R23", cat="AI 모델관리", sub="추론",
    req="Continuous Batching등 다수의 동시 추론 요청을 효율적으로 처리할 수 있어야 함",
    short="Continuous Batching 동시 처리",
    phase=D1, area=AI, sup=FULL,
    day1="vLLM continuous batching 기본 제공",
    day2="목표 동시성·TPS 부하시험 및 튜닝, 오토스케일링",
    day2_owner="Red Hat 컨설팅·기술지원",
    ai_part="vLLM, KServe 오토스케일링",
    check="목표 TPS 달성 튜닝은 컨설팅/기술지원 범위로 명시")

# ── API Gateway ─────────────────────────────────────────────────────────────
add(id="R24", cat="API Gateway", sub="AI API 통합관리",
    req="AI서비스 및 모델 호출을 위한 단일 API Gateway 구성",
    short="단일 AI API Gateway",
    phase=D12, area=AI, sup=PART,
    day1="Gateway API + MaaS 구성, 대표 LLM 공통 진입점 제공",
    day2="OCR·KMS 등 비 LLM 서비스 편입, 라우팅 정책 확장",
    day2_owner="Red Hat 컨설팅(MaaS 정책) + SI/고객 연동",
    ai_part="Models-as-a-Service(MaaS)",
    ocp_part="Gateway API, MetalLB(LoadBalancer)",
    extra="Red Hat Connectivity Link(RHCL) — 구독 범위 확인 / 비 LLM 통합 시 기존·별도 API GW",
    check="MaaS Gateway는 LoadBalancer 전제 → MetalLB 필요(미사용 시 Route 우회는 공식 가이드 아님, RFE OCPSTRAT-3781) / MaaS 멀티테넌시 TP(3.5)")

add(id="R25", cat="API Gateway", sub="AI API 통합관리",
    req="AI서비스 및 모델 등록, 배포, 버전 및 라우팅 통합 관리",
    short="등록·배포·버전·라우팅 통합관리",
    phase=D12, area=AI, sup=PART,
    day1="대표 모델 등록(Registry)→배포(Serving)→Gateway 연결을 제품 화면·설정으로 수행",
    day2="단일 통합관리 화면·이력 연결 개발",
    day2_owner="SI/고객 개발·연동",
    ai_part="Model Registry, Model Serving, MaaS",
    extra="통합 관리 화면 연동 개발")

add(id="R26", cat="API Gateway", sub="인증 및 보안관리",
    req="API 호출 주체에 대한 인증, 인가 및 접근 통제 수행",
    short="API 인증·인가·접근통제",
    phase=D12, area=AI, sup=PART,
    day1="MaaS API Key·인가 정책으로 대표 모델 허용/거부 정책 적용·검증",
    day2="API Key 발급·회수·로테이션 운영, 사내 IAM/OIDC 연동 확장",
    day2_owner="고객 운영 + Red Hat 컨설팅",
    ai_part="MaaS(API Key·티어 정책), 모델 엔드포인트 토큰 인증",
    ocp_part="OpenShift OAuth·RBAC",
    extra="RHCL(AuthPolicy·Authorino)",
    check="MaaS 외부 OIDC 연동은 TP — 버전 확인")

add(id="R27", cat="API Gateway", sub="인증 및 보안관리",
    req="서비스별 보안정책과 감사로그 통합 관리",
    short="보안정책·감사로그 통합",
    phase=D12, area=OCP, sup=PART,
    day1="RBAC·NetworkPolicy·Gateway 정책 기본 구성, 감사로그 항목·조회 방법 정리, 로그 포워딩 기본 구성",
    day2="SIEM·기존 로그 수집계 연동, 통합 관리 화면 개발",
    day2_owner="SI/고객 연동",
    ocp_part="API 감사로그, OpenShift Logging(LokiStack·로그 포워딩), RBAC, NetworkPolicy",
    ai_part="MaaS·Gateway 호출 로그",
    extra="RHACS(보안정책 통합, 별도 구독), 고객 SIEM",
    check="플랫폼 감사로그와 모델 호출 로그는 별도 — 통합 범위 합의")

add(id="R28", cat="API Gateway", sub="트래픽 및 서비스 제어",
    req="AI서비스 및 모델별 처리용량을 고려하여 호출량, 동시 요청 제어",
    short="호출량·동시 요청 제어",
    phase=D12, area=AI, sup=PART,
    day1="대표 모델 요청·토큰 사용량 제한 + vLLM 동시성 설정, 초과 동작 확인",
    day2="테넌트·모델·사용자별 쿼터 정책 운영, 사용량 리포트",
    day2_owner="고객 운영 + Red Hat 컨설팅",
    ai_part="MaaS Rate·Token Limit, vLLM 동시 처리 설정",
    extra="RHCL(Limitador)",
    check="전역 동시성 제어는 Gateway 정책 별도 구성·검증")

add(id="R29", cat="API Gateway", sub="트래픽 및 서비스 제어",
    req="부하분산 및 장애 격리를 통해 안정적인 서비스 제공 가능",
    short="부하분산·장애 격리",
    phase=D1, area=OCP, sup=PART,
    day1="Service·Gateway 부하분산, 복제본·Health Probe·PDB, 프로젝트 격리, HA 설계",
    day2="장애 시나리오 훈련, 용량 계획",
    day2_owner="고객 운영 + Red Hat 컨설팅",
    ocp_part="Service·Route·Gateway, Deployment 복제본, Probe, PodDisruptionBudget",
    ai_part="KServe 복제본·오토스케일링",
    check="운영 GPU 1노드 → GPU 노드 장애 시 HA 불가, 여유 자원 필요(사전 합의)")

# ── 모니터링 ───────────────────────────────────────────────────────────────
add(id="R30", cat="모니터링", sub="통합 모니터링 체계 구축",
    req="GPU·서버·K8s·AI 서비스의 상태 및 성능을 통합적으로 모니터링",
    short="통합 모니터링",
    phase=D12, area=OCP, sup=PART,
    day1="OpenShift 기본 모니터링 + 사용자 워크로드 모니터링 활성화, 대시보드 예제",
    day2="통합 화면·알림 체계 구성, 기존 관제 시스템 연동",
    day2_owner="SI/고객 연동 + Red Hat 컨설팅",
    ocp_part="OpenShift Monitoring(Prometheus·Alertmanager·Thanos), 콘솔 대시보드, Cluster Observability Operator",
    ai_part="모델 서빙 메트릭",
    extra="Grafana(커뮤니티 오퍼레이터 — Red Hat 지원 대상 아님)",
    check="Grafana 사용 시 지원 범위 명시")

add(id="R31", cat="모니터링", sub="통합 모니터링 체계 구축",
    req="GPU Utilization, VRAM, 온도, 전력, ECC Error 등 주요 GPU 상태 및 성능지표 모니터링",
    short="GPU 상태·성능 지표",
    phase=D1, area=OCP, sup=FULL,
    day1="DCGM Exporter 지표 수집, OpenShift 콘솔(Observe) GPU 대시보드 구성",
    day2="임계치 알림 룰 운영",
    day2_owner="고객 운영",
    ocp_part="NVIDIA GPU Operator DCGM Exporter, OpenShift Monitoring",
    extra="NVIDIA GPU Operator(기술지원 주체 NVIDIA)",
    check="B300 ECC·전력·MIG 지표 collector 설정 확인")

add(id="R32", cat="모니터링", sub="통합 모니터링 체계 구축",
    req="AI서비스별 TPS, TTFT, Latency 등의 정보를 수집 및 모니터링",
    short="AI 서비스 TPS·TTFT·Latency",
    phase=D12, area=AI, sup=PART,
    day1="vLLM 지표(TTFT·토큰 처리량·지연) 대시보드 구성",
    day2="비 LLM 서비스(OCR 등) 계측 개발, TPS 정의·측정 위치·집계식 합의",
    day2_owner="SI/고객 개발",
    ai_part="vLLM 메트릭, OpenShift AI 모델 메트릭",
    ocp_part="사용자 워크로드 모니터링",
    extra="비 LLM 앱 계측 개발")

# ── 기존 AI 서비스 이전 / 인증 ──────────────────────────────────────────────
add(id="R33", cat="기존 AI 서비스 이전", sub="서비스 이전",
    req="기 구축(혹은 구축 진행 中) AI 서비스(코드어시스턴트, KMS, AI OCR)의 GPU클러스터 이전을 지원하여야 함",
    short="기존 AI 서비스 3종 이전",
    phase=D2, area=OCP, sup=OUT,
    day1="이전 대상 분석(범위·수량·의존성), 샘플 앱 컨테이너화·배포 절차 예제",
    day2="3개 서비스 실제 이전(컨테이너화·API 이전·테스트)",
    day2_owner="SI 마이그레이션·테스트",
    ocp_part="컨테이너 실행환경, Migration Toolkit for Applications(이전 분석)",
    ai_part="서비스 내 모델을 vLLM·KServe 서빙으로 전환",
    extra="마이그레이션·테스트 인력",
    check="이전 범위·수량 파악 필요")

add(id="R34", cat="인증", sub="SSO연동",
    req="관리자 페이지나 기타 포털에 대해 SSO나 2차인증을 지원하여야 함",
    short="SSO·2차 인증",
    phase=D12, area=OCP, sup=FULL,
    day1="OpenShift OAuth–사내 IdP(OIDC·LDAP) 연동 → 콘솔·OpenShift AI 대시보드 SSO",
    day2="IdP 기반 MFA 강제, 자체 포털 적용",
    day2_owner="고객 IdP + SI(자체 포털)",
    ocp_part="OpenShift OAuth(IdP 연동), Red Hat build of Keycloak(IdP 브로커 필요 시)",
    ai_part="OpenShift AI 대시보드(OpenShift 인증 연동)",
    extra="고객 IdP(MFA 기능)",
    check="MFA는 IdP에서 강제 / Keycloak 구독 포함 범위 확인")

# ── 인프라구성 ─────────────────────────────────────────────────────────────
add(id="R35", cat="인프라구성", sub="GPU 클러스터 구축",
    req="GPU 서버 운영 1노드, 개발 1노드 및 CPU영역 서버 운영 1노드, 개발 1노드의 클러스터를 구축하여야 함",
    short="4노드 GPU 클러스터 구축",
    phase=D1, area=OCP, sup=FULL,
    day1="폐쇄망 OpenShift 설치·GPU 노드 구성, Control Plane 배치 재설계",
    day2="노드 증설·업그레이드",
    day2_owner="고객 운영 + Red Hat 기술지원",
    ocp_part="OpenShift 설치(폐쇄망), NVIDIA GPU Operator",
    check="Control Plane 3노드 기본 → 서버 4대로 개발/운영 2클러스터 불가. 단일 클러스터+논리 분리 또는 Control Plane 추가 확보 재협의 / 운영 GPU 1노드 HA 부재")

add(id="R36", cat="인프라구성", sub="GPU 클러스터 구축",
    req="향후 외부 시스템 연계 시, 내부 데이터의 유출이 발생하지 않도록 확장성을 고려한 구조로 설계",
    short="데이터 유출 방지 확장 구조",
    phase=D12, area=OCP, sup=PART,
    day1="NetworkPolicy·Egress 통제(EgressFirewall·Egress IP) 기본 구성, 폐쇄망 구조 설계",
    day2="DLP·반출/마스킹 정책, 망연계 설계, LLM 입출력 Guardrails 적용",
    day2_owner="고객 보안정책 + SI 연동",
    ocp_part="NetworkPolicy, AdminNetworkPolicy, EgressFirewall, Egress IP",
    ai_part="TrustyAI Guardrails(PII 탐지·마스킹)",
    extra="DLP·망연계 솔루션")

# ── 기술이전 ───────────────────────────────────────────────────────────────
add(id="R37", cat="기술이전", sub="기술이전 및 운영자 교육",
    req="플랫폼 구축·운영·장애대응 및 AI 서비스 배포 등에 대한 기술이전 및 교육 수행",
    short="운영자 기술이전·교육",
    phase=D12, area=OCP, sup=SVC,
    day1="구축 완료 시 구축·운영·장애대응·배포 교육 및 인수인계(교재·실습·산출물)",
    day2="운영 중 심화 교육, 기술 내재화 지원",
    day2_owner="Red Hat Training·Consulting",
    ocp_part="Red Hat Training(DO180·DO280 등 OpenShift 운영 과정)",
    ai_part="AI 서비스 배포 실습",
    extra="Red Hat Consulting 기술이전")

add(id="R38", cat="기술이전", sub="기술이전 및 운영자 교육",
    req="내부개발 인력들이 자체적으로 AI모델을 개발/운영 할 수 있도록 플랫폼 교육 실시",
    short="내부 개발자 AI 플랫폼 교육",
    phase=D12, area=AI, sup=SVC,
    day1="AI267 등 OpenShift AI 공식 교육",
    day2="고객 환경 실습 워크숍(Workbench·Pipelines·Training Hub·평가·모델 배포), 독립 수행 검증",
    day2_owner="Red Hat Training·Consulting",
    ai_part="Red Hat Training AI267",
    extra="워크숍은 컨설팅 범위")

# ── 오픈소스 ───────────────────────────────────────────────────────────────
add(id="R39", cat="오픈소스", sub="패치 및 업그레이드",
    req="프로젝트에 적용되는 오픈소스의 최신성을 보장하여야 함",
    short="오픈소스 최신성",
    phase=D2, area=COM, sup=SVC,
    day1="지원 버전·보안 패치 기준 합의(구축 버전 선정)",
    day2="정기 릴리스·업그레이드로 최신성 유지(업스트림을 하드닝한 제품 형태)",
    day2_owner="Red Hat 구독(기술지원)",
    ocp_part="OpenShift 릴리스·EUS 라이프사이클",
    ai_part="OpenShift AI 릴리스 채널(빠른 업스트림 반영)",
    extra="비제품 OSS는 별도 유지관리",
    check="'최신 업스트림 상시 보장'이 아닌 'Red Hat 지원 버전 기준'으로 합의")

add(id="R40", cat="오픈소스", sub="패치 및 업그레이드",
    req="플랫폼에 적용되는 오픈소스의 구성, 버전, 라이선스, 취약점, EoS/EoL 정보를 체계적으로 관리하고, 보안 패치 및 버전 업그레이드 등 지속적인 유지관리 체계를 제공",
    short="OSS 자산·취약점·EOL 관리",
    phase=D2, area=COM, sup=PART,
    day1="구독 제품 CVE·EOL 관리 방법 안내, 폐쇄망 업데이트 경로(OSUS·oc-mirror) 구성",
    day2="정기 패치·업그레이드 운영, SCA/SBOM 운영 체계",
    day2_owner="Red Hat 구독 + 고객 운영(별도 도구)",
    ocp_part="Red Hat 제품 라이프사이클·Errata·CVE 정보, OpenShift Update Service(폐쇄망)",
    ai_part="OpenShift AI 라이프사이클·Errata",
    extra="RHACS·Quay(취약점 스캔), Trusted Profile Analyzer(SBOM) — 별도 구독",
    check="구독 제품 유지관리와 전체 OSS 자산 관리를 구분")

# ── 기타 ───────────────────────────────────────────────────────────────────
add(id="R41", cat="기타", sub="변경관리",
    req="당사 변경관리 프로세스를 준용하여 PCMS(변경관리 시스템)와 연계하여야 함(쿠버네티스 컨테이너 및 AI모델 전반)",
    short="PCMS 변경관리 연계",
    phase=D2, area=OCP, sup=OUT,
    day1="OpenShift GitOps·Pipelines 배포 흐름 예제",
    day2="PCMS 연동 개발(승인 후 배포 강제)",
    day2_owner="SI 개발·연동",
    ocp_part="OpenShift GitOps(Argo CD), OpenShift Pipelines(Tekton)",
    ai_part="Data Science Pipelines(모델 배포 흐름)",
    extra="PCMS API·EAI 연동 개발",
    check="PCMS 표준 커넥터 없음")

assert len(R) == 41, len(R)
assert [r["id"] for r in R] == [f"R{i:02d}" for i in range(1, 42)]

# ── 확인 필요 사항 / 리스크 ───────────────────────────────────────────────
RISKS = [
    ("서버 4대 클러스터 구성", "R01, R35",
     "Control Plane 3노드가 기본이라 서버 4대로 개발/운영 2클러스터를 만들 수 없음",
     "① 단일 클러스터(Control Plane 3대는 소형 서버·VM으로 확보) + 프로젝트 기반 개발/운영 논리 분리 ② 환경별 2노드+Arbiter 토폴로지(지원 버전·HW 요건 확인) ③ 환경별 SNO(HA 없음, 운영 비권장) — 제안 전 고객 합의"),
    ("운영 GPU 1노드", "R29, R35",
     "GPU 노드 장애 시 운영 추론 중단(GPU HA 불가)",
     "GPU 노드 추가 또는 장애 시 개발 GPU 전환 절차·SLA를 제안서에 명시"),
    ("B300 GPU 지원 매트릭스", "R04, R21, R31",
     "최신 세대 GPU — GPU Operator·드라이버·vLLM·OpenShift AI 지원 버전 의존",
     "제안 버전 확정 전 지원 매트릭스 검증, 폐쇄망 드라이버 이미지 반입 계획 수립"),
    ("MaaS 구독·성숙도", "R24, R26, R28",
     "MaaS 정책(인증·Rate Limit)은 RHCL 구성요소 사용, 멀티테넌시·외부 OIDC는 TP(3.5)",
     "RHCL 구독 포함 여부 확인, TP 기능은 제안서에 '기술 검토' 수준으로 표기"),
    ("MaaS Gateway LoadBalancer", "R24",
     "MaaS Gateway는 LoadBalancer 서비스 전제 — 온프렘은 MetalLB 필요",
     "MetalLB(OCP 포함) L2/BGP 구성 협의. 미사용 시 ClusterIP+Route 우회는 공식 가이드 아님(RFE OCPSTRAT-3781)"),
    ("스토리지·DB 선행 조건", "R06, R10, R11, R16, R27",
     "데이터셋·모델·파이프라인 아티팩트·LokiStack용 S3, Registry·Pipelines·MaaS용 DB 필요",
     "고객 보유 S3 활용 또는 ODF(별도 구독) 산정, 구성요소별 DB 엔진·외부 DB 정책 확정"),
    ("모델 폐쇄망 반입", "R10",
     "대용량 가중치는 기존 컨테이너 이미지 반입 절차로 처리하기 어려움",
     "ModelCar(OCI)·S3 반입 경로를 보안팀과 사전 협의"),
    ("Grafana 지원 범위", "R30",
     "Grafana는 커뮤니티 오퍼레이터로 Red Hat 지원 대상 아님",
     "OpenShift 콘솔 대시보드·COO를 기본으로 제안, Grafana는 지원 범위 외로 명시"),
    ("신규 기능 GA/TP 상태", "R11, R13, R17, R21",
     "MLflow·EvalHub·Training Hub(LoRA)·llm-d 등은 버전에 따라 지원 상태가 다름",
     "제안 버전(OpenShift AI 3.x) 기준 GA/TP 확인 후 지원 수준 표기 확정"),
    ("오픈소스 최신성 해석", "R39, R40",
     "'최신 업스트림 상시 보장'은 제품 구독으로 약속 불가",
     "'Red Hat 지원 버전·보안 패치 기준'으로 합의, 비제품 OSS·고객 앱 의존성은 별도 관리"),
    ("NVIDIA GPU Operator 지원 주체", "R02, R04, R31",
     "GPU Operator는 NVIDIA 인증 오퍼레이터 — 기술지원 주체 NVIDIA",
     "NVIDIA 기술지원 체계(예: NVIDIA AI Enterprise) 포함 여부 확인"),
]

# ── 구독·서비스 구성 ──────────────────────────────────────────────────────
SUBS = [
    ("컨테이너 플랫폼", "Red Hat OpenShift Container Platform",
     "GitOps·Pipelines·Logging·Monitoring·MetalLB·Gateway API·Red Hat build of Kueue·MTA 포함", "OCP"),
    ("AI", "Red Hat OpenShift AI",
     "MaaS·Model Registry·KServe/vLLM·llm-d·Training Hub·Kubeflow Trainer·TrustyAI·Pipelines 포함", "AI"),
    ("파트너", "NVIDIA GPU Operator", "NVIDIA 인증 오퍼레이터(GPU 드라이버·MIG·DCGM)", "R02, R04, R31, R35"),
    ("별도 구독(확인)", "Red Hat Connectivity Link", "MaaS 인증·Rate Limit 정책 구성요소", "R24, R26, R28"),
    ("별도 구독(선택)", "OpenShift Data Foundation", "고객 S3 보유 시 불필요", "R06, R10, R16, R27"),
    ("별도 구독(선택)", "RHACS · Quay · Trusted Profile Analyzer", "보안정책·이미지 취약점·SBOM 관리", "R27, R40"),
    ("서비스", "Red Hat Consulting", "설계·정책 수립·튜닝·기술이전", "R03, R09, R24, R35, R37, R38"),
    ("서비스", "Red Hat Training", "DO180·DO280(OpenShift), AI267(OpenShift AI)", "R37, R38"),
    ("서비스", "기술지원·TAM", "구독 기술지원, 라이프사이클·패치", "R09, R39, R40"),
    ("고객/SI", "개발·연동·마이그레이션", "제품 범위 외 개발 항목", "R33, R41 + Day2 개발 항목"),
]


def ids_where(**cond):
    return [r["id"] for r in R if all(r[k] == v for k, v in cond.items())]


# 구독 행의 "커버 요건"을 영역 기준으로 계산
_ocp_ids = [r["id"] for r in R if r["area"] in (OCP, COM) or r["ocp_part"]]
_ai_ids = [r["id"] for r in R if r["area"] in (AI, COM) or r["ai_part"]]
