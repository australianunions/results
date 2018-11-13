import results

SAMPLE = [
    dict(
        a="hi", b="2019-12-25", c="2018-11-03T15:16:25.066890+11:00", d=5, e=5.5, f=None
    )
]


GUESSED = {
    "a": "text",
    "b": "date",
    "c": "timestamp",
    "d": "int",
    "e": "decimal",
    "f": "text",
}


CREATE = """create table "ttt" (
  "a" text,
  "b" date,
  "c" timestamp,
  "d" int,
  "e" decimal,
  "f" text
);

"""


def test_guessing():
    assert results.guess_value_type("") is None
    assert results.guess_value_type(1.1) == float
    r = results.Results(SAMPLE)
    guessed = r.guessed_sql_column_types()
    assert guessed == GUESSED
    assert results.create_table_statement("ttt", guessed) == CREATE
    assert r.guessed_create_table_statement("ttt") == CREATE
