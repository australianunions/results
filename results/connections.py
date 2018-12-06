from contextlib import contextmanager
from functools import partial
from pathlib import Path

from schemainspect import get_inspector
from sqlbag import S, raw_execute

from .inserting import insert
from .migration import SchemaManagement
from .paging import Paging, paging_wrapped_query
from .resultset import resultproxy_to_results


def build_proc_call_query(_proc_name, *args, **kwargs):
    _proc_name = _proc_name.replace("__", ".")
    params = {f"positional{i}": x for i, x in enumerate(args)}
    params.update(**dict(kwargs))
    paramnames = params.keys()
    bindparams = [f":{name}" for name in list(paramnames)]
    paramspec = ", ".join(bindparams)
    query = f"select * from {_proc_name}({paramspec})"
    return query, params


class transactionprocs:
    def __init__(self, sess):
        self.session = sess

    def __getattr__(self, name):
        return partial(self.call, name)

    def call(self, _proc_name, *args, **kwargs):
        query, params = build_proc_call_query(_proc_name, *args, **kwargs)

        return self.session.ex(query, params)


class transaction:
    def __init__(self, s):
        self.s = s
        self.procs = transactionprocs(self)

    def ex(self, *args, **kwargs):
        _resultproxy = self.s.execute(*args, **kwargs)
        results = resultproxy_to_results(_resultproxy)
        return results

    def paged(
        self,
        query,
        bookmark,
        ordering,
        per_page,
        backwards,
        *args,
        use_top=False,
        supports_row=True,
        **kwargs,
    ):
        query, page_params = paging_wrapped_query(
            query, ordering, bookmark, per_page, backwards, use_top, supports_row
        )

        argslist = list(args)
        try:
            params = argslist[0]
        except IndexError:
            argslist.append({})
            params = argslist[0]

        params.update(page_params)

        argslist[0] = params

        args = tuple(argslist)

        results = self.ex(query, *args, **kwargs)
        results.paging = Paging(results, per_page, ordering, bookmark, backwards)

        return results

    def insert(self, table, rowlist, upsert_on=None, returning=None):
        return insert(self.s, table, rowlist, upsert_on, returning)


class procs:
    def __init__(self, db):
        self.db = db

    def __getattr__(self, name):
        return partial(self.call, name)

    def call(self, _proc_name, *args, **kwargs):
        _proc_name = _proc_name.replace("__", ".")

        with self.db.transaction() as s:
            query, params = build_proc_call_query(_proc_name, *args, **kwargs)
            return s.ex(query, params)


class db(SchemaManagement):
    def __init__(self, *args, **kwargs):
        self._args = args
        if args and args[0].startswith("postgres"):
            kwargs.setdefault("use_batch_mode", True)
        self._kwargs = kwargs

    @contextmanager
    def transaction(self):
        with S(*self._args, **self._kwargs) as s:
            yield transaction(s)

    @property
    def procs(self):
        return procs(self)

    @property
    def db_url(self):
        return self._args[0]

    def ss(self, *args, **kwargs):
        with self.transaction() as t:
            return t.ex(*args, **kwargs)

    def paged(self, *args, **kwargs):
        with self.transaction() as t:
            return t.paged(*args, **kwargs)

    def raw_from_file(self, f):
        sql = Path(f).read_text()
        return self.raw(sql)

    def ss_from_file(self, f, *args, **kwargs):
        sql = Path(f).read_text()
        return self.ss(sql, *args, **kwargs)

    def paged_from_file(self, f, *args, **kwargs):
        sql = Path(f).read_text()
        return self.paged(sql, *args, **kwargs)

    def insert(self, table, rowlist, upsert_on=None, returning=None):
        with self.transaction() as s:
            inserted = s.insert(table, rowlist, upsert_on, returning)
        return inserted

    def raw(self, sql):
        with S(*self._args, **self._kwargs) as s:
            _results = raw_execute(s, sql)
            return _results

    def inspect(self):
        with S(*self._args, **self._kwargs) as s:
            i = get_inspector(s)
        return i
