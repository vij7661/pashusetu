from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent


def test_transaction_router_does_not_expose_party_close_endpoint():
    source = (BACKEND_ROOT / "app/transaction/router.py").read_text(encoding="utf-8")

    assert '/{transaction_id}/close' not in source
    assert 'close_transaction_reputation' not in source


def test_settlement_service_owns_final_close_and_reputation_transition():
    source = (BACKEND_ROOT / "app/payments/settlement_service.py").read_text(encoding="utf-8")

    assert 'transition_transaction(db, tx, "CLOSED")' in source
    assert 'close_transaction_reputation(db, tx)' in source
    assert '_finalize_transaction_after_settlement(db, tx)' in source


def test_farmer_mobile_cannot_call_transaction_close_mutation():
    source = (
        REPO_ROOT
        / "apps/farmer_mobile/lib/src/features/transaction/transaction_repository.dart"
    ).read_text(encoding="utf-8")

    assert '/close' not in source
    assert 'Future<Map<String, dynamic>> close' not in source
