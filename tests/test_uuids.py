import uuid

import results

SAMPLE_DOMAIN = "australianunions.org.au"


def test_deterministic_uuids(sample):
    r = results.Results(sample)
    r = r.with_standardized_keys()
    duuid = r[0].deterministic_uuid(
        ["first_name", "last_name"], uuid_domain=SAMPLE_DOMAIN
    )

    UUID = "01c6bd2f-a45c-54eb-94f8-43cf01a38efc"
    assert str(duuid) == UUID
    assert duuid == uuid.UUID(f"urn:uuid:{UUID}")
