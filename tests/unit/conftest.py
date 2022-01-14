"""
Common test fixtures and utilities, for unit tests
"""
import pytest
from pytest_mock import MockerFixture

from wystia import WistiaDataApi


@pytest.fixture
def mock_log(mocker: MockerFixture):
    return mocker.patch('wystia.errors.LOG')


@pytest.fixture(scope='session', autouse=True)
def global_setup():
    """Setup that runs before the unit test suite."""
    WistiaDataApi.configure(None)
    WistiaDataApi.reset_request_count()


@pytest.fixture(autouse=True)
def mock_request(mocker: MockerFixture):
    """
    Mock the underlying :meth:`request.Session.request` method
    so that any HTTP requests are mocked.
    """
    mocker.patch('wystia.api_base.SessionWithRetry.request')


@pytest.fixture
def mock_from_dict(mocker: MockerFixture):
    """
    Mock the underlying :meth:`JSONSerializable.from_dict` method
    so that the de-serialization process is mocked.
    """
    mocker.patch('dataclass_wizard.JSONSerializable.from_dict')


@pytest.fixture
def mock_open(mocker: MockerFixture):
    mocker.patch('wystia.api_upload.open', return_value=b'')
