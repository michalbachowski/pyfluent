from operator import methodcaller
from typing import Any, Iterable, Optional, Tuple

import mock
import unittest

from pyfluent.iterator import FluentIterator


def _get_iterable(iterable_values: Iterable[Any],
                  with_next: bool = True
                  ) -> Tuple[mock.Mock, mock.Mock, Optional[mock.Mock]]:
    localized_iterable = iter(list(iterable_values))
    iter_mock = mock.Mock(return_value=localized_iterable)
    iterable = mock.Mock()
    iterable.__iter__ = iter_mock
    if with_next:
        next_mock = mock.Mock(side_effect=lambda: next(localized_iterable))
        iterable.__next__ = next_mock
    else:
        next_mock = None
    return (iterable, iter_mock, next_mock)


class FluentIteratorTestBase(unittest.TestCase):

    def setUp(self) -> None:
        self.sentinel = mock.Mock()
        self.iterator_values = [1, 2, 3]
        (self.inner_iterable, self.iter_mock, self.next_mock) = \
            _get_iterable(self.iterator_values)
        self.iterator = FluentIterator(self.inner_iterable)


class FluentIteratorTerminatorsTestCase(FluentIteratorTestBase):

    def assertIterableEqual(self, iter1: Iterable[Any],
                            iter2: Iterable[Any]) -> None:
        self.assertSequenceEqual(list(iter1), list(iter2))

    def test_if_iterator_is_given_iter_and_get_will_return_it(self) -> None:
        iterable_values = iter([1, 2, 3])
        iterable = FluentIterator(iterable_values)
        self.assertIs(iterable_values, iter(iterable))
        self.assertIs(iterable_values, iterable.get())

    def test_iter_returns_iterator_different_than_given(self) -> None:
        iter1 = iter(self.iterator)
        self.assertIsNot(iter1, self.iterator_values)

    def test_iter_returns_iterator_with_all_values(self) -> None:
        iter1 = iter(self.iterator)
        self.assertIterableEqual(iter1, self.iterator_values)

    def test_get_returns_iterator_different_than_given(self) -> None:
        iter1 = self.iterator.get()
        self.assertIsNot(iter1, self.iterator_values)

    def test_get_returns_iterator_with_all_values(self) -> None:
        iter1 = self.iterator.get()
        self.assertIterableEqual(iter1, self.iterator_values)

    def test_get_returns_same_iterator(self) -> None:
        iter1 = self.iterator.get()
        iter2 = self.iterator.get()
        self.assertIs(iter1, iter2)

    def test_get_and_iter_return_same_iterator(self) -> None:
        iter1 = iter(self.iterator)
        iter2 = self.iterator.get()
        self.assertIs(iter1, iter2)

    def test_collect_exhaust_iterator(self):
        collection1 = self.iterator.collect()
        self.assertIsInstance(collection1, list)
        self.assertSequenceEqual(collection1, self.iterator_values)

        collection2 = self.iterator.collect()
        self.assertIterableEqual(collection2, [])

    def test_fluent_is_also_an_iterator(self):
        iterator = FluentIterator(self.iterator_values)
        for item in self.iterator_values:
            self.assertEqual(item, next(iterator))

    def test_next_exhausts_iterator(self):
        iterator = FluentIterator(self.iterator_values)
        for item in self.iterator_values:
            self.assertEqual(item, next(iterator))

        self.assertIterableEqual(iterator, [])


class FluentIteratorSinglePropertyNonTerminalMethodMixin(object):

    def setUp(self):
        super().setUp()
        self.new_iterator = getattr(self.iterator, self.METHOD)(self.sentinel)

    def test_predicate_is_called_for_each_element(self):
        self.new_iterator.collect()

        self.sentinel.assert_has_calls(
            [mock.call(item) for item in self.iterator_values]
        )

    def test_method_does_not_exhaust_iterator(self):
        self.iter_mock.assert_not_called()
        self.next_mock.assert_not_called()

    def test_method_returns_new_fluentiterator_instance(self):
        self.assertIsNot(self.new_iterator, self.iterator)

    def test_method_new_iterator_shares_the_same_internal_iterator(self):
        self.iterator.collect()
        self.assertSequenceEqual(self.new_iterator.collect(), [])

    def test_method_returns_new_instance_of_FluentIterator(self):
        self.assertIsInstance(self.new_iterator, FluentIterator)


class FluentIteratorPeekTestCase(
        FluentIteratorSinglePropertyNonTerminalMethodMixin,
        FluentIteratorTestBase):

    METHOD = 'peek'

    def test_peek_leaves_elements_in_place(self):
        self.assertSequenceEqual(
            self.new_iterator.collect(),
            self.iterator_values
        )


