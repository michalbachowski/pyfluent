from __future__ import annotations
from collections.abc import Callable, Iterator, Iterable
from itertools import chain, filterfalse, islice
from functools import partial, reduce
from typing import Any, Generic, Optional, TypeVar, Union

I = TypeVar('I')
O = TypeVar('O')
T = TypeVar('T')


def _peek_item(predicate: Callable[[I], None], item: I) -> I:
    predicate(item)
    return item


class FluentIterator(Generic[I], Iterator):

    def __init__(self, iterator: Iterator[I]) -> None:
        super().__init__()
        self._iterator = iter(iterator)

    def peek(self, predicate: Callable[[I], None]) -> FluentIterator[I]:
        return self.map(partial(_peek_item, predicate))

    def map(self, predicate: Callable[[I], O]) -> FluentIterator[O]:
        return FluentIterator(map(predicate, self._iterator))

    def filter(self, predicate: Callable[[I], bool]) -> FluentIterator[I]:
        return FluentIterator(filter(predicate, self._iterator))

    def filterfalse(self, predicate: Callable[[I], bool]) -> FluentIterator[I]:
        return FluentIterator(filterfalse(predicate, self._iterator))

    def flatten(self) -> FluentIterator[Any]:
        return FluentIterator(chain.from_iterable(self._iterator))

    def enumerate(self) -> FluentIterator[Tuple[int, I]]:
        return FluentIterator(enumerate(self._iterator))

    def skip(self, num: int) -> FluentIterator[I]:
        return FluentIterator(islice(self._iterator, num, None))

    def prepend(self, item: Union[Iterable[I], I]) -> FluentIterator[I]:
        if isinstance(item, Iterable):
            return FluentIterator(chain(item, self._iterator))
        return FluentIterator(chain([item], self._iterator))

    def append(self, item: Union[Iterable[I], I]) -> FluentIterator[I]:
        if isinstance(item, Iterable):
            return FluentIterator(chain(self._iterator, item))
        return FluentIterator(chain(self._iterator, [item]))

    def allMatch(self, predicate: Callable[[I], bool]) -> bool:
        return all(self.map(predicate))

    def anyMatch(self, predicate: Callable[[I], bool]) -> bool:
        return any(self.map(predicate))

    def noneMatch(self, predicate: Callable[[I], bool]) -> bool:
        return not self.anyMatch(predicate)

    def first(self) -> Optional[I]:
        return next(self._iterator, None)

    def reduce(self,
               predicate: Callable[[I], O], initializer: Optional[O] = None
               ) -> Optional[O]:
        return reduce(predicate, self._iterator, initializer)

    def collect(self,
                factory: Callable[[Iterable[I]], Iterator[O]] = list
                ) -> Iterator[O]:
        return factory(self._iterator)

    def get(self) -> Iterator[I]:
        return iter(self)

    def __iter__(self) -> Iterator[I]:
        return self._iterator

    def __next__(self) -> I:
        return next(self._iterator)

