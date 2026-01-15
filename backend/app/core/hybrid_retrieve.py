"""SQL-backed retrieval helpers for products and ingredients.

Functions in this module query the database to find relevant products and
ingredients based on a user's natural language query and intake/profile
information. These are used by the RAG pipeline to build context for the
LLM generation step.
"""

from typing import List, Dict
import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import Product, Ingredient, SkinType

logger = logging.getLogger(__name__)
DEFAULT_K = 8


def sql_retrieve(
    db_session: Session,
    query: str,
    intake_data: Dict = None,
    concern: str | None = None,
    k: int = 8,
) -> List[Dict]:
    """SQL-backed retrieval for products and ingredients based on user profile.

    Args:
        db_session: SQLAlchemy database session
        query: Natural language query from user
        intake_data: User's intake form responses
        concern: Additional concern parameter
        k: Number of results to return

    Returns:
        List of dicts with keys: id, text, source_id, score, metadata
    """
    results = []

    # Extract user attributes from intake data and query
    skin_type, concerns = _extract_skin_attributes(query, intake_data, concern)
    is_sensitive = intake_data.get("sensitive") == "yes" if intake_data else None

    try:
        _append_skin_type_products(results, db_session, skin_type, k)
        _append_concern_products(results, db_session, concerns, k)
        _append_beneficial_ingredients(
            results, db_session, skin_type, concerns, is_sensitive
        )
        _append_avoid_ingredients(results, db_session, is_sensitive)
        _append_general_products(results, db_session, k)
    except SQLAlchemyError as e:
        logger.warning("SQL query failed: %s", e)
        return []

    return results[:k]


