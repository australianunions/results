import results


def test_hist():
    r = results.Results(
        [dict(a=1, b=2, c=0, d="yo", e=-1), dict(a=5, b=-1, c=0, d="a", e=None)]
    )

    r.annotate_histogram_amplitudes()

    def get_annotations(rows):
        def histos(r):
            return [getattr(r[k], "histo", None) for k in r.keys()]

        return [histos(_) for _ in rows]

    assert get_annotations(r) == [
        [(0.0, 20.0), (33.333_333_333_333_33, 100.0), (0.0, 0.0), None, (0.0, 100.0)],
        [(0.0, 100.0), (0.0, 33.333_333_333_333_33), (0.0, 0.0), None, None],
    ]
