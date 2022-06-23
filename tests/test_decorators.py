
import copy
from pytools.inPlace import InPlaceOption


class DummyClass:
    def __init__(self, num=1, aList=None):
        self.num = num
        self.aList = aList or [0, 1, 2, 3]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.num}, {self.aList}>"

    def __eq__(self, other):
        return other.num == self.num and other.aList == self.aList

    @InPlaceOption
    def add(self, n=1, inPlace=False):
        self.num += n
        return self

    @InPlaceOption
    def append(self, item, inPlace=False):
        self.aList.append(item)
        return self

    @InPlaceOption
    def addAndCopy(self, n=1, inPlace=False):
        new_dummy = DummyClass()
        new_dummy.add(n, inPlace=True)
        return new_dummy


def test_in_place():
    dummy = DummyClass()
    original_dummy = copy.deepcopy(dummy)

    # NOT In Place
    with_add = dummy.add(1, inPlace=False)
    assert dummy != with_add
    assert dummy == original_dummy
    with_append = dummy.append(4, inPlace=False)
    assert dummy != with_append
    assert dummy == original_dummy

    with_add_and_copy = dummy.addAndCopy(1, inPlace=False)
    assert dummy != with_add_and_copy
    assert dummy == original_dummy

    # In Place
    in_place_add = dummy.add(1, inPlace=True)
    assert dummy == in_place_add
    in_place_append = dummy.append(4, inPlace=True)
    assert dummy == in_place_append
    in_place_add_and_copy = dummy.addAndCopy(1, inPlace=True)
    assert in_place_add_and_copy == dummy
