# -*- coding: utf-8 -*-
"""rfp_data.py → README.md + 요건매트릭스.xlsx 생성."""
import math
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from rfp_data import (AI, COM, D1, D12, D2, FULL, LEGEND_AREA, LEGEND_PHASE,
                      LEGEND_SUPPORT, OCP, OUT, PART, R, RISKS, SOURCE_1021,
                      SOURCE_V04, SUBS, SVC)

OUT_DIR = Path(sys.argv[1])
XLSX_NAME = "우리카드_AI플랫폼_Day1-Day2_요건매트릭스.xlsx"
TODAY = "2026-11-04"

AREA_LABEL = {OCP: "🐳 컨테이너 플랫폼", AI: "🧠 AI", COM: "🔗 공통"}
AREA_PRODUCT = {OCP: "OpenShift", AI: "OpenShift AI", COM: "OpenShift + OpenShift AI"}
PHASES = [D1, D12, D2]
AREAS = [OCP, AI, COM]
SUPS = [FULL, PART, OUT, SVC]

# 구독 행의 커버 요건(주 영역 기준) 채우기
_cov = {
    "OCP": ", ".join(r["id"] for r in R if r["area"] in (OCP, COM)),
    "AI": ", ".join(r["id"] for r in R if r["area"] in (AI, COM)),
}
SUBS = [(a, b, c, _cov.get(d, d)) for a, b, c, d in SUBS]


def cnt(**cond):
    return sum(1 for r in R if all(r[k] == v for k, v in cond.items()))


def esc(s):
    return s.replace("|", "\\|")


def components(r):
    """주 영역 구성요소 + 타 영역 연계."""
    if r["area"] == OCP:
        main, other, other_lbl = r["ocp_part"], r["ai_part"], "AI 연계"
    elif r["area"] == AI:
        main, other, other_lbl = r["ai_part"], r["ocp_part"], "OpenShift 기반"
    else:
        parts = []
        if r["ocp_part"]:
            parts.append(f"**OpenShift**: {r['ocp_part']}")
        if r["ai_part"]:
            parts.append(f"**OpenShift AI**: {r['ai_part']}")
        if r["extra"]:
            parts.append(f"＋ 별도·타사: {r['extra']}")
        return "<br>".join(parts)
    s = main
    if other:
        s += f"<br>↔ {other_lbl}: {other}"
    if r["extra"]:
        s += f"<br>＋ 별도·타사: {r['extra']}"
    return s


