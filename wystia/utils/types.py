__all__ = [
    'R',
    'LIST_OR_NONE',
    'STR_OR_NONE'
]

from typing import TypeVar, Optional, List


R = TypeVar('R')

LIST_OR_NONE = Optional[List[str]]

STR_OR_NONE = Optional[str]
