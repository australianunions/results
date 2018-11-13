from results import csv_column_names, fast_csv_it, standardized_key_mapping


def test_fastit():
    path = "tests/FIXTURES/datafiles/x.csv"

    cols = csv_column_names(path)

    renamed = standardized_key_mapping(cols)
    renamed = list(renamed.values())

    fit = fast_csv_it(path, renamed_keys=renamed)

    assert list(fit) == [
        {"a": "1", "b": "2", "c": "3"},
        {"a": "4", "b": "5 ", "c": "6"},
    ]

    # default
    fit = fast_csv_it(path)

    assert list(fit) == [
        {"A": "1", "b": "2", "c": "3"},
        {"A": "4", "b": "5 ", "c": "6"},
    ]