def _append_skin_type_products(
    results: List[Dict], db_session: Session, skin_type: str | None, k: int
) -> None:
    if not skin_type:
        return

    skin_type_query = (
        db_session.query(Product)
        .join(Product.skin_types)
        .filter(SkinType.type_name.ilike(f"%{skin_type}%"))
    )

    skin_type_query = skin_type_query.filter(
        Product.rank.isnot(None), Product.rank >= 3.5
    ).order_by(Product.rank.desc())

    skin_type_products = skin_type_query.limit(max(k // 2, 2)).all()
    for product in skin_type_products:
        results.append(
            {
                "id": f"skintype_product_{product.product_id}",
                "text": _format_product_text(product, context="skin_type_match"),
                "source_id": "products_db",
                "score": 0.95,
                "metadata": {
                    "type": "product",
                    "match_type": "skin_type",
                    "skin_type": skin_type,
                    "category": product.category,
                },
            }
        )


def _append_concern_products(
    results: List[Dict], db_session: Session, concerns: List[str], k: int
) -> None:
    if not concerns:
        return

    concern_mappings = {
        "acne": ["Cleanser", "Treatment"],
        "aging": ["Moisturizer", "Treatment", "Serum"],
        "pigmentation": ["Treatment", "Serum"],
        "dryness": ["Moisturizer", "Oil"],
        "blackheads": ["Cleanser", "Treatment"],
        "sun_damage": ["Treatment", "Sunscreen"],
    }

    relevant_categories = set()
    for concern_item in concerns:
        relevant_categories.update(concern_mappings.get(concern_item, []))

    if not relevant_categories:
        return

    conds = [Product.category.ilike(f"%{cat}%") for cat in relevant_categories]
    concern_query = (
        db_session.query(Product)
        .filter(or_(*conds))
        .filter(Product.rank.isnot(None), Product.rank >= 3.0)
        .order_by(Product.rank.desc())
    )

    concern_products = concern_query.limit(max(k // 3, 2)).all()
    for product in concern_products:
        if not any(
            r["id"] == f"skintype_product_{product.product_id}" for r in results
        ):
            results.append(
                {
                    "id": f"concern_product_{product.product_id}",
                    "text": _format_product_text(product, context="concern_match"),
                    "source_id": "products_db",
                    "score": 0.85,
                    "metadata": {
                        "type": "product",
                        "match_type": "concern",
                        "concerns": concerns,
                        "category": product.category,
                    },
                }
            )


def _append_beneficial_ingredients(
    results: List[Dict],
    db_session: Session,
    skin_type: str | None,
    concerns: List[str],
    is_sensitive: bool,
) -> None:
    beneficial_ingredients = _get_beneficial_ingredients(
        db_session, skin_type, concerns, is_sensitive
    )
    limit = max(DEFAULT_K // 4, 1)
    for ingredient in beneficial_ingredients[:limit]:
        results.append(
            {
                "id": f"ingredient_{ingredient.ingredient_id}",
                "text": _format_ingredient_text(ingredient, skin_type, concerns),
                "source_id": "ingredients_db",
                "score": 0.75,
                "metadata": {
                    "type": "ingredient",
                    "beneficial": True,
                    "skin_type": skin_type,
                },
            }
        )


def _append_avoid_ingredients(
    results: List[Dict], db_session: Session, is_sensitive: bool
) -> None:
    if not is_sensitive:
        return

    avoid_ingredients = _get_ingredients_to_avoid(db_session, is_sensitive)
    for ingredient in avoid_ingredients[:1]:
        results.append(
            {
                "id": f"avoid_ingredient_{ingredient.ingredient_id}",
                "text": (
                    f"AVOID: {ingredient.inci_name} - " "may irritate sensitive skin"
                ),
                "source_id": "ingredients_db",
                "score": 0.6,
                "metadata": {"type": "ingredient", "beneficial": False, "avoid": True},
            }
        )


def _append_general_products(results: List[Dict], db_session: Session, k: int) -> None:
    if len(results) >= k // 2:
        return

    general_query = (
        db_session.query(Product)
        .filter(Product.rank.isnot(None), Product.rank >= 4.0)
        .order_by(Product.rank.desc())
    )
    general_products = general_query.limit(k - len(results)).all()
    for product in general_products:
        if not any(f"product_{product.product_id}" in r["id"] for r in results):
            results.append(
                {
                    "id": f"general_product_{product.product_id}",
                    "text": _format_product_text(product, context="top_rated"),
                    "source_id": "products_db",
                    "score": 0.7,
                    "metadata": {
                        "type": "product",
                        "match_type": "general",
                        "category": product.category,
                    },
                }
            )


def _extract_skin_attributes(
    query: str, intake_data: Dict = None, concern: str | None = None
) -> tuple[str | None, List[str]]:
    """Extract skin type and concerns from intake data and natural language query."""
    query_lower = query.lower() if query else ""

    # Priority 1: Use intake form data if available
    skin_type = None
    concerns = []

    if intake_data:
        skin_type = (
            intake_data.get("skin_type", "").title()
            if intake_data.get("skin_type")
            else None
        )

        # Extract concerns from intake form
        intake_concerns = intake_data.get("concerns", [])
        if isinstance(intake_concerns, str):
            concerns.extend([c.strip().lower() for c in intake_concerns.split(",")])
        elif isinstance(intake_concerns, list):
            concerns.extend([c.lower() for c in intake_concerns])

    # Priority 2: Extract from query if intake data is missing
    if not skin_type and query_lower:
        skin_types = ["oily", "dry", "normal", "combination", "sensitive"]
        for st in skin_types:
            if st in query_lower:
                skin_type = st.title()
                break

    # Extract additional concerns from query
    if query_lower:
        concern_keywords = {
            "acne": ["acne", "breakout", "pimple", "blemish"],
            "dryness": ["dry", "dehydrated", "flaky", "tight"],
            "aging": ["wrinkle", "fine lines", "anti-aging", "firming"],
            "pigmentation": [
                "dark spots",
                "hyperpigmentation",
                "melasma",
                "uneven tone",
            ],
            "sensitivity": ["sensitive", "irritation", "redness", "reactive"],
            "blackheads": ["blackhead", "clogged pores", "comedone"],
            "sun_damage": ["sun damage", "age spots", "photo damage"],
        }

        for concern_cat, keywords in concern_keywords.items():
            if (
                any(keyword in query_lower for keyword in keywords)
                and concern_cat not in concerns
            ):
                concerns.append(concern_cat)

    if concern and concern not in concerns:
        concerns.append(concern)

    return skin_type, concerns


def _format_product_text(product: Product, context: str = "general") -> str:
    """Format product information for context with enhanced details."""
    ingredients_str = ", ".join([ing.inci_name for ing in product.ingredients[:5]])
    if len(product.ingredients) > 5:
        ingredients_str += f" (+ {len(product.ingredients) - 5} more)"

    skin_types_str = ", ".join([st.type_name for st in product.skin_types])

    rating_text = (
        f"Rating: {product.rank:.1f}/5" if product.rank else "Rating: Not rated"
    )

    context_prefix = ""
    if context == "skin_type_match":
        context_prefix = "PERFECT MATCH: "
    elif context == "concern_match":
        context_prefix = "TARGETED: "

    return f"""{context_prefix}Product: {product.brand_name} {product.product_name}
Category: {product.category}
Suitable for: {skin_types_str} skin
Key ingredients: {ingredients_str}
{rating_text}"""


def _format_ingredient_text(
    ingredient: Ingredient, skin_type: str = None, concerns: List[str] = None
) -> str:
    """Format ingredient information with benefits and tailor to profile."""
    benefits = _get_ingredient_benefits(ingredient.inci_name)

    # Include optional profile context if provided to avoid unused-argument warnings
    profile_parts = []
    if skin_type:
        profile_parts.append(f"suitable for {skin_type} skin")
    if concerns:
        if isinstance(concerns, (list, tuple)):
            profile_parts.append(f"targets {', '.join(concerns)}")
        else:
            profile_parts.append(f"targets {concerns}")

    profile_suffix = f" ({'; '.join(profile_parts)})" if profile_parts else ""

    return f"BENEFICIAL INGREDIENT: {ingredient.inci_name} - {benefits}{profile_suffix}"


def _get_beneficial_ingredients(
    db_session: Session,
    skin_type: str | None,
    concerns: List[str],
    is_sensitive: bool = False,
) -> List[Ingredient]:
    """Get ingredients beneficial for specific skin types/concerns with sensitivity
    consideration."""
    beneficial_names = []

    # Base ingredients by skin type
    if skin_type == "Oily":
        beneficial_names.extend(
            ["Niacinamide", "Salicylic Acid", "Zinc Oxide", "Clay", "Witch Hazel"]
        )
    elif skin_type == "Dry":
        beneficial_names.extend(
            ["Hyaluronic Acid", "Ceramides", "Glycerin", "Squalane", "Shea Butter"]
        )
    elif skin_type == "Combination":
        beneficial_names.extend(["Niacinamide", "Hyaluronic Acid", "Glycerin"])
    elif skin_type == "Normal":
        beneficial_names.extend(["Vitamin C", "Hyaluronic Acid", "Niacinamide"])
    elif skin_type == "Sensitive" or is_sensitive:
        beneficial_names.extend(
            [
                "Aloe Vera",
                "Chamomile",
                "Allantoin",
                "Colloidal Oatmeal",
                "Centella Asiatica",
            ]
        )

    # Additional ingredients by concerns
    concern_ingredients = {
        "acne": ["Salicylic Acid", "Benzoyl Peroxide", "Tea Tree Oil", "Zinc"],
        "aging": ["Retinol", "Vitamin C", "Peptides", "Alpha Hydroxy Acids"],
        "pigmentation": ["Vitamin C", "Kojic Acid", "Arbutin", "Licorice Root"],
        "dryness": ["Hyaluronic Acid", "Ceramides", "Glycerin", "Squalane"],
        "blackheads": ["Salicylic Acid", "Retinol", "Clay"],
        "sun_damage": ["Vitamin C", "Retinol", "Niacinamide"],
    }

    for concern in concerns:
        if concern in concern_ingredients:
            beneficial_names.extend(concern_ingredients[concern])

    # Remove duplicates while preserving order
    seen = set()
    unique_names = []
    for name in beneficial_names:
        if name.lower() not in seen:
            seen.add(name.lower())
            unique_names.append(name)

    if not unique_names:
        return []

    conds = [Ingredient.inci_name.ilike(f"%{name}%") for name in unique_names[:10]]
    return db_session.query(Ingredient).filter(or_(*conds)).limit(8).all()


def _get_ingredients_to_avoid(
    db_session: Session, is_sensitive: bool = False
) -> List[Ingredient]:
    """Get ingredients that sensitive skin should avoid."""
    if not is_sensitive:
        return []

    avoid_names = [
        "Fragrance",
        "Alcohol",
        "Sulfates",
        "Parabens",
        "Essential Oils",
        "Menthol",
        "Eucalyptus",
        "Citrus",
        "Formaldehyde",
    ]

    return (
        db_session.query(Ingredient)
        .filter(or_(*[Ingredient.inci_name.ilike(f"%{name}%") for name in avoid_names]))
        .limit(5)
        .all()
    )


def _get_ingredient_benefits(ingredient_name: str) -> str:
    """Get specific benefits of an ingredient for the user's profile."""
    benefits_db = {
        "niacinamide": "controls oil production, minimizes pores, reduces inflammation",
        "salicylic acid": "exfoliates inside pores, reduces blackheads and acne",
        "hyaluronic acid": "deeply hydrates, plumps skin, reduces fine lines",
        "retinol": "accelerates cell turnover, reduces wrinkles, improves texture",
        "vitamin c": "brightens skin, fades dark spots, provides antioxidant protection",
        "ceramides": "strengthens skin barrier, locks in moisture",
        "glycerin": "attracts moisture to skin, maintains hydration",
        "zinc": "reduces inflammation, controls acne bacteria",
    }

    ingredient_lower = ingredient_name.lower()
    for key, benefit in benefits_db.items():
        if key in ingredient_lower:
            return benefit

    return "provides skincare benefits for your skin type"
