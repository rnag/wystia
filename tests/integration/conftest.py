"""
Common test fixtures and utilities, for integration tests
"""
from datetime import timedelta
from logging import getLogger
from time import time

import pytest

from wystia import *


# TODO Replace
WISTIA_API_TOKEN = 'REPLACE-ME'   # noqa: E501

# TODO Update below values as needed
VIDEO_ID = 'abc1234567'
PROJECT_ID = 'xyz7654321'
PRESIGNED_URL = 'https://my-bucket.s3.amazonaws.com/path/to/file.mp4?' \
                'X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=TODO...' \
                '&X-Amz-Signature=TODO'

VIDEO_PATH = 'testdata/sample-video.mp4'
CAPTIONS_FILE_PATH = 'testdata/sample-captions.srt'

# Turn down logging for the ``urllib3`` library
getLogger('urllib3').setLevel('INFO')


@pytest.fixture(autouse=True, scope='session')
def configure_wistia_api():
    WistiaDataApi.configure(WISTIA_API_TOKEN)


@pytest.fixture(autouse=True)
def reset_request_count():
    """Resets the request count after each test case."""
    WistiaDataApi.reset_request_count()


@pytest.fixture(scope='session')
def real_presigned_url():
    return PRESIGNED_URL


@pytest.fixture(scope='session')
def real_video_path():
    return VIDEO_PATH


@pytest.fixture(scope='session')
def real_captions_path():
    return CAPTIONS_FILE_PATH


@pytest.fixture(scope='session')
def real_project_id():
    return PROJECT_ID


@pytest.fixture(scope='session')
def real_video_id():
    return VIDEO_ID


@pytest.fixture(scope='session')
def customizations_to_set():
    """
    Return customizations data to set for a Wistia video.

    https://wistia.com/support/developers/data-api#example-json-response
    """
    return {'playerColor': '#ffffcc'}


@pytest.fixture(scope='session')
def customizations_to_update():
    """
    Return customizations data to update for a Wistia video.
    """
    return {'playerColor': '160214'}


def assert_time(start: float, is_mock=False, min_live_call_sec=0.005):
    """
    Assert we have made a live API call (if `is_mock` if false), or a mock call
    otherwise.
    """
    elapsed = timedelta(seconds=time() - start)
    if is_mock:
        assert elapsed.total_seconds() < min_live_call_sec, \
            'Made a live API call, but expected it to be mocked'
    else:
        # Assert it's a live call (takes more than 5ms)
        assert elapsed.total_seconds() > min_live_call_sec, \
            'Made a mock call, but expected it to be a live API call'
