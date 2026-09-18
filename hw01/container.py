from collections.abc import Iterable, Iterator, Sequence
from typing import Any, TypeVar

T = TypeVar("T")


class RingBuffer(Sequence[T]):
    """кольцевой буфер фиксированной ёмкости: append вытесняет самый старый элемент."""

    def __init__(self, capacity: int, items: Iterable[T] = ()) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._data: list[Any] = [None] * capacity
        self._start = 0
        self._size = 0
        for value in items:
            self.append(value)

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def is_full(self) -> bool:
        return self._size == self._capacity

    def append(self, value: T) -> None:
        self._data[(self._start + self._size) % self._capacity] = value
        if self.is_full:
            self._start = (self._start + 1) % self._capacity
        else:
            self._size += 1

    def extend(self, items: Iterable[T]) -> None:
        for value in items:
            self.append(value)

    def pop(self) -> T:
        if self._size == 0:
            raise IndexError("pop from empty buffer")
        self._size -= 1
        position = (self._start + self._size) % self._capacity
        value = self._data[position]
        self._data[position] = None
        return value

    def clear(self) -> None:
        self._data = [None] * self._capacity
        self._start = 0
        self._size = 0

    def _normalize(self, index: int) -> int:
        if index < 0:
            index += self._size
        if not 0 <= index < self._size:
            raise IndexError("buffer index out of range")
        return index

    def _position(self, index: int) -> int:
        return (self._start + self._normalize(index)) % self._capacity

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> T:
        return self._data[self._position(index)]

    def __setitem__(self, index: int, value: T) -> None:
        self._data[self._position(index)] = value

    def __delitem__(self, index: int) -> None:
        values = list(self)
        del values[self._normalize(index)]
        self.clear()
        self.extend(values)

    def __iter__(self) -> Iterator[T]:
        for offset in range(self._size):
            yield self._data[(self._start + offset) % self._capacity]

    def __reversed__(self) -> Iterator[T]:
        for offset in reversed(range(self._size)):
            yield self._data[(self._start + offset) % self._capacity]

    def __contains__(self, value: object) -> bool:
        return any(item == value for item in self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RingBuffer):
            return NotImplemented
        return self._capacity == other._capacity and list(self) == list(other)

    def __repr__(self) -> str:
        return f"RingBuffer(capacity={self._capacity}, items={list(self)!r})"

    def __str__(self) -> str:
        return f"[{', '.join(repr(value) for value in self)}]"
