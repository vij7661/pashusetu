from app.agreement.schemas import AgreementCreate


def test_tolerance_percent_is_validated():
    payload = AgreementCreate(
        pickup_point="Verified pickup point",
        final_weighing_point="Verified final weighing point",
        tolerance_percent=1.5,
    )
    assert payload.tolerance_percent == 1.5
