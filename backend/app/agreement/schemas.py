from typing import Literal
from pydantic import BaseModel, Field


class AgreementCreate(BaseModel):
    price_basis: Literal["ORIGIN_VERIFIED_WEIGHT", "DELIVERY_ADJUSTED_NET_KG"]
    pickup_point: str = Field(min_length=3, max_length=255)
    final_weighing_point: str = Field(min_length=3, max_length=255)
    tolerance_percent: float = Field(gt=0, le=10)
    transport_responsibility: Literal["FARMER", "BUYER", "PLATFORM"]
    dispute_rule: str = Field(min_length=10, max_length=2000)


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
