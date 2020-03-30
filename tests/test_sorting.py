import results
from results import noneslarger, nonessmaller


def test_sorting():
    EXAMPLE = [2, None, 1, None]

    keyslist = list(map(noneslarger, EXAMPLE))

    assert keyslist == [(0, 2), (1, None), (0, 1), (1, None)]

    keyslist = list(map(nonessmaller, EXAMPLE))

    assert keyslist == [(0, 2), (-1, None), (0, 1), (-1, None)]

    e = list(EXAMPLE)
    e.sort(key=noneslarger)
    assert e == [1, 2, None, None]

    e.sort(key=nonessmaller)
    assert e == [None, None, 1, 2]


def test_results_sort():
    FULL = [
        dict(k=None, c=3, d=5),
        dict(k=3, c=None, d=6),
        dict(k=1, c=2, d=None),
        dict(k=2, c=3, d=4),
        dict(k=3, c=3, d=6),
        dict(k=3, c=3, d=5),
    ]

    r = results.Results(FULL)

    r.ltrsort()

    SORTED = [
        dict(k=1, c=2, d=None),
        dict(k=2, c=3, d=4),
        dict(k=3, c=3, d=5),
        dict(k=3, c=3, d=6),
        dict(k=3, c=None, d=6),
        dict(k=None, c=3, d=5),
    ]

    assert r == SORTED

    r.ltrsort(reverse=["c"])

    SORTED = [
        dict(k=1, c=2, d=None),
        dict(k=2, c=3, d=4),
        dict(k=3, c=None, d=6),
        dict(k=3, c=3, d=5),
        dict(k=3, c=3, d=6),
        dict(k=None, c=3, d=5),
    ]

    assert r == SORTED

    r.ltrsort(reverse=["c"], noneslarger=False)

    SORTED = [
        dict(k=None, c=3, d=5),
        dict(k=1, c=2, d=None),
        dict(k=2, c=3, d=4),
        dict(k=3, c=3, d=5),
        dict(k=3, c=3, d=6),
        dict(k=3, c=None, d=6),
    ]

    assert r == SORTED
