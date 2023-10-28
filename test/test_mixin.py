# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,E0611


"mixin"


import unittest


from obj import Object, read, write


class Test:

    pass


class TestMixin(unittest.TestCase):

    def test_object(self):
        class Mixin(Object, object):
            pass
        mixin = Mixin()
        mixin.a = "b"
        write(mixin, ".test/mixin")
        mixin2 = Mixin()
        read(mixin2, ".test/mixin")        
        self.assertEqual(mixin2.a, "b")

    def test_Test(self):
        class Mixin(Test, Object):
            pass
        mixin = Mixin()
        mixin.a = "b"
        write(mixin, ".test/mixin")
        mixin2 = Mixin()
        read(mixin2, ".test/mixin")        
        self.assertEqual(mixin2.a, "b")
