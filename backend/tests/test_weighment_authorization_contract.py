import inspect

from app.weighment.router import (
    create_session,
    farmer_required,
    operator_required,
    post_acknowledge,
    post_lock,
    post_reading,
    post_receipt,
    post_reweigh,
    post_verification_video,
)

OPERATOR_MUTATIONS = (
    create_session,
    post_reading,
    post_lock,
    post_verification_video,
    post_reweigh,
)

FARMER_MUTATIONS = (
    post_acknowledge,
    post_receipt,
)


def _user_dependency(endpoint):
    return inspect.signature(endpoint).parameters["user"].default.dependency


def test_operator_weighment_mutations_require_operator_role():
    for endpoint in OPERATOR_MUTATIONS:
        assert _user_dependency(endpoint) is operator_required, endpoint.__name__


def test_farmer_weighment_mutations_require_farmer_role():
    for endpoint in FARMER_MUTATIONS:
        assert _user_dependency(endpoint) is farmer_required, endpoint.__name__


def test_farmer_acknowledgement_and_receipt_check_session_ownership():
    for endpoint in FARMER_MUTATIONS:
        source = inspect.getsource(endpoint)
        assert "_require_farmer_session_owner" in source, endpoint.__name__
