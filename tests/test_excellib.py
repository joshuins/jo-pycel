# -*- coding: UTF-8 -*-
#
# Copyright 2011-2019 by Dirk Gorissen, Stephen Rauch and Contributors
# All rights reserved.
# This file is part of the Pycel Library, Licensed under GPLv3 (the 'License')
# You may not use this work except in compliance with the License.
# You may obtain a copy of the Licence at:
#   https://www.gnu.org/licenses/gpl-3.0.en.html

import math

import pytest

import pycel.excellib
from datetime import datetime
from pycel.excellib import (
    _numerics,
    average,
    averageif,
    averageifs,
    ceiling,
    ceiling_math,
    ceiling_precise,
    conditional_format_ids,
    count,
    countif,
    countifs,
    even,
    fact,
    factdouble,
    floor,
    floor_math,
    floor_precise,
    isblank,
    iserr,
    iserror,
    iseven,
    isna,
    isnumber,
    isodd,
    istext,
    # ::TODO:: finish test cases for remainder of functions
    # linest,
    large,
    ln,
    log,
    maxifs,
    minifs,
    mod,
    normsdist,
    now,
    npv,
    numbervalue,
    odd,
    power,
    product,
    rounddown,
    roundup,
    sign,
    small,
    sumif,
    sumifs,
    sumproduct,
    text,
    trunc,
    x_abs,
    x_int,
    x_round,
    xatan2,
    xmax,
    xmin,
    xsum,
    bitand,
    bitor,
    bitxor,
    bitlshift,
    bitrshift
)
from pycel.excelutil import (
    DIV0,
    EMPTY,
    NA_ERROR,
    NAME_ERROR,
    NUM_ERROR,
    REF_ERROR,
    VALUE_ERROR,
)
from pycel.lib.function_helpers import load_to_test_module


# dynamic load the lib functions from excellib and apply metadata
load_to_test_module(pycel.excellib, __name__)


def test_numerics():
    assert (1, 2, 3.1) == _numerics(1, '3', 2.0, pytest, 3.1, 'x')
    assert (1, 2, 3.1) == _numerics((1, '3', (2.0, pytest, 3.1), 'x'))


def test_average():
    assert 2 == average(1, '3', 2.0, pytest, 3, 'x')
    assert 2 == average((1, '3', (2.0, pytest, 3), 'x'))

    assert -0.1 == average((-0.1, None, 'x', True))

    assert DIV0 == average(['x'])

    assert VALUE_ERROR == average(VALUE_ERROR)
    assert VALUE_ERROR == average((2, VALUE_ERROR))

    assert DIV0 == average(DIV0)
    assert DIV0 == average((2, DIV0))


@pytest.mark.parametrize(
    'data, result', (
        ((12, 12), AssertionError),
        ((12, 12, 12), 12),
        ((((1, 1, 2, 2, 2), ), ((1, 1, 2, 2, 2), ), 2), 2),
        ((((1, 1, 2, 2, 2), ), ((1, 1, 2, 2, 2), ), 3), DIV0),
        ((((1, 2, 3, 4, 5), ), ((1, 2, 3, 4, 5), ), ">=3"), 4),
        ((((100, 123, 12, 23, 634), ),
          ((1, 2, 3, 4, 5), ), ">=3"), 223),
        ((((100, 123), (12, 23)), ((1, 2), (3, 4)), ">=3"), 35 / 2),
        ((((100, 123, 12, 23, None), ),
          ((1, 2, 3, 4, 5), ), ">=3"), 35 / 2),
        (('JUNK', ((), ), ((), ), ), VALUE_ERROR),
        ((((1, 2), ), ((1,), ), '', ((1, 2), ), ''), VALUE_ERROR),
        ((((1, 2, 3, 4, 5), ),
          ((1, 2, 3, 4, 5), ), ">=3",
          ((1, 2, 3, 4, 5), ), "<=4"), 7 / 2),
    )
)
def test_averageifs(data, result):
    if isinstance(result, type(Exception)):
        with pytest.raises(result):
            averageifs(*data)
    else:
        assert averageifs(*data) == result


@pytest.mark.parametrize(
    'value, expected', (
        (1, 1),
        (-2, 2),
        (((2, -3, 4, -5), ), ((2, 3, 4, 5), )),
        (DIV0, DIV0),
        (NUM_ERROR, NUM_ERROR),
        (VALUE_ERROR, VALUE_ERROR),
    )
)
def test_x_abs(value, expected):
    assert x_abs(value) == expected


