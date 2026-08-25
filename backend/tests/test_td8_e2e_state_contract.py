from app.transaction.state_machine import assert_transition

def test_full_happy_path_transition_contract():
    path = [
        ("OFFER_ACCEPTED","AGREEMENT_PENDING"),
        ("AGREEMENT_PENDING","AGREEMENT_LOCKED"),
        ("AGREEMENT_LOCKED","FUNDS_SECURED"),
        ("FUNDS_SECURED","PICKUP_SCHEDULED"),
        ("PICKUP_SCHEDULED","PICKED_UP"),
        ("PICKED_UP","IN_TRANSIT"),
        ("IN_TRANSIT","DELIVERED"),
        ("DELIVERED","DELIVERY_VERIFICATION"),
        ("DELIVERY_VERIFICATION","TOLERANCE_CHECK"),
        ("TOLERANCE_CHECK","SETTLED"),
        ("SETTLED","CLOSED"),
    ]
    for current,target in path:
        assert_transition(current,target)

def test_full_dispute_path_transition_contract():
    path = [
        ("TOLERANCE_CHECK","DISPUTED"),
        ("DISPUTED","RESOLVED"),
        ("RESOLVED","SETTLED"),
        ("SETTLED","CLOSED"),
    ]
    for current,target in path:
        assert_transition(current,target)
