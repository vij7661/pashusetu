from pydantic import BaseModel


class TransactionResponse(BaseModel):
    transaction_id: str
    listing_id: str
    accepted_bid_id: str
    state: str
    active_agreement_id: str | None