class FluentIteratorMapTestCase(
        FluentIteratorSinglePropertyNonTerminalMethodMixin,
        FluentIteratorTestBase):

    METHOD = 'map'

    def test_map_transforms_elements(self):
        self.sentinel.side_effect = lambda item: item * 10

        self.assertSequenceEqual(
            self.new_iterator.collect(),
            [item * 10 for item in self.iterator_values]
        )


class FluentIteratorFilterTestCase(
        FluentIteratorSinglePropertyNonTerminalMethodMixin,
        FluentIteratorTestBase):

    METHOD = 'filter'

    def test_filter_removes_elements_for_which_returned_value_is_False(self):
        self.sentinel.side_effect = [True, False, True]

        self.assertSequenceEqual(
            self.new_iterator.collect(),
            [item for item in self.iterator_values if item != 2]
        )


class FluentIteratorFilterFalseTestCase(
        FluentIteratorSinglePropertyNonTerminalMethodMixin,
        FluentIteratorTestBase):

    METHOD = 'filterfalse'

    def setUp(self):
        super().setUp()
        self.sentinel.return_value = False

    def test_filter_removes_elements_for_which_returned_value_is_True(self):
        self.sentinel.return_value = None
        self.sentinel.side_effect = [True, False, True]

        self.assertSequenceEqual(
            self.new_iterator.collect(),
            [item for item in self.iterator_values if item == 2]
        )


class FluentIteratorSinglePropertyInsertMethodMixin(object):

    def setUp(self):
        super().setUp()
        self.iterator_values_iterable = list(self.iterator_values)
        self.new_iterator_primitive = getattr(self.iterator, self.METHOD)(4)
        self.new_iterator_iterable = getattr(self.iterator, self.METHOD)([4, 5])
        self.new_iterator_iterator = getattr(self.iterator, self.METHOD)(iter([4, 5]))

    def test_method_does_not_exhaust_iterator(self):
        self.iter_mock.assert_not_called()
        self.next_mock.assert_not_called()

    def test_method_returns_new_fluentiterator_instance(self):
        self.assertIsNot(self.new_iterator_primitive, self.iterator)
        self.assertIsNot(self.new_iterator_iterable, self.iterator)

    def test_method_new_iterator_shares_the_same_internal_iterator(self):
        self.iterator.collect()
        self.assertSequenceEqual(self.new_iterator_primitive.collect(), [4])
        self.assertSequenceEqual(self.new_iterator_iterable.collect(), [4, 5])

    def test_method_adds_new_primitive_where_expected(self):
        self.assertSequenceEqual(
                self.new_iterator_primitive.collect(),
                self.iterator_values)

    def test_method_adds_new_iterable_where_expected(self):
        self.assertSequenceEqual(
                self.new_iterator_iterable.collect(),
                self.iterator_values_iterable)

    def test_method_adds_new_iterator_where_expected(self):
        self.assertSequenceEqual(
                self.new_iterator_iterator.collect(),
                self.iterator_values_iterable)


class FluentIteratorPrependTestCase(
        FluentIteratorSinglePropertyInsertMethodMixin,
        FluentIteratorTestBase):

    METHOD = 'prepend'

    def setUp(self):
        super().setUp()
        self.iterator_values.insert(0, 4)
        self.iterator_values_iterable.insert(0, 5)
        self.iterator_values_iterable.insert(0, 4)


class FluentIteratorAppendTestCase(
        FluentIteratorSinglePropertyInsertMethodMixin,
        FluentIteratorTestBase):

    METHOD = 'append'

    def setUp(self):
        super().setUp()
        self.iterator_values.append(4)
        self.iterator_values_iterable.extend([4, 5])


class FluentIteratorAllMatchTestCase(FluentIteratorTestBase):

    def setUp(self):
        super().setUp()
        self.sentinel.return_value = True

    def test_noneMatch_returns_True_if_iterator_was_exhausted(self):
        self.iterator.collect()
        self.assertTrue(self.iterator.noneMatch(self.sentinel))

    def test_iterator_is_exhausted_after_the_call_only_if_returning_True(self):
        self.assertTrue(self.iterator.allMatch(self.sentinel))
        self.assertSequenceEqual(self.iterator.collect(), [])

    def test_iterator_might_not_be_exhausted_after_the_call_if_returning_False(self):
        self.sentinel.return_value = False
        self.assertFalse(self.iterator.allMatch(self.sentinel))
        self.assertSequenceEqual(self.iterator.collect(), [2, 3])

    def test_iterator_might_be_exhausted_after_the_call_even_if_returning_False(self):
        self.sentinel.side_effect = [True, True, False]
        self.assertFalse(self.iterator.allMatch(self.sentinel))
        self.assertSequenceEqual(self.iterator.collect(), [])

    def test_iterator_might_not_be_exhausted_after_the_call(self):
        self.sentinel.return_value = False
        self.iterator.allMatch(self.sentinel)
        self.assertSequenceEqual(self.iterator.collect(), [2, 3])

    def test_allMatch_returns_True_when_predicate_is_True_for_all_items(self):
        self.assertTrue(self.iterator.allMatch(self.sentinel))

    def test_allMatch_returns_False_when_predicate_is_True_for_any_item(self):
        self.sentinel.return_value = None
        self.sentinel.side_effect = lambda item: item > 1
        self.assertFalse(self.iterator.allMatch(self.sentinel))

    def test_predicate_is_called_for_each_element(self):
        self.iterator.allMatch(self.sentinel)

        self.sentinel.assert_has_calls(
            [mock.call(item) for item in self.iterator_values]
        )


