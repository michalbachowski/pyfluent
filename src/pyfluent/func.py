from typing import Any, Callable, Iterator, TypeVar

O = TypeVar('O')
T = TypeVar('T')


def callUnpacked(predicate: T) -> Callable[[Iterator[Any]], O]:
    return lambda it: predicate(*it)

