
from pytools.inPlace import InPlaceOption


class DummyClass:
    def __init__(self, num=1, aList=None):
        self.num = num
        self.aList = aList or [0, 1, 2, 3]

    @InPlaceOption
    def add(self, n=1, inPlace=False):
        self.num += n
        return self

    @InPlaceOption
    def append(self, item, inPlace=False):
        self.aList.append(item)
        return self


def test_in_place():
    dummy = DummyClass()
    with_add = dummy.add(1, inPlace=False)
    assert dummy != with_add
    with_append = dummy.append(4, inPlace=False)
    assert dummy != with_append

    in_place_add = dummy.add(1, inPlace=True)
    assert dummy == in_place_add
    in_place_append = dummy.append(4, inPlace=True)
    assert dummy == in_place_append
