from types import SimpleNamespace
from uuid import uuid4

from app.weighment import service as weighment_service


class FakeDb:
    def __init__(self):
        self.added = []
        self.commit_count = 0
        self.flush_count = 0

    def add(self, value):
        self.added.append(value)

    def flush(self):
        self.flush_count += 1
        for value in self.added:
            if getattr(value, "id", None) is None:
                value.id = uuid4()

    def commit(self):
        self.commit_count += 1

    def refresh(self, _value):
        return None


def test_weighment_start_and_audit_share_one_authoritative_commit(monkeypatch):
    db = FakeDb()
    operator_user_id = uuid4()
    operator = SimpleNamespace(id=uuid4(), centre_id=uuid4())
    target = SimpleNamespace(id=uuid4(), farmer_profile_id=uuid4())
    scale = SimpleNamespace(id=uuid4())
    events = []

    monkeypatch.setattr(weighment_service, "operator_for_user", lambda _db, _user_id: operator)
    monkeypatch.setattr(
        weighment_service,
        "resolve_target",
        lambda _db, _target_type, _target_code: target,
    )
    monkeypatch.setattr(
        weighment_service,
        "resolve_scale_for_operator",
        lambda _db, _operator, _scale_code: scale,
    )

    def fake_append_event(
        event_db,
        aggregate_type,
        aggregate_id,
        event_type,
        actor_user_id=None,
        request_id=None,
        payload=None,
        *,
        commit=True,
    ):
        events.append(
            {
                "aggregate_type": aggregate_type,
                "aggregate_id": aggregate_id,
                "event_type": event_type,
                "actor_user_id": actor_user_id,
                "request_id": request_id,
                "payload": payload,
                "commit": commit,
            }
        )
        event_db.flush()
        return SimpleNamespace()

    monkeypatch.setattr(weighment_service, "append_event", fake_append_event)

    session = weighment_service.start_weighment(
        db,
        operator_user_id=operator_user_id,
        target_type="GOAT",
        target_code="GOAT-TEST",
        scale_code="SCALE-TEST",
    )

    assert session.status == "LIVE"
    assert db.commit_count == 1
    assert events == [
        {
            "aggregate_type": "WEIGHMENT",
            "aggregate_id": session.id,
            "event_type": "WEIGHMENT_STARTED",
            "actor_user_id": operator_user_id,
            "request_id": None,
            "payload": {
                "status": "LIVE",
                "target_type": "GOAT",
                "target_id": str(target.id),
                "centre_id": str(operator.centre_id),
                "scale_id": str(scale.id),
                "reweigh_of_id": None,
            },
            "commit": False,
        }
    ]
