from typing import Literal

from pydantic import BaseModel, Field

PILOT_PRICE_BASIS = "DELIVERY_ADJUSTED_NET_KG"
PILOT_TRANSPORT_RESPONSIBILITY = "BUYER"
PILOT_DISPUTE_RULE = (
    "Controlled reweigh, independent verified scale if unresolved, then evidence review."
)


class AgreementCreate(BaseModel):
    price_basis: Literal["ORIGIN_VERIFIED_WEIGHT", "DELIVERY_ADJUSTED_NET_KG"] = PILOT_PRICE_BASIS
    pickup_point: str = Field(min_length=3, max_length=255)
    final_weighing_point: str = Field(min_length=3, max_length=255)
    tolerance_percent: float = Field(gt=0, le=10)
    transport_responsibility: Literal["FARMER", "BUYER", "PLATFORM"] = (
        PILOT_TRANSPORT_RESPONSIBILITY
    )
    dispute_rule: str = Field(default=PILOT_DISPUTE_RULE, min_length=10, max_length=2000)


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


class AgreementConfirmRequest(BaseModel):
    confirm: bool = True
