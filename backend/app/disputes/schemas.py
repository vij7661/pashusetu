from typing import Literal
from pydantic import BaseModel, Field


class DisputeOpenRequest(BaseModel):
    reason: Literal["WEIGHT_DIFFERENCE", "WRONG_ANIMAL", "QUANTITY_MISMATCH", "OTHER"]
    disputed_amount_paise: int = Field(ge=0)


class EvidenceAddRequest(BaseModel):
    evidence_type: str = Field(min_length=3, max_length=50)
    evidence_reference: str = Field(min_length=3, max_length=255)


class ReweighAttachRequest(BaseModel):
    weighment_id: str
    stage: Literal["CONTROLLED", "INDEPENDENT"]


class DisputeResolveRequest(BaseModel):
    final_decision: str = Field(min_length=10, max_length=2000)
    settlement_adjustment_paise: int
    resolution_rule: str = Field(min_length=5, max_length=2000)


class DisputeResponse(BaseModel):
    dispute_id: str
    transaction_id: str
    reason: str
    disputed_amount_paise: int
    status: str
    settlement_adjustment_paise: int
    final_decision: str | None