class TestCeilingFloor:
    data_columns = "floor floor_prec floor_math_m floor_math " \
                   "ceil ceil_prec ceil_math_m ceil_math " \
                   "number significance".split()
    data_values = (
        (0, 0, 0, 0, 0, 0, 0, 0, None, 1),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        (2, 2, 2, 2, 2, 2, 2, 2, 2, 1),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 1),
        (4, 4, 4, 4, 5, 5, 5, 5, 4.9, 1),
        (5, 5, 5, 5, 6, 6, 6, 6, 5.1, 1),
        ((VALUE_ERROR, ) * 8 + ("AA", 1)),
        ((VALUE_ERROR, ) * 8 + (1, "AA")),
        (-1, -1, 0, -1, 0, 0, -1, 0, -0.001, 1),
        (0, -1, 0, -1, -1, 0, -1, 0, -0.001, -1),
        (0, 0, 0, 0, 1, 1, 1, 1, 0.001, 1),
        (NUM_ERROR, 0, 0, 0, NUM_ERROR, 1, 1, 1, 0.001, -1),
        (1, 1, 1, 1, 1, 1, 1, 1, True, 1),
        (0, 0, 0, 0, 0, 0, 0, 0, False, 1),
        (1, 1, 1, 1, 1, 1, 1, 1, 1, True),
        (DIV0, 0, 0, 0, 0, 0, 0, 0, 1, False),
        ((DIV0, ) * 8 + (DIV0, 1)),
        ((DIV0, ) * 8 + (2.5, DIV0)),
        ((NAME_ERROR, ) * 8 + (NAME_ERROR, 1)),
        ((NAME_ERROR, ) * 8 + (2.5, NAME_ERROR)),
        (2, 2, 2, 2, 3, 3, 3, 3, 2.5, 1),
        (2, 2, 2, 2, 3, 3, 3, 3, 2.5, 1),
        (2, 2, 2, 2, 4, 4, 4, 4, 2.5, 2),
        (0, 0, 0, 0, 3, 3, 3, 3, 2.5, 3),
        (-2, -3, -2, -3, -3, -2, -3, -2, -2.5, -1),
        (-2, -4, -2, -4, -4, -2, -4, -2, -2.5, -2),
        (0, -3, 0, -3, -3, 0, -3, 0, -2.5, -3),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (DIV0, 0, 0, 0, 0, 0, 0, 0, -2.5, 0),
        (-1, -1, -1, -1, -1, -1, -1, -1, -1, 1),
        (NUM_ERROR, 1, 1, 1, NUM_ERROR, 1, 1, 1, 1, -1),
    )

    data = {dc: dv for dc, dv in zip(data_columns, tuple(zip(*data_values)))}

    params = 'number, significance, result'
    inputs = data['number'], data['significance']

    @staticmethod
    @pytest.mark.parametrize(params, tuple(zip(*inputs, data['ceil'])))
    def test_ceiling(number, significance, result):
        assert ceiling(number, significance) == result

    @staticmethod
    @pytest.mark.parametrize(params, tuple(zip(*inputs, data['ceil_math'])))
    def test_ceiling_math(number, significance, result):
        assert ceiling_math(number, significance, False) == result

    @staticmethod
    @pytest.mark.parametrize(params, tuple(zip(*inputs, data['ceil_math_m'])))
    def test_ceiling_math_mode(number, significance, result):
        assert ceiling_math(number, significance, True) == result

    @staticmethod
    @pytest.mark.parametrize(params, tuple(zip(*inputs, data['ceil_prec'])))
    def test_ceiling_precise(number, significance, result):
        assert ceiling_precise(number, significance) == result

    @staticmethod
    @pytest.mark.parametrize(params, tuple(zip(*inputs, data['floor'])))
    def test_floor(number, significance, result):
        assert floor(number, significance) == result

    @staticmethod
    @pytest.mark.parametrize(params, tuple(zip(*inputs, data['floor_math'])))
    def test_floor_math(number, significance, result):
        assert floor_math(number, significance, False) == result

    @staticmethod
    @pytest.mark.parametrize(params, tuple(zip(*inputs, data['floor_math_m'])))
    def test_floor_math_mode(number, significance, result):
        assert floor_math(number, significance, True) == result

    @staticmethod
    @pytest.mark.parametrize(params, tuple(zip(*inputs, data['floor_prec'])))
    def test_floor_precise(number, significance, result):
        assert floor_precise(number, significance) == result


@pytest.mark.parametrize(
    'args, result', (
        (((True, 1, 0), (True, 2, 1), (True, 3, 0)), [1, 2]),
        (((False, 1, 0), (True, 2, 1), (True, 3, 0)), [2]),
        (((False, 1, 0), (True, 2, 0), (True, 3, 0)), [2, 3]),
        (((False, 1, 0), (False, 2, 0), (True, 3, 0)), [3]),
        (((False, 1, 0), (False, 2, 0), (False, 3, 0)), []),
        ((), []),
    )
)
def test_conditional_format_ids(args, result):
    assert conditional_format_ids(*args) == result


def test_count():
    data = (
        0,
        1,
        1.1,
        '1.1',
        True,
        False,
        'A',
        'TRUE',
        'FALSE',
    )
    assert count(data, data[3], data[5], data[7])


@pytest.mark.parametrize(
    'value, criteria, result', (
        (((7, 25, 13, 25), ), '>10', 3),
        (((7, 25, 13, 25), ), '<10', 1),
        (((7, 10, 13, 25), ), '>=10', 3),
        (((7, 10, 13, 25), ), '<=10', 2),
        (((7, 10, 13, 25), ), '<>10', 3),
        (((7, 'e', 13, 'e'), ), 'e', 2),
        (((7, 'e', 13, 'f'), ), '>e', 1),
        (((7, 25, 13, 25), ), 25, 2),
        (((7, 25, None, 25),), '<10', 1),
        (((7, 25, None, 25),), '>10', 2),
    )
)
def test_countif(value, criteria, result):
    assert countif(value, criteria) == result


