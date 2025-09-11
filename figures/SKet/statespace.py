from __future__ import annotations

from abc import ABC, abstractmethod
import collections.abc
from enum import Enum
from typing import *


class StateSpace(ABC, collections.abc.Collection):
    """
    StateSpace base class

    """

    def __init__(self, basis_elements: Collection[str | int | float] = ("e",)):
        """
        Create StateSpace with the provided basis elements.
        Elements are stringified if any are float or int

        Args:
            basis_elements: Collection[str | int | float]
        """
        stringified_elements = []
        for e in basis_elements:
            stringified_elements.append(str(e))
        self.basis_elements = tuple(stringified_elements)

        # initialize scalars with zero
        self.scalars = {key: 0 for key in self.basis_elements}

    @abstractmethod
    def check(self):
        """
        Check if scalar values satisfy provided invariant conditions
        """
        ...

    @abstractmethod
    def update(self, *args, **kwargs):
        """
        Update scalar values according to provided algorithm

        Args:
            *args:
            **kwargs:
        """
        ...

    @abstractmethod
    def resolve(self, *args, **kwargs):
        """
        Collapse the superposition of states to a minimum according to provided algorithm

        Args:
            *args:
            **kwargs:
        """
        ...

    # BELOW HERE is Pythonification Fluff
    # Not necessary to understand StateSpaces

    def __str__(self):
        """ return stringifcation of scalars and basis elements """

        results = []
        for key in self.basis_elements:
            scalar = self.scalars[key]
            results.append("%s<%s>" % (str(scalar), str(key)))

        return " + ".join(results)

        # return results.join(" + ")

    # required method implementatons for abstract type Collection
    def __contains__(self, __x: object) -> bool:
        """ return x in self """
        if __x in self.basis_elements:
            return True
        else:
            return False

    def __len__(self) -> int:
        """ return len(x) """
        return len(self.basis_elements)

    def __iter__(self) -> Iterator[str]:
        """ for x in self """
        for x in self.basis_elements:
            yield x

    # Inequalities comparing number of basis elements
    def __le__(self, other: Collection[Any]) -> bool:
        """ Return self <= other """
        return len(self) <= len(other)

    def __lt__(self, other: Collection[Any]) -> bool:
        """ Return self < other """
        return len(self) < len(other)

    def __gt__(self, other: Collection[Any]) -> bool:
        """ Return self > other """
        return len(self) > len(other)

    def __ge__(self, other: Collection[Any]) -> bool:
        """ Return self >= other """
        return len(self) >= len(other)

    # Other set-like operations not implemented
    # def __and__(self, other: Collection[Any]) -> Collection[_T_co]: ...
    # """ Return self & other """
    #
    # def __or__(self, other: Collection[_T]) -> Collection[_T_co | _T]: ...
    # """ Return self | other """
    #
    # def __sub__(self, other: Collection[Any]) -> Collection[_T_co]: ...
    # """ Return self - other """
    #
    # def __xor__(self, other: Collection[_T]) -> Collection[_T_co | _T]: ...
    # """ Return self ^ other """
    #
    # def isdisjoint(self, other: Iterable[Any]) -> bool: ...
    # """ Return True if two sets have a null intersection. """


class EnumStateSpace(StateSpace):

    def __init__(self, basis_elements: Collection[str | int | float] = ("e",), enum_states: Collection[str] = ("0",)):
        """
        StateSpace implementation where scalars are discrete members of an enumeration,
        and updates increment selected basis elements along the ordered enumeration.
        Increments beyond the length of the enumeration rollover back to the start.

        Provides check() and update(), but resolve() does nothing.

        Args:
            basis_elements:
            enum_states:
        """
        super().__init__(basis_elements=basis_elements)

        self.enum_states = Enum('scalar_states', enum_states, start=0)

        # first value of enumeration is the origin state for each scalar
        origin_state = self.enum_states(0)

        # initialize scalars with origin_state
        self.scalars = {key: origin_state for key in self.basis_elements}

    def check(self):
        """
        Check if scalar values satisfy provided invariant conditions
        """

        # verify that scalar states are part of enumeration
        for basis_name, state_name in self.scalars.items():
            if state_name not in self.enum_states:
                return False
        return True

    def update(self, basis_element: str | int | float, *args, **kwargs):
        """
        Increment state on provided basis element
        """

        # FIXME: so many steps to increment an enumeration in a cycle!
        total_states = len(self.enum_states)
        basis_elem = str(basis_element)
        scalar_state = self.scalars[basis_elem]
        int_value = scalar_state.value
        new_value = (int_value + 1) % total_states
        new_state = self.enum_states(new_value)
        self.scalars[basis_elem] = new_state

    def resolve(self, *args, **kwargs):
        """
        Collapse the superposition of states to a minimum according to provided algorithm

        Args:
            *args:
            **kwargs:
        """
        return None

    def __str__(self):
        """ override default and stringify Enum members """

        results = []
        for key in self.basis_elements:
            scalar = self.scalars[key].name
            results.append("%s<%s>" % (str(scalar), str(key)))

        return " + ".join(results)


# cyclical enumeration for scalar state space of each basis element
bar = EnumStateSpace(basis_elements=["e1", "e2", "e3"], enum_states=["state0", "state1", "state2"])

# Update function increments selected basis element's scalar

# increment full cycle (goes back to zero)
bar.update("e1")
bar.update("e1")
bar.update("e1")

# increment 1
bar.update("e2")

# increment 2
bar.update("e3")
bar.update("e3")

# Check function ensures each scalar is within the enumeration of states
bar.check()

# Resolve function does nothing for this state space implementation
bar.resolve()

# print stringified version of superposition
print(bar)

# FIXME: no longer works instantiating StateSpace directly since it now has
#  @abstractmethod functions to be implemented by subclasses

# Demonstrate implemented methods so far
# foo = StateSpace(["a", "b", "c", 3.3])
# bar = StateSpace(["c", "d", "e", "f", -3])
# print(list(foo))
# print(list(bar))
# print(len(foo))
# print(len(bar))
# print(foo < bar)
# print(foo <= bar)
# print(foo >= bar)
# print(foo > bar)
# print(foo)
# print(bar)