# ═════════════════════════════════════════════════════════════════════════
# Markdown
# ═════════════════════════════════════════════════════════════════════════
def md():
    L = []
    a = L.append
    total = len(R)
    a("# 우리카드 AI 플랫폼 RFP — Day1 / Day2 요건 정리 및 Red Hat 지원 범위")
    a("")
    a(f"> **대상**: 우리카드 AI 플랫폼(Kubernetes 기반 GPU 통합·MLOps) 제안요청사항 **{total}건**  ")
    a(f"> **원본**: [우리카드_AI_플랫폼_요구사항_지원분석_v0_4]({SOURCE_V04}) (2026-10-29), "
      f"[AI_플랫폼_요구사항_검토_Red_Hat_AI_기능_비교]({SOURCE_1021}) (2026-10-21)  ")
    a("> **판단 기준 버전**: OpenShift 4.22 · OpenShift AI 3.5 — 제안 버전 확정 시 GA/TP 상태 재확인  ")
    a(f"> **엑셀**: [`{XLSX_NAME}`](./{XLSX_NAME.replace(' ', '%20')}) — 필터 가능한 전체 매트릭스(원문·Day1·Day2·구성요소·확인사항)  ")
    a(f"> **작성일**: {TODAY}")
    a("")
    a("---")
    a("")

    # 0. 한눈 요약
    a("## 0. 한눈 요약")
    a("")
    a("### 단계 × 제공 영역 (건수)")
    a("")
    a("| 단계 | 🐳 컨테이너 플랫폼<br>(OpenShift) | 🧠 AI<br>(OpenShift AI) | 🔗 공통 | 합계 |")
    a("|---|:-:|:-:|:-:|:-:|")
    for p in PHASES:
        row = [cnt(phase=p, area=x) for x in AREAS]
        a(f"| **{p}** | {row[0]} | {row[1]} | {row[2]} | **{sum(row)}** |")
    cols = [cnt(area=x) for x in AREAS]
    a(f"| **합계** | **{cols[0]}** | **{cols[1]}** | **{cols[2]}** | **{total}** |")
    a("")
    a("### Red Hat 지원 수준 (건수)")
    a("")
    a("| " + " | ".join(f"{s} {n}" for s, n, _ in LEGEND_SUPPORT) + " |")
    a("|" + ":-:|" * len(LEGEND_SUPPORT))
    a("| " + " | ".join(f"**{cnt(sup=s)}**" for s, _, _ in LEGEND_SUPPORT) + " |")
    a("")
    full_d1 = sum(1 for r in R if r["sup"] == FULL and r["phase"] == D1)
    ai_d12 = cnt(area=AI, phase=D12)
    a("### 핵심 메시지")
    a("")
    a(f"1. **AI 요건이 {cols[1]}건으로 과반**이지만, 그중 **{ai_d12}건은 Day1→Day2**입니다. "
      "OpenShift AI가 기능(학습·평가·Registry·서빙·MaaS)은 제공하고, 고객 정책·데이터 반영"
      "(업무 평가지표, 승격 게이트, 이력 자동화, MaaS 정책)은 Day2 개발·컨설팅입니다. "
      "→ 제안서에 **\"Day1 = 제품 기능 구성·샘플 1건 검증 / Day2 = 정책 반영·개발\"**을 명시해 범위 분쟁을 막습니다.")
    a(f"2. **Day1 단독 {cnt(phase=D1)}건 중 {full_d1}건은 제품 기능(●)만으로 충족**됩니다. GPU 인프라(MIG·스케줄링·DCGM)와 추론(vLLM·API·Continuous Batching)이 중심이며, 나머지 1건(R29 부하분산·장애 격리)은 GPU 1노드 제약으로 ◐입니다.")
    a("3. **컨테이너 플랫폼 영역은 Day1 인프라 결정이 전체를 좌우합니다.** 서버 4대로는 개발/운영 2클러스터가 불가(R35)하고, "
      "운영 GPU 1노드라 GPU HA가 없습니다(R29). 제안 전 토폴로지 합의가 1순위입니다.")
    a(f"4. **제품 범위 외(○) {cnt(sup=OUT)}건** — 기존 AI 서비스 이전(R33), PCMS 연동(R41)은 SI 개발·마이그레이션 범위로 분리합니다.")
    a("5. **별도 구독 확인**: MaaS 정책용 **Red Hat Connectivity Link**, 데이터셋·모델용 **S3 스토리지(ODF 또는 고객 보유)**, "
      "보안·SBOM용 RHACS·Quay·Trusted Profile Analyzer(선택).")
    a("")
    a("---")
    a("")

    # 1. 분류 기준
    a("## 1. 분류 기준")
    a("")
    a("### 1-1. Day1 / Day2")
    a("")
    a("기존 v0.4 시트의 **\"1단계(예제제공) / 2단계(정책반영)\"** 및 **\"1차 / 2차\"** 구분을 Day1/Day2로 매핑했습니다.")
    a("")
    a("| 단계 | 의미 |")
    a("|---|---|")
    for p, d in LEGEND_PHASE:
        a(f"| **{p}** | {d} |")
    a("")
    a("### 1-2. AI vs 컨테이너 플랫폼 구분 원칙")
    a("")
    a("| 영역 | 제공 제품 | 판단 기준 |")
    a("|---|---|---|")
    for k, prod, d in LEGEND_AREA:
        a(f"| {AREA_LABEL[k]} | {prod} | {d} |")
    a("")
    a("계층으로 보면 아래와 같습니다. 위로 갈수록 OpenShift AI, 아래로 갈수록 OpenShift가 담당합니다.")
    a("")
    a("| 계층 | 제공 | 주요 구성요소 | 관련 요건 |")
    a("|---|---|---|---|")
    a("| AI 서비스 접점 (API·Gateway) | 🧠 OpenShift AI | MaaS(API Key·Rate/Token Limit), OpenAI 호환 API | R22, R24–R26, R28 |")
    a("| 모델 라이프사이클 (MLOps) | 🧠 OpenShift AI | Workbench, Data Science Pipelines, Training Hub·Kubeflow Trainer, TrustyAI LM-Eval, Model Registry, KServe·vLLM·llm-d | R06–R08, R10–R21, R23, R32 |")
    a("| AI 자원 추상화 | 🔗 공통 | Hardware Profile(AI) + Red Hat build of Kueue·ResourceQuota(OpenShift) | R02, R05, R15 |")
    a("| GPU 인프라 | 🐳 OpenShift + NVIDIA | NVIDIA GPU Operator(MIG·DCGM), Node Feature Discovery | R02, R04, R31 |")
    a("| 컨테이너 플랫폼 | 🐳 OpenShift | 클러스터(폐쇄망), Project·RBAC·NetworkPolicy, OAuth/IdP, Monitoring·Logging, GitOps·Pipelines, Gateway API·MetalLB | R01, R27, R29–R30, R33–R36, R41 |")
    a("| 별도 구독·타사·SI | — | RHCL, ODF/S3, RHACS·Quay·TPA, 고객 IdP·SIEM·DLP·PCMS | R24, R27, R36, R40, R41 |")
    a("")
    a("### 1-3. 지원 수준")
    a("")
    a("| 표시 | 의미 | 설명 |")
    a("|:-:|---|---|")
    for s, n, d in LEGEND_SUPPORT:
        a(f"| {s} | {n} | {d} |")
    a("")
    a("---")
    a("")

    # 2. 한 장 요약
    a("## 2. 한 장 요약 — 단계 × 영역 매트릭스")
    a("")
    a("| 단계 | 🐳 컨테이너 플랫폼 (OpenShift) | 🧠 AI (OpenShift AI) | 🔗 공통 |")
    a("|---|---|---|---|")
    for p in PHASES:
        cells = []
        for x in AREAS:
            items = [f"{r['sup']} {r['id']} {r['short']}" for r in R if r["phase"] == p and r["area"] == x]
            cells.append("<br>".join(items) if items else "—")
        a(f"| **{p}** | " + " | ".join(cells) + " |")
    a("")
    a("---")
    a("")

    # 3. Day1
    a("## 3. Day1 요건 — 구축 (1차)")
    a("")
    a(f"Day1 단독 {cnt(phase=D1)}건 + Day1→Day2 {cnt(phase=D12)}건의 Day1 범위입니다. (Day2 단독 항목의 Day1 준비 작업은 엑셀 참조)")
    a("")
    sec = {OCP: "3-1", AI: "3-2", COM: "3-3"}
    for x in AREAS:
        rows = [r for r in R if r["area"] == x and r["phase"] in (D1, D12)]
        a(f"### {sec[x]}. {AREA_LABEL[x]} — {AREA_PRODUCT[x]}로 제공 ({len(rows)}건)")
        a("")
        a("| ID | 요건 | 단계 | Day1 제공 내용 | Red Hat 구성요소 | 지원 |")
        a("|---|---|---|---|---|:-:|")
        for r in rows:
            a(f"| {r['id']} | {esc(r['short'])} | {r['phase']} | {esc(r['day1'])} | {esc(components(r))} | {r['sup']} |")
        a("")
    a("---")
    a("")

    # 4. Day2
    a("## 4. Day2 요건 — 운영·고도화 (2차)")
    a("")
    a(f"Day1→Day2 {cnt(phase=D12)}건 + Day2 단독 {cnt(phase=D2)}건입니다. "
      f"Day1 단독 {cnt(phase=D1)}건은 Day2에 일상 운영(정책 조정·업그레이드)만 필요합니다(엑셀 'Day2' 열 참조).")
    a("")
    sec = {OCP: "4-1", AI: "4-2", COM: "4-3"}
    for x in AREAS:
        rows = [r for r in R if r["area"] == x and r["phase"] in (D12, D2)]
        a(f"### {sec[x]}. {AREA_LABEL[x]} — {AREA_PRODUCT[x]} ({len(rows)}건)")
        a("")
        if not rows:
            a("해당 없음")
            a("")
            continue
        a("| ID | 요건 | 단계 | Day2 수행 내용 | 수행 주체 | 지원 |")
        a("|---|---|---|---|---|:-:|")
        for r in rows:
            a(f"| {r['id']} | {esc(r['short'])} | {r['phase']} | {esc(r['day2'])} | {esc(r['day2_owner'])} | {r['sup']} |")
        a("")
    a("---")
    a("")

    # 5. 리스크
    a("## 5. 확인 필요 사항 / 리스크 (제안 전 합의)")
    a("")
    a("| # | 항목 | 관련 요건 | 영향 | 권장 대응 |")
    a("|:-:|---|---|---|---|")
    for i, (t, ids, imp, act) in enumerate(RISKS, 1):
        a(f"| {i} | **{esc(t)}** | {ids} | {esc(imp)} | {esc(act)} |")
    a("")
    a("---")
    a("")

    # 6. 구독
    a("## 6. 필요 구독·서비스 구성")
    a("")
    a("| 구분 | 제품/서비스 | 내용 | 관련 요건 |")
    a("|---|---|---|---|")
    for g, p, d, ids in SUBS:
        a(f"| {g} | **{p}** | {esc(d)} | {ids} |")
    a("")
    a("> OpenShift·OpenShift AI 행의 관련 요건은 **주 제공 영역 기준**입니다(공통 포함). 구독 SKU·GPU 노드 산정 기준은 영업/파트너와 확인이 필요합니다.")
    a("")
    a("---")
    a("")

    # 7. 전체
    a(f"## 7. 전체 요건 매트릭스 ({total}건, 원문 대비)")
    a("")
    a("| ID | 구분 | 세부 구분 | 제안 요청 사항 (원문) | 단계 | 영역 | 지원 | 별도·타사·SI / 확인 사항 |")
    a("|---|---|---|---|---|---|:-:|---|")
    for r in R:
        note = " / ".join(x for x in (r["extra"], r["check"]) if x) or "—"
        a(f"| {r['id']} | {r['cat']} | {r['sub']} | {esc(r['req'])} | {r['phase']} | {AREA_LABEL[r['area']]} | {r['sup']} | {esc(note)} |")
    a("")
    a("---")
    a("")
    a("### 참고")
    a("")
    a("- 기존 MaaS·DB·Gateway LB 제품 요청 정리: `openshift-ai/product-requests-maas-db-lb.md` (branch `claude/admiring-fermat-mqr4q4`)")
    a("- RFE OCPSTRAT-3781 (MaaS Gateway ClusterIP 정식 지원): https://issues.redhat.com/browse/OCPSTRAT-3781")
    a("- OpenShift AI 3.5 MaaS 문서: https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/html/govern_llm_access_with_models-as-a-service/deploy-and-manage-models-as-a-service")
    a("- 재생성: `src/rfp_data.py`(요건 41건 단일 데이터)를 수정한 뒤 `cd src && python3 build.py ..` 실행 → README.md·엑셀 동시 갱신")
    a("")
    return "\n".join(L)


