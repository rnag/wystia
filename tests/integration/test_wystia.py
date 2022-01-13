"""
Integration Tests for the `wystia` package.
"""
import math
import os.path
from json import dumps
from logging import getLogger
from textwrap import dedent
from time import time

import pytest

from wystia import *
from wystia.errors import *
from wystia.models import *
from .conftest import assert_time


log = getLogger(__name__)
log.setLevel('INFO')


def test_call_embed_api(real_video_id):
    """Test calling the Wistia Embed API."""
    start = time()
    ved = WistiaEmbedApi.get_data(real_video_id)
    assert_time(start, is_mock=False)

    log.info('Video Embed object: %s', ved)

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


def test_list_all_projects():
    r = WistiaDataApi.list_all_projects(SortBy.NAME, SortDir.DESC)
    assert r

    project_ids = [proj['hashedId'] for proj in r]

    log.info('Num. projects: %d', len(project_ids))
    log.debug('Project IDs: %s', project_ids)
    log.info('Num. requests: %d', WistiaDataApi.request_count())


def test_list_project(real_project_id):
    """Test retrieving a list of videos for a Wistia project."""
    r = WistiaDataApi.list_project(real_project_id)
    log.info('Num. videos: %d', len(r))
    assert len(r) >= 1

    expected_num_calls = math.ceil(len(r) / 500)
    log.info('Expected num API calls: %d', expected_num_calls)

    actual_num_calls = WistiaDataApi.request_count()
    assert actual_num_calls == expected_num_calls


def test_list_project_when_no_such_project(mock_project_id):
    """Test case for `list_project` using an invalid video id"""
    with pytest.raises(NoSuchProject):
        _ = WistiaDataApi.list_project(mock_project_id)


@pytest.mark.mutative
def test_create_project():
    proj_data = WistiaDataApi.create_project(
        'My Test Proj', public_upload=True, public_download=True)
    log.info('Response: %s', proj_data)


@pytest.mark.mutative
def test_create_and_update_project():
    original_name = 'My Test Proj'
    proj_data = WistiaDataApi.create_project(
        original_name, public_upload=True, public_download=True)
    log.info('Response: %s', proj_data)

    assert proj_data['name'] == original_name
    assert proj_data['anonymousCanUpload']
    assert proj_data['anonymousCanDownload']
    assert proj_data['public']

    project_id = proj_data['hashedId']
    new_name = 'My Test Project'

    proj_data = WistiaDataApi.update_project(
        project_id, new_name, public_upload=True, public_download=False)
    log.info('Response: %s', proj_data)

    assert proj_data['name'] == new_name
    assert proj_data['anonymousCanUpload']
    assert not proj_data['anonymousCanDownload']
    assert proj_data['public']


def test_delete_project_when_no_such_project(mock_project_id):
    """Test case for `delete_project` using an invalid project id"""
    success = WistiaDataApi.delete_project(mock_project_id)
    log.info('Success: %s', success)
    assert not success


@pytest.mark.mutative
def test_copy_project(real_project_id):
    r = WistiaDataApi.copy_project(real_project_id)
    log.info('Response: %s', r)
    assert r['hashedId'] != real_project_id


def test_list_videos_for_project(real_project_id):
    """Test retrieving a list of videos for a Wistia project."""
    r = WistiaDataApi.list_videos(real_project_id)
    assert len(r) >= 1
    log.info('Num. videos: %d', len(r))

    expected_num_calls = math.ceil(len(r) / 100)
    log.info('Expected num API calls: %d', expected_num_calls)

    actual_num_calls = WistiaDataApi.request_count()
    assert actual_num_calls == expected_num_calls


def test_get_video(real_video_id):
    """Test retrieving info on a Wistia video."""
    r = WistiaDataApi.get_video(real_video_id)
    assert r
    assert r.get('name')

    vd = VideoData(**r)
    # If the video has captions, that won't be included in the `Medias#show`
    # response by default, so we'll need a separate API call as below.
    # vd.process_captions(
    #     WistiaDataApi.list_captions(real_video_id))
    log.info('Video Data object: %r', vd)


def test_get_video_when_no_such_video(mock_video_id):
    """Test case for `get_video` using an invalid video id"""
    with pytest.raises(NoSuchVideo):
        _ = WistiaDataApi.get_video(mock_video_id)


@pytest.mark.mutative
def test_update_video(real_video_id):
    """Test updating attributes on a Wistia video."""
    new_title, new_desc = 'My Title', 'My Desc'
    r = WistiaDataApi.update_video(real_video_id, new_title, new_desc)
    log.info('Response: %s', dumps(r))

    assert r
    assert r['hashed_id'] == real_video_id
    assert r['name'] == new_title
    assert new_desc in r['description']


def test_delete_video_when_no_such_video(mock_video_id):
    """Test case for `delete_video` using an invalid video id"""
    success = WistiaDataApi.delete_video(mock_video_id)
    assert not success


@pytest.mark.mutative
def test_copy_video(real_video_id):
    """Test copying a Wistia video."""
    r = WistiaDataApi.copy_video(real_video_id)
    log.info('Response: %s', dumps(r))

    assert r
    assert r.get('name')


