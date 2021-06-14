import math
import os.path
from logging import getLogger
from time import time

import pytest

from wystia import *
from wystia.errors import *
from .conftest import assert_time


log = getLogger(__name__)
log.setLevel('INFO')


def test_call_embed_api(real_video_id):
    """Test calling the Wistia Embed API."""
    start = time()
    ved = WistiaEmbedApi.get_data(real_video_id)
    assert_time(start, is_mock=False)

    start = time()
    num_assets = WistiaEmbedApi.num_assets(media_data=ved)
    # Assert that we don't make the same API call again
    assert_time(start, is_mock=True)

    start = time()
    source_url = WistiaEmbedApi.asset_url(media_data=ved)
    assert_time(start, is_mock=True)

    log.debug('Media Embed data: %s', ved)
    log.info('Num. Assets: %d', num_assets)
    log.info('Source URL: %s', source_url)


def test_get_video(real_video_id):
    """Test retrieving info on a Wistia video."""
    r = WistiaDataApi.get_video(real_video_id)
    assert r
    assert r.get('name')


def test_get_videos_for_project(real_project_id):
    """Test retrieving a list of videos for a Wistia project."""
    r = WistiaDataApi.get_videos_for_project(real_project_id)
    assert len(r) >= 1

    expected_num_calls = math.ceil(len(r) / 100)
    log.info('Expected num API calls: %d', expected_num_calls)

    actual_num_calls = WistiaDataApi.request_count()
    assert actual_num_calls == expected_num_calls


def test_list_project(real_project_id):
    """Test retrieving a list of videos for a Wistia project."""
    r = WistiaDataApi.list_project(real_project_id)
    assert len(r) >= 1

    expected_num_calls = math.ceil(len(r) / 500)
    log.info('Expected num API calls: %d', expected_num_calls)

    actual_num_calls = WistiaDataApi.request_count()
    assert actual_num_calls == expected_num_calls


def test_get_video_when_no_such_video(mock_video_id):
    """Test case for `get_video` using an invalid video id"""
    with pytest.raises(NoSuchVideo):
        _ = WistiaDataApi.get_video(mock_video_id)


def test_list_project_when_no_such_project(mock_project_id):
    """Test case for `list_project` using an invalid video id"""
    with pytest.raises(NoSuchProject):
        _ = WistiaDataApi.list_project(mock_project_id)


def test_upload_to_wistia_when_no_such_file(mock_file_name):
    """Test case for `upload_file` using an invalid file path"""
    with pytest.raises(FileNotFoundError):
        _ = WistiaUploadApi.upload_file(mock_file_name)


@pytest.mark.long
def test_upload_file_to_wistia(real_file_path):
    """Test case for `upload_file` to confirm intended operation"""
    r = WistiaUploadApi.upload_file(real_file_path)
    expected_name = os.path.basename(real_file_path)
    log.debug('Upload File response: %s', r)

    assert r.created
    assert r.name == expected_name
    assert not r.description
    assert r.hashed_id


@pytest.mark.long
def test_upload_link_to_wistia(real_presigned_url):
    """Test case for `upload_link` to confirm intended operation"""
    r = WistiaUploadApi.upload_link(real_presigned_url,
                                    title='My Video Name',
                                    description='My Description')
    log.debug('Upload Link response: %s', r)

    assert r.created
    assert r.name
    assert r.description
    assert r.hashed_id
