"""
Common test fixtures and utilities, for unit tests
"""
import pytest

from wystia import WistiaDataApi


@pytest.fixture
def mock_log(mocker):
    return mocker.patch('wystia.errors.LOG')


@pytest.fixture(scope='session', autouse=True)
def global_setup():
    """Setup that runs before the unit test suite."""
    WistiaDataApi.configure(None)
    WistiaDataApi.reset_request_count()


@pytest.fixture(autouse=True)
def mock_request(mocker):
    """
    Mock the underlying :meth:`request.Session.request` method
    so that any HTTP requests are mocked.
    """
    mocker.patch('wystia.api_base.SessionWithRetry.request')


@pytest.fixture
def mock_open(mocker):
    mocker.patch('wystia.api_upload.open', return_value=b'')
