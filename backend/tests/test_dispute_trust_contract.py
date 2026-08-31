from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import AppError
from app.disputes.service import _assert_reweigh_matches_listing, _require_open_dispute


def _listing_target():
    return SimpleNamespace(
        target_type="LOT",
        target_id=uuid4(),
        seller_farmer_profile_id=uuid4(),
    )


def test_open_dispute_accepts_additional_evidence():
    _require_open_dispute(SimpleNamespace(status="OPEN"))


def test_resolved_dispute_rejects_additional_evidence():
    with pytest.raises(AppError) as exc:
        _require_open_dispute(SimpleNamespace(status="RESOLVED"))
    assert exc.value.code == "DISPUTE_NOT_OPEN"


def test_reweigh_must_match_disputed_listing_target_and_farmer():
    listing = _listing_target()
    matching = SimpleNamespace(
        target_type=listing.target_type,
        target_id=listing.target_id,
        farmer_profile_id=listing.seller_farmer_profile_id,
    )
    _assert_reweigh_matches_listing(matching, listing)

    wrong_target = SimpleNamespace(
        target_type=listing.target_type,
        target_id=uuid4(),
        farmer_profile_id=listing.seller_farmer_profile_id,
    )
    with pytest.raises(AppError) as exc:
        _assert_reweigh_matches_listing(wrong_target, listing)
    assert exc.value.code == "REWEIGH_TARGET_MISMATCH"

    wrong_farmer = SimpleNamespace(
        target_type=listing.target_type,
        target_id=listing.target_id,
        farmer_profile_id=uuid4(),
    )
    with pytest.raises(AppError) as exc:
        _assert_reweigh_matches_listing(wrong_farmer, listing)
    assert exc.value.code == "REWEIGH_TARGET_MISMATCH"
