from pytest import raises

import results
from results import standardized_key_mapping, trunc

test_keys = {"   abc DE !!!()f": "abc_de_f", "Abc_123": "abc_123"}


def test_standardized_keys():
    renamed = standardized_key_mapping(test_keys.keys())
    assert renamed == test_keys


def test_key_renaming():
    SAMPLE = dict(a=None, b=None, c=None, d=None)

    r = results.Results([SAMPLE])
    assert r.keys() == "a b c d".split()

    with raises(ValueError):
        r.with_renamed_keys({"d": "a"})

    # shouldn't raise
    r2 = r.with_renamed_keys(dict(a="e", d="a"))
    assert r2.keys() == "e b c a".split()

    renames = dict(a="a", b="bb", c=None,)  # unchanged  # changed  # removed

    r2 = r.with_renamed_keys(renames)
    assert r2.keys() == "a bb d".split()

    r2 = r.with_renamed_keys(renames, keep_unmapped_keys=False)
    assert r2.keys() == "a bb".split()

    with raises(ValueError):
        r2 = r.with_renamed_keys(renames, fail_on_unmapped_keys=True)

    r3 = r.with_reordered_keys("b a".split())
    assert r3.keys() == "b a".split()

    r3 = r.with_reordered_keys("b a".split(), include_unordered=True)
    assert r3.keys() == "b a c d".split()

    r3 = r.with_reordered_keys("b a extra".split(), include_nonexistent=True)
    assert r3.keys() == "b a extra".split()

    r3 = r.with_reordered_keys(
        "b a extra".split(), include_unordered=True, include_nonexistent=True
    )
    assert r3.keys() == "b a extra c d".split()


def test_trunc():
    assert trunc("abcd", 3) == "abc\u2026"
