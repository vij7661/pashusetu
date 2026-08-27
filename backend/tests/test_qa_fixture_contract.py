from app.db.qa_fixtures import QA_USERS, QA_USERS_BY_ID


def test_canonical_qa_user_contract_is_exact_and_unique():
    assert {
        fixture.fixture_id: (fixture.local_mobile, fixture.role, fixture.language)
        for fixture in QA_USERS
    } == {
        "FARMER_EN_001": ("6123456789", "FARMER", "en"),
        "FARMER_TE_001": ("7234567890", "FARMER", "te"),
        "FARMER_SUB3_001": ("8345678901", "FARMER", "en"),
        "BUYER_001": ("9456789012", "BUYER", "en"),
        "OPERATOR_001": ("6789012345", "OPERATOR", "en"),
        "ADMIN_001": ("7890123456", "ADMIN", "en"),
    }
    assert len({fixture.local_mobile for fixture in QA_USERS}) == len(QA_USERS)
    assert QA_USERS_BY_ID["FARMER_SUB3_001"].local_mobile == "8345678901"
    assert {fixture.local_mobile[0] for fixture in QA_USERS} == {"6", "7", "8", "9"}