class TestCountIfs:
    # more tests might be welcomed

    def test_countifs_regular(self):
        assert 1 == countifs(((7, 25, 13, 25), ), 25,
                             ((100, 102, 201, 20), ), ">100")

    def test_countifs_odd_args_len(self):
        with pytest.raises(AssertionError):
            countifs(((7, 25, 13, 25), ), 25, ((100, 102, 201, 20), ))


class TestVariousIfsSizing:

    test_vector = tuple(range(1, 7)) + tuple('abcdef')
    test_vectors = ((test_vector, ), ) * 4 + (test_vector[0],) * 4

    conditions = '>3', '<=2', '<=c', '>d'
    data_columns = ('averageif', 'countif', 'sumif', 'averageifs',
                    'countifs', 'maxifs', 'minifs', 'sumifs')

    responses_list = (
        (5, 3, 15, 5, 3, 6, 4, 15),
        (1.5, 2, 3, 1.5, 2, 2, 1, 3),
        (DIV0, 3, 0, DIV0, 3, 0, 0, 0),
        (DIV0, 2, 0, DIV0, 2, 0, 0, 0),

        (DIV0, 0, 0, DIV0, 0, 0, 0, 0),
        (1, 1, 1, 1, 1, 1, 1, 1),
        (DIV0, 0, 0, DIV0, 0, 0, 0, 0),
        (DIV0, 0, 0, DIV0, 0, 0, 0, 0),
    )

    responses = dict(
        (dc, tuple((r, cond, tv) for r, cond, tv in zip(resp, conds, tvs)))
        for dc, resp, tvs, conds in zip(
            data_columns, zip(*responses_list), (test_vectors, ) * 8,
            ((conditions + conditions), ) * 8
        ))

    params = 'result, criteria, values'

    @staticmethod
    @pytest.mark.parametrize(params, responses['averageif'])
    def test_averageif(result, criteria, values):
        assert averageif(values, criteria) == result
        assert averageif(values, criteria, values) == result

    @staticmethod
    @pytest.mark.parametrize(params, responses['countif'])
    def test_countif(result, criteria, values):
        assert countif(values, criteria) == result

    @staticmethod
    @pytest.mark.parametrize(params, responses['sumif'])
    def test_sumif(result, criteria, values):
        assert sumif(values, criteria) == result
        assert sumif(values, criteria, values) == result

    @staticmethod
    @pytest.mark.parametrize(params, responses['averageifs'])
    def test_averageifs(result, criteria, values):
        assert averageifs(values, values, criteria) == result

    @staticmethod
    @pytest.mark.parametrize(params, responses['countifs'])
    def test_countifs(result, criteria, values):
        assert countifs(values, criteria) == result

    @staticmethod
    @pytest.mark.parametrize(params, responses['maxifs'])
    def test_maxifs(result, criteria, values):
        assert maxifs(values, values, criteria) == result

    @staticmethod
    @pytest.mark.parametrize(params, responses['minifs'])
    def test_minifs(result, criteria, values):
        assert minifs(values, values, criteria) == result

    @staticmethod
    @pytest.mark.parametrize(params, responses['sumifs'])
    def test_sumifs(result, criteria, values):
        assert sumifs(values, values, criteria) == result

    def test_ifs_size_errors(self):
        criteria, v1 = self.responses['sumifs'][0][1:]
        v2 = (v1[0][:-1], )
        assert countifs(v1, criteria, v2, criteria) == VALUE_ERROR
        assert sumifs(v1, v1, criteria, v2, criteria) == VALUE_ERROR
        assert maxifs(v1, v1, criteria, v2, criteria) == VALUE_ERROR
        assert minifs(v1, v1, criteria, v2, criteria) == VALUE_ERROR
        assert averageifs(v1, v1, criteria, v2, criteria) == VALUE_ERROR


@pytest.mark.parametrize(
    '_iseven, _isodd, _sign, _odd, _even, value', (
        (True, False, -1, -101, -102, -100.1),
        (True, False, -1, -101, -102, '-100.1'),
        (True, False, -1, -101, -100, -100),
        (False, True, -1, -101, -100, -99.9),
        (True, False, 0, 1, 0, 0),
        (False, True, 1, 1, 2, 1),
        (True, False, 1, 1, 2, 0.1),
        (True, False, 1, 1, 2, '0.1'),
        (True, False, 1, 3, 2, '2'),
        (True, False, 1, 3, 4, 2.9),
        (False, True, 1, 3, 4, 3),
        (False, True, 1, 5, 4, 3.1),
        (VALUE_ERROR, VALUE_ERROR, 1, 1, 2, True),
        (VALUE_ERROR, VALUE_ERROR, 0, 1, 0, False),
        (VALUE_ERROR, ) * 5 + ('xyzzy', ),
        (VALUE_ERROR, ) * 6,
        (DIV0, ) * 6,
    )
)
def test_even_odd_sign(_iseven, _isodd, _sign, _odd, _even, value):
    assert iseven(value) == _iseven
    assert isodd(value) == _isodd
    assert sign(value) == _sign
    assert odd(value) == _odd
    assert even(value) == _even


@pytest.mark.parametrize(
    'result, number', (
        (1, None),
        (1, 0),
        (1, 1),
        (2, 2),
        (6, 3),
        (24, 4.9),
        (120, 5.1),
        (1, True),
        (1, False),
        (VALUE_ERROR, 'AA'),
        (NUM_ERROR, -1),
        (DIV0, DIV0),
    )
)
def test_fact(result, number):
    assert fact(number) == result


