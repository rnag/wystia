"""
Common test fixtures and utilities
"""
import sys
from typing import Union, List

import pytest

from wystia.utils.parse import as_list


# Check if system Python version is 3.6 or greater
PY36 = sys.version_info[0:2] >= (3, 6)


@pytest.fixture(scope='session')
def mock_video_id():
    """Returns a dummy hashed video ID for testing purposes."""
    return 'abc-01234567'


@pytest.fixture(scope='session')
def mock_project_id():
    """Returns a dummy hashed project ID for testing purposes."""
    return 'xyz-76543210'


@pytest.fixture(scope='session')
def mock_api_token():
    """Returns a dummy Wistia API token for testing purposes."""
    return 'abc-xyz-123456789'


@pytest.fixture(scope='session')
def mock_file_name():
    """Returns a dummy file path for testing purposes."""
    return 'abc-1234567.mp4'


class TestsWithMarkSkipper:
    """
    Util to skip tests with mark, unless cli option provided.
    """
    def __init__(self, test_marks: Union[str, List[str]],
                 cli_option_name: str,
                 cli_option_help: str):

        self.test_marks = as_list(test_marks)
        self.cli_option_name = cli_option_name
        self.cli_option_help = cli_option_help

    def pytest_addoption_hook(self, parser):
        parser.addoption(
            self.cli_option_name,
            action='store_true',
            default=False,
            help=self.cli_option_help,
        )

    def pytest_runtest_setup(self, item):
        if any(mark in item.keywords for mark in self.test_marks) \
                and not item.config.getoption(self.cli_option_name):
            self._skip_test()

    def _skip_test(self):
        reason = 'need {} option to run this test'.format(self.cli_option_name)
        pytest.skip(reason)


mark_skipper = TestsWithMarkSkipper(
    test_marks=['mutative', 'long'],
    cli_option_name="--run-all",
    cli_option_help="run all test cases, including any potentially "
                    "destructive tests",
)


pytest_addoption = mark_skipper.pytest_addoption_hook
pytest_runtest_setup = mark_skipper.pytest_runtest_setup
