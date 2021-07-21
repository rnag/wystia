from json import loads

from wystia.utils.response import format_error


def test_format_error():
    msg, code, status = 'Test message', 'MyCode', '402'

    r = format_error(msg, code, status)

    assert 'body' in r
    assert 'statusCode' in r

    assert r['statusCode'] == int(status)

    body_dict = loads(r['body'])

    assert body_dict.get('success') is False
    assert 'error' in body_dict
