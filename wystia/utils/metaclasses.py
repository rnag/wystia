"""
Metaclass utilities
"""
import pprint


def display_with_pformat(name: str, bases: tuple, cls_dict: dict):
    """
    Metaclass which overrides the :meth:`__str__` of a class to use the
    `pprint` module to pretty-format the class's default :meth:`__repr__`.
    """
    def __str__(self):
        return pprint.pformat(self)

    cls_dict['__str__'] = __str__

    return type(name, bases, cls_dict)
