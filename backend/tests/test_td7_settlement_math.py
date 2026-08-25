def settlement(gross:int, adjustment:int, fee_bps:int=150):
    fee=max(0,int((gross+adjustment)*fee_bps/10000))
    return gross+adjustment-fee,fee

def test_platform_fee_1_5_percent():
    final,fee=settlement(2_460_000,0,150)
    assert fee==36_900
    assert final==2_423_100

def test_negative_adjustment_reduces_settlement():
    final,fee=settlement(2_460_000,-100_000,150)
    assert final < 2_423_100
