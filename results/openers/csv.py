import csv
from itertools import islice
from pathlib import Path

from ..resultset import Results
from ..util import is_pathlike


def csv_column_names(path):
    return from_csv(path, max_rows=0).keys()


def sniff_csv_dialect(f, sniff_bytes=1024, seek_back_to_start=True):
    first_portion = f.read(sniff_bytes)

    if seek_back_to_start:
        f.seek(0)
    sniffer = csv.Sniffer()
    return sniffer.sniff(first_portion)


def csv_raw_rows_it(f, dialect=None, *args, **kwargs):
    dialect = dialect or sniff_csv_dialect(f)
    return csv.DictReader(f, dialect=dialect, *args, **kwargs)


def csv_rows_it(f, renamed_keys=None, *args, **kwargs):
    for row in csv_raw_rows_it(f):
        if renamed_keys:
            row = dict(zip(renamed_keys, row.values()))
        yield row


def from_csv(f, *args, dialect=None, encoding=None, max_rows=None, **kwargs):
    def make_results(reader):
        fieldnames = reader.fieldnames

        if max_rows is not None:
            reader = islice(reader, max_rows)

        r = Results(reader)
        r._keys_if_empty = fieldnames
        return r

    if is_pathlike(f):
        encoding = encoding or "utf-8-sig"

        with Path(f).open(encoding=encoding) as f:
            ri = csv_raw_rows_it(f, *args, dialect=dialect, **kwargs)
            return make_results(ri)
    else:
        ri = csv_raw_rows_it(f, *args, dialect=dialect, **kwargs)
        return make_results(ri)


def write_csv_to_filehandle(f, rows, **kwargs):
    try:
        first_row = rows[0]
        rows = rows[1:]
    except TypeError:
        first_row = next(rows)

    fieldnames = list(first_row.keys())

    class Dialect(csv.excel):
        lineterminator = "\n"

    w = csv.DictWriter(f, fieldnames=fieldnames, dialect=Dialect(), **kwargs)
    w.writeheader()
    w.writerow(first_row)
    w.writerows(rows)


def write_csv_to_f(f, rows, encoding=None):
    if is_pathlike(f):
        with Path(f).expanduser().open("w", encoding=encoding, newline="") as _f:
            write_csv_to_filehandle(_f, rows)
    else:
        write_csv_to_filehandle(f, rows)
