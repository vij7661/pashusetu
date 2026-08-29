from dataclasses import dataclass

from app.identity.schemas import FarmerPayoutSubmission


@dataclass(frozen=True)
class PayoutSetupResult:
    status: str
    method: str
    masked_reference: str


class PayoutDetailsService:
    """Replaceable setup boundary; it performs no transfer or provider call."""

    def setup(self, payout: FarmerPayoutSubmission) -> PayoutSetupResult:
        if payout.method == "UPI":
            handle = payout.upi_id.strip()
            local, domain = handle.split("@", 1)
            masked = f"{local[0]}***@{domain}"
        else:
            account = payout.account_number.strip()
            masked = f"XXXXXXXX{account[-4:]}"
        return PayoutSetupResult("QA_CONFIGURED", payout.method, masked)
