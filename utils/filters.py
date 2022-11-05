"""
Module for list-like filters that generate statistics based on a source list. 
Changes to the source list result in changes in the filters' results.

Author: Ryan Au
"""

import math
from collections import UserList, deque
from statistics import mean, median
import threading


def range_limit(value: float, lower: float, upper: float) -> float:
    """Prevents the value from going beyond the upper or lower values.

    Example:
    range_limit(40,30,50)->40 (within bounds)
    range_limit(60,30,50)->50 (upper limit)
    range_limit(20,30,50)->30 (lower limit)

    >>> range_limit(40,30,50)
    40
    >>> range_limit(60,30,50)
    50
    >>> range_limit(20,30,50)
    30
    """
    return min(max(value, lower), upper)


def _wrap_index(i, l):
    """Changes an index from negative to the wrapped index based on length l.

    >>> _wrap_index(10, 5)
    10
    >>> _wrap_index(-10, 5)
    -5
    >>> _wrap_index(-4, 5)
    1
    """
    if i < 0:
        return l + i
    else:
        return i


class CircularList:
    class Empty:
        def __eq__(self, __o: object) -> bool:
            return isinstance(__o, CircularList.Empty)

        def __repr__(self):
            return "Empty"

        def __bool__(self):
            return False

    def __init__(self, size: int):
        """Initializes the CircularList with a given size

        >>> c = CircularList(4)
        >>> len(c.data)
        4
        >>> c = CircularList(1)
        >>> len(c.data)
        1
        >>> c = CircularList(0) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: size must be positive non-zero value
        """
        if type(size) != int:
            raise ValueError("size must be of type int")
        if size <= 0:
            raise ValueError("size must be positive non-zero value")
        self.size = size
        self.head = 0
        self.tail = None
        self.data = [CircularList.Empty() for i in range(size)]

    def __repr__(self):
        """String representation of this CircularList"""
        return repr(self.to_list())

    def update(self, iterable):
        """Appends each element of the iterable to this list.
        The normal CircularList.append rules apply, and will overwrite
        the oldest added element always.

        >>> c = CircularList(3)
        >>> c.update([1,2,3,4,5])
        >>> c
        [3, 4, 5]
        >>> c.update([6,7,8,9])
        >>> c
        [7, 8, 9]
        >>> c.update([10, 11])
        >>> c
        [9, 10, 11]
        """
        for i in iterable:
            self.append(i)

    def to_list(self):
        """
        Returns a List form of this CircularList.

        >>> c = CircularList(4)
        >>> c.to_list()
        []
        >>> c.append(1)
        Empty
        >>> c.to_list()
        [1]
        >>> c.update([2, 3, 4, 5])
        >>> c.to_list()
        [2, 3, 4, 5]
        >>> c.data
        [5, 2, 3, 4]
        """
        if self.tail is None:
            return list()
        if self.head <= self.tail:
            return self.data[self.head:self.tail+1]
        if self.tail < self.head:
            return [self.data[i] for i in self._slice(self.head, self.tail)]

    def append(self, element):
        """
        Append an item to this list. Returns element if overriden,
        CircularList.Empty object if there was no element overriden.
        The first element is removed, if list would exceed its size.

        >>> c = CircularList(2)
        >>> c.append(1)
        Empty
        >>> c.append(2)
        Empty
        >>> c.append(3)
        1
        >>> c
        [2, 3]
        >>> c = CircularList(1)
        >>> c.append(1)
        Empty
        >>> c.append(2)
        1
        >>> c.append(3)
        2
        >>> c
        [3]
        >>> c.pophead()
        3
        >>> c.append(4)
        Empty
        >>> c
        [4]
        """

        if isinstance(element, CircularList.Empty):
            raise ValueError(
                "list element cannot be of the CircularList.Empty class")

        if self.tail is None:
            self.tail = self.head
        else:
            # Increment tail from current last element, to next element
            self.tail = (self.tail + 1) % self.size  # 0 to size-1
            if self.tail == self.head:
                self.head = (self.head + 1) % self.size

        last_item = self.data[self.tail]
        self.data[self.tail] = element
        return last_item

    def pop(self):
        """Remove last added item and return it.

        >>> c = CircularList(2)
        >>> c.update([1, 2, 3])
        >>> c.pop()
        3
        >>> c.pop()
        2
        >>> c.append(4)
        Empty
        """
        if self.tail is None:
            raise RuntimeError("There are no items in this list")

        item = self.data[self.tail]
        self.data[self.tail] = CircularList.Empty()

        if self.head == self.tail:
            self.tail = None
        else:
            self.tail = (self.tail - 1) % self.size

        return item

    def poptail(self):
        """Remove last added item and return it."""
        return self.pop()

    def pophead(self):
        """Remove first added item and return it."""
        if self.tail is None:
            raise RuntimeError("There are no items in this list")

        item = self.data[self.head]
        self.data[self.head] = CircularList.Empty()

        if self.head == self.tail:
            self.tail = None
        else:
            self.head = (self.head + 1) % self.size

        return item

    def _convert_index(self, index):
        """Converts any given index, into the corresponding circular index.
        Includes values 0 to size-1.

        Internally, it is only based self.head and self.size
        It ignores the current value of self.tail

        >>> c = CircularList(3)
        >>> c._convert_index(1)
        1
        >>> c.update([1, 2, 3, 4])
        >>> c._convert_index(1)
        2
        >>> c.update([5])
        >>> c._convert_index(1)
        0

        """
        index = index % self.size
        index = (self.head + index) % self.size
        return index

    def _slice(self, start, stop, step=1):
        """Slice for this CircularList, but STOP is inclusive

        Internally, only based on self.size

        >>> c = CircularList(5)
        >>> list(c._slice(0, 2))
        [0, 1, 2]
        >>> list(c._slice(0, 0))
        [0]
        >>> list(c._slice(2, 0))
        [2, 3, 4, 0]
        >>> list(c._slice(2, 1))
        [2, 3, 4, 0, 1]
        >>> list(c._slice(4, 1))
        [4, 0, 1]
        """
        start = start % self.size
        stop = stop % self.size
        if stop >= start:
            for i in range(start, stop+1, step):
                yield i
        elif start > stop:
            n = (self.size - start) + (stop+1)
            for i in range(0, n, step):
                yield (i+start) % self.size

    def _index_within(self, i):
        """Returns True if i is a valid element within the CircularList. False if not present."""
        if self.tail is None:
            return False
        elif self.tail >= self.head:
            return i <= self.tail and i >= self.head
        elif self.head > self.tail:
            return (i >= self.head and i < self.size) or (i >= 0 and i <= self.tail)

    def __len__(self):
        """Get the length of the added elements

        >>> c = CircularList(5)
        >>> len(c)
        0
        >>> c.update([1,2,3])
        >>> len(c)
        3
        >>> c.update([4,5,6,7])
        >>> len(c)
        5
        >>> c.pophead()
        3
        >>> c.pophead()
        4
        >>> len(c)
        3
        """
        if self.tail is None:
            return 0
        elif self.head <= self.tail:
            return self.tail - self.head + 1
        elif self.head > self.tail:
            return self.size - self.head + (self.tail + 1)

    def __getitem__(self, i: slice | int):
        """Gets an item from the list. 

        Raises IndexError if index is out of bounds or the list is empty

        >>> c = CircularList(5)
        >>> c.update([1])
        >>> c.update([2, 3, 4, 5, 6])
        >>> c[1:4]
        [3, 4, 5]
        >>> c.update([7, 8, 9, 10])
        >>> c[1:4]
        [7, 8, 9]
        >>> c.update([11, 12, 13])
        >>> c[1:4]
        [10, 11, 12]
        >>> c[2:0]
        []
        """
        if type(i) == int:
            if i >= self.__len__():
                raise IndexError("Index out of bounds")
            i = self._convert_index(i)
            item = self.data[i]
            if isinstance(item, CircularList.Empty):
                raise IndexError("Index is out of bounds")
            return item
        if type(i) == slice:
            start = 0 if i.start is None else i.start
            # Becomes the last index we do want to get. Might match start
            stop = self.size-1 if i.stop is None else i.stop-1

            if start > stop:
                return []

            n = self.__len__()
            start = range_limit(start % self.size, 0, n)
            stop = range_limit(stop % self.size, 0, n)

            start = self._convert_index(start)
            # inclusive stop, the index of the last element to get
            stop = self._convert_index(stop)
            step = 1 if i.step is None else i.step

            return [self.data[i] for i in self._slice(start, stop, step)]

    def __setitem__(self, i: int, value):
        """Sets an index's position in the circular list.

        >>> c = CircularList(4)
        >>> c.update([1,2])
        >>> c[1] = 0
        >>> c
        [1, 0]
        >>> c[2] = 3 # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        IndexError: Index is out of bounds
        >>> c[1] = CircularList.Empty() # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: list element cannot be of the CircularList.Empty class
        >>> c.update([4, 5, 6, 7])
        >>> c[2] = 1
        >>> c
        [4, 5, 1, 7]
        """
        i = self._convert_index(i)
        item = self.data[i]
        if isinstance(item, CircularList.Empty):
            raise IndexError("Index is out of bounds")
        if isinstance(value, CircularList.Empty):
            raise ValueError(
                "list element cannot be of the CircularList.Empty class")
        self.data[i] = value

    def __contains__(self, value):
        if isinstance(value, CircularList.Empty):
            raise ValueError(
                "list element cannot be of the CircularList.Empty class")
        return value in self.data

    def __reversed__(self):
        c = CircularList(self.size)
        c.update(reversed(self.data))
        return c

    def clear(self):
        n = self.__len__()
        for i in range(n):
            self.pop()

    def copy(self):
        c = CircularList(self.size)
        c.update(c.to_list())
        return c

    def extend(self, iterable):
        self.update(iterable)

    def count(self, value):
        """"""
        return self.to_list().count(value)  # TODO: Optimize this

    def index(self, value):
        """"""
        return self.to_list().index(value)  # TODO: Optimize this

    def remove(self, value):
        """"""
        raise Exception("Unimplemented function")

    def reverse(self):
        """"""
        raise Exception("Unimplemented function")

    def sort(self):
        """"""
        raise Exception("Unimplemented function")


