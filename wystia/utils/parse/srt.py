__all__ = ['total_seconds',
           'total_ms',
           'get_srt_duration']

from functools import reduce


def total_seconds(ts: str) -> str:
    """
    Converts a timestamp containing hours, minutes, seconds, and milliseconds
    (for example, in the "HH:mm:ss,SSS" format) to a string representing the
    total seconds, along with the millisecond part.

    For example, a string like "1:20:32,5" will be returned as "4832.005"

    Supports parsing the following input formats:
        - (H)H:mm:ss,SSS
        - (H)H:mm:ss.SSS
        - (H)H:mm:ss:SSS

    A modified version of the following (great) solution:
    https://stackoverflow.com/a/57610198

    """
    seconds, milliseconds = divmod(total_ms(ts), 1000)

    return f'{seconds}.{milliseconds:0>3}'


def total_ms(ts: str) -> int:
    """
    Converts a timestamp containing hours, minutes, seconds, and milliseconds
    (for example, in the "HH:mm:ss,SSS" format) to an integer value
    representing the total milliseconds.

    For example, a string like "1:20:32,5" will be returned as 4832005

    Supports parsing the following input formats:
        - (H)H:mm:ss,SSS
        - (H)H:mm:ss.SSS
        - (H)H:mm:ss:SSS

    A modified version of the following (great) solution:
    https://stackoverflow.com/a/57610198

    """
    try:
        h_m_s, milliseconds = ts.replace('.', ',').rsplit(',', 1)
    except ValueError:
        h_m_s, milliseconds = ts.rsplit(':', 1)

    seconds = reduce(lambda sum, d: sum * 60 + int(d), h_m_s.split(':'), 0)

    return (seconds * 1000) + int(milliseconds)


def get_srt_duration(srt_contents: str, default_end_seconds=0.0) -> float:
    """
    Gets the total duration (based on end timestamp) of an SRT file
    """
    caption_text = srt_contents.split('\n')
    captions_end_seconds = default_end_seconds
    following_line = ''

    for line in reversed(caption_text):
        if '-->' in line:
            # Fix: sometimes the durations will be listed for
            # a blank line (no dialogue)
            if not following_line.strip():
                continue

            end = line.replace(' ', '').rsplit('-->', 1)[-1]
            captions_end_seconds = float(total_seconds(end))
            break

        following_line = line

    return captions_end_seconds
