#!/usr/bin/env python

"""Tests for `wystia` package."""

import pytest


from wystia import WistiaDataApi
from wystia.errors import NoVideoCaptions


@pytest.fixture
def mock_log(mocker):
    return mocker.patch('wystia.errors.LOG')


def test_wistia_error_logs_with_expected_kwargs(mock_log, mock_video_id):
    _err = NoVideoCaptions(mock_video_id)

    mock_log.error.assert_called_with(
        f'NoVideoCaptions: No captions exist for the Wistia video. '
        f'video_id={mock_video_id}')


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
