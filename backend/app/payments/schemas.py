from pydantic import BaseModel


class SettlementResponse(BaseModel):
    settlement_id: str
    gross_amount_paise: int
    adjustment_paise: int
    platform_fee_paise: int
    final_amount_paise: int
    status: str
