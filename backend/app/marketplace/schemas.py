from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field


class ListingCreate(BaseModel):
    target_type: Literal["GOAT", "LOT"]
    target_id: str
    farmer_price_per_kg_paise: int = Field(gt=0)
    sale_type: Literal["COMPETITIVE_BIDDING", "FIXED_PRICE"] = "COMPETITIVE_BIDDING"
    opens_at: datetime
    closes_at: datetime
    recommendation_id: str | None = None


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


class ListingSearchResult(BaseModel):
    listing_id: str
    target_type: str
    verified_weight_kg: Decimal
    farmer_price_per_kg_paise: int
    farmer_total_value_paise: int
    status: str