class FluentIteratorNoneMatchTestCase(FluentIteratorTestBase):

    def setUp(self):
        super().setUp()
        self.sentinel.return_value = False

    def test_noneMatch_returns_True_if_iterator_was_exhausted(self):
        self.iterator.collect()
        self.assertTrue(self.iterator.noneMatch(self.sentinel))

    def test_iterator_is_exhausted_after_the_call_only_if_returning_True(self):
        self.assertTrue(self.iterator.noneMatch(self.sentinel))
        self.assertSequenceEqual(self.iterator.collect(), [])

    def test_iterator_might_not_be_exhausted_after_the_call_if_returning_False(self):
        self.sentinel.return_value = True
        self.assertFalse(self.iterator.noneMatch(self.sentinel))
        self.assertSequenceEqual(self.iterator.collect(), [2, 3])

    def test_iterator_might_be_exhausted_after_the_call_even_if_returning_False(self):
        self.sentinel.side_effect = [False, False, True]
        self.assertFalse(self.iterator.noneMatch(self.sentinel))
        self.assertSequenceEqual(self.iterator.collect(), [])

    def test_noneMatch_returns_True_when_predicate_is_False_for_all_items(self):
        self.assertTrue(self.iterator.noneMatch(self.sentinel))

    def test_noneMatch_returns_False_when_predicate_is_True_for_any_item(self):
        self.sentinel.return_value = None
        self.sentinel.side_effect = lambda item: item > 2
        self.assertFalse(self.iterator.noneMatch(self.sentinel))

    def test_predicate_is_called_for_each_element(self):
        self.iterator.noneMatch(self.sentinel)

        self.sentinel.assert_has_calls(
            [mock.call(item) for item in self.iterator_values]
        )


class FluentIteratorAnyMatchTestCase(FluentIteratorTestBase):

    def setUp(self):
        super().setUp()
        self.sentinel.return_value = False

    def test_anyMatch_returns_False_if_iterator_was_exhausted(self):
        self.iterator.collect()
        self.sentinel.return_value = True
        self.assertFalse(self.iterator.anyMatch(self.sentinel))

    def test_iterator_is_exhausted_after_the_call_only_if_returning_False(self):
        self.assertFalse(self.iterator.anyMatch(self.sentinel))
        self.assertSequenceEqual(self.iterator.collect(), [])

    def test_iterator_might_not_be_exhausted_after_the_call_if_returning_True(self):
        self.sentinel.return_value = True
        self.assertTrue(self.iterator.anyMatch(self.sentinel))
        self.assertSequenceEqual(self.iterator.collect(), [2, 3])

    def test_iterator_might_be_exhausted_after_the_call_even_if_returning_True(self):
        self.sentinel.side_effect = [False, False, True]
        self.assertTrue(self.iterator.anyMatch(self.sentinel))
        self.assertSequenceEqual(self.iterator.collect(), [])

    def test_noneMatch_returns_True_when_predicate_is_False_for_all_items(self):
        self.assertTrue(self.iterator.noneMatch(self.sentinel))

    def test_noneMatch_returns_False_when_predicate_is_True_for_any_item(self):
        self.sentinel.return_value = None
        self.sentinel.side_effect = lambda item: item > 2
        self.assertFalse(self.iterator.noneMatch(self.sentinel))

    def test_predicate_is_called_for_each_element(self):
        self.iterator.anyMatch(self.sentinel)

        self.sentinel.assert_has_calls(
            [mock.call(item) for item in self.iterator_values]
        )


class FluentIteratorFirstTestCase(FluentIteratorTestBase):

    def setUp(self):
        super().setUp()
        self.sentinel.return_value = False

    def test_iterator_is_exhausted_after_the_call_only_if_returning_last_value(self):
        self.iterator.first()
        self.iterator.first()
        self.assertEqual(self.iterator.first(), self.iterator_values.pop())
        self.assertSequenceEqual(self.iterator.collect(), [])

    def test_iterator_wll_not_be_exhausted_after_the_call_if_there_are_more_values(self):
        self.assertEqual(self.iterator.first(), self.iterator_values.pop(0))
        self.assertSequenceEqual(self.iterator.collect(), self.iterator_values)

    def test_first_returns_None_if_iterator_is_exhausted(self):
        self.iterator.collect()
        self.assertIsNone(self.iterator.first())


