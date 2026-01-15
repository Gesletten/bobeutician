"""Utilities to compose user-facing context and routine suggestions.

This module turns SQL-backed retrieval results and intake/profile data
into a concise context summary, citations, and simple routine suggestions
that are consumed by the RAG pipeline and LLM generation code.
"""

from typing import List, Dict


def compose_context(
    results: List[Dict], token_budget: int = 400, intake_data: Dict = None
) -> Dict:
    """Compose personalized skincare context from SQL query results and intake data.

    Args:
        results: Retrieved products/ingredients from SQL queries
        token_budget: Maximum token budget for context
        intake_data: User's intake form responses

    Returns:
        {"summary": str, "citations": [...], "used_results": [...], "user_profile": str}
    """
    if not results:
        return {
            "summary": "No relevant products found for your specific needs.",
            "citations": [],
            "used_results": [],
            "user_profile": _format_user_profile(intake_data) if intake_data else "",
        }

    groups = _group_results(results)

    summary_parts = _build_summary_parts(groups, intake_data)

    # Join and manage token budget
    summary = "\n".join(summary_parts)
    if len(summary) > token_budget * 4:  # rough char budget
        summary = summary[: token_budget * 4] + "..."

    # Create citations from SQL query results
    citations = [
        {"id": r.get("id"), "source": r.get("source_id"), "score": r.get("score", 0)}
        for r in results
    ]

    return {
        "summary": summary,
        "citations": citations,
        "used_results": results,
        "user_profile": _format_user_profile(intake_data) if intake_data else "",
    }


def _group_results(results: List[Dict]) -> Dict[str, List[Dict]]:
    """Group results into named buckets used for summary building."""
    return {
        "perfect_matches": [
            r for r in results if r.get("metadata", {}).get("match_type") == "skin_type"
        ],
        "targeted_products": [
            r for r in results if r.get("metadata", {}).get("match_type") == "concern"
        ],
        "beneficial_ingredients": [
            r
            for r in results
            if r.get("metadata", {}).get("type") == "ingredient"
            and r.get("metadata", {}).get("beneficial")
        ],
        "avoid_ingredients": [r for r in results if r.get("metadata", {}).get("avoid")],
    }


def _build_summary_parts(
    groups: Dict[str, List[Dict]], intake_data: Dict = None
) -> List[str]:
    """Build summary text parts from grouped results and intake data."""
    summary_parts: List[str] = []

    # User profile summary
    if intake_data:
        profile = _format_user_profile(intake_data)
        if profile:
            summary_parts.append(f"YOUR PROFILE: {profile}")

    # Perfect matches for skin type
    perfect_matches = groups.get("perfect_matches", [])
    if perfect_matches:
        summary_parts.append("\nPERFECT MATCHES FOR YOUR SKIN:")
        for product in perfect_matches[:2]:
            summary_parts.append(f"• {product['text']}")

    # Products for specific concerns
    targeted_products = groups.get("targeted_products", [])
    if targeted_products:
        summary_parts.append("\nTARGETED SOLUTIONS:")
        for product in targeted_products[:2]:
            summary_parts.append(f"• {product['text']}")

    # Beneficial ingredients
    beneficial_ingredients = groups.get("beneficial_ingredients", [])
    if beneficial_ingredients:
        summary_parts.append("\nKEY INGREDIENTS FOR YOU:")
        for ingredient in beneficial_ingredients[:3]:
            summary_parts.append(f"• {ingredient['text']}")

    # Ingredients to avoid
    avoid_ingredients = groups.get("avoid_ingredients", [])
    if avoid_ingredients:
        summary_parts.append("\n INGREDIENTS TO AVOID:")
        for ingredient in avoid_ingredients[:2]:
            summary_parts.append(f"• {ingredient['text']}")

    # Routine suggestion
    if perfect_matches or targeted_products:
        routine = _generate_routine_suggestion(perfect_matches, targeted_products)
        if routine:
            summary_parts.append(f"\n SUGGESTED ROUTINE:\n{routine}")

    return summary_parts


def _format_user_profile(intake_data: Dict = None) -> str:
    """Format user's profile from intake data."""
    if not intake_data:
        return ""

    profile_parts = []

    if intake_data.get("skin_type"):
        profile_parts.append(f"{intake_data['skin_type']} skin")

    if intake_data.get("sensitive") == "yes":
        profile_parts.append("sensitive")
    elif intake_data.get("sensitive") == "no":
        profile_parts.append("non-sensitive")

    concerns = intake_data.get("concerns", [])
    if concerns:
        if isinstance(concerns, str):
            concerns = [c.strip() for c in concerns.split(",")]
        profile_parts.append(f"concerns: {', '.join(concerns)}")

    return " | ".join(profile_parts) if profile_parts else ""


def _generate_routine_suggestion(
    perfect_matches: List[Dict], targeted_products: List[Dict]
) -> str:
    """Generate a simple routine suggestion based on products."""
    routine_steps = []
    cleansers = [
        p
        for p in perfect_matches + targeted_products
        if "cleanser" in p.get("text", "").lower()
    ]
    treatments = [
        p
        for p in perfect_matches + targeted_products
        if any(
            word in p.get("text", "").lower() for word in ["serum", "treatment", "acid"]
        )
    ]
    moisturizers = [
        p
        for p in perfect_matches + targeted_products
        if "moisturizer" in p.get("text", "").lower()
    ]

    # Build routine
    if cleansers:
        product_name = cleansers[0]["text"].split(":")[1].split("\n")[0].strip()
        routine_steps.append(f"1. Cleanse: {product_name}")

    if treatments:
        product_name = treatments[0]["text"].split(":")[1].split("\n")[0].strip()
        routine_steps.append(f"2. Treat: {product_name}")

    if moisturizers:
        product_name = moisturizers[0]["text"].split(":")[1].split("\n")[0].strip()
        routine_steps.append(f"3. Moisturize: {product_name}")

    routine_steps.append("4. Protect: Apply SPF 30+ sunscreen (AM only)")

    return "\n".join(routine_steps) if routine_steps else ""


# Notes for teammates: keep token budget and result shapes in mind.
