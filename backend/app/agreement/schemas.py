from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AgreementCreate(BaseModel):
    price_basis: Literal["ORIGIN_VERIFIED_WEIGHT", "DELIVERY_ADJUSTED_NET_KG"]
    pickup_point: str = Field(min_length=3, max_length=255)
    final_weighing_point: str = Field(min_length=3, max_length=255)
    tolerance_percent: float = Field(gt=0, le=10)
    transport_responsibility: Literal["FARMER", "BUYER", "PLATFORM"]
    dispute_rule: str = Field(min_length=10, max_length=2000)

    @field_validator("tolerance_percent")
    @classmethod
    def approved_pilot_tolerance(cls, value: float) -> float:
        if value != 1.5:
            raise ValueError("pilot tolerance must be the approved 1.5 percent")
        return value


class AgreementResponse(BaseModel):
    agreement_id: str
    transaction_id: str
    version: int
    price_basis: str
    pickup_point: str
    final_weighing_point: str
    tolerance_percent: float
    transport_responsibility: str
    dispute_rule: str
    farmer_confirmed: bool
    buyer_confirmed: bool
    locked: bool
    status: str
    accepted_bid_id: str
    listing_id: str
    farmer_profile_id: str
    buyer_profile_id: str
    selected_goat_ids: list[str]
    whole_lot: bool
    accepted_price_per_kg_paise: int
    agreed_weight_kg: float
    livestock_amount_paise: int


class AgreementConfirmRequest(BaseModel):
    confirm: bool = True
