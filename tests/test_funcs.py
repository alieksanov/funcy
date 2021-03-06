from operator import __add__, __sub__
import pytest
from whatever import _

from funcy.py2 import map, merge_with
from funcy.funcs import *
from funcy.seqs import keep


def test_caller():
    assert caller([1, 2])(sum) == 3

def test_constantly():
    assert constantly(42)() == 42
    assert constantly(42)('hi', 'there', volume='shout') == 42

def test_partial():
    assert partial(__add__, 10)(1) == 11
    assert partial(__add__, 'abra')('cadabra') == 'abracadabra'

    merge = lambda a=None, b=None: a + b
    assert partial(merge, a='abra')(b='cadabra') == 'abracadabra'
    assert partial(merge, b='abra')(a='cadabra') == 'cadabraabra'

def test_func_partial():
    class A(object):
        f = func_partial(lambda x, self: x + 1, 10)

    assert A().f() == 11

def test_back_partial():
    assert rpartial(__sub__, 10)(1) == -9
    assert rpartial(pow, 2, 85)(10) == 15


def test_curry():
    assert curry(lambda: 42)() == 42
    assert curry(_ * 2)(21) == 42
    assert curry(_ * _)(6)(7) == 42
    assert curry(__add__, 2)(10)(1) == 11
    assert curry(__add__)(10)(1) == 11  # Introspect builtin
    assert curry(lambda x,y,z: x+y+z)('a')('b')('c') == 'abc'

def test_curry_funcy():
    # curry() doesn't handle required star args,
    # but we can code inspection for funcy utils.
    assert curry(map)(int)('123') == [1, 2, 3]
    assert curry(merge_with)(sum)({1: 1}) == {1: 1}

def test_rcurry():
    assert rcurry(__sub__, 2)(10)(1) == -9
    assert rcurry(lambda x,y,z: x+y+z)('a')('b')('c') == 'cba'

def test_autocurry():
    at = autocurry(lambda a, b, c: (a, b, c))

    assert at(1)(2)(3) == (1, 2, 3)
    assert at(1, 2)(3) == (1, 2, 3)
    assert at(1)(2, 3) == (1, 2, 3)
    assert at(1, 2, 3) == (1, 2, 3)
    with pytest.raises(TypeError): at(1, 2, 3, 4)
    with pytest.raises(TypeError): at(1, 2)(3, 4)

    assert at(a=1, b=2, c=3) == (1, 2, 3)
    assert at(c=3)(1, 2) == (1, 2, 3)
    assert at(c=4)(c=3)(1, 2) == (1, 2, 3)
    with pytest.raises(TypeError): at(a=1)(1, 2, 3)

def test_autocurry_named():
    at = autocurry(lambda a, b, c=9: (a, b, c))

    assert at(1)(2) == (1, 2, 9)
    assert at(1)(2, 3) == (1, 2, 3)
    assert at(a=1)(b=2) == (1, 2, 9)
    assert at(c=3)(1)(2) == (1, 2, 3)

def test_autocurry_builtin():
    assert autocurry(complex)(imag=1)(0) == 1j
    assert autocurry(map)(_ + 1)([1, 2]) == [2, 3]
    assert autocurry(int)(base=12)('100') == 144

def test_autocurry_hard():
    def required_star(f, *seqs):
        return map(f, *seqs)

    assert autocurry(required_star)(__add__)('12', 'ab') == ['1a', '2b']

    _iter = autocurry(iter)
    assert list(_iter([1, 2])) == [1, 2]
    assert list(_iter([0, 1, 2].pop)(0)) == [2, 1]

    _keep = autocurry(keep)
    assert list(_keep('01')) == ['0', '1']
    assert _keep(int)('01') == [1]
    with pytest.raises(TypeError): _keep(1, 2, 3)

def test_autocurry_class():
    class A:
        def __init__(self, x, y=0):
            self.x, self.y = x, y

    assert autocurry(A)(1).__dict__ == {'x': 1, 'y': 0}

    class B: pass
    autocurry(B)()

    class I(int): pass
    assert autocurry(int)(base=12)('100') == 144


def test_compose():
    double = _ * 2
    inc    = _ + 1
    assert compose()(10) == 10
    assert compose(double)(10) == 20
    assert compose(inc, double)(10) == 21
    assert compose(str, inc, double)(10) == '21'
    assert compose(int, r'\d+')('abc1234xy') == 1234

def test_rcompose():
    double = _ * 2
    inc    = _ + 1
    assert rcompose()(10) == 10
    assert rcompose(double)(10) == 20
    assert rcompose(inc, double)(10) == 22
    assert rcompose(double, inc)(10) == 21

def test_complement():
    assert complement(identity)(0) is True
    assert complement(identity)([1, 2]) is False

def test_juxt():
    assert juxt(__add__, __sub__)(10, 2) == [12, 8]
    assert map(juxt(_ + 1, _ - 1), [2, 3]) == [[3, 1], [4, 2]]

def test_iffy():
    assert map(iffy(_ % 2, _ * 2, _ / 2), [1,2,3,4]) == [2,1,6,2]
    assert map(iffy(_ % 2, _ * 2), [1,2,3,4]) == [2,2,6,4]
    assert map(iffy(_ * 2), [21, '', None]) == [42, '', None]
    assert map(iffy(_ % 2, _ * 2, None), [1,2,3,4]) == [2, None, 6, None]
    assert map(iffy(_ + 1, default=1), [1, None, 2]) == [2, 1, 3]
