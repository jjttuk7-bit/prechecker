from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import BASE_DIR
from .rag_retriever import group_evidence_by_category
from .risk_analyzer import LABELS


DISCLAIMER = (
    "본 리포트는 KIPRIS 검색 결과와 AI 분석을 기반으로 한 예비 검토 자료입니다. "
    "상표 등록 가능성, 침해 여부, 분쟁 가능성에 대한 최종 판단은 변리사 등 전문가 검토가 필요합니다. "
    "본 리포트는 법률 자문이 아니며, 실제 출원 또는 상업적 사용 전에는 추가 확인이 필요합니다."
)


def generate_alternatives(brand_name: str) -> list[str]:
    base = brand_name.replace(" ", "")
    return [f"{base}랩", f"{base}플러스", f"{base}스튜디오"]


def generate_html_report(context: dict) -> str:
    template_dir = Path(BASE_DIR / "templates")
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(["html"]))
    template = env.get_template("report.html")
    risk = context.get("risk", {})
    overall = risk.get("overall_risk", "low")
    one_line = (
        f"'{context.get('brand_name')}'은(는) KIPRIS 후보 기준 예비 위험도 "
        f"{LABELS.get(overall, overall)}으로 분류되며, 추가 확인이 필요합니다."
    )
    return template.render(
        **context,
        one_line=one_line,
        disclaimer=DISCLAIMER,
        alternatives=generate_alternatives(context.get("brand_name", "")),
        evidence_by_category=group_evidence_by_category(context.get("evidence", []), per_category_limit=2),
    )
