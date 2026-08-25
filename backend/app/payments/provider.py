from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class ProviderPayment:
    provider_reference: str
    status: str

class FundsProvider(ABC):
    @abstractmethod
    def create_secure_funds_intent(self, transaction_code: str, amount_paise: int) -> ProviderPayment: ...
    @abstractmethod
    def verify_callback(self, payload: dict, signature: str|None) -> bool: ...

class SimulatedFundsProvider(FundsProvider):
    def create_secure_funds_intent(self, transaction_code, amount_paise):
        return ProviderPayment(f"SIM-{uuid4().hex[:12].upper()}", "PENDING")
    def verify_callback(self, payload, signature):
        return True