@pytest.mark.parametrize(
    'result, number', (
        (1, None),
        (1, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (8, 4.9),
        (15, 5.1),
        (VALUE_ERROR, True),
        (VALUE_ERROR, False),
        (VALUE_ERROR, 'AA'),
        (NUM_ERROR, -1),
        (DIV0, DIV0),
    )
)
def test_factdouble(result, number):
    assert factdouble(number) == result

@pytest.mark.parametrize(
    'value, expected', (
        ('', False),
        (1, False),
        (-1, False),
        ('a', False),
        (None, True)
    )
)
def test_isblank(value, expected):
    assert isblank(value) == expected


@pytest.mark.parametrize(
    'value, expected', (
        (0, False),
        (1, False),
        (1.0, False),
        (-1, False),
        ('a', False),
        (((1, NUM_ERROR), ('2', DIV0)), ((False, True), (False, True))),
        (NA_ERROR, False),
        (NUM_ERROR, True),
        (REF_ERROR, True),
    )
)
def test_iserr(value, expected):
    assert iserr(value) == expected


@pytest.mark.parametrize(
    'value, expected', (
        (0, False),
        (1, False),
        (1.0, False),
        (-1, False),
        ('a', False),
        (((1, NA_ERROR), ('2', DIV0)), ((False, True), (False, True))),
        (NUM_ERROR, True),
        (REF_ERROR, True),
    )
)
def test_iserror(value, expected):
    assert iserror(value) == expected


@pytest.mark.parametrize(
    'value, expected', (
        (0, False),
        (1, False),
        (1.0, False),
        (-1, False),
        ('a', False),
        (((1, NA_ERROR), ('2', 3)), ((False, True), (False, False))),
        (NA_ERROR, True),
        (VALUE_ERROR, False),
    )
)
def test_isna(value, expected):
    assert isna(value) == expected


@pytest.mark.parametrize(
    'value, expected', (
        (0, True),
        (1, True),
        (1.0, True),
        (-1, True),
        ('a', False),
        (((1, NA_ERROR), ('2', 3)), ((True, False), (False, True))),
        (NA_ERROR, False),
        (VALUE_ERROR, False),
    )
)
def test_isnumber(value, expected):
    assert isnumber(value) == expected


@pytest.mark.parametrize(
    'value, expected', (
        ('a', True),
        (1, False),
        (1.0, False),
        (None, False),
        (DIV0, False),
        (((1, NA_ERROR), ('2', 3)), ((False, False), (True, False))),
        (NA_ERROR, False),
        (VALUE_ERROR, False),
    )
)
def test_istext(value, expected):
    assert istext(value) == expected


@pytest.mark.parametrize(
    'data, k, result', (
        ([3, 1, 2], 0, NUM_ERROR),
        ([3, 1, 2], 1, 3),
        ([3, 1, 2], 2, 2),
        ([3, 1, 2], 3, 1),
        ([3, 1, 2], 4, NUM_ERROR),
        ([3, 1, 2], '2', 2),
        ([3, 1, 2], 1.1, 2),
        ([3, 1, 2], '1.1', 2),
        ([3, 1, 2], 0.1, NUM_ERROR),
        ([3, 1, 2], 3.1, NUM_ERROR),
        ([3, 1, 2], 'abc', VALUE_ERROR),
        ([3, 1, 2], True, 3),
        ([3, 1, 2], False, NUM_ERROR),
        ([3, 1, 2], 'True', VALUE_ERROR),
        ([3, 1, 2], REF_ERROR, REF_ERROR),
        ([3, 1, 2], EMPTY, VALUE_ERROR),
        (REF_ERROR, 2, REF_ERROR),
        (None, 2, NUM_ERROR),
        ('abc', 2, NUM_ERROR),
        (99, 1, 99),
        ('99', 1, 99),
        ('99.9', 1, 99.9),
        (['99', 9], 1, 99),
        (['99.9', 9], 1, 99.9),
        ([3, 1, 2], None, NUM_ERROR),
        ([3, 1, 2], 0, NUM_ERROR),
        ([3, 1, 2], 4, NUM_ERROR),
        ([3, 1, 'aa'], 2, 1),
        ([3, 1, 'aa'], 3, NUM_ERROR),
        ([3, 1, True], 1, 3),
        ([3, 1, True], 3, NUM_ERROR),
        ([3, 1, '2'], 2, 2),
        ([3, 1, REF_ERROR], 1, REF_ERROR),
    )
)
def test_large(data, k, result):
    assert result == large(data, k)


@pytest.mark.parametrize(
    'expected, value',
    (
        (math.log(5), 5),
        (math.log(2), 2),
        (NUM_ERROR, None),
        (VALUE_ERROR, VALUE_ERROR),
        (DIV0, DIV0),
        (math.log(5), 5),
        (((math.log(5), math.log(6)), ), ((5, 6), )),
        (((math.log(5), math.log(6)), ), ((5, 6), )),
        # (((math.log(5), math.log(6)), ), np.array(((5, 6), ))),
        (NUM_ERROR, None),
        (VALUE_ERROR, VALUE_ERROR),
        (((math.log(2), VALUE_ERROR), ), ((2, VALUE_ERROR), )),
        (DIV0, DIV0),
        (((math.log(2), DIV0), ), ((2, DIV0), )),
    )
)
def test_ln(expected, value):
    assert ln(value) == expected


@pytest.mark.parametrize(
    'expected, value',
    (
        (math.log(5, 10), 5),
        (math.log(2, 10), 2),
        (NUM_ERROR, None),
        (VALUE_ERROR, VALUE_ERROR),
        (DIV0, DIV0),
        (math.log(5, 10), 5),
        (((math.log(5, 10), math.log(6, 10)), ), ((5, 6), )),
        (((math.log(5, 10), math.log(6, 10)), ), ((5, 6), )),
        # (((math.log(5), math.log(6)), ), np.array(((5, 6), ))),
        (NUM_ERROR, None),
        (VALUE_ERROR, VALUE_ERROR),
        (((math.log(2, 10), VALUE_ERROR), ), ((2, VALUE_ERROR), )),
        (DIV0, DIV0),
        (((math.log(2, 10), DIV0), ), ((2, DIV0), )),
    )
)
def test_log(expected, value):
    assert log(value) == expected


lookup_vector = (('b', 'c', 'd'), )
lookup_result = ((1, 2, 3), )
lookup_rows = lookup_vector[0], lookup_result[0]
lookup_columns = tuple(zip(*lookup_rows))


class TestMod:

    def test_first_argument_validity(self):
        assert mod(VALUE_ERROR, 1) == VALUE_ERROR
        assert mod('x', 1) == VALUE_ERROR

    def test_second_argument_validity(self):
        assert mod(2, VALUE_ERROR) == VALUE_ERROR
        assert mod(2, 'x') == VALUE_ERROR
        assert mod(2, 0) == DIV0
        assert mod(2, None) == DIV0

    def test_output_value(self):
        assert 2 == mod(10, 4)
        assert mod(2.2, 1) == pytest.approx(0.2)
        assert mod(2, 1.1) == pytest.approx(0.9)


@pytest.mark.parametrize(
    'param, result', (
        (1, 0.8413447460685429),
        (2, 0.9772498680518208),
    )
)
def test_normsdist(param, result):
    # we are currently using mean=0 and stddev=1
    assert result == normsdist(param)


@pytest.mark.parametrize(
    'data, expected', (
        ((0.1, ((-10000,), (3000,), (4200,), (6800,))), 1188.44),
        ((0.08, ((1, 3), (2, 4))), 8.02572628005743),
        (("a", ((-10000,), (3000,), (4200,), (6800,))), VALUE_ERROR),
        ((0.08, (8000, 9200, 10000, 12000, 14500)), 41922.06),
        ((0.07, (8000, "a", 10000, True, 14500)), 28047.34),
        ((0.08, (8000, 9200, 10000, 12000, 14500, -9000)), 40000 - 3749.47),
        ((0.08, (8000, DIV0, 10000, 12000, 14500, -9000)), DIV0),
        ((0.08, (8000, NUM_ERROR, 10000, 12000, 14500, -9000)), NUM_ERROR),
        ((NA_ERROR, (8000, 9200, 10000, 12000, 14500, -9000)), NA_ERROR),
    )
)
def test_npv(data, expected):
    result = npv(*data)

    if isinstance(result, str):
        assert result == expected
    else:
        assert result == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize(
    'arguments, expected', (
        (1, 1.0),
        (-1, -1.0),
        ('1', 1.0),
        ('12.5', 12.5),
        ('    3  ', 3.0),
        (('1@34', '@'), 1.34),
        (('1@34', ''), VALUE_ERROR),
        ('12a', VALUE_ERROR),
        ('', VALUE_ERROR),
        (None, VALUE_ERROR)
    )
)
def test_numbervalue(arguments, expected):
    if isinstance(arguments, tuple):
        value, decimal_separator = arguments
        assert numbervalue(value, decimal_separator) == expected

    else:
        assert numbervalue(arguments) == expected


@pytest.mark.parametrize(
    'args, result', (
        ((((1, 2), (3, 4)), ((1, 3), (2, 4))), 576),
        ((((1, 2), (3, None)), ((1, 3), (2, 4))), 144),
        ((((1, 2), (3, 4)), ((1, 3), (2, '4'))), 144),
        ((((1, 2), (3, 4)), ((1, 3), (2, True))), 144),
        ((((1, NAME_ERROR), (3, 4)), ((1, 3), (2, 4))), NAME_ERROR),
        ((((1, 2), (3, 4)), ((1, 3), (NAME_ERROR, 4))), NAME_ERROR),
    )
)
def test_product(args, result):
    assert product(*args) == result


@pytest.mark.parametrize(
    'data, expected', (
        ((0, 0), NA_ERROR),
        ((0, 1), 0),
        ((1, 0), 1),
        ((1, 2), 1),
        ((2, 1), 2),
        ((2, -1), 0.5),
        ((-2, 1), -2),
        ((0.1, 0.1), 0.1 ** 0.1),
        ((True, 1), 1),
        (('x', 1), VALUE_ERROR),
        ((1, 'x'), VALUE_ERROR),
        ((NA_ERROR, 1), NA_ERROR),
        ((1, NA_ERROR), NA_ERROR),
        ((0, -1), DIV0),
        ((1, DIV0), DIV0),
        ((DIV0, 1), DIV0),
        ((NA_ERROR, DIV0), NA_ERROR),
        ((DIV0, NA_ERROR), DIV0),
    )
)
def test_power(data, expected):
    result = power(*data)
    if isinstance(result, str):
        assert result == expected
    else:
        assert result == pytest.approx(expected, rel=1e-3)


class TestRounding:
    data_columns = "rounddown roundup number digits ".split()
    data_values = (
        (3, 4, 3.2, 0),
        (76, 77, 76.9, 0),
        (3.141, 3.142, 3.14159, 3),
        (-3.1, -3.2, -3.14159, 1),
        (31400, 31500, 31415.92654, -2),
        (0, 0, None, -2),
        (0, 100, True, -2),
        (VALUE_ERROR, VALUE_ERROR, 3.2, 'X'),
        (VALUE_ERROR, VALUE_ERROR, 'X', 0),
        (VALUE_ERROR, VALUE_ERROR, 3.2, VALUE_ERROR),
        (VALUE_ERROR, VALUE_ERROR, VALUE_ERROR, 0),
    )

    data = {dc: dv for dc, dv in zip(data_columns, tuple(zip(*data_values)))}

    params = 'number, digits, result'
    inputs = data['number'], data['digits']

    @staticmethod
    @pytest.mark.parametrize(params, tuple(zip(*inputs, data['rounddown'])))
    def test_rounddown(number, digits, result):
        assert result == rounddown(number, digits)

    @staticmethod
    @pytest.mark.parametrize(params, tuple(zip(*inputs, data['roundup'])))
    def test_roundup(number, digits, result):
        assert result == roundup(number, digits)


@pytest.mark.parametrize(
    'data, k, result', (
        ([3, 1, 2], 0, NUM_ERROR),
        ([3, 1, 2], 1, 1),
        ([3, 1, 2], 2, 2),
        ([3, 1, 2], 3, 3),
        ([3, 1, 2], 4, NUM_ERROR),
        ([3, 1, 2], '2', 2),
        ([3, 1, 2], 1.1, 2),
        ([3, 1, 2], '1.1', 2),
        ([3, 1, 2], 0.1, NUM_ERROR),
        ([3, 1, 2], 3.1, NUM_ERROR),
        ([3, 1, 2], 'abc', VALUE_ERROR),
        ([3, 1, 2], True, 1),
        ([3, 1, 2], False, NUM_ERROR),
        ([3, 1, 2], 'True', VALUE_ERROR),
        ([3, 1, 2], REF_ERROR, REF_ERROR),
        ([3, 1, 2], EMPTY, VALUE_ERROR),
        (REF_ERROR, 2, REF_ERROR),
        (None, 2, NUM_ERROR),
        ('abc', 2, NUM_ERROR),
        (99, 1, 99),
        ('99', 1, 99),
        ('99.9', 1, 99.9),
        (['99', 999], 1, 99),
        (['99.9', 999], 1, 99.9),
        ([3, 1, 2], None, NUM_ERROR),
        ([3, 1, 2], 0, NUM_ERROR),
        ([3, 1, 2], 4, NUM_ERROR),
        ([3, 1, 'aa'], 2, 3),
        ([3, 1, 'aa'], 3, NUM_ERROR),
        ([3, 1, True], 1, 1),
        ([3, 1, True], 3, NUM_ERROR),
        ([3, 1, '2'], 2, 2),
        ([3, 1, REF_ERROR], 1, REF_ERROR),
    )
)
def test_small(data, k, result):
    assert result == small(data, k)


@pytest.mark.parametrize(
    'data, result', (
        ((12, 12), 12),
        ((12, 12, 12), 12),
        ((((1, 1, 2, 2, 2), ), 2), 6),
        ((((1, 2, 3, 4, 5), ), ">=3"), 12),
        ((((1, 2, 3, 4, 5), ), ">=3",
          ((100, 123, 12, 23, 633), )), 668),
        ((((1, 2, 3, 4, 5),), ">=3",
          ((100, 123, 12, 23, 633, 1),)), VALUE_ERROR),
        ((((1, 2, 3, 4, 5),), ">=3", ((100, 123, 12, 23),)), VALUE_ERROR),
        (([], [], 'JUNK'), IndexError),
    )
)
def test_sumif(data, result):
    if isinstance(result, type(Exception)):
        with pytest.raises(result):
            sumif(*data)
    else:
        assert sumif(*data) == result


@pytest.mark.parametrize(
    'data, result', (
        ((12, 12), AssertionError),
        ((12, 12, 12), 12),
        ((((1, 1, 2, 2, 2), ), ((1, 1, 2, 2, 2), ), 2), 6),
        ((((1, 2, 3, 4, 5), ), ((1, 2, 3, 4, 5), ), ">=3"), 12),
        ((((100, 123, 12, 23, 633), ),
          ((1, 2, 3, 4, 5), ), ">=3"), 668),
        ((((100, 123), (12, 23)), ((1, 2), (3, 4)), ">=3"), 35),
        ((((100, 123, 12, 23, None), ),
          ((1, 2, 3, 4, 5), ), ">=3"), 35),
        (('JUNK', ((), ), ((), ), ), VALUE_ERROR),
        ((((1, 2, 3, 4, 5), ),
          ((1, 2, 3, 4, 5), ), ">=3",
          ((1, 2, 3, 4, 5), ), "<=4"), 7),
    )
)
def test_sumifs(data, result):
    if isinstance(result, type(Exception)):
        with pytest.raises(result):
            sumifs(*data)
    else:
        assert sumifs(*data) == result


def test_now():
    dt = datetime.now().replace(second=0, microsecond=0)
    assert now().replace(second=0, microsecond=0) == dt


@pytest.mark.parametrize(
    'args, result', (
        ((((1, 2), (3, 4)), ((1, 3), (2, 4))), 29),
        ((((3, 4), (8, 6), (1, 9)), ((2, 7), (6, 7), (5, 3))), 156),
        ((((1, 2), (3, None)), ((1, 3), (2, 4))), 13),
        ((((1, 2), (3, 4)), ((1, 3), (2, '4'))), 13),
        ((((1, 2), (3, 4)), ((1, 3), (2, True))), 13),
        ((((1, NAME_ERROR), (3, 4)), ((1, 3), (2, 4))), NAME_ERROR),
        ((((1, 2), (3, 4)), ((1, 3), (NAME_ERROR, 4))), NAME_ERROR),
        ((((1, 2, 3), (3, 4, 6)), ((1, 3), (2, 4))), VALUE_ERROR),
    )
)
def test_sumproduct(args, result):
    assert sumproduct(*args) == result


@pytest.mark.parametrize(
    'text_value, value_format, result', (
            (now(), "DD/MM/YY hh:mm:ss", datetime.now().strftime('%d/%m/%y %H:%M:%S')),
            # Thousand separator
            ("12200000", "#,###", "12,200,000"),
            ("12200000", "0,000.00", "12,200,000.00"),
            # Number, currency, accounting
            ("1234.56", "0.00", "1234.56"),
            ("1234.56", "#,##0", "1,235"),
            ("1234.56", "#,##0.00", "1,234.56"),
            ("1234.56", "$#,##0", "$1,235"),
            ("1234.56", "$#,##0.00", "$1,234.56"),
            ("1234.56", "$ * #,##0", "$1,235"),
            ("1234.56", "$ * #,##0.00", "$1,234.56"),
            # Months, days, years
            ('15/01/2021', "m", '01'),  # Excel returns 1
            ('15/01/2021', "mm", '01'),
            ('15/01/2021', "mmm", 'Jan'),
            ('15/01/2021', "mmmm", 'January'),
            ('15/01/2021', "mmmmm", 'Jan'),  # Excel returns J
            ('15/01/2021', "d", '15'),
            ('15/01/2021', "dd", '15'),
            ('15/01/2021', "ddd", 'Fri'),
            ('15/01/2021', "dddd", 'Friday'),
            ('15/01/2021', "yy", '21'),
            ('15/01/2021', "yyyy", '2021'),
            # Hours, minutes and seconds
            ('3:33 am', "h", '03'),
            ('3:33 am', "hh", '03'),
            ('3:33 pm', "h", '15'),
            ('3:33 pm', "hh", '15'),
            ('3:33 pm', "m", '01'),  # Excel returns 1
            ('3:33 pm', "mm", '01'),
            ('3:33:30 pm', "s", '30'),
            ('3:33:30 pm', "ss", '30'),
            ('3:33 pm', "h AM/PM", '03 pm'),
            ('3:33 pm', "h:mm AM/PM", '03:33 pm'),
            ('3:33:30 pm', "h:mm:ss A/P", '15:33:30 A/P'),
            ('3:33 pm', "h:mm:ss.00", '15:33:00.00'),
            # not supported
            # ('3:33 pm', "[h]:mm", '1:02'),
            # ('3:33 pm', "[mm]:ss", '62:16'),
            # ('3:33 pm', "[ss].00", '3735.80'),
            # Date & Time
            ("31/12/1989 15:30:00", "MM/DD/YYYY", "12/31/1989"),
            ("31/12/1989 15:30:00", "MM/DD/YYYY hh:mm AM/PM", "12/31/1989 03:30 pm"),
            # Percentage
            ('0.244740088392962', '0%', '24%'),
            ('0.244740088392962', '0.0%', '24.5%'),
            ('0.244740088392962', '0.00%', '24.47%'),
    )
)
def test_text(text_value, value_format, result):
    assert text(text_value, value_format).lower() == result.lower()


@pytest.mark.parametrize(
    'number, num_digits, result', (
        (2.5, -1, 0),
        (2.5, 0, 2),
        (2.5, 1, 2.5),
        (-2.5, -1, 0),
        (-2.5, 0, -2),
        (-2.5, 1, -2.5),
        (NUM_ERROR, 1, NUM_ERROR),
        (1, NUM_ERROR, NUM_ERROR),
    )
)
def test_trunc(number, num_digits, result):
    assert trunc(number, num_digits) == result


@pytest.mark.parametrize(
    'param1, param2, result', (
        (1, 1, math.pi / 4),
        (1, 0, 0),
        (0, 1, math.pi / 2),
        (NA_ERROR, 1, NA_ERROR),
        (1, NA_ERROR, NA_ERROR),
        (DIV0, 1, DIV0),
        (1, DIV0, DIV0),
    )
)
def test_xatan2(param1, param2, result):
    assert xatan2(param1, param2) == result


@pytest.mark.parametrize(
    'value, expected', (
        (1, 1),
        (1.2, 1),
        (-1.2, -2),
        (((2.1, -3.9, 4.6, -5.3),), ((2, -4, 4, -6),)),
        (DIV0, DIV0),
        (NUM_ERROR, NUM_ERROR),
        (VALUE_ERROR, VALUE_ERROR),
    )
)
def test_x_int(value, expected):
    assert x_int(value) == expected


def test_xmax():
    assert 0 == xmax('abcd')
    assert 3 == xmax((2, None, 'x', 3))

    assert -0.1 == xmax((-0.1, None, 'x', True))

    assert VALUE_ERROR == xmax(VALUE_ERROR)
    assert VALUE_ERROR == xmax((2, VALUE_ERROR))

    assert DIV0 == xmax(DIV0)
    assert DIV0 == xmax((2, DIV0))


def test_xmin():
    assert 0 == xmin('abcd')
    assert 2 == xmin((2, None, 'x', 3))

    assert -0.1 == xmin((-0.1, None, 'x', True))

    assert VALUE_ERROR == xmin(VALUE_ERROR)
    assert VALUE_ERROR == xmin((2, VALUE_ERROR))

    assert DIV0 == xmin(DIV0)
    assert DIV0 == xmin((2, DIV0))


@pytest.mark.parametrize(
    'result, digits', (
        (0, -5),
        (10000, -4),
        (12000, -3),
        (12300, -2),
        (12350, -1),
        (12346, 0),
        (12345.7, 1),
        (12345.68, 2),
        (12345.679, 3),
        (12345.6789, 4),
    )
)
def test_x_round(result, digits):
    assert result == x_round(12345.6789, digits)
    assert result == x_round(12345.6789, digits + (-0.9 if digits < 0 else 0.9))


@pytest.mark.parametrize(
    'number, digits, result', (
        (2.15, 1, 2.2),
        (2.149, 1, 2.1),
        (-1.475, 2, -1.48),
        (21.5, -1, 20),
        (626.3, -3, 1000),
        (1.98, -1, 0),
        (-50.55, -2, -100),
        (DIV0, 1, DIV0),
        (1, DIV0, DIV0),
        ('er', 1, VALUE_ERROR),
        (2.323, 'ze', VALUE_ERROR),
        (2.675, 2, 2.68),
        (2352.67, -2, 2400),
        ("2352.67", "-2", 2400),
    )
)
def test_x_round2(number, digits, result):
    assert result == x_round(number, digits)


def test_xsum():
    assert 0 == xsum('abcd')
    assert 5 == xsum((2, None, 'x', 3))

    assert -0.1 == xsum((-0.1, None, 'x', True))

    assert VALUE_ERROR == xsum(VALUE_ERROR)
    assert VALUE_ERROR == xsum((2, VALUE_ERROR))

    assert DIV0 == xsum(DIV0)
    assert DIV0 == xsum((2, DIV0))


@pytest.mark.parametrize(
    'op_x, op_y, result', (
            (32, 48, 32),
            (1, 2, 0),
            (DIV0, 1, DIV0),
            (1, DIV0, DIV0),
            ('er', 1, VALUE_ERROR),
            (2, 'ze', VALUE_ERROR),
            (NUM_ERROR, 1, NUM_ERROR),
            (1, NUM_ERROR, NUM_ERROR),
            (-1, 1, NUM_ERROR),
            (1, -1, NUM_ERROR),
            )
    )
def test_bitand(op_x, op_y, result):
    assert result == bitand(op_x, op_y)


@pytest.mark.parametrize(
    'op_x, op_y, result', (
            (32, 16, 48),
            (1, 2, 3),
            (-1, 1, NUM_ERROR),
            (1, -1, NUM_ERROR),
            )
    )
def test_bitor(op_x, op_y, result):
    assert result == bitor(op_x, op_y)


@pytest.mark.parametrize(
    'op_x, op_y, result', (
            (16, 15, 31),
            (1, 3, 2),
            (-1, 1, NUM_ERROR),
            (1, -1, NUM_ERROR),
            )
    )
def test_bitxor(op_x, op_y, result):
    assert result == bitxor(op_x, op_y)


@pytest.mark.parametrize(
    'number, pos, result', (
            (6, 1, 12),
            (6, -1, 3),
            (6, 0, 6),
            ('er', 1, VALUE_ERROR),
            (2, 'ze', VALUE_ERROR),
            (-1, 0, NUM_ERROR),
            (2**48, 0, NUM_ERROR),
            (6, 54, NUM_ERROR),
            (6, -54, NUM_ERROR),
            )
    )
def test_bitlshift(number, pos, result):
    assert result == bitlshift(number, pos)


@pytest.mark.parametrize(
    'number, pos, result', (
            (6, 1, 3),
            (6, -1, 12),
            (6, 0, 6),
            ('er', 1, VALUE_ERROR),
            (2, 'ze', VALUE_ERROR),
            (-1, 0, NUM_ERROR),
            (2**48, 0, NUM_ERROR),
            (6, 54, NUM_ERROR),
            (6, -54, NUM_ERROR),
            )
    )
def test_bitrshift(number, pos, result):
    assert result == bitrshift(number, pos)
