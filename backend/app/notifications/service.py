from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class NotificationMessage:
    channel: str
    recipient: str
    template: str
    variables: dict


class NotificationProvider(ABC):
    @abstractmethod
    def send(self, message: NotificationMessage) -> str:
        raise NotImplementedError


class DevelopmentNotificationProvider(NotificationProvider):
    def send(self, message: NotificationMessage) -> str:
        print(f"[DEV NOTIFICATION] {message}")
        return "DEV-NOTIFICATION"