# class RangeLimitFilter(SimpleFunctionFilter):
#     def __init__(self, source, lower, upper):
#         super().__init__(source, lambda x: range_limit(x, lower, upper))


# class ModulusFilter(SimpleFunctionFilter):
#     def __init__(self, source, mod):
#         super().__init__(source, lambda x: x % mod)


# class MaximumFilter(WidthFunctionFilter):
#     def __init__(self, source, N):
#         super().__init__(source, N, max)


# class MinimumFilter(WidthFunctionFilter):
#     def __init__(self, source, N):
#         super().__init__(source, N, min)


# class MeanFilter(WidthFunctionFilter):
#     def __init__(self, source, N):
#         super().__init__(source, N, mean)


# class MedianFilter(WidthFunctionFilter):
#     def __init__(self, source, N):
#         super().__init__(source, N, median)


# class SumFilter(WidthFunctionFilter):
#     def __init__(self, source, N):
#         super().__init__(source, N, sum)


# class IntegrationTracker(AppendingList):
#     """IntegrationTracker is a special type of list which finds the trapezoidal integral of added values.

#     For Example:
#     tracker = IntegrationTracker() # instantiate tracker
#     tracker.append(0,1) # append with values (y-value, delta-x)
#     tracker.append(1)   # same as .append(1,1)
#     tracker.append(2,1)
#     tracker.append(3,1)

