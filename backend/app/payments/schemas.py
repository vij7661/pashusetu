from typing import Literal

from pydantic import BaseModel, Field


class SecureFundsResponse(BaseModel):
    payment_intent_id: str
    provider_reference: str
    amount_paise: int = Field(gt=0)
    status: Literal["SECURED"]
    transaction_state: Literal["FUNDS_SECURED"]


class SettlementResponse(BaseModel):
    settlement_id: str
    gross_amount_paise: int
    adjustment_paise: int
    platform_fee_paise: int
    final_amount_paise: int
    status: str
