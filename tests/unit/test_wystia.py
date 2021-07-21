"""
Unit Tests for the `wystia` package.
"""
import logging
from unittest.mock import Mock

import pytest

from wystia import *
from wystia.api_base import _BaseWistiaApi
from wystia.errors import *
from wystia.models import *
from conftest import PY36

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def test_configure_works_as_expected(mock_open, mock_api_token):
    """
    Test that the :attr:`_API_TOKEN` class attribute is shared
    between sibling classes that share the same base class.

    """
    for cls in _BaseWistiaApi, WistiaDataApi, WistiaUploadApi:
        assert cls._API_TOKEN is None

    WistiaDataApi.configure(mock_api_token)

    for cls in _BaseWistiaApi, WistiaDataApi, WistiaUploadApi:
        assert cls._API_TOKEN is not None
        assert cls._API_TOKEN is mock_api_token

    WistiaDataApi.configure(None)

    for cls in _BaseWistiaApi, WistiaDataApi, WistiaUploadApi:
        assert cls._API_TOKEN is None


def test_request_count_is_shared(mock_open, mock_video_id, mock_file_name):
    """
    Test that the :attr:`_REQUEST_COUNT` class attribute is shared
    between sibling classes that share the same base class.

    """
    r = WistiaDataApi.get_video(mock_video_id)
    assert isinstance(r, Mock)

    r = WistiaUploadApi.upload_file(mock_file_name)
    assert isinstance(r, UploadResponse)

    for cls in WistiaDataApi, WistiaUploadApi:
        assert cls.request_count() == 2, \
            'Wrong request count for class: ' + cls.__name__

    WistiaDataApi.reset_request_count()

    for cls in WistiaDataApi, WistiaUploadApi:
        assert cls.request_count() == 0, \
            'Request count not reset for class: ' + cls.__name__


def test_wistia_error_logs_with_expected_kwargs(mock_log, mock_video_id):
    _ = NoSuchVideo(mock_video_id)

    mock_log.error.assert_called_with(
        '%s: %s',
        'NoSuchVideo',
        'Video does not exist, or was deleted from Wistia. video_id={}'.format(
            mock_video_id))


def test_create_captions_when_no_content(mock_video_id, mock_log):
    """Test case for `create_captions` when captions are not provided."""
    with pytest.raises(ContentIsEmpty):
        _ = WistiaDataApi.create_captions(
            mock_video_id)

    if PY36:
        mock_log.error.assert_called_once()


def test_update_captions_when_no_content(mock_video_id, mock_log):
    """Test case for `update_captions` when captions are not provided."""
    with pytest.raises(ContentIsEmpty):
        _ = WistiaDataApi.update_captions(
            mock_video_id, LanguageCode.ENGLISH)

    if PY36:
        mock_log.error.assert_called_once()


def test_is_archived_video():
    assert WistiaHelper.is_archived_video(
        'My Video Title [Archived on August 13, 2015]')


def test_video_data_methods():
    vd = VideoData(**{'type': 'Video', 'duration': 7.2})

    assert vd.duration == 7.2
    assert vd.status == VideoStatus.NOT_FOUND
    assert vd.ad_disabled is False

    log.debug('Video Data object: %r', vd)
    assert repr(vd).startswith(VideoData.__name__ + '(')

    log.debug('Video Data dictionary result: %s', vd.dict())


def test_video_embed_data_methods(mock_video_id):
    video_name = 'my-video.mp4'
    created_ts = 1234567
    duration = 7.2

    ved = VideoEmbedData(**{'type': 'Video',
                            'hashedId': mock_video_id,
                            'name': video_name,
                            'createdAt': created_ts,
                            'duration': duration})

    assert ved.name == video_name
    assert ved.hashed_id == mock_video_id
    assert ved.duration == duration
    assert ved.created.timestamp() == created_ts
    assert not ved.source_url

    log.debug('Video Embed Data object: %r', ved)
    assert repr(ved).startswith(VideoEmbedData.__name__ + '(')

    if not PY36:
        log.debug('Video Embed Data property values: %s',
                  ved.get_property_values())
        assert 'ad_enabled' in ved.get_property_values(
            check_value=lambda x: True)


def test_upload_response_methods(mock_video_id):
    video_name = 'my-video.mp4'
    created_string = '2021-01-02T14:30:59'
    status = 'queued'
    duration = 7.2

    ur = UploadResponse(**{'type': 'Video',
                           'hashed_id': mock_video_id,
                           'name': video_name,
                           'created': created_string,
                           'status': status,
                           'duration': duration})

    assert ur.name == video_name
    assert ur.hashed_id == mock_video_id
    assert ur.duration == duration
    assert ur.status == VideoStatus(status)
    assert ur.created.isoformat() == created_string
    assert not ur.progress

    log.debug('Video Upload Response object: %r', ur)
    assert repr(ur).startswith(UploadResponse.__name__ + '(')

    if not PY36:
        log.debug('Video Upload Response property values: %s',
                  ur.get_property_values())
        assert 'thumbnail' in ur.get_property_values(
            check_value=lambda x: True)
