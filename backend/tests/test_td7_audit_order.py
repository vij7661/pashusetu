def test_event_sequences_are_ordered():
    seq=[1,2,3,4,5]
    assert seq==sorted(seq)
    assert len(seq)==len(set(seq))
