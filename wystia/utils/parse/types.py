__all__ = ['as_bool',
           'as_int',
           'as_str',
           'as_list']

from typing import Union, List, Any, Type


def as_bool(o: Union[str, bool], default=False):
    """
    Return `o` if already a boolean, otherwise return the boolean value for a
    string. If `o` is None or an empty string, return `default` instead.

    """
    if isinstance(o, bool):
        return o

    if not o:
        return default

    return o.upper() == 'TRUE'


def as_type(o: Any, _type: Type = str, default=None, raise_=True):
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


def as_int(o: Union[str, int], default=0, raise_=True):
    """
    Return `o` if already a int, otherwise return the int value for a
    string. If `o` is None or an empty string, return `default` instead.

    If `o` cannot be converted to an int, raise an error if `raise_` is true,
    other return `default` instead.

    """
    return as_type(o, int, default, raise_)


def as_str(o: Union[str, None], default='', raise_=True):
    """
    Return `o` if already a str, otherwise return the string value for `o`.
    If `o` is None or an empty string, return `default` instead.

    If `o` cannot be converted to an str, raise an error if `raise_` is true,
    other return `default` instead.

    """
    return as_type(o, str, default, raise_)


def as_list(o: Union[str, List[str]], sep=','):
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
