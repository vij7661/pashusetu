from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class UploadContract:
    storage_key: str
    upload_url: str
    method: str = "PUT"
    expires_in_seconds: int = 900


class ObjectStorage(ABC):
    @abstractmethod
    def create_upload_contract(self, namespace: str, file_name: str, mime_type: str) -> UploadContract:
        raise NotImplementedError


class DevelopmentObjectStorage(ObjectStorage):
    def create_upload_contract(self, namespace: str, file_name: str, mime_type: str) -> UploadContract:
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else "bin"
        key = f"{namespace}/{uuid4().hex}.{ext}"
        return UploadContract(
            storage_key=key,
            upload_url=f"http://localhost:8000/dev-upload/{key}",
        )
