import json
import logging
from typing import Any

from google import genai
from google.genai import types  # pyright: ignore[reportMissingImports]
try:
    from PIL import Image as PILImage  # pyright: ignore[reportMissingImports]
except ImportError:
    PILImage = None

from app.core.config import settings  # pyright: ignore[reportMissingImports]
from app.schemas.planners import (  # pyright: ignore[reportMissingImports]
    BudgetAllocation,
    RecommendationResponse,
)
from app.services.catalog import (  # pyright: ignore[reportMissingImports]
    catalog_for,
)


logger = logging.getLogger(__name__)


def _create_gemini_client(api_key: str) -> tuple[Any, Any]:
    client = genai.Client(api_key=api_key)
    return client, types


def _generate_with_gemini(
    client: Any,
    gemini_types: Any,
    planner: str,
    request: Any,
    image: Any | None,
) -> RecommendationResponse:
    contents: list[Any] = [
        _prompt(planner, request, catalog_for(planner))
    ]
    if image is not None:
        contents.append(image)

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=contents,
        config=gemini_types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=3000,
            response_mime_type="application/json",
            response_schema=RecommendationResponse,
        ),
    )
    if not response.text:
        raise ValueError("Gemini returned an empty response")

    result = RecommendationResponse.model_validate_json(response.text)
    result.budget_total = float(request.budget)
    result.budget_remaining = round(
        float(request.budget) - result.estimated_total,
        2,
    )
    return result


def _fallback(
    planner: str,
    request: Any,
) -> RecommendationResponse:

    budget = float(request.budget)

    catalog = catalog_for(planner)

    if planner == "home":

        allocations = [
            BudgetAllocation(
                category="furniture",
                amount=budget * 0.40,
                percentage=40,
            ),
            BudgetAllocation(
                category="lighting",
                amount=budget * 0.15,
                percentage=15,
            ),
            BudgetAllocation(
                category="decor",
                amount=budget * 0.20,
                percentage=20,
            ),
            BudgetAllocation(
                category="storage",
                amount=budget * 0.15,
                percentage=15,
            ),
            BudgetAllocation(
                category="contingency",
                amount=budget * 0.10,
                percentage=10,
            ),
        ]

        desired = [
            x.name.lower()
            for x in request.items
        ]

        selected = [
            x
            for x in catalog
            if any(
                keyword in x["name"].lower()
                for keyword in desired
            )
        ]

        selected = selected or catalog[:5]

        summary = (
            f"A practical {request.style} home plan "
            f"for a ₹{budget:,.0f} budget across "
            f"{', '.join(request.rooms)}."
        )

        tips = [
            "Verify dimensions before buying.",
            "Keep a 10% contingency for delivery and installation.",
            "Compare final prices including delivery and taxes.",
        ]

    elif planner == "party":

        allocations = [
            BudgetAllocation(
                category="food",
                amount=budget * 0.45,
                percentage=45,
            ),
            BudgetAllocation(
                category="venue",
                amount=budget * 0.20,
                percentage=20,
            ),
            BudgetAllocation(
                category="decoration",
                amount=budget * 0.15,
                percentage=15,
            ),
            BudgetAllocation(
                category="entertainment",
                amount=budget * 0.10,
                percentage=10,
            ),
            BudgetAllocation(
                category="contingency",
                amount=budget * 0.10,
                percentage=10,
            ),
        ]

        selected = catalog

        summary = (
            f"A budget-conscious "
            f"{request.event_type} plan "
            f"for {request.guests} guests."
        )

        tips = [
            "Get per-person catering quotes.",
            "Confirm venue inclusions before paying.",
            "Keep a contingency for last-minute guest changes.",
        ]

    else:

        allocations = [
            BudgetAllocation(
                category="earrings",
                amount=budget * 0.25,
                percentage=25,
            ),
            BudgetAllocation(
                category="necklace",
                amount=budget * 0.45,
                percentage=45,
            ),
            BudgetAllocation(
                category="bracelet",
                amount=budget * 0.20,
                percentage=20,
            ),
            BudgetAllocation(
                category="contingency",
                amount=budget * 0.10,
                percentage=10,
            ),
        ]

        selected = catalog

        summary = (
            f"An {request.style} jewelry shortlist "
            f"for a {request.occasion} "
            f"within ₹{budget:,.0f}."
        )

        tips = [
            "Check metal composition and return policy.",
            "Match jewelry scale to the outfit neckline.",
            "Treat listed prices as estimates until verified.",
        ]

    recommendations = []

    running = 0.0

    for item in selected[:6]:

        price = float(item["price"])

        if (
            running + price <= budget * 0.95
            or not recommendations
        ):

            recommendations.append(
                {
                    "name": item["name"],
                    "category": item["category"],
                    "platform": item["platform"],
                    "estimated_price": price,
                    "reason": (
                        "Selected from the project's "
                        "demo catalog as a "
                        "budget-compatible option."
                    ),
                    "search_url": item["search_url"],
                    "budget_share": round(
                        price / budget * 100,
                        2,
                    ),
                }
            )

            running += price

    return RecommendationResponse(
        summary=summary,
        budget_total=budget,
        estimated_total=round(
            running,
            2,
        ),
        budget_remaining=round(
            budget - running,
            2,
        ),
        allocations=allocations,
        recommendations=recommendations,
        tips=tips,
    )


def _prompt(
    planner: str,
    request: Any,
    catalog: list[dict],
) -> str:

    catalog_text = json.dumps(
        catalog,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
You are PocketSmart AI,
a budget-aware recommendation assistant.

Planner:
{planner}

User request:

{request.model_dump_json(indent=2)}

Use ONLY the supplied demo catalog
for concrete product/vendor names and links.

Do not claim that prices are live.

Treat catalog prices as estimates.

Keep the estimated total at or below
the user's budget whenever possible.

Explain assumptions briefly.

Recommendations should be practical,
diverse, and relevant.

Return JSON matching the supplied schema.

Demo catalog:

{catalog_text}
"""


def generate_recommendation(
    planner: str,
    request: Any,
    image: Any | None = None,
) -> RecommendationResponse:

    if not settings.gemini_api_key:
        return _fallback(
            planner,
            request,
        )

    try:
        client, gemini_types = _create_gemini_client(
            settings.gemini_api_key
        )
        return _generate_with_gemini(
            client,
            gemini_types,
            planner,
            request,
            image,
        )

    except Exception as exc:

        logger.exception(
            "Gemini request failed; "
            "using fallback: %s",
            exc,
        )

        return _fallback(
            planner,
            request,
        )
