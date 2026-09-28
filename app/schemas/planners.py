from typing import Literal

from pydantic import BaseModel, Field  # type: ignore[import-not-found]


PlannerType = Literal[
    "home",
    "party",
    "jewelry",
]


class HomeItem(BaseModel):

    name: str

    category: str

    quantity: int = Field(
        ge=1,
        le=100,
    )

    notes: str = ""


class HomeRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    rooms: list[str] = Field(
        min_length=1
    )

    items: list[HomeItem] = Field(
        min_length=1
    )

    style: str = "modern"

    city: str = ""

    priorities: str = ""


class PartyRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    guests: int = Field(
        gt=0,
        le=100_000,
    )

    event_type: str = Field(
        min_length=2,
        max_length=80,
    )

    venue: str = ""

    city: str = ""

    food_preference: str = ""

    decoration_style: str = ""

    priorities: str = ""


class JewelryRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    occasion: str = Field(
        min_length=2,
        max_length=80,
    )

    style: str = "elegant"

    metal: str = ""

    outfit_description: str = ""

    city: str = ""


class ProductRecommendation(BaseModel):

    name: str

    category: str

    platform: str

    estimated_price: float = Field(
        ge=0
    )

    reason: str

    search_url: str

    budget_share: float = Field(
        ge=0,
        le=100,
    )


class BudgetAllocation(BaseModel):

    category: str

    amount: float = Field(
        ge=0
    )

    percentage: float = Field(
        ge=0,
        le=100,
    )


class RecommendationResponse(BaseModel):

    summary: str

    budget_total: float

    estimated_total: float

    budget_remaining: float

    allocations: list[BudgetAllocation]

    recommendations: list[
        ProductRecommendation
    ]

    tips: list[str]
