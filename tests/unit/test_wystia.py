"""
Unit Tests for the `wystia` package.
"""
from unittest.mock import Mock

import pytest

from wystia import *
from wystia.api_base import _BaseWistiaApi
from wystia.errors import *
from wystia.models import *


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
            f'Wrong request count for class: {cls.__name__}'

    WistiaDataApi.reset_request_count()

    for cls in WistiaDataApi, WistiaUploadApi:
        assert cls.request_count() == 0, \
            f'Request count not reset for class: {cls.__name__}'


def test_wistia_error_logs_with_expected_kwargs(mock_log, mock_video_id):
    _ = NoSuchVideo(mock_video_id)

    mock_log.error.assert_called_with(
        f'NoSuchVideo: Video does not exist, or was deleted from Wistia. '
        f'video_id={mock_video_id}')


def test_create_captions_when_no_content(mock_video_id):
    """Test case for `create_captions` when captions are not provided."""
    with pytest.raises(ContentIsEmpty):
        _ = WistiaDataApi.create_captions(
            mock_video_id)


def test_update_captions_when_no_content(mock_video_id):
    """Test case for `update_captions` when captions are not provided."""
    with pytest.raises(ContentIsEmpty):
        _ = WistiaDataApi.update_captions(
            mock_video_id, LanguageCode.ENGLISH)


def test_is_archived_video():
    assert WistiaHelper.is_archived_video(
        'My Video Title [Archived on August 13, 2015]')
