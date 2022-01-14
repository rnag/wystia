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


def test_request_count_is_shared(
    mock_from_dict,
    mock_open,
    mock_video_id,
    mock_file_name
):
    """
    Test that the :attr:`_REQUEST_COUNT` class attribute is shared
    between sibling classes that share the same base class.

    """
    r = WistiaDataApi.get_video(mock_video_id)
    assert isinstance(r, Mock)

    r = WistiaUploadApi.upload_file(mock_file_name)
    assert isinstance(r, Mock)

    for cls in WistiaDataApi, WistiaUploadApi:
        assert cls.request_count() == 2, \
            'Wrong request count for class: ' + cls.__name__

    WistiaDataApi.reset_request_count()

    for cls in WistiaDataApi, WistiaUploadApi:
        assert cls.request_count() == 0, \
            'Request count not reset for class: ' + cls.__name__


def test_wistia_error_logs_with_expected_kwargs(mock_log, mock_video_id):
    _ = NoSuchMedia(mock_video_id)

    mock_log.error.assert_called_with(
        '%s: %s',
        'NoSuchMedia',
        'Video (or media) does not exist, or was deleted from Wistia. media_id={}'.format(
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
    vd = Video.from_dict(
        {
            'type': 'Video',
            'duration': 7.2,
            "hashedId": "abc12345",
            "id": 987654321,
            "name": "My Video",
            "description": "Some Description",
            "created": "2020-10-22T16:07:24Z",
            "updated": "2021-12-14T14:09:59Z",
            "progress": 1.0,
            "thumbnail": {
                "url": "https://embed-ssl.wistia.com/deliveries/abc.jpg",
                "width": 200,
                "height": 120
            }
        }
    )

    assert vd.duration == 7.2
    assert vd.status == MediaStatus.NOT_FOUND
    assert not vd.ad_disabled

    log.debug('Video Data object: %s', vd)
    assert repr(vd).startswith(Video.__name__ + '(')

    log.debug('Video Data dictionary result: %s', vd.to_dict())


def test_video_embed_data_methods(mock_video_id):
    video_name = 'my-video.mp4'
    created_ts = 1234567
    duration = 7.2
    my_src_url = "https://embed-ssl.wistia.com/deliveries/abc.bin"

    ved = VideoEmbedData.from_dict({'type': 'Video',
                                    'hashedId': mock_video_id,
                                    'name': video_name,
                                    'createdAt': created_ts,
                                    'duration': duration,
                                    "assets": [
                                        {
                                            "type": "original",
                                            "slug": "original",
                                            "displayName": "Original file",
                                            "bitrate": 2356,
                                            "public": True,
                                            "status": 2,
                                            "progress": 1.0,
                                            "url": my_src_url,
                                            "createdAt": "2021-12-29T16:34:39",
                                            "size": 132180888,
                                            "metadata": {
                                                "servedByMediaApi": 1
                                            },
                                            "width": 1920,
                                            "height": 1080
                                        }
                                    ],
                                    "projectId": 1234567,
                                    "stats": {
                                        "loadCount": 3128,
                                        "playCount": 2011,
                                        "uniqueLoadCount": 2502,
                                        "uniquePlayCount": 2111,
                                        "averageEngagement": 0.1
                                    },
                                    "distilleryUrl": "https://distillery.wistia.com/x",
                                    "accountKey": "wistia-production_3210",
                                    "mediaKey": "wistia-production_112233",
                                    "mediaType": "Video",
                                    "progress": 1.0,
                                    "status": 2,
                                    "branding": False,
                                    "enableCustomerLogo": True,
                                    "seoDescription": "sample description",
                                    "preloadPreference": None,
                                    "flashPlayerUrl": "https://embed-ssl.wistia.com/flash/embed_player_v2.0.swf",
                                    "showAbout": True,
                                    "firstEmbedForAccount": False,
                                    "firstShareForAccount": False,
                                    "keyframeAlign": True,
                                    "useMediaDataHostLogic": True,
                                    "trackingTransmitInterval": 20,
                                    "integrations": {},
                                    "hlsEnabled": True,
                                    "embedOptions": {
                                        "volumeControl": True,
                                        "fullscreenButton": True,
                                        "controlsVisibleOnLoad": True,
                                        "playerColor": "12345",
                                        "bpbTime": False,
                                        "plugin": {
                                            "captionsV1": {
                                                "on": True
                                            }
                                        },
                                        "vulcan": True,
                                        "playsinline": True,
                                    }
                                    })

    assert ved.name == video_name
    assert ved.hashed_id == mock_video_id
    assert ved.duration == duration
    assert ved.created_at.timestamp() == created_ts
    assert '/abc/' in ved.source_url

    log.debug('Video Embed Data object: %r', ved)
    assert repr(ved).startswith(VideoEmbedData.__name__ + '(')


def test_upload_response_methods(mock_video_id):
    video_name = 'my-video.mp4'
    description = 'my desc'
    created_string = '2021-01-02T14:30:59'
    status = 'queued'
    duration = 7.2

    ur = UploadResponse.from_dict(
        {'type': 'Video',
         'id': 2208087,
         'hashed_id': mock_video_id,
         'name': video_name,
         'description': description,
         'created': created_string,
         'updated': created_string,
         'progress': '0',
         'status': status,
         'duration': duration,
         'thumbnail':
             {
                 'url': 'http://embed.wistia.com/deliveries/abc.jpg',
                 'width': 100,
                 'height': 60
             },
         'accountId': 12345
         },
    )

    assert ur.name == video_name
    assert ur.description == description
    assert ur.hashed_id == mock_video_id
    assert ur.duration == duration
    assert ur.status == MediaStatus(status)
    assert ur.created.isoformat() == created_string
    assert not ur.progress  # eq: 0

    log.debug('Video Upload Response object: %r', ur)
    assert repr(ur).startswith(UploadResponse.__name__ + '(')
