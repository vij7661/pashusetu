def test_approved_weighment_flow_order():
    flow = [
        "LIVE",
        "WEIGHT_LOCKED",
        "FARMER_REVIEW",
        "ACKNOWLEDGED",
        "VERIFIED",
    ]
    assert flow.index("ACKNOWLEDGED") > flow.index("FARMER_REVIEW")
    assert flow.index("VERIFIED") > flow.index("ACKNOWLEDGED")
