"""
Utilities for projects
"""

import datetime
import socket
import sys
from contextlib import contextmanager
from functools import reduce
from io import StringIO
from typing import Callable, Generator, Iterable, List, Tuple

from django.conf import settings
from django.db.models.query import QuerySet

from .constants import WEEKDAYS


def get_day_value(day: str):
    return WEEKDAYS[day]


def get_model_fields(model):
    return [field.name for field in model._meta.fields]


def invalid_str(value):
    """
    To validate model data like charfield
    """
    for i in '@#$%^&*+=://;?><}{[]()':
        if i in value:
            return True
    return False


def convert_bytes_to_mb(num):
    """Convert bytes to megabyte"""
    return num / 1024 / 1024


def choices_to_dict(list_tup: Iterable[Tuple[str, str]]):
    """
    Converts model choices to dictionary format
    like
    [
        {
            'name': ...,
            'value': ...
        }
    ]
    """
    return [{'value': a[0], 'name': a[1]} for a in list_tup]


def printt(*args, **kwargs):
    """
    Override python print to only print when allowed
    """
    if settings.PRINT_LOG is True:
        return print(*args, **kwargs)


def remove_session(request, name):
    """
    Remove sessions from request
    """
    session = request.session.get(name, None)
    if session is not None:
        del request.session[name]


def tup_to_dict(tup: tuple) -> dict:
    """
    Convert model choices (tuples) to dictionary
    """
    jsonObj = []

    for key, value in tup:
        obj = dict()
        obj['key'] = key
        obj['value'] = value
        jsonObj.append(obj)

    return jsonObj


def verify_ip(ip):
    """
    Verify that ip is valid
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        pass
    return False


def get_client_ip(request):
    """
    Get ip address from request obj
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if verify_ip(ip):
        return ip


def verify_next_link(next):
    """
    Validates the next value
    """
    if next:
        if next.startswith('/'):
            return next


def get_next_link(request):
    """
    Get the next link from the url
    """
    next = request.GET.get('next')
    return verify_next_link(next)


def deslug(text):
    """
    Convert string from snake casing to normal
    """
    texts = text.split('_')
    texts = [i.capitalize() for i in texts]
    return ' '.join(texts)


def add_queryset(a, b) -> QuerySet:
    """
    Add two querysets
    """
    return a | b


def merge_querysets(*args) -> QuerySet:
    """
    Merge querysets
    """
    return reduce(add_queryset, args)


def url_with_params(url, params):
    """
    Url is a relative or full link,
    params is a dictionary of key/value pairs of the query parameters
    {id: 3, name: 'John doe'}
    """
    # Add trailing backslash to url
    if not url.endswith('/'):
        url += '/'

    # Join the key/value pairs into a string
    assiged = [f'{key}={value}' for key, value in params.items()]

    return url + '?' + '&'.join(assiged)


def is_exc_obj_does_not_exist(e: Exception):
    return e.__class__.__name__\
        == 'RelatedObjectDoesNotExist'


def check_raise_exc(e: Exception):
    """
    Raise exception if not RelatedObjectDoesNotExist

    :param e: Supplied exception class
    :type e: Exception
    :raises e: Raise exception passed to it
    """

    if not is_exc_obj_does_not_exist(e):
        raise e


def split_datetime(datetime) -> List[str]:
    """
    Split passed datetime into date and time

    :return: YYYY-mm-dd and H:M:S
    :rtype: List[str]
    """
    date, time = str(datetime).split()
    time = time.split('.')[0]
    return date, time


def regexify(name: str) -> str:
    """Wraps name with regex to use in restframework action url path"""
    return f"(?P<{name}>[^/.]+)"


def today():
    """Return today's date only"""
    return datetime.date.today()


@contextmanager
def capture_output(func: Callable[..., None]) -> Generator[str, None, None]:
    """Context manager to capture
    standart output when calling function as
    a string"""
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    func()
    sys.stdout = old_stdout

    yield mystdout.getvalue()
