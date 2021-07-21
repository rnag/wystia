"""
Tests for the module `types`
"""
from datetime import datetime

import pytest

from wystia.utils.parse.types import *
from .conftest import does_not_raise


@pytest.mark.parametrize(
    'input,default,expected',
    [
        [None, False, False],
        ['tRuE', False, True],
        [True, False, True],
        [False, True, False],
        ['Nope', True, False],
    ]
)
def test_as_bool(input, default, expected):
    actual = as_bool(input, default)
    assert actual == expected


@pytest.mark.parametrize(
    'input,expected,default,raise_,expectation',
    [
        [None, 0, 0, True, does_not_raise()],
        [1, 1, 0, True, does_not_raise()],
        ['3', 3, 1, True, does_not_raise()],
        ['a', 3, 3, False, does_not_raise()],
        ['a', None, 3, True, pytest.raises(ValueError)],
        [172.75, 172, 3, True, does_not_raise()],
    ]
)
def test_as_int(input, expected, default, raise_, expectation):
    with expectation:
        actual = as_int(input, default, raise_)
        assert actual == expected


@pytest.mark.parametrize(
    'input,expected,default,raise_,expectation',
    [
        [None, '0', '0', True, does_not_raise()],
        [1, '1', 0, True, does_not_raise()],
        ['', 'hello world', 'hello world', True, does_not_raise()],
        ['testing', 'testing', 'hello world', True, does_not_raise()],
    ]
)
def test_as_str(input, expected, default, raise_, expectation):
    with expectation:
        actual = as_str(input, default, raise_)
        assert actual == expected


@pytest.mark.parametrize(
    'input,sep,expected',
    [
        [None, '|', []],
        ['True', '|', ['True']],
        ['hello,world', ',', ['hello', 'world']],
        ['hello|world', ',', ['hello|world']],
        ['hello|world', '|', ['hello', 'world']],
        ['this is a test', ' ', ['this', 'is', 'a', 'test']],
        [['this is a test'], ' ', ['this is a test']],
    ]
)
def test_as_list(input, sep, expected):
    actual = as_list(input, sep)
    assert actual == expected


@pytest.mark.parametrize(
    'input,expected,default,raise_,expectation',
    [
        [None, None, None, True, does_not_raise()],
        ['', datetime.min, datetime.min, True, does_not_raise()],
        [12345, datetime.fromtimestamp(12345), None, True, does_not_raise()],
        [datetime(2001, 11, 22, 23, 59, 1), datetime(2001, 11, 22, 23, 59, 1),
         None, True, does_not_raise()],
        ['2021-01-02T03:00:01', datetime(2021, 1, 2, 3, 0, 1),
         None, True, does_not_raise()],
        ['abc', 'testing', None, True, pytest.raises(ValueError)],
        ['abc', 'testing', 'testing', False, does_not_raise()],
    ]
)
def test_as_datetime(input, expected, default, raise_, expectation):
    with expectation:
        actual = as_datetime(input, default, raise_)
        assert actual == expected
