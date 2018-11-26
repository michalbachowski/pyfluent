from typing import Any, Iterable, Optional, Tuple, Callable

import mock
import unittest

from pyfluent.func import callUnpacked


class FuncCallUnpackedTest(unittest.TestCase):

    def setUp(self) -> None:
        self.predicate = mock.Mock()
        self.callable = callUnpacked(self.predicate)

    def test_raises_exception_if_predicate_is_missing(self) -> None:
        with self.assertRaises(TypeError):
            callUnpacked()

    def test_returns_callable(self) -> None:
        self.assertIsInstance(callUnpacked(self.predicate), Callable)

    def test_calls_predicate_with_args_unpacked(self) -> None:
        self.callable([1, 2, 3])

        self.predicate.assert_called_once_with(1, 2, 3)

    def test_created_callable_requires_iterator_as_an_arg(self) -> None:
        with self.assertRaises(TypeError):
            self.callable(1)

        with self.assertRaises(TypeError):
            self.callable(None)

        self.callable('abc')
        self.predicate.assert_called_once_with('a', 'b', 'c')

