ASC_OR_DESC = ("desc", "asc")


def quoted(column_name):
    return f'"{column_name}"'


def parse_ordering_col(c):
    tokens = c.rsplit(None, 1)

    if len(tokens) > 1:
        possible_direction = tokens[-1].lower()
        if possible_direction in ASC_OR_DESC:
            c = tokens[0]
            descending = possible_direction == "desc"
        else:
            descending = False
    else:
        descending = False

    c = c.strip().strip('"')
    return c, descending


def parse_ordering(ordering):
    cols = ordering.split(",")
    return [parse_ordering_col(c) for c in cols]


def reversed_ordering(ordering):
    return [(c[0], not c[1]) for c in ordering]


def ordering_from_parsed(cols):
    clist = [(quoted(c) + (descending and " desc" or "")) for c, descending in cols]

    return ", ".join(clist)


def create_table_statement(table_name, colspec):
    quoted_name = quoted(table_name)
    colspec = ",\n  ".join(f"{quoted(k)} {v}" for k, v in colspec.items())

    return f"""create table {quoted_name} (
  {colspec}
);

"""
