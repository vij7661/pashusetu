def priority_key(price_per_kg_paise: int, server_sequence: int):
    return (-price_per_kg_paise, server_sequence)


def test_highest_price_wins():
    bids = [(48800, 1839), (49200, 1842)]
    assert sorted(bids, key=lambda x: priority_key(*x))[0] == (49200, 1842)


def test_earliest_server_sequence_wins_equal_price():
    bids = [(49200, 1842), (49200, 1838)]
    assert sorted(bids, key=lambda x: priority_key(*x))[0] == (49200, 1838)