# ═════════════════════════════════════════════════════════════════════════
# XLSX
# ═════════════════════════════════════════════════════════════════════════
FONT = "맑은 고딕"
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
BODY = Font(name=FONT, size=10)
BOLD = Font(name=FONT, size=10, bold=True)
TITLE = Font(name=FONT, size=14, bold=True)
SUB = Font(name=FONT, size=10, italic=True, color="595959")
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="top", wrap_text=True)

PHASE_FILL = {D1: "E2EFDA", D12: "FFF2CC", D2: "FCE4D6"}
AREA_FILL = {OCP: "DDEBF7", AI: "E4DFEC", COM: "EDEDED"}
SUP_FILL = {FULL: "C6EFCE", PART: "FFEB9C", OUT: "FFC7CE", SVC: "D9E1F2"}


def fill(hex_):
    return PatternFill("solid", fgColor=hex_)


def est_lines(text, width):
    if not text:
        return 1
    # 한글은 대략 1.8자 폭, 그 외 1자 폭
    lines = 0
    for para in str(text).split("\n"):
        w = sum(1.8 if ord(c) > 0x2E80 else 1.0 for c in para)
        lines += max(1, math.ceil(w / max(width - 1, 1)))
    return lines


def header(ws, row, titles, widths=None):
    for i, t in enumerate(titles, 1):
        c = ws.cell(row=row, column=i, value=t)
        c.font, c.fill, c.alignment, c.border = HDR_FONT, HDR_FILL, CENTER, BORDER
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def autoheight(ws, row, widths, values):
    n = max(est_lines(v, w) for v, w in zip(values, widths))
    ws.row_dimensions[row].height = max(18, 14.5 * n + 3)


