import io
import itertools
from itertools import groupby
from numbers import Number

from .annotations import AnnotationsMixin
from .cleaning import standardized_key_mapping
from .result import Result
from .saving import save_xlsx
from .sqlutil import create_table_statement
from .typeguess import guess_sql_column_type
from .util import noneslarger as _noneslarger
from .util import nonessmaller as _nonessmaller


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


def get_keyfunc(column=None, columns=None, noneslarger=True):
    if noneslarger is True:
        f = _noneslarger
    elif noneslarger is False:
        f = _nonessmaller
    elif noneslarger is None:

        def ident(x):
            return x

        f = ident

    def _keyfunc(x):
        if column:
            return f(x[column])
        if columns:
            return tuple(f(x[k]) for k in columns)

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

    def with_join(
        self,
        other,
        column=None,
        columns=None,
        left=False,
        right=False,
        noneslarger=True,
    ):

        a = self
        b = other

        a_keys = self.keys()
        b_keys = other.keys()

        a_other = {_: None for _ in a_keys if _ not in b_keys}
        b_other = {_: None for _ in b_keys if _ not in a_keys}

        if column is None and columns is None:
            column = a_keys[0]

        keyfunc = get_keyfunc(column, columns, noneslarger=noneslarger)

        b_grouped = b.grouped_by(
            column=column, columns=columns, noneslarger=noneslarger
        )

        if right:
            a_grouped = a.grouped_by(
                column=column, columns=columns, noneslarger=noneslarger
            )

        def do_join_it():
            for a_row in a:
                k = keyfunc(a_row)

                if noneslarger is not None:
                    k = k[1]

                if k in b_grouped and k is not None:
                    for b_row in b_grouped[k]:
                        yield {**a_row, **b_row}
                elif left:
                    yield {**a_row, **b_other}

            if right:
                for b_row in b:
                    k = keyfunc(b_row)

                    if noneslarger is not None:
                        k = k[1]

                    if k is None or k not in a_grouped:
                        yield {**a_other, **b_row}

        return Results(do_join_it())

    def transposed(self):
        first_key, *remainder = self.keys()

        first_values = self[first_key]

        new_keys = (first_key, *first_values)

        def do_it():
            for k in remainder:
                yield dict(zip(new_keys, [k, *(self[k])]))

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
        self,
        mapping,
        keep_unmapped_keys=True,
        fail_on_unmapped_keys=False,
        fail_on_overwrite=True,
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
                    renamed_key(k): v
                    for k, v in row.items()
                    if renamed_key(k) is not None  # noqa
                }
                yield d

        # overwrite_check

        if fail_on_overwrite:
            original = self.keys()
            k_dict = {k: None for k in original}

            for o in original:
                renamed = renamed_key(o)

                if renamed != o:
                    if renamed in k_dict:
                        raise ValueError(
                            f"renaming {o} to {renamed} would overwrite {renamed}"
                        )

                k_dict.pop(o)
                if renamed is not None:
                    k_dict[renamed] = None

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
        save_xlsx({"Sheet1": self}, destination)

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

    def grouped_by(self, column=None, columns=None, sort=True, noneslarger=True):
        keyfunc = get_keyfunc(column, columns, noneslarger=noneslarger)

        copied = Results(self)

        if sort:
            copied.sort(key=keyfunc)

        def grouped_by_it():
            for k, g in itertools.groupby(copied, key=keyfunc):
                if noneslarger is not None:
                    if columns:
                        k = tuple(_[1] for _ in k)
                    else:
                        k = k[1]

                yield k, Results(g)

        return dict(grouped_by_it())

    def ltrsort(self, key=None, reverse=None, noneslarger=True, **kwargs):
        rev_keys = self.keys()

        if isinstance(reverse, bool):
            sort_order = {_: reverse for _ in rev_keys}
        else:
            reverse = reverse or []
            reverse = set(reverse)
            sort_order = {_: _ in reverse for _ in rev_keys}

        # sort from last -> first column
        sort_order = dict(reversed(sort_order.items()))

        for k, g in groupby(sort_order.items(), key=lambda x: x[1]):
            g = list(g)

            cols = [_[0] for _ in reversed(g)]

            keyfunc = get_keyfunc(column=None, columns=cols, noneslarger=noneslarger)

            self.sort(reverse=k, key=keyfunc)

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

    def new_row(self):
        return Result({k: None for k in self.keys()})

    def append_empty_row(self):
        row = self.new_row()
        self.append(row)
        return row