def test_get_stats_for_video(real_video_id):
    """Test retrieving info on a Wistia video."""
    stats = WistiaDataApi.get_stats_for_video(real_video_id)
    log.info('Response: %s', dumps(stats))

    assert stats['name']
    assert stats['hashed_id'] == real_video_id


def test_get_customizations_when_no_such_video(mock_video_id):
    """Test case for `get_customizations` using an invalid video id"""
    with pytest.raises(NoSuchVideo):
        _ = WistiaDataApi.get_customizations(mock_video_id)


def test_get_customizations(real_video_id):
    customizations = WistiaDataApi.get_customizations(real_video_id)
    log.info('Response: %s', dumps(customizations))
    assert isinstance(customizations, dict)


def test_create_customizations_when_no_such_video(
        mock_video_id, customizations_to_set):
    """Test case for `create_customizations` using an invalid video id"""
    with pytest.raises(NoSuchVideo):
        _ = WistiaDataApi.create_customizations(
            mock_video_id, customizations_to_set)


@pytest.mark.mutative
def test_create_customizations(real_video_id, customizations_to_set):
    customizations = WistiaDataApi.create_customizations(
        real_video_id, customizations_to_set)
    log.info('Response: %s', dumps(customizations))
    assert isinstance(customizations, dict)


@pytest.mark.mutative
def test_update_customizations(real_video_id, customizations_to_update):
    customizations = WistiaDataApi.update_customizations(
        real_video_id, customizations_to_update)
    log.info('Response: %s', dumps(customizations))
    assert isinstance(customizations, dict)


def test_delete_customizations_when_no_such_video(mock_video_id):
    """Test case for `delete_customizations` using an invalid video id"""
    success = WistiaDataApi.delete_customizations(mock_video_id)
    assert not success


@pytest.mark.mutative
def test_delete_customizations(real_video_id):
    success = WistiaDataApi.delete_customizations(real_video_id)
    assert success


def test_list_captions(real_video_id):
    """
    Test case for retrieving all the captions for a video.
    """
    captions = WistiaDataApi.list_captions(real_video_id)
    log.info('Response: %s', dumps(captions))
    assert isinstance(captions, list)


def test_list_captions_when_no_such_video(mock_video_id):
    """Test case for `list_captions` using an invalid video id"""
    with pytest.raises(NoSuchVideo):
        _ = WistiaDataApi.list_captions(mock_video_id)


def test_get_captions(real_video_id):
    """
    Test case for retrieving an individual captions file for a video.
    """
    customizations = WistiaDataApi.get_captions(
        real_video_id, LanguageCode.SPANISH)
    log.info('Response: %s', dumps(customizations))
    assert isinstance(customizations, dict)


@pytest.mark.mutative
def test_create_captions(real_video_id, real_captions_path):
    """
    Test case for creating captions for a video.
    """
    WistiaDataApi.create_captions(
        real_video_id, LanguageCode.SPANISH, srt_file=real_captions_path)


@pytest.mark.mutative
def test_update_captions(real_video_id, real_captions_path):
    """
    Test case for updating captions for a video.
    """
    with open(real_captions_path) as in_file:
        contents = in_file.read()

    contents_to_append = dedent(
        """\
        3
        00:00:04,000 --> 00:00:07,250
        [END TEST]
        """)

    contents = contents + '\n' + contents_to_append

    WistiaDataApi.update_captions(
        real_video_id, LanguageCode.SPANISH, contents)

    # Confirm that captions for the language code have been updated
    caption_text = WistiaDataApi.get_captions(
        real_video_id, LanguageCode.SPANISH)['text']

    assert caption_text.endswith(contents_to_append)


def test_delete_captions_when_no_such_video(mock_video_id):
    """Test case for `delete_captions` using an invalid video id"""
    success = WistiaDataApi.delete_captions(
        mock_video_id, LanguageCode.ENGLISH)
    log.info('Success: %s', success)
    assert not success


@pytest.mark.mutative
def test_delete_captions(real_video_id, real_captions_path):
    """
    Test case for deleting captions for a video.
    """
    success = WistiaDataApi.delete_captions(
        real_video_id, LanguageCode.SPANISH)
    assert success


def test_order_captions_when_no_such_video(mock_video_id):
    """Test case for `order_captions` using an invalid video id"""
    with pytest.raises(NoSuchVideo):
        _ = WistiaDataApi.order_captions(
            mock_video_id)


def test_upload_to_wistia_when_no_such_file(mock_file_name):
    """Test case for `upload_file` using an invalid file path"""
    with pytest.raises(FileNotFoundError):
        _ = WistiaUploadApi.upload_file(mock_file_name)


@pytest.mark.long
def test_upload_file_to_wistia(real_video_path):
    """Test case for `upload_file` to confirm intended operation"""
    r = WistiaUploadApi.upload_file(real_video_path)
    expected_name = os.path.basename(real_video_path)
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


def test_project_details(real_project_id):
    # Confirm we make a live API call to retrieve a list of *all* projects
    assert WistiaDataApi.request_count() == 0
    projects = WistiaDataApi.list_all_projects()
    assert WistiaDataApi.request_count() >= 1

    WistiaDataApi.reset_request_count()

    r = WistiaHelper.project_details(real_project_id, projects)
    # Assert no new API call is made
    assert WistiaDataApi.request_count() == 0

    log.info('Response: %s', dumps(r))
