from pathlib import Path

from py._path.local import LocalPath


def is_pathlike(f):
    return isinstance(f, (str, Path, LocalPath))


def noneslarger(x):
    if x is None:
        return 1, x
    else:
        return 0, x


def nonessmaller(x):
    if x is None:
        return -1, x
    else:
        return 0, x


ELLIPSIS = "\u2026"


def trunc(s, length=25):
    if len(s) > length:
        s = s[:length] + ELLIPSIS
    return s
