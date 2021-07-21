import pytest

from wystia.utils.parse.srt import *


@pytest.mark.parametrize(
    'input,expected',
    [
        ('1:20:32.172', '4832.172'),
        ('01:23:45,5', '5025.005'),
        ('0:07:00:1', '420.001'),
        ('3:01:10:000', '10870.000'),
        ('12:57:42:500', '46662.500'),
    ]
)
def test_total_seconds(input, expected):
    actual = total_seconds(input)
    assert actual == expected, 'Total seconds not as expected'


@pytest.mark.parametrize(
    'input,expected',
    [
        ('1:20:32.172', 4832172),
        ('01:23:45,5', 5025005),
        ('0:07:00:1', 420001),
        ('3:01:10:000', 10870000),
        ('12:57:42:500', 46662500),
    ]
)
def test_total_ms(input, expected):
    actual = total_ms(input)
    assert actual == expected, 'Total seconds not as expected'


@pytest.mark.parametrize(
    'srt_contents,default_end_seconds,expected',
    [
        (
            """
            1
            00:00:01,250 --> 00:07:07,250
            Testing.

            1
            00:07:07,250 --> 00:07:10,160
            Hello world!

            4
            00:07:13,880 --> 00:07:15,950
            Another value.
            """, 0.5, 435.95
        ),
        (
            """
            1
            Invalid srt contents here
            """, 0.5, 0.5
        ),
        (
            """
            1
            00:00:01,250 --> 00:03:00,000
            Testing.

            2
            00:03:00,020 --> 00:03:00,040
            """, 0.5, 180.0
        ),
    ],
    # Attempt to shorten the test case names that are displayed
    # Ref: https://docs.pytest.org/en/stable/example/parametrize.html#different-options-for-test-ids    # noqa: E501
    ids=['Valid SRT', 'Invalid SRT', 'Skip Line with Empty Dialogue']
)
def test_get_srt_duration(srt_contents, default_end_seconds, expected):
    actual = get_srt_duration(srt_contents, default_end_seconds)
    assert actual == expected
