from pathlib import Path

import pytest
from sqlbag import S, temporary_database

FUNCTIONS_SQL = Path("tests/FIXTURES/sql/functions.sql").read_text()


@pytest.fixture
def tmpdb():
    with temporary_database(host="localhost") as db_url:
        yield db_url


@pytest.fixture
def tmpdbwithfunctions(tmpdb):
    with S(tmpdb) as s:
        s.execute(FUNCTIONS_SQL)
    yield tmpdb


@pytest.fixture
def sample():
    yield [
        {"First Name ": "Ice", " Last_Name": "T"},
        {"First Name ": "Ice", " Last_Name": "Cube"},
        {"First Name ": "    ", " Last_Name": "  "},
    ]
