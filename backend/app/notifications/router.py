from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.dependencies import require_permission
from app.identity.models import User
from app.notifications.service import (
    DevelopmentNotificationProvider,
    NotificationMessage,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationTestRequest(BaseModel):
    channel: str = "SMS"
    recipient: str
    template: str
    variables: dict = {}


@router.post("/test")
def send_test_notification(
    payload: NotificationTestRequest,
    user: User = Depends(require_permission("transaction:view")),
):
    reference = DevelopmentNotificationProvider().send(
        NotificationMessage(
            channel=payload.channel,
            recipient=payload.recipient,
            template=payload.template,
            variables=payload.variables,
        )
    )
    return {"notification_reference": reference}
