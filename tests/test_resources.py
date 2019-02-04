from pathlib import Path

from results import resource_data, resource_path, resource_stream, resource_text


def test_resources():
    REL_PATH = "tests/FIXTURES/sql/select1.sql"
    RESOURCE_PATH = "FIXTURES/sql/select1.sql"

    TEXT = Path(REL_PATH).read_text()

    RP = resource_path(RESOURCE_PATH)
    assert RP.endswith(RESOURCE_PATH)

    assert resource_stream(RESOURCE_PATH).read().decode() == TEXT
    assert resource_data(RESOURCE_PATH).decode() == TEXT
    assert resource_text(RESOURCE_PATH) == TEXT
