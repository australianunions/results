import io
import itertools
from itertools import product
from numbers import Number

from .annotations import AnnotationsMixin
from .cleaning import standardized_key_mapping
from .result import Result
from .sqlutil import create_table_statement
from .typeguess import guess_sql_column_type


def results(rows):
    return Results(rows)


def resultproxy_to_results(rp):
    if rp.returns_rows:
        cols = rp.context.cursor.description
        keys = [c[0] for c in cols]

        r = Results(rp)
        r._keys_if_empty = keys
        return r
    else:
        return None


def get_keyfunc(column, columns):
    def _keyfunc(x):
        if column:
            return x[column]
        if columns:
            return tuple([x[k] for k in columns])

    return _keyfunc


class Results(list, AnnotationsMixin):
    def __init__(self, *args, **kwargs):
        try:
            given = args[0]
            given = [Result(_) for _ in given]

            args = list(args)
            args[0] = given
            args = tuple(args)

            self.paging = None
        except IndexError:
            pass
        self._keys_if_empty = None
        super().__init__(*args, **kwargs)

    def with_join(self, other, column=None, columns=None, left=False, right=False):

        a = self
        b = other

        a_keys = self.keys()
        b_keys = other.keys()

        a_other = {_: None for _ in a_keys if _ not in b_keys}
        b_other = {_: None for _ in b_keys if _ not in a_keys}

        if column is None and columns is None:
            column = a_keys[0]

        keyfunc = get_keyfunc(column, columns)

        bg = b.grouped_by(column=column, columns=columns)
        if right:
            ag = a.grouped_by(column=column, columns=columns)

        def do_it():
            for a_row in a:
                k = keyfunc(a_row)

                if k in bg:
                    for b_row in bg[k]:
                        yield {**a_row, **b_row}

                elif left:
                    yield {**a_row, **b_other}

            if right:
                for b_row in b:
                    k = keyfunc(b_row)

                    if k not in ag:
                        yield {**a_other, **b_row}

        return Results(do_it())

    def all_keys(self):
        keylist = dict()

        for row in self:
            rowkeys = row.keys()

            for key in rowkeys:
                if key not in keylist:
                    keylist[key] = True
        return list(keylist.keys())

    def by_key(self, key, value=None):
        def get_value(row):
            if value is None:
                return row
            else:
                return row[value]

        return {_[key]: get_value(_) for _ in self}

    def with_key_superset(self):
        all_keys = self.all_keys()

        def dict_with_all_keys(d):
            return {k: d.get(k, None) for k in all_keys}

        return Results([dict_with_all_keys(_) for _ in self])

    def with_renamed_keys(
        self, mapping, keep_unmapped_keys=True, fail_on_unmapped_keys=False
    ):
        def renamed_key(x):
            try:
                return mapping[x]
            except KeyError:
                if fail_on_unmapped_keys:
                    raise ValueError(f"unmapped key: {x}")
                if keep_unmapped_keys:
                    return x

        def renamed_it():
            for row in self:
                d = {
                    k_new: v
                    for k, v in row.items()
                    if (k_new := renamed_key(k)) is not None  # noqa
                }
                yield d

        return Results(renamed_it())

    def standardized_key_mapping(self):
        return standardized_key_mapping(self.keys())

    def with_standardized_keys(self):
        return self.with_renamed_keys(self.standardized_key_mapping())

    def with_reordered_keys(
        self, ordering, include_nonexistent=False, include_unordered=False
    ):
        if include_unordered:
            oset = set(ordering)
            ordering = ordering + [k for k in self.keys() if k not in oset]

        return Results(
            {k: _.get(k) for k in ordering if k in _ or include_nonexistent}
            for _ in self
        )

    def strip_values(self):
        for row in self:
            for k, v in row.items():
                if v and isinstance(v, str):
                    stripped = v.strip()

                    if stripped != v:
                        row[k] = stripped

    def strip_all_values(self):
        self.strip_values()

    def standardize_spaces(self):
        self.clean_whitespace()

    def clean_whitespace(self):
        for row in self:
            for k, v in row.items():
                if v and isinstance(v, str):
                    standardized = " ".join(v.split())

                    if standardized != v:
                        row[k] = standardized

    def delete_key(self, column=None):
        self.delete_keys([column])

    def delete_keys(self, columns=None):
        if not self:
            if self._keys_if_empty:
                for column in columns:
                    if column in self._keys_if_empty:
                        self._keys_if_empty.remove(column)
            return

        for row in self:
            for c in columns:
                try:
                    del row[c]
                except KeyError:
                    pass

    def set_blanks_to_none(self):
        for row in self:
            for k, v in row.items():
                if isinstance(v, str) and not v.strip():
                    row[k] = None

    def replace_values(self, before, after):
        for row in self:
            for k, v in row.items():
                if v == before:
                    row[k] = after

    def values_for(self, column=None, columns=None):
        if column is not None:
            values = [_[column] for _ in self]
        elif columns is not None:
            values = [tuple(_[c] for c in columns) for _ in self]
        else:
            values = list(self.values())
        return values

    def pop(self, column=None, default=None):
        if column is None:
            return list.pop(self)

        if isinstance(column, int):
            return list.pop(self, column)

        values = self.values_for(column=column)

        if column:
            columns = [column]
        self.delete_keys(columns)

        return values

    def distinct_values(self, column=None, columns=None):
        values = self.values_for(column, columns)

        d = {k: True for k in values}
        return list(d.keys())

    @property
    def csv(self):
        from .openers import write_csv_to_filehandle

        f = io.StringIO()
        write_csv_to_filehandle(f, self)
        return f.getvalue()

    def save_csv(self, destination):
        from .openers import write_csv_to_f

        write_csv_to_f(destination, self)

    def save_xlsx(self, destination):
        from xlsxwriter import Workbook

        workbook = Workbook(destination)
        worksheet = workbook.add_worksheet()

        for r, row in enumerate([self.keys()] + self):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)

        workbook.close()

    def keys(self):
        try:
            first = self[0]
        except IndexError:
            if self._keys_if_empty is None:
                return []
            else:
                return self._keys_if_empty
        return list(first.keys())

    def copy(self):
        return Results(self)

    def grouped_by(self, column=None, columns=None):
        keyfunc = get_keyfunc(column, columns)

        copied = Results(self)

        copied.sort(key=keyfunc)

        def grouped_by_it():
            for k, g in itertools.groupby(copied, keyfunc):
                yield k, Results(g)

        return dict(grouped_by_it())

    def __getitem__(self, x):
        if isinstance(x, slice):
            return Results(list(self)[x])
        elif isinstance(x, Number):
            return list.__getitem__(self, x)
        else:
            return [_[x] for _ in self]

    def one(self):
        length = len(self)
        if not length:
            raise RuntimeError("should be exactly one result, but there is none")
        elif length > 1:
            raise RuntimeError("should be exactly one result, but there is multiple")
        return self[0]

    def scalar(self):
        return self.one()[0]

    def pivoted(self):
        from .pivoting import pivoted

        return pivoted(self)
        try:
            down, across, values = self.keys()
        except ValueError:
            raise ValueError("pivoting requires exactly 3 columns")

        downvalues = self.distinct_values(down)
        acrossvalues = self.distinct_values(across)

        d = {(row[down], row[across]): row[values] for row in self}

        def pivoted_it():
            for downvalue in downvalues:
                out = {down: downvalue}
                row = {
                    acrossvalue: d.get((downvalue, acrossvalue), None)
                    for acrossvalue in acrossvalues
                }
                out.update(row)
                yield out

        return Results(pivoted_it())

    def make_hierarchical(self):
        previous = None

        for r in self:
            original = Result(r)
            if previous:
                for k, v in r.items():
                    if previous[k] == v:
                        r[k] = ""
                    else:
                        break
            previous = original

    @property
    def md(self):
        from tabulate import tabulate

        return tabulate(self, headers="keys", tablefmt="pipe")

    def guessed_sql_column_types(self):
        return {k: guess_sql_column_type(self.values_for(k)) for k in self.keys()}

    def guessed_create_table_statement(self, name):
        guessed = self.guessed_sql_column_types()
        return create_table_statement(name, guessed)

    def sort(self, **kwargs):
        if "key" not in kwargs:
            kwargs["key"] = lambda x: tuple(x.values())

        super().sort(**kwargs)
