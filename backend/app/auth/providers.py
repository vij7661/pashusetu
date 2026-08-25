from abc import ABC, abstractmethod


class OTPProvider(ABC):
    @abstractmethod
    def send(self, mobile_e164: str, otp: str) -> None:
        raise NotImplementedError


class DevelopmentOTPProvider(OTPProvider):
    def send(self, mobile_e164: str, otp: str) -> None:
        # Never use this provider in pilot/production.
        print(f"[DEV OTP] {mobile_e164}: {otp}")
