import results


def test_joining():
    A = [dict(k=1, c=2), dict(k=2, c=3)]
    B = [dict(k=2, d=4), dict(k=2, d=5), dict(k=3, d=6)]

    INNER = [dict(k=2, c=3, d=4), dict(k=2, c=3, d=5)]

    LEFT = [dict(k=1, c=2, d=None), dict(k=2, c=3, d=4), dict(k=2, c=3, d=5)]

    RIGHT = [dict(k=2, c=3, d=4), dict(k=2, c=3, d=5), dict(k=3, c=None, d=6)]

    FULL = [
        dict(k=1, c=2, d=None),
        dict(k=2, c=3, d=4),
        dict(k=2, c=3, d=5),
        dict(k=3, c=None, d=6),
    ]

    a = results.Results(A)
    b = results.Results(B)

    joined = a.with_join(b)

    assert joined == results.Results(INNER)

    joined = a.with_join(b, left=True)
    assert joined == results.Results(LEFT)

    joined = a.with_join(b, right=True)
    assert joined == results.Results(RIGHT)

    joined = a.with_join(b, left=True, right=True)
    assert joined == results.Results(FULL)


def test_joining_with_nulls():

    A = [dict(k=1, c=2), dict(k=2, c=None), dict(k=None, c=9)]
    B = [dict(k=2, d=4), dict(k=2, d=5), dict(k=3, d=6), dict(k=None, d=10)]

    INNER = [dict(k=2, c=None, d=4), dict(k=2, c=None, d=5)]

    LEFT = [
        dict(k=1, c=2, d=None),
        dict(k=2, c=None, d=4),
        dict(k=2, c=None, d=5),
        dict(k=None, c=9, d=None),
    ]

    RIGHT = [
        dict(k=2, c=None, d=4),
        dict(k=2, c=None, d=5),
        dict(k=3, c=None, d=6),
        dict(k=None, c=None, d=10),
    ]

    FULL = [
        dict(k=1, c=2, d=None),
        dict(k=2, c=None, d=4),
        dict(k=2, c=None, d=5),
        dict(k=None, c=9, d=None),
        dict(k=3, c=None, d=6),
        dict(k=None, c=None, d=10),
    ]

    a = results.Results(A)
    b = results.Results(B)

    joined = a.with_join(b)

    assert joined == results.Results(INNER)

    joined = a.with_join(b, left=True)
    assert joined == results.Results(LEFT)

    joined = a.with_join(b, right=True)
    assert joined == results.Results(RIGHT)

    joined = a.with_join(b, left=True, right=True)
    assert joined == results.Results(FULL)
