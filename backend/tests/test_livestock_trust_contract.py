import inspect
from types import SimpleNamespace
from uuid import uuid4

from app.livestock.schemas import GoatCreate
from app.livestock.service import create_evidence_upload_contract, create_goat, create_lot


class _FakeDb:
    def __init__(self):
        self.flush_count = 0
        self.commit_count = 0
        self.refresh_count = 0

    def add(self, row):
        if getattr(row, "id", None) is None:
            row.id = uuid4()

    def flush(self):
        self.flush_count += 1

    def commit(self):
        self.commit_count += 1

    def refresh(self, _row):
        self.refresh_count += 1


def test_goat_registration_and_audit_share_one_commit(monkeypatch):
    user_id = uuid4()
    farmer = SimpleNamespace(id=uuid4())
    db = _FakeDb()
    events = []
    monkeypatch.setattr("app.livestock.service.farmer_profile_for_user", lambda *_args: farmer)
    monkeypatch.setattr(
        "app.livestock.service.append_event",
        lambda *args, **kwargs: events.append((args, kwargs)),
    )

    goat = create_goat(
        db,
        user_id,
        GoatCreate(breed="Sirohi", sex="MALE", age_months=12, health_notes=None),
    )

    assert goat.farmer_profile_id == farmer.id
    assert db.flush_count == 1
    assert db.commit_count == 1
    assert db.refresh_count == 1
    assert len(events) == 1
    args, kwargs = events[0]
    assert args[1:5] == ("GOAT", goat.id, "GOAT_REGISTERED", user_id)
    assert kwargs["commit"] is False


def test_lot_and_evidence_mutations_append_audit_before_commit():
    lot_source = inspect.getsource(create_lot)
    evidence_source = inspect.getsource(create_evidence_upload_contract)

    assert '"LOT_REGISTERED"' in lot_source
    assert "commit=False" in lot_source
    assert '"EVIDENCE_UPLOAD_CONTRACT_CREATED"' in evidence_source
    assert "commit=False" in evidence_source
