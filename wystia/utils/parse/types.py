from __future__ import annotations

__all__ = ['as_bool',
           'as_int',
           'as_str',
           'as_list',
           'as_datetime']

from datetime import datetime
from numbers import Number
from typing import Any


def as_bool(o: str | bool, default=False):
    """
    Return `o` if already a boolean, otherwise return the boolean value for a
    string. If `o` is None or an empty string, return `default` instead.

    """
    if isinstance(o, bool):
        return o

    if not o:
        return default

    return o.upper() == 'TRUE'


def as_type(o: Any, _type: type = str, default=None, raise_=True):
    if isinstance(o, _type):
        return o

    if not o:
        return default

    try:
        return _type(o)
    except ValueError:
        if raise_:
            raise
        return default


def as_int(o: str | int, default=0, raise_=True):
    """
    Return `o` if already a int, otherwise return the int value for a
    string. If `o` is None or an empty string, return `default` instead.

    If `o` cannot be converted to an int, raise an error if `raise_` is true,
    other return `default` instead.

    """
    return as_type(o, int, default, raise_)


def as_str(o: str | None, default='', raise_=True):
    """
    Return `o` if already a str, otherwise return the string value for `o`.
    If `o` is None or an empty string, return `default` instead.

    If `o` cannot be converted to an str, raise an error if `raise_` is true,
    other return `default` instead.

    """
    return as_type(o, str, default, raise_) or default


def as_list(o: str | list[str], sep=','):
    """
    Return `o` if already a list. If `o` is None or an empty string,
    return an empty list. Otherwise, split the string on `sep` and
    return the list result.

    """
    if not o:
        return []

    if isinstance(o, list):
        return o

    return o.split(sep)


def as_datetime(o: str | Number | datetime, default=None, raise_=True):
    """
    Return `o` if already a :class:`datetime` object, otherwise convert the
    object to a :class:`datetime` object using the below logic.

        * ``str``: convert date strings (in ISO format) via the built-in
          ``fromisoformat`` method.
        * ``Number`` (int or float): Convert a numeric timestamp via the
            built-in `fromtimestamp`` method.

    If `o` is None or false-y, return `default` instead.

    Otherwise, if we're unable to convert the value of `o` to a
    :class:`datetime` as expected, raise an error if the `raise_` parameter
    is true.

    """
    if not o:
        return default

    if isinstance(o, datetime):
        return o

    try:
        if isinstance(o, Number):
            # noinspection PyTypeChecker
            return datetime.fromtimestamp(o)

        return datetime.fromisoformat(o)

    except (TypeError, ValueError):
        if raise_:
            raise
        return default
