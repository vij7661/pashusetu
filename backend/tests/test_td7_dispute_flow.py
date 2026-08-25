from app.transaction.state_machine import assert_transition

def test_dispute_resolve_settle_flow():
    assert_transition("DISPUTED","RESOLVED")
    assert_transition("RESOLVED","SETTLED")
    assert_transition("SETTLED","CLOSED")
