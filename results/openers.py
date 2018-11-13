import io
from itertools import islice
from pathlib import Path

import chardet
import csvx

from .resultset import Results


def detect_string_enc(contents):
    b = io.BytesIO(contents)
    b.seek(0)
    return detect_enc(b)


def detect_enc(f):
    return chardet.detect(f.read())["encoding"]


def smart_open(f):
    try:
        return io.open(f)
    except TypeError:
        return f


def first_n_lines(stream, n=10):
    head = list(islice(stream, n))
    return head


def csv_column_names(f, *args, **kwargs):
    if isinstance(f, str):
        f = Path(f)

    f = smart_open(f)
    head = first_n_lines(f, n=1)[0]
    f.seek(0)

    headf = io.StringIO(head)

    with csvx.OrderedDictReader(headf, *args, **kwargs) as r:
        return r.fieldnames


def csv_rows_it(f, *args, **kwargs):
    with csvx.OrderedDictReader(f, *args, **kwargs) as r:
        for row in r:
            yield row


def csv_row_tuples_it(f, *args, **kwargs):
    with csvx.Reader(f, *args, **kwargs) as r:
        for row in r:
            yield row


def from_csv(f, *args, **kwargs):
    return Results(csv_rows_it(f, *args, **kwargs))


def dicts_from_rows(rows):
    try:
        first = rows[0]
    except IndexError:
        return []
    rest = rows[1:]

    def it():
        for d in rest:
            dd = dict(zip(first, d))
            yield dd

    return list(it())


def from_xlsx(f):
    from openpyxl import load_workbook

    if isinstance(f, Path):
        f = str(f)
    wb = load_workbook(filename=f)

    wsheets = list(wb)

    def xget_row_values(row):
        return [c.internal_value or "" for c in list(row)]

    def do_sheet(ws):
        rows = [xget_row_values(_) for _ in list(ws.rows)]
        return dicts_from_rows(rows)

    return dict(zip(wb.sheetnames, (Results(do_sheet(_)) for _ in wsheets)))


def from_xls(f, file_contents=None):
    from xlrd import open_workbook

    wb = open_workbook(str(f), file_contents=file_contents)

    def get_row_values(ws, rownum):
        return [str(ws.cell_value(rowx=rownum, colx=c) or "") for c in range(ws.ncols)]

    def do_sheet(ws):
        rows = [get_row_values(ws, rx) for rx in range(ws.nrows)]
        return dicts_from_rows(rows)

    wsheets = [wb.sheet_by_index(_) for _ in range(wb.nsheets)]

    return dict(zip(wb.sheet_names(), (Results(do_sheet(_)) for _ in wsheets)))


OPENERS = {".xlsx": from_xlsx, ".xls": from_xls, ".csv": from_csv}


def from_file(f):
    p = Path(f)

    extension = p.suffix

    try:
        return OPENERS[extension](f)
    except KeyError:
        raise ValueError(f"cannot open a file with extension: {extension}")
