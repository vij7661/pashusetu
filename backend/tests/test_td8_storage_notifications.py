from app.core.storage import DevelopmentObjectStorage
from app.notifications.service import DevelopmentNotificationProvider, NotificationMessage

def test_dev_storage_contract():
    c = DevelopmentObjectStorage().create_upload_contract("goat/photo","goat.jpg","image/jpeg")
    assert c.method == "PUT"
    assert c.storage_key.endswith(".jpg")

def test_dev_notification_provider():
    ref = DevelopmentNotificationProvider().send(
        NotificationMessage(channel="SMS", recipient="+919999999999", template="TEST", variables={})
    )
    assert ref == "DEV-NOTIFICATION"
