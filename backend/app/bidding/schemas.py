from decimal import Decimal

from pydantic import BaseModel, Field


class BidCreate(BaseModel):
    price_per_kg_paise: int = Field(gt=0)
    selected_goat_ids: list[str] = []
    whole_lot: bool = False


class BidResponse(BaseModel):
    bid_id: str
    listing_id: str
    price_per_kg_paise: int
    total_offer_paise: int
    server_sequence: int
    status: str
    reject_reason: str | None = None
    selected_goat_ids: list[str] = []
    selected_quantity: int
    selected_weight_kg: Decimal | None
    whole_lot: bool
    transaction_id: str | None = None


class BidAcceptanceResponse(BaseModel):
    listing_id: str
    accepted_bid_id: str
    accepted_server_sequence: int
    status: str
    transaction_id: str
