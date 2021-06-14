from datetime import timedelta
from logging import getLogger
from time import time

import pytest

from wystia import *


# TODO Replace
WISTIA_API_TOKEN = 'REPLACE-ME'

# TODO Update below values as needed
VIDEO_ID = 'abc1234567'
PROJECT_ID = 'xyz7654321'
FILE_PATH = 'testdata/sample-file.mp4'
PRESIGNED_URL = 'https://my-bucket.s3.amazonaws.com/path/to/file.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256' \
                '&X-Amz-Credential=TODO...&X-Amz-Signature=TODO'


# Turn down logging for the ``urllib3`` library
getLogger('urllib3').setLevel('INFO')


@pytest.fixture(autouse=True, scope='session')
def configure_wistia_api():
    for cls in WistiaDataApi, WistiaUploadApi:
        cls.configure(WISTIA_API_TOKEN)


@pytest.fixture(scope='session')
def real_presigned_url():
    return PRESIGNED_URL


@pytest.fixture(scope='session')
def real_file_path():
    return FILE_PATH


@pytest.fixture(scope='session')
def real_project_id():
    return PROJECT_ID


@pytest.fixture(scope='session')
def real_video_id():
    return VIDEO_ID


def assert_time(start: float, is_mock=False, min_live_call_sec=0.005):
    """
    Assert we have made a live API call (if `is_mock` if false), or a mock call
    otherwise.
    """
    elapsed = timedelta(seconds=time()-start)
    if is_mock:
        assert elapsed.total_seconds() < min_live_call_sec, \
            'Made a live API call, but expected it to be mocked'
    else:
        # Assert it's a live call (takes more than 5ms)
        assert elapsed.total_seconds() > min_live_call_sec, \
            'Made a mock call, but expected it to be a live API call'
