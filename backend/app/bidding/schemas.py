from decimal import Decimal
from pydantic import BaseModel, Field


class BidCreate(BaseModel):
    price_per_kg_paise: int = Field(gt=0)


class BidResponse(BaseModel):
    bid_id: str
    listing_id: str
    price_per_kg_paise: int
    total_offer_paise: int
    server_sequence: int
    status: str
    reject_reason: str | None = None


class BidAcceptanceResponse(BaseModel):
    listing_id: str
    accepted_bid_id: str
    accepted_server_sequence: int
    status: str
