from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ScaleSample:
    gross_kg: Decimal
    tare_kg: Decimal
    stable: bool

    @property
    def net_kg(self) -> Decimal:
        return self.gross_kg - self.tare_kg


class ScaleAdapter(ABC):
    """Vendor-neutral contract used by the Operator app/integration layer."""

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_sample(self) -> ScaleSample:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        raise NotImplementedError


class SimulatedScaleAdapter(ScaleAdapter):
    def __init__(self, gross_kg: Decimal, tare_kg: Decimal, stable: bool = True):
        self.sample = ScaleSample(gross_kg=gross_kg, tare_kg=tare_kg, stable=stable)
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def read_sample(self) -> ScaleSample:
        if not self.connected:
            raise RuntimeError("scale not connected")
        return self.sample

    def disconnect(self) -> None:
        self.connected = False
