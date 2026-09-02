from tests.fixtures.farmer_lifecycle_v3 import FARMER_LIFECYCLE_QA


def test_farmer_lifecycle_v3_fixture_integrity():
    assert [row["lifecycle_state"] for row in FARMER_LIFECYCLE_QA] == [
        "NEW_NOT_STARTED",
        "REGISTRATION_STARTED",
        "DETAILS_COMPLETED",
        "KYC_PENDING",
        "KYC_VERIFIED",
    ]
    assert len({row["mobile_e164"] for row in FARMER_LIFECYCLE_QA}) == 5
    assert len({row["fixture_id"] for row in FARMER_LIFECYCLE_QA}) == 5

    for row in FARMER_LIFECYCLE_QA:
        assert row["dev_otp"].isdigit()
        assert len(row["dev_otp"]) == 4
        assert row["reuse_policy"] in {
            "CONSUMABLE_RESET_REQUIRED",
            "STABLE_UNTIL_MUTATED",
            "STABLE_READ_ONLY",
        }

    fresh, started, details, pending, verified = FARMER_LIFECYCLE_QA

    assert fresh["registration_exists"] is False
    assert fresh["farmer_account_exists"] is False
    assert fresh["expected_registration_next_step"] == "FARMER_DETAILS"

    assert started["registration_exists"] is True
    assert started["details_completed"] is False
    assert started["farmer_account_exists"] is False
    assert started["expected_registration_next_step"] == "FARMER_DETAILS"

    assert details["registration_exists"] is True
    assert details["details_completed"] is True
    assert details["farmer_account_exists"] is False
    assert details["expected_registration_next_step"] == "KYC"

    assert pending["farmer_account_exists"] is True
    assert pending["kyc_status"] == "KYC_PENDING"
    assert pending["expected_registration_next_step"] is None

    assert verified["farmer_account_exists"] is True
    assert verified["kyc_status"] == "KYC_VERIFIED"
    assert verified["expected_registration_next_step"] is None
