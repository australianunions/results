import string

ALLOWED = string.ascii_lowercase + "_" + string.digits


allowed = {k: True for k in ALLOWED}


def whitespace_to_underscore(x):
    return "_".join(x.split())


def standardize_key(k):
    cleaned = k.strip().lower().encode("ascii", errors="ignore").decode()
    underscored = whitespace_to_underscore(cleaned)
    return filtered(underscored)


def filtered(x):
    return "".join(_ for _ in x if _ in allowed)


def standardized_key_mapping(keyslist):
    return {k: standardize_key(k) for k in keyslist}
