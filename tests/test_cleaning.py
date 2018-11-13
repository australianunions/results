from results import standardized_key_mapping

test_keys = {"   abc DE !!!()f": "abc_de_f", "Abc_123": "abc_123"}


def test_standardized_keys():
    renamed = standardized_key_mapping(test_keys.keys())
    assert renamed == test_keys