def xlsx(path):
    wb = Workbook()

    # ── Sheet: 요건매트릭스 ────────────────────────────────────────────
    ws = wb.active
    ws.title = "요건매트릭스"
    cols = [
        ("ID", 6), ("구분", 12), ("세부 구분", 16), ("제안 요청 사항 (원문)", 40), ("요건 요약", 22),
        ("단계", 11), ("주 제공 영역", 13), ("지원 수준", 8),
        ("Day1 (구축·1차)", 42), ("Day2 (운영·고도화·2차)", 40), ("Day2 수행 주체", 20),
        ("OpenShift AI 제공", 36), ("OpenShift 제공", 36), ("별도 구독·타사·SI", 30), ("확인 필요 사항", 36),
    ]
    header(ws, 1, [c[0] for c in cols], [c[1] for c in cols])
    widths = [c[1] for c in cols]
    for i, r in enumerate(R, start=2):
        vals = [r["id"], r["cat"], r["sub"], r["req"], r["short"], r["phase"], r["area"], r["sup"],
                r["day1"], r["day2"], r["day2_owner"], r["ai_part"] or "—", r["ocp_part"] or "—",
                r["extra"] or "—", r["check"] or "—"]
        for j, v in enumerate(vals, 1):
            c = ws.cell(row=i, column=j, value=v)
            c.font, c.alignment, c.border = BODY, WRAP, BORDER
        for j in (1, 6, 7, 8):
            ws.cell(row=i, column=j).alignment = CENTER
        ws.cell(row=i, column=1).font = BOLD
        ws.cell(row=i, column=6).fill = fill(PHASE_FILL[r["phase"]])
        ws.cell(row=i, column=7).fill = fill(AREA_FILL[r["area"]])
        ws.cell(row=i, column=8).fill = fill(SUP_FILL[r["sup"]])
        # 주 영역 제공 열 강조
        if r["area"] in (AI, COM):
            ws.cell(row=i, column=12).fill = fill(AREA_FILL[AI])
        if r["area"] in (OCP, COM):
            ws.cell(row=i, column=13).fill = fill(AREA_FILL[OCP])
        autoheight(ws, i, widths, vals)
    last = len(R) + 1
    ws.freeze_panes = "F2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{last}"
    ws.row_dimensions[1].height = 30
    note_row = last + 2
    ws.cell(row=note_row, column=1,
            value=f"출처: Google Sheets「우리카드_AI_플랫폼_요구사항_지원분석_v0_4」(2026-10-29) 제안 요청 사항 원문. "
                  f"분류(단계·영역·지원 수준)는 OpenShift 4.22 · OpenShift AI 3.5 기준 판단이며 제안 버전 확정 시 재확인 필요.").font = SUB
    ws.cell(row=note_row + 1, column=1,
            value="열 L·M 음영 = 해당 요건의 주 제공 제품. 단계·영역·지원 수준 값을 바꾸면 '요약' 시트 건수가 자동 갱신됩니다.").font = SUB

    # ── Sheet: 요약 ────────────────────────────────────────────────────
    sm = wb.create_sheet("요약", 0)
    for col, w in zip("ABCDEF", (24, 22, 22, 22, 12, 60)):
        sm.column_dimensions[col].width = w
    sm["A1"] = "우리카드 AI 플랫폼 RFP — Day1/Day2 요건 정리 및 Red Hat 지원 범위"
    sm["A1"].font = TITLE
    sm["A2"] = f"제안요청사항 {len(R)}건 · 작성일 {TODAY} · 원본: 우리카드_AI_플랫폼_요구사항_지원분석_v0_4"
    sm["A2"].font = SUB

    # 표1 단계 × 영역
    sm["A4"] = "① 단계 × 제공 영역 (건수, '요건매트릭스' 시트 기준 자동 집계)"
    sm["A4"].font = BOLD
    hdr = ["단계", "컨테이너 플랫폼\n(OpenShift)", "AI\n(OpenShift AI)", "공통\n(OpenShift + AI)", "합계"]
    for j, t in enumerate(hdr, 1):
        c = sm.cell(row=5, column=j, value=t)
        c.font, c.fill, c.alignment, c.border = HDR_FONT, HDR_FILL, CENTER, BORDER
    sm.row_dimensions[5].height = 32
    rng_p = f"요건매트릭스!$F$2:$F${last}"
    rng_a = f"요건매트릭스!$G$2:$G${last}"
    rng_s = f"요건매트릭스!$H$2:$H${last}"
    for i, p in enumerate(PHASES):
        row = 6 + i
        c = sm.cell(row=row, column=1, value=p)
        c.font, c.border, c.fill, c.alignment = BOLD, BORDER, fill(PHASE_FILL[p]), CENTER
        for j, x in enumerate(AREAS, 2):
            c = sm.cell(row=row, column=j, value=f'=COUNTIFS({rng_p},"{p}",{rng_a},"{x}")')
            c.font, c.border, c.alignment = BODY, BORDER, CENTER
        c = sm.cell(row=row, column=5, value=f"=SUM(B{row}:D{row})")
        c.font, c.border, c.alignment = BOLD, BORDER, CENTER
    trow = 6 + len(PHASES)
    c = sm.cell(row=trow, column=1, value="합계")
    c.font, c.border, c.alignment = BOLD, BORDER, CENTER
    for j in range(2, 6):
        col = get_column_letter(j)
        c = sm.cell(row=trow, column=j, value=f"=SUM({col}6:{col}{trow - 1})")
        c.font, c.border, c.alignment = BOLD, BORDER, CENTER

    # 표2 지원 수준
    r0 = trow + 2
    sm.cell(row=r0, column=1, value="② Red Hat 지원 수준 (건수, 자동 집계)").font = BOLD
    for j, t in enumerate(["표시", "의미", "건수", "", "", "설명"], 1):
        if t:
            c = sm.cell(row=r0 + 1, column=j, value=t)
            c.font, c.fill, c.alignment, c.border = HDR_FONT, HDR_FILL, CENTER, BORDER
    for i, (s, n, d) in enumerate(LEGEND_SUPPORT):
        row = r0 + 2 + i
        c = sm.cell(row=row, column=1, value=s)
        c.font, c.border, c.alignment, c.fill = BOLD, BORDER, CENTER, fill(SUP_FILL[s])
        c = sm.cell(row=row, column=2, value=n)
        c.font, c.border, c.alignment = BODY, BORDER, WRAP
        c = sm.cell(row=row, column=3, value=f'=COUNTIF({rng_s},A{row})')
        c.font, c.border, c.alignment = BOLD, BORDER, CENTER
        c = sm.cell(row=row, column=6, value=d)
        c.font, c.alignment = BODY, WRAP
    srow = r0 + 2 + len(LEGEND_SUPPORT)
    sm.cell(row=srow, column=2, value="합계").font = BOLD
    c = sm.cell(row=srow, column=3, value=f"=SUM(C{r0 + 2}:C{srow - 1})")
    c.font, c.alignment, c.border = BOLD, CENTER, BORDER

    # 표3 범례
    r1 = srow + 2
    sm.cell(row=r1, column=1, value="③ 분류 기준").font = BOLD
    row = r1 + 1
    for p, d in LEGEND_PHASE:
        c = sm.cell(row=row, column=1, value=p)
        c.font, c.fill, c.border, c.alignment = BOLD, fill(PHASE_FILL[p]), BORDER, CENTER
        sm.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
        c = sm.cell(row=row, column=2, value=d)
        c.font, c.alignment = BODY, WRAP
        sm.row_dimensions[row].height = 30
        row += 1
    for k, prod, d in LEGEND_AREA:
        c = sm.cell(row=row, column=1, value=k)
        c.font, c.fill, c.border, c.alignment = BOLD, fill(AREA_FILL[k]), BORDER, CENTER
        sm.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
        c = sm.cell(row=row, column=2, value=f"{prod} — {d}")
        c.font, c.alignment = BODY, WRAP
        sm.row_dimensions[row].height = 30
        row += 1

    # 표4 목록
    r2 = row + 1
    sm.cell(row=r2, column=1, value="④ 단계 × 영역 요건 목록 (작성 시점 기준 목록)").font = BOLD
    for j, t in enumerate(["단계", "컨테이너 플랫폼 (OpenShift)", "AI (OpenShift AI)", "공통"], 1):
        c = sm.cell(row=r2 + 1, column=j, value=t)
        c.font, c.fill, c.alignment, c.border = HDR_FONT, HDR_FILL, CENTER, BORDER
    for i, p in enumerate(PHASES):
        row = r2 + 2 + i
        c = sm.cell(row=row, column=1, value=p)
        c.font, c.fill, c.border, c.alignment = BOLD, fill(PHASE_FILL[p]), BORDER, CENTER
        vals = []
        for j, x in enumerate(AREAS, 2):
            items = [f"{r['sup']} {r['id']} {r['short']}" for r in R if r["phase"] == p and r["area"] == x]
            v = "\n".join(items) if items else "—"
            vals.append(v)
            c = sm.cell(row=row, column=j, value=v)
            c.font, c.border, c.alignment = BODY, BORDER, WRAP
        sm.row_dimensions[row].height = max(18, 14.5 * max(v.count("\n") + 1 for v in vals) * 1.15 + 3)
    for col, w in zip("BCD", (34, 34, 30)):
        sm.column_dimensions[col].width = w

    # ── Sheet: 확인필요사항 ────────────────────────────────────────────
    rk = wb.create_sheet("확인필요사항")
    w = [5, 24, 18, 44, 60]
    header(rk, 1, ["#", "항목", "관련 요건", "영향", "권장 대응"], w)
    for i, (t, ids, imp, act) in enumerate(RISKS, 2):
        vals = [i - 1, t, ids, imp, act]
        for j, v in enumerate(vals, 1):
            c = rk.cell(row=i, column=j, value=v)
            c.font, c.alignment, c.border = BODY, WRAP, BORDER
        rk.cell(row=i, column=1).alignment = CENTER
        rk.cell(row=i, column=2).font = BOLD
        autoheight(rk, i, w, vals)
    rk.freeze_panes = "A2"

    # ── Sheet: 구독구성 ────────────────────────────────────────────────
    sb = wb.create_sheet("구독구성")
    w = [16, 34, 56, 50]
    header(sb, 1, ["구분", "제품/서비스", "내용", "관련 요건"], w)
    for i, (g, p, d, ids) in enumerate(SUBS, 2):
        vals = [g, p, d, ids]
        for j, v in enumerate(vals, 1):
            c = sb.cell(row=i, column=j, value=v)
            c.font, c.alignment, c.border = BODY, WRAP, BORDER
        sb.cell(row=i, column=2).font = BOLD
        autoheight(sb, i, w, vals)
    n = len(SUBS) + 3
    sb.cell(row=n, column=1,
            value="OpenShift·OpenShift AI 행의 관련 요건은 주 제공 영역 기준(공통 포함). 구독 SKU·GPU 노드 산정 기준은 영업/파트너 확인 필요.").font = SUB
    sb.freeze_panes = "A2"

    for sheet in wb.worksheets:
        sheet.page_setup.orientation = "landscape"
        sheet.page_setup.paperSize = sheet.PAPERSIZE_A4
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0
        sheet.sheet_properties.pageSetUpPr.fitToPage = True
        sheet.print_options.horizontalCentered = True
    ws.print_title_rows = "1:1"
    wb.save(path)


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "README.md").write_text(md(), encoding="utf-8")
    xlsx(OUT_DIR / XLSX_NAME)
    print("ok", len(R))
