from __future__ import annotations

import pandas as pd
import streamlit as st

from src.pipeline import run_precheck
from src.config import get_settings
from src.rag_retriever import group_evidence_by_category, related_evidence_for_candidate, retrieve_evidence
from src.storage import save_report_html


st.set_page_config(page_title="상표 프리체크 MVP", layout="wide")

RISK_LABELS = {"high": "높음", "medium": "중간", "low": "낮음"}
RISK_CLASS = {"high": "risk-high", "medium": "risk-medium", "low": "risk-low"}


def render_chips(items: list[str], css_class: str = "chip") -> None:
    chips = "".join(f"<span class='{css_class}'>{item}</span>" for item in items)
    st.markdown(f"<div class='chip-row'>{chips}</div>", unsafe_allow_html=True)


def candidate_table_rows(candidates: list[dict]) -> list[dict]:
    rows = []
    for item in candidates:
        designated_goods = item.get("designated_goods", [])
        rows.append(
            {
                "상표명": item.get("trademark_name"),
                "상태": item.get("status"),
                "상품류": ", ".join(item.get("nice_classes", [])),
                "지정상품": ", ".join(designated_goods[:3]) if designated_goods else "상세 조회 필요",
                "이름 유사도": item.get("name_similarity"),
                "상품류 겹침": item.get("class_similarity"),
                "상태 위험도": item.get("status_risk"),
                "종합 점수": item.get("total_score"),
                "예비 위험": RISK_LABELS.get(item.get("risk_level"), item.get("risk_level")),
            }
        )
    return rows


def evidence_items(result: dict, business_description: str) -> list[dict]:
    if result.get("evidence") is not None:
        return result.get("evidence", [])
    return retrieve_evidence(
        business_description=business_description,
        likely_classes=result.get("likely_classes", []),
        top_candidates=result.get("risk", {}).get("top_candidates", []),
    )


def evidence_summary_for_candidate(candidate: dict, evidence: list[dict]) -> str:
    related = related_evidence_for_candidate(candidate, evidence, limit=1)
    if not related:
        return "연결된 근거 지식 없음"
    item = related[0]
    return f"{item['category']}: {item['title']}"


