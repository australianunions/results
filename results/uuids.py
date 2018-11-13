import json
import uuid


def dns_uuid(domain_name):
    return uuid.uuid5(uuid.NAMESPACE_DNS, domain_name)


def stringified_dict(d):
    return {str(k): str(v) for k, v in d.items()}


def contents_json(contents_dict):
    d = stringified_dict(contents_dict)
    return json.dumps(d, sort_keys=True)


def deterministic_uuid(domain, contents_dict):
    dns = dns_uuid(domain)
    j = contents_json(contents_dict)
    return uuid.uuid5(dns, j)
