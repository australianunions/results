import inspect

from pkg_resources import resource_filename as pkg_resource_filename
from pkg_resources import resource_stream as pkg_resource_stream


def external_caller():
    i = inspect.stack()
    names = (inspect.getmodule(i[x][0]).__name__ for x in range(len(i)))
    return next(name for name in names if name != __name__)


def resource_path(subpath):
    module_name = external_caller()
    return pkg_resource_filename(module_name, subpath)


def resource_stream(subpath):
    module_name = external_caller()
    return pkg_resource_stream(module_name, subpath)


def resource_data(subpath):
    return resource_stream(subpath).read()
