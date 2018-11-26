import base64
import csv
import io
import json
from itertools import zip_longest

from .sqlutil import ordering_from_parsed, parse_ordering, reversed_ordering

sio = io.StringIO
csvreader = csv.reader
csvwriter = csv.writer


PAGED_QUERY = """
select * from
(
{q}
) unpaged_table
{bookmark}
{order_by}
{limit}
"""

PAGED_QUERY_MSSQL = """
select {limit} * from
(
{q}
) unpaged_table
{bookmark}
{order_by}
"""

PARAM_PREFIX = "paging_bookmark_"


def encode_bookmark_values(decoded):
    j = json.dumps(decoded)
    j8 = j.encode("utf-8")
    return base64.urlsafe_b64encode(j8).decode("utf-8")


def decode_bookmark(encoded):
    j = base64.urlsafe_b64decode(encoded)
    jt = j.decode("utf-8")
    return json.loads(jt)


def bind_pairs_iter(cols, bookmark, swap_on_descending=False):
    for i, zipped in enumerate(zip(cols, bookmark)):
        col, val = zipped
        name, is_descending = col
        lowercase_name = name.lower()
        bind = f":{PARAM_PREFIX}{lowercase_name}"

        if swap_on_descending and is_descending:
            yield name, bind
        else:
            yield bind, name


def generate_or_statement(a, b, a_compared, b_compared):
    if a and b:
        a_first, b_first = a[0], b[0]
        or_statement = generate_or_statement(
            a[1:], b[1:], a_compared + [a[0]], b_compared + [b[0]]
        )
        equalities = [f"{x} = {y}" for x, y in zip(a_compared, b_compared)]
        equalities_joined = " and ".join(equalities)
        if or_statement:
            return f"({equalities_joined} and {a_first} > {b_first}) or {or_statement}"
        else:
            return f"({equalities_joined} and {a_first} > {b_first})"


def recursive_comparison(a, b):
    or_statement = generate_or_statement(a[1:], b[1:], [a[0]], [b[0]])
    return f"({a[0]} > {b[0]} or {or_statement})"


def make_bookmark_where_clause(cols, bookmark, backwards=False, supports_row=True):
    if bookmark is None:
        return ""

    pairslist = bind_pairs_iter(cols, bookmark, swap_on_descending=True)

    b, a = zip(*pairslist)
    if len(a) > 1 or len(b) > 1:
        if supports_row:
            a, b = ", ".join(a), ", ".join(b)
            return f"where row({a}) > row({b})"
        else:
            return f"where {recursive_comparison(a, b)}"
    else:
        return f"where {a[0]} > {b[0]}"


def paging_params(cols, bookmark):
    names = [PARAM_PREFIX + c[0].lower() for c in cols]
    return dict(zip_longest(names, bookmark or []))


def paging_wrapped_query(
    query, ordering, bookmark, per_page, backwards, use_top=False, supports_row=True
):
    cols = parse_ordering(ordering)
    if backwards:
        cols = reversed_ordering(cols)

    bookmark_clause = make_bookmark_where_clause(
        cols, bookmark, backwards, supports_row=supports_row
    )
    order_list = ordering_from_parsed(cols)
    order_by = f"order by {order_list}"
    if use_top:
        limit = f"top {per_page + 1}"
    else:
        limit = f"limit {per_page + 1}"

    params = paging_params(cols, bookmark)
    formatted = (PAGED_QUERY_MSSQL if use_top else PAGED_QUERY).format(
        q=query, bookmark=bookmark_clause, order_by=order_by, limit=limit
    )
    return formatted, params


class Paging:
    def __init__(self, results, per_page, ordering, bookmark, backwards):
        self.results = results
        self.per_page = per_page
        self.ordering = ordering
        self.bookmark = bookmark
        self.backwards = backwards
        self.parsed_ordering = parse_ordering(ordering)
        self.order_keys = [c[0] for c in self.parsed_ordering]

        try:
            self.discarded_item = results.pop(per_page)
            self.has_more = True
        except IndexError:
            self.discarded_item = None
            self.has_more = False

        if backwards:
            results.reverse()
        self.count = len(self.results)

    @property
    def has_after(self):
        return self.discarded_item is not None

    @property
    def has_before(self):
        return self.bookmark is not None

    @property
    def has_next(self):
        if self.backwards:
            return self.has_before
        else:
            return self.has_after

    @property
    def has_prev(self):
        if self.backwards:
            return self.has_after
        else:
            return self.has_before

    @property
    def at_start(self):
        return not self.has_prev

    @property
    def at_end(self):
        return not self.has_next

    @property
    def is_all(self):
        return self.at_start and self.at_end

    @property
    def is_full(self):
        return self.count == self.per_page

    @property
    def past_start(self):
        return self.backwards and self.at_start and not self.is_full

    @property
    def past_end(self):
        return not self.backwards and self.at_end and not self.is_full

    @property
    def next(self):
        if not self.is_empty:
            return self.get_bookmark(self.results[-1])

    @property
    def prev(self):
        if not self.is_empty:
            return self.get_bookmark(self.results[0])

    @property
    def is_empty(self):
        return not bool(self.count)

    @property
    def current(self):
        return self.bookmark

    @property
    def current_reversed(self):
        if self.discarded_item:
            return self.get_bookmark(self.discarded_item)

    def get_bookmark(self, result_row):
        return tuple(result_row[k] for k in self.order_keys)