class FluentIteratorEnumerateTestCase(FluentIteratorTestBase):

    def setUp(self) -> None:
        self.iterator_values = ['a', 'b', 'c']

        (self.inner_iterable, self.iter_mock, self.next_mock) = \
            _get_iterable(self.iterator_values)
        self.iterator = FluentIterator(iter(self.inner_iterable))

    def test_enumerate_is_non_terminal(self):
        itr = self.iterator.enumerate()
        self.iter_mock.assert_not_called()
        self.next_mock.assert_not_called()
        self.assertIsNot(itr, self.iterator)
        self.assertIsInstance(itr, FluentIterator)
        self.assertSequenceEqual(self.iterator.collect(), self.iterator_values)

    def test_enumerate_transforms_elements(self):
        self.assertSequenceEqual(
            self.iterator.enumerate().collect(),
            [(0, 'a'), (1, 'b'), (2, 'c')]
        )


class FluentIteratorSkipTestCase(FluentIteratorTestBase):

    def setUp(self) -> None:
        self.iterator_values = [1, 2, 3]

        (self.inner_iterable, self.iter_mock, self.next_mock) = \
            _get_iterable(self.iterator_values)
        self.iterator = FluentIterator(iter(self.inner_iterable))

    def test_skip_is_non_terminal(self):
        itr = self.iterator.skip(1)
        self.iter_mock.assert_not_called()
        self.next_mock.assert_not_called()
        self.assertIsNot(itr, self.iterator)
        self.assertIsInstance(itr, FluentIterator)
        self.assertSequenceEqual(self.iterator.collect(), self.iterator_values)

    def test_skip_removes_elements(self):
        self.assertSequenceEqual(
            self.iterator.skip(1).collect(),
            self.iterator_values[1:]
        )

    def test_skip_returns_no_items_if_requested_to_skip_too_much(self) -> None:
        self.assertSequenceEqual(
            self.iterator.skip(10).collect(),
            []
        )

    def test_skip_expects_positive_value(self) -> None:
        with self.assertRaises(ValueError):
            self.iterator.skip(-1)

    def test_skip_returns_all_items_if_given_0(self) -> None:
        self.assertSequenceEqual(
            self.iterator.skip(0).collect(),
            self.iterator_values)


class FluentIteratorFlattenTestCase(FluentIteratorTestBase):

    def setUp(self) -> None:
        self.iter1 = [1, 2]
        self.iter2 = [3, 4]
        self.iter3 = [5]
        self.iterator_values = [self.iter1, self.iter2, self.iter3]

        (self.inner_iterable, self.iter_mock, self.next_mock) = \
            _get_iterable(self.iterator_values)
        self.iterator = FluentIterator(iter(self.inner_iterable))

    def test_flatten_requires_iterator_if_iterator_as_input(self):
        iterator_values = [1, 2]
        iterator = FluentIterator(iter(iterator_values))
        with self.assertRaises(TypeError):
            iterator.flatten().collect()

    def test_flatten_is_non_terminal(self):
        itr = self.iterator.flatten()
        self.iter_mock.assert_not_called()
        self.next_mock.assert_not_called()
        self.assertIsNot(itr, self.iterator)
        self.assertIsInstance(itr, FluentIterator)
        self.assertSequenceEqual(self.iterator.collect(), self.iterator_values)

    def test_flatten_iterates_over_internal_iterator(self):
        self.assertSequenceEqual(
            self.iterator.flatten().collect(),
            self.iter1 + self.iter2 + self.iter3
        )


class FluentIteratorReduceTestCase(FluentIteratorTestBase):

    def setUp(self):
        super().setUp()
        self.accumulator = mock.Mock()
        self.predicate = mock.Mock(return_value=self.accumulator)

    def test_reduce_is_called_for_each_element(self):
        self.iterator.reduce(self.predicate)
        self.inner_iterable.__iter__.called_once_with()
        self.predicate.assert_has_calls(
                [mock.call(None, self.iterator_values.pop(0))] +
                [mock.call(self.accumulator, item) for item in self.iterator_values])

    def test_reduce_is_terminal(self):
        self.iterator.reduce(self.predicate)
        self.assertSequenceEqual(self.iterator.collect(), [])

    def test_reduce_returns_accumulator(self):
        self.assertIs(self.iterator.reduce(self.predicate), self.accumulator)

    def test_reduce_can_accept_accumulator(self):
        self.predicate.return_value = None
        self.predicate.side_effect = lambda acc, item: acc + item
        self.assertEqual(self.iterator.reduce(self.predicate, 0), 6)
        self.predicate.assert_has_calls(
                [mock.call(0, 1), mock.call(1, 2), mock.call(3, 3)])

