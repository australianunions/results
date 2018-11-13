# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pendulum
import six
from pendulum.date import Date as date_type
from pendulum.datetime import DateTime as datetime_type


def guess_value_type(x):
    if x == "":
        return None

    try:
        f = float(x)
        if f.is_integer():
            return int
        else:
            return float
    except (ValueError, TypeError):
        pass

    try:
        p = pendulum.parse(x, exact=True)

        if isinstance(p, datetime_type):
            return datetime_type

        if isinstance(p, date_type):
            return date_type

    except Exception:
        pass

    return six.text_type


def guess_column_type(values):
    present = {guess_value_type(x) for x in values if x is not None}

    if six.text_type in present:
        return six.text_type
    if datetime_type in present:
        return datetime_type
    if date_type in present:
        return date_type
    if float in present:
        return float
    if int in present:
        return int
    return six.text_type


def guess_sql_column_type(values):
    return PY_TO_SQL[guess_column_type(values)]


PY_TO_SQL = {
    six.text_type: "text",
    datetime_type: "timestamp",
    date_type: "date",
    float: "decimal",
    int: "int",
    None: "text",
}
