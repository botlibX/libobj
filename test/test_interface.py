# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,E0611,C0103,R0903,I1101


"interface"


import logging
import sys
import unittest


from obj import Object


import obj


METHODS = [
           'items',
           'keys',
           'read',
           'construct',
           'update',
           'write',
           'values'
          ]


METHOS = [
          'JSONDecoder',
          'JSONEncoder',
          'Object',
          'ObjectDecoder',
          'ObjectEncoder',
          '__builtins__',
          '__cached__',
          '__file__',
          '__loader__',
          '__name__',
          '__package__',
          '__spec__',
          'construct',
          'dump',
          'dumps',
          'hook',
          'json',
          'load',
          'loads',
          'write',
          'read'
        ]



class A(Object):

    def a(self):
        return "b"


DICT = {}


DIFF = [
        '__dict__',
        '__module__',
        '__slots__',
       ]


OBJECT = obj


class TestInterface(unittest.TestCase):

    def test_methodinterface(self):
        okd = True
        for meth in METHODS:
            func1 = getattr(OBJECT, meth)
            if not func1:
                continue
            func2 = DICT.get(meth)
            if not func2:
                continue
            if dir(func1) != dir(func2):
                okd = False
            sys.stdout.flush()
        self.assertTrue(okd)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("SomeTest.testSomething").setLevel(logging.DEBUG)
    unittest.main()
