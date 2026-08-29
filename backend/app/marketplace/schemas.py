from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ListingCreate(BaseModel):
    target_type: Literal["GOAT", "LOT"]
    target_id: str
    farmer_price_per_kg_paise: int = Field(gt=0)
    sale_type: Literal["COMPETITIVE_BIDDING", "FIXED_PRICE"] = "COMPETITIVE_BIDDING"
    opens_at: datetime
    closes_at: datetime
    recommendation_id: str | None = None


class ListingContextResponse(BaseModel):
    target_type: str
    target_id: str
    verified_weight_kg: Decimal
    market_code: str


class ListingResponse(BaseModel):
    listing_id: str
    target_type: str
    target_id: str
    verified_weight_kg: Decimal
    farmer_price_per_kg_paise: int
    farmer_total_value_paise: int
    sale_type: str
    opens_at: datetime
    closes_at: datetime
    status: str


class MarketRecommendationResponse(BaseModel):
    recommendation_id: str
    market_code: str
    breed: str | None
    price_per_kg_paise: int
    source_label: str
    valid_from: datetime
    valid_to: datetime | None


class _MarketReferenceFields(BaseModel):
    market_code: str = Field(min_length=2, max_length=40)
    breed: str | None = Field(default=None, max_length=80)
    price_per_kg_paise: int = Field(gt=0)
    source_label: str = Field(min_length=3, max_length=160)
    valid_to: datetime | None = None

    @field_validator("market_code", "source_label", mode="before")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("market_code")
    @classmethod
    def normalize_market_code(cls, value: str) -> str:
        return value.upper()

    @field_validator("breed", mode="before")
    @classmethod
    def trim_optional_breed(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class AdminMarketReferenceCreate(_MarketReferenceFields):
    valid_from: datetime


class AdminMarketReferenceEdit(_MarketReferenceFields):
    effective_from: datetime


class AdminMarketReferenceResponse(BaseModel):
    recommendation_id: str
    market_code: str
    breed: str | None
    price_per_kg_paise: int
    source_label: str
    valid_from: datetime
    valid_to: datetime | None
    created_at: datetime
    active: bool


class ListingSearchResult(BaseModel):
    listing_id: str
    target_type: str
    verified_weight_kg: Decimal
    farmer_price_per_kg_paise: int
    farmer_total_value_paise: int
    status: str
