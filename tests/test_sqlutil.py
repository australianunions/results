from results.sqlutil import ordering_from_parsed, parse_ordering, parse_ordering_col


def test_parse_ordering_col():
    x = parse_ordering_col
    assert x("abc") == ("abc", False)
    assert x("ABc") == ("ABc", False)
    assert x("ABC asc") == ("ABC", False)
    assert x("ABC desc") == ("ABC", True)
    assert x('"ABC " desc') == ("ABC ", True)

    # possibly this should throw an error instead?
    assert x("abc bad") == ("abc bad", False)


def test_parsing():
    x = ordering_from_parsed
    parsed = parse_ordering("a, b desc, C")
    assert x(parsed) == '"a", "b" desc, "C"'
