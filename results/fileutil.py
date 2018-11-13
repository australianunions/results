from collections.abc import Mapping
from pathlib import Path

from .openers import from_file


def files(path, extensions=None):
    p = Path(path)
    p = p.expanduser()

    return [
        child
        for child in sorted(p.iterdir())
        if child.is_file and (not extensions or child.suffix in extensions)
    ]


def file_text(fpath):
    path = Path(fpath)
    return path.read_text()


def is_mapping(x):
    return isinstance(x, Mapping)


def from_files_it(files, ignore_unopenable=True):
    for f in files:
        try:
            results = from_file(f)
        except ValueError:
            if ignore_unopenable:
                continue
            raise
        if is_mapping(results):
            for k, result in results.items():
                yield f.with_name(f"{f.name}::{k}"), result
        else:
            yield f, results


def from_files(files, ignore_unopenable=True):
    return dict(from_files_it(files, ignore_unopenable))
