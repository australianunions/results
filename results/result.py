from .uuids import deterministic_uuid


class Result(dict):
    def __init__(self, *args, **kwargs):
        self.annotations = {}
        super().__init__(*args, **kwargs)

    def deterministic_uuid(self, columns, uuid_domain):
        return deterministic_uuid(
            uuid_domain, {k: v for k, v in self.items() if k in columns}
        )

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        if name == "annotations":
            object.__setattr__(self, name, value)
        else:
            self[name] = value

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)

    def __iter__(self):
        for k, v in self.items():
            if k != "annotations":
                yield v

    def scalar(self):
        return self[0]