st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 1240px;
        padding-top: 2.4rem;
    }
    .page-kicker {
        color: #5a6675;
        font-size: 0.92rem;
        margin-bottom: 0.25rem;
    }
    .page-title {
        color: #111827;
        font-size: 2.35rem;
        font-weight: 760;
        letter-spacing: 0;
        margin: 0 0 0.35rem;
    }
    .page-subtitle {
        color: #596579;
        margin-bottom: 1.4rem;
    }
    .summary-band {
        border: 1px solid #d9e1ea;
        border-radius: 8px;
        padding: 18px 20px;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        margin: 8px 0 22px;
    }
    .summary-band strong {
        color: #111827;
        font-size: 1.35rem;
    }
    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 8px 0 12px;
    }
    .chip {
        border: 1px solid #d8e0ea;
        border-radius: 999px;
        color: #1f2a37;
        background: #f7fafc;
        padding: 6px 10px;
        font-size: 0.9rem;
        white-space: nowrap;
    }
    .class-chip {
        border: 1px solid #bcd1e4;
        border-radius: 999px;
        color: #123552;
        background: #eef6fb;
        padding: 6px 10px;
        font-size: 0.9rem;
        white-space: nowrap;
    }
    .risk-card {
        border: 1px solid #d9e1ea;
        border-radius: 8px;
        padding: 15px 16px;
        background: #ffffff;
        min-height: 148px;
    }
    .evidence-hint {
        border-top: 1px solid #e6edf3;
        margin-top: 12px;
        padding-top: 10px;
        color: #526173;
        font-size: 0.84rem;
    }
    .evidence-card {
        border: 1px solid #d9e1ea;
        border-radius: 8px;
        padding: 14px 15px;
        background: #ffffff;
        min-height: 142px;
        margin-bottom: 10px;
    }
    .evidence-card h4 {
        margin: 5px 0 8px;
        color: #17202a;
        font-size: 0.98rem;
    }
    .evidence-category {
        color: #38536b;
        background: #eef6fb;
        border: 1px solid #c7dceb;
        border-radius: 999px;
        display: inline-block;
        font-size: 0.78rem;
        padding: 3px 8px;
    }
    .risk-card h3 {
        margin: 0 0 8px;
        font-size: 1.08rem;
        color: #111827;
    }
    .risk-meta {
        color: #5b6675;
        font-size: 0.86rem;
        margin-bottom: 10px;
    }
    .risk-pill {
        display: inline-block;
        border-radius: 999px;
        padding: 4px 9px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-right: 6px;
    }
    .risk-high { color: #8f1f1f; background: #fff0ed; border: 1px solid #f3bbb2; }
    .risk-medium { color: #805200; background: #fff7df; border: 1px solid #efd68c; }
    .risk-low { color: #17613b; background: #ecf8f1; border: 1px solid #b7dec8; }
    .small-note {
        color: #6b7280;
        font-size: 0.88rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='page-kicker'>KIPRIS + AI 기반 예비 검토</div>", unsafe_allow_html=True)
st.markdown("<h1 class='page-title'>상표 프리체크 MVP</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='page-subtitle'>브랜드명과 사용 분야를 입력하면 검색 확장, 후보 정규화, 예비 위험도 산출, HTML 리포트 생성을 한 번에 진행합니다.</div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("설정")
    mock_mode = st.toggle("Mock mode", value=True)
    settings = get_settings()
    if mock_mode:
        st.info("Mock mode: 모의 데이터로 분석합니다.")
    elif settings.kipris_endpoint and settings.kipris_api_key:
        st.success("실 KIPRIS API 사용 중")
    else:
        st.warning("실 API 설정이 부족합니다.")

brand_name = st.text_input("브랜드명", placeholder="예: 먼저체크")
business_description = st.text_area("사용 분야", placeholder="예: AI 기반 상표 검색 웹서비스", height=120)

if st.button("상표 프리체크 실행", type="primary", disabled=not brand_name or not business_description):
    with st.spinner("검색 변형어 생성, KIPRIS 조회, 위험도 분석을 진행 중입니다."):
        result = run_precheck(brand_name, business_description, mock_mode=mock_mode)
        report_path = save_report_html(brand_name, result["report_html"])
        evidence = evidence_items(result, business_description)

    risk_label = result["risk"]["overall_risk_label"]
    st.markdown(
        f"""
        <section class="summary-band">
            <div class="small-note">종합 예비 위험도</div>
            <strong>{risk_label}</strong>
            <p>{result["risk"]["summary"]}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    overview_col, action_col = st.columns([3, 1])
    with overview_col:
        st.subheader("검색 변형어")
        render_chips(result["variants"].get("recommended_search_terms", []))
        st.markdown("<div class='small-note'>예상 상품류/서비스류</div>", unsafe_allow_html=True)
        render_chips(result["likely_classes"], "class-chip")
    with action_col:
        st.metric("예비 위험도", risk_label)
        st.metric("후보 수", len(result["candidates"]))

    if result["errors"]:
        st.warning("일부 API 호출에서 오류가 있었습니다. 설정값 또는 KIPRIS 응답을 확인하세요.")
        st.write(result["errors"])

    st.subheader("위험 후보 TOP 3")
    card_columns = st.columns(3)
    for index, item in enumerate(result["risk"]["top_candidates"]):
        with card_columns[index]:
            item_risk = item.get("risk_level", "medium")
            evidence_hint = evidence_summary_for_candidate(item, evidence)
            st.markdown(
                f"""
                <div class="risk-card">
                    <div class="risk-meta">#{index + 1} 위험 후보</div>
                    <h3>{item.get("trademark_name")}</h3>
                    <div>
                        <span class="risk-pill {RISK_CLASS.get(item_risk, "risk-medium")}">{RISK_LABELS.get(item_risk, item_risk)}</span>
                        <span class="risk-meta">점수 {item.get("total_score")}</span>
                    </div>
                    <p class="risk-meta">상태 {item.get("status")} · 상품류 {", ".join(item.get("nice_classes", []))}</p>
                    <p>{item.get("risk_reason")}</p>
                    <div class="evidence-hint">{evidence_hint}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    table_tab, report_tab = st.tabs(["후보 상세", "HTML 리포트"])
    with table_tab:
        st.subheader("유사 상표 후보 TOP 10")
        st.dataframe(pd.DataFrame(candidate_table_rows(result["candidates"])), use_container_width=True, hide_index=True)
        st.markdown(
            "<div class='small-note'>점수는 이름, 발음, 문자 구성, 상품류 겹침 가능성, 상태값을 조합한 예비 지표입니다.</div>",
            unsafe_allow_html=True,
        )
        st.subheader("RAG 근거 지식")
        if evidence:
            categories = ["상품류 근거", "상태값 근거", "유사 판단 근거"]
            grouped_evidence = group_evidence_by_category(evidence, per_category_limit=2)
            for category in categories:
                items = grouped_evidence.get(category, [])
                if not items:
                    continue
                st.markdown(f"**{category}**")
                cols = st.columns(min(3, len(items)))
                for index, item in enumerate(items):
                    with cols[index % len(cols)]:
                        st.markdown(
                            f"""
                            <div class="evidence-card">
                                <span class="evidence-category">{item['category']}</span>
                                <h4>{item['title']}</h4>
                                <p>{item['text']}</p>
                                <div class="small-note">source: {item['source']} · match score: {item['score']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
        else:
            st.info("이번 결과와 연결된 RAG 근거 지식이 없습니다. 검색어 또는 사용 분야를 더 구체화해 보세요.")

    with report_tab:
        st.subheader("HTML 리포트")
        with st.expander("리포트 미리보기", expanded=True):
            st.components.v1.html(result["report_html"], height=640, scrolling=True)
        st.download_button(
            "HTML 리포트 다운로드",
            data=result["report_html"],
            file_name=f"{brand_name}_precheck_report.html",
            mime="text/html",
        )
        st.caption(f"저장 위치: {report_path}")
