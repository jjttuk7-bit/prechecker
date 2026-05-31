from __future__ import annotations

from .kipris_client import search_trademark
from .query_expander import generate_query_variants, infer_likely_classes
from .rag_retriever import retrieve_evidence
from .report_generator import generate_html_report
from .risk_analyzer import analyze_risk
from .similarity_scorer import score_candidates
from .trademark_normalizer import normalize_items


def run_precheck(brand_name: str, business_description: str, mock_mode: bool = False) -> dict:
    variants = generate_query_variants(brand_name, business_description, mock_mode=mock_mode)
    search_terms = variants.get("recommended_search_terms") or [brand_name]

    raw_items: list[dict] = []
    errors: list[str] = []
    for term in search_terms:
        items, error = search_trademark(term, mock_mode=mock_mode)
        raw_items.extend(items)
        if error:
            errors.append(f"{term}: {error}")

    candidates = normalize_items(raw_items)
    likely_classes = infer_likely_classes(business_description)
    scored_candidates = score_candidates(brand_name, likely_classes, candidates)
    risk = analyze_risk(scored_candidates)
    evidence = retrieve_evidence(business_description, likely_classes, risk["top_candidates"])
    context = {
        "brand_name": brand_name,
        "business_description": business_description,
        "variants": variants,
        "likely_classes": likely_classes,
        "candidates": scored_candidates[:10],
        "risk": risk,
        "evidence": evidence,
        "errors": errors,
    }
    context["report_html"] = generate_html_report(context)
    return context
