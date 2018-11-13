from pathlib import Path

from .openers import csv_row_tuples_it, csv_rows_it


def fast_csv_it(f, renamed_keys=None, *args, **kwargs):
    if isinstance(f, str):
        f = Path(f)

    if renamed_keys:
        ii = csv_row_tuples_it(f, *args, **kwargs)
        next(ii)  # skip header row

        for r in ii:
            yield dict(zip(renamed_keys, r))

    else:
        for r in csv_rows_it(f, *args, **kwargs):
            yield r