#     print(tracker.get_original()) # gives list of added values (y,dx)
#     print(tracker)     # gives integrated values: [0, 0.5, 2, 4.5]
#     print(tracker[-1]) # gives 4.5, last added value
#     tracker[2] = 3     # will not work, only append or extend can change tracker

#     tracker += [0,1,2,3] # appends each element of list
#     tracker.extend([0,1,2,3]) # appends each element of list

#     tracker += [(0,2), (0,3)] # appends each pair from list as y and dx to tracker
#     tracker.extend([(0,2), (0,3)]) # appends each pair from list as y and dx to tracker
#     """

#     def __init__(self):
#         super().__init__()
#         self._result = 0
#         self._last = 0
#         self._original = []

#     def append(self, value, dx=1):
#         if type(value) != float and type(value) != int:
#             raise ValueError(
#                 "Parameter 'value' must be an acceptable numerical value, float or int")
#         if type(dx) != float and type(dx) != int:
#             raise ValueError(
#                 "Parameter 'dx' must be an acceptable numerical value, float or int")

#         self._original.append((value, dx))
#         if len(self) > 0:
#             self._result += (self._last + value) * dx * 0.5
#         self._last = value
#         super().append(self._result)

#     def extend(self, ls):
#         self.__iadd__(ls)

#     def __iadd__(self, ls):
#         ls = list(ls)
#         for o in ls:
#             try:
#                 i = iter(o)
#                 if len(i) > 1:
#                     self.append(i[0], i[1])
#                 else:
#                     self.append(i[0])
#             except TypeError:
#                 self.append(o)
#         return self

#     def reset(self, value=0):
#         self._result = value
#         self._last = 0

#     def get_original(self):
#         return tuple(self._original)


# def integration(samples: list, delta_time=1):
#     """Returns the trapezoidal integration of the samples, given a constant sample time interval.

#     Example:
#     samples = [0,1,2,3,4] and delta_time=1
#     result => [0, 0.5, 2, 4.5, 8]
#     (Equivalent of f(x)=x integrated to g(x)=x^2/2)

#     delta_time can be a float or a list of floats (the list must be length N-1 as samples N)
#     """
#     if type(delta_time) == list:
#         if not all([type(d) == float or type(d) == int for d in delta_time]):
#             return None
#         if len(delta_time) != len(samples)-1:
#             return None
#     elif type(delta_time) == int or type(delta_time) == float:
#         m = float(delta_time)
#         delta_time = [m for m in range(len(samples)-1)]
#     else:
#         return None

#     N = len(samples)
#     result = 0
#     ls = [0]
#     for i in range(N-1):
#         j = i + 1
#         result += (samples[i] + samples[j]) * delta_time[i] * 0.5
#         ls.append(result)
#     return ls


if __name__ == '__main__':
    import doctest
    doctest.testmod()
