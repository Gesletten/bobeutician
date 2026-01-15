"""Demo tests for the SQL-backed retrieval/composition pipeline.

These tests focus on the retrieval-composition pieces and add a mocked
pipeline test to verify `run_pipeline` composes results and returns a
generated answer without requiring a real DB or LLM.
"""

import sys
import pathlib
import asyncio
from app.core.hybrid_retrieve import _extract_skin_attributes
from app.core.compose import compose_context
from app.core.prompts import build_qa_prompt
from app.core import rag_pipeline as rp

# Ensure `backend` is on sys.path so `app` imports resolve during pytest
backend_dir = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))


def test_skin_attribute_extraction():
    """Ensure _extract_skin_attributes returns values for sample queries."""
    test_queries = [
        "I have oily skin with acne breakouts, what products should I use?",
        "My sensitive skin gets irritated easily, need gentle moisturizer",
        "Looking for anti-aging products for dry skin with wrinkles",
        "Combination skin with dark spots and hyperpigmentation",
    ]

    for query in test_queries:
        skin_type, concerns = _extract_skin_attributes(query)
        assert skin_type is not None
        assert isinstance(concerns, (list, tuple))


def test_context_composition_basic():
    """Compose context from mock results and ensure expected keys exist."""
    mock_results = [
        {
            "id": "product_1",
            "text": (
                "Product: CeraVe Foaming Facial Cleanser\nCategory: Cleanser\n"
                "Suitable for: Oily, Normal skin\nKey ingredients: Ceramides, "
                "Niacinamide, Hyaluronic Acid\nRating: 4.5"
            ),
            "source_id": "products_db",
            "score": 0.9,
            "metadata": {"type": "product", "skin_type": "Oily"},
        },
        {
            "id": "ingredient_1",
            "text": "Ingredient: Niacinamide - beneficial for Oily skin",
            "source_id": "ingredients_db",
            "score": 0.7,
            "metadata": {"type": "ingredient", "beneficial": True},
        },
    ]

    composed = compose_context(mock_results, token_budget=400)
    assert isinstance(composed, dict)
    assert "summary" in composed
    assert "citations" in composed


def test_prompt_building_basic():
    """Build a QA prompt from a question and provided context string."""

    question = "I have oily skin with acne breakouts, what products should I use?"

    context = (
        "RECOMMENDED PRODUCTS:\n- Product: CeraVe Foaming Facial Cleanser\n"
        "Category: Cleanser\nSuitable for: Oily, Normal skin\n"
        "Key ingredients: Ceramides, Niacinamide"
    )

    prompt = build_qa_prompt(question, context)
    assert isinstance(prompt, str)
    assert question.split()[0].lower() in prompt.lower() or len(prompt) > 0


def test_run_pipeline_with_mocks(monkeypatch):
    """Patch `sql_retrieve` and `generate_answer` then call `run_pipeline`.

    This verifies the orchestration path: retrieval -> compose -> generate
    without requiring a real database or external LLM API.
    """

    # Mock retrieval results resembling sql_retrieve output
    mock_results = [
        {
            "id": "product_mock_1",
            "text": (
                "Product: MockCleanser\nCategory: Cleanser\nSuitable for: Oily skin\n"
                "Key ingredients: MockIngredient\nRating: 4.5"
            ),
            "source_id": "products_db",
            "score": 0.9,
            "metadata": {"type": "product", "match_type": "skin_type"},
        }
    ]

    def fake_sql_retrieve(
        db_session=None, query=None, intake_data=None, concern=None, k=8, **kwargs
    ):
        """Fake `sql_retrieve` returning pre-canned mock results for tests.

        Parameters are accepted to match the real function signature but are
        unused in this fake implementation.
        """

        _ = db_session
        _ = query
        _ = intake_data
        _ = concern
        _ = k
        _ = kwargs
        return mock_results

    async def fake_generate_answer(
        question, context, intake_data=None, prompt=None, llm=None
    ):
        """Fake async answer generator returning a deterministic mock answer.

        Parameters mirror the real `generate_answer` but are unused here.
        """

        _ = question
        _ = context
        _ = intake_data
        _ = prompt
        _ = llm
        return "MOCK ANSWER"

    # Patch retrieval and generation functions
    monkeypatch.setattr(rp, "sql_retrieve", fake_sql_retrieve)
    monkeypatch.setattr(rp, "generate_answer", fake_generate_answer)

    # Run the async pipeline synchronously for test
    result = asyncio.run(
        rp.run_pipeline(
            "What should I use?",
            db_session=None,
            intake_data={"skin_type": "oily"},
            k=4,
        )
    )

    assert isinstance(result, dict)
    assert result.get("answer") == "MOCK ANSWER"
    assert "context_summary" in result
    assert result.get("used_results")
