from collections.abc import Callable, Iterator
from typing import Any, TypeVar

O = TypeVar('O')
T = TypeVar('T')


def callUnpacked(predicate: T) -> Callable[Iterator[Any], O]:
    def wrap(iterator: Iterator[Any]) -> O:
        return predicate(*i)
    return wrap

