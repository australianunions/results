from pathlib import Path

from py._path.local import LocalPath


def is_pathlike(f):
    return isinstance(f, (str, Path, LocalPath))
