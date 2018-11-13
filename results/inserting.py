INSERT = """
    insert into
        {table} ({colspec})
    values
        ({valuespec})
"""

INSERT_UPSERT = """
    on conflict ({upsertkeyspec})
    do update set
        {upsertspec}
"""


INSERT_UPSERT = """
    on conflict ({upsertkeyspec})
    do update set
        {upsertspec}
"""


INSERT_UPSERT_DO_NOTHING = """
    on conflict ({upsertkeyspec})
    do nothing
"""


def insert(s, table, rowslist, upsert_on=None):
    if not rowslist:
        raise ValueError("empty list of rows, nothing to upsert")

    keys = rowslist[0].keys()

    colspec = ", ".join([f'"{k}"' for k in keys])
    valuespec = ", ".join(":{}".format(k) for k in keys)

    q = INSERT.format(table=table, colspec=colspec, valuespec=valuespec)

    if upsert_on:
        upsert_keys = list(keys)
        for k in upsert_on:
            upsert_keys.remove(k)

        upsertkeyspec = ", ".join([f'"{k}"' for k in upsert_on])

        if upsert_keys:
            upsertspec = ", ".join(f'"{k}" = excluded."{k}"' for k in upsert_keys)

            q_upsert = INSERT_UPSERT.format(
                upsertkeyspec=upsertkeyspec, upsertspec=upsertspec
            )
        else:
            q_upsert = INSERT_UPSERT_DO_NOTHING.format(upsertkeyspec=upsertkeyspec)

        q = q + q_upsert

    s.execute(q, rowslist)
