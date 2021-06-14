""""
Base API Classes
"""
import functools
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union

from requests import Session, RequestException

from .constants import WISTIA_API_TOKEN
from .models.requests import SessionWithRetry, prefix_url_session


class _BaseApi(ABC):
    """
    Abstract base class for sending requests to an :attr:`API_ENDPOINT`
    """

    # Base API endpoint
    API_ENDPOINT: str = NotImplemented

    # Requests Session object, can be used if session caching is needed
    _SESSION: Optional[Session] = None

    @classmethod
    def get(cls, api, **kwargs):
        """Shortcut to make a ``GET`` request via the API"""
        return cls.request('GET', api, **kwargs)

    @classmethod
    def request(cls, method, api, **kwargs) -> Union[Dict, List]:
        """
        Makes an API request using an HTTP `method`.

        Returns the response data as a Python object, after validating that
        the request was a success.

        """
        # Make the API request
        r = cls._get_session().request(method, api, **kwargs)
        # Check if the request was a success
        r.raise_for_status()
        # Return the JSON response
        return r.json()

    @classmethod
    def session(cls):
        """Shortcut to retrieve the :class:`requests.Session` object"""
        return cls._get_session()

    @classmethod
    @abstractmethod
    def _get_session(cls) -> Session:
        """
        Return the :class:`requests.Session` object for an API request.
        """

    @staticmethod
    def _has_resp_status(e: RequestException, status: int) -> bool:
        """Check if the response in an error has a specified status code"""
        return e.response is not None and e.response.status_code == status


class _BaseWistiaApi(_BaseApi):
    """
    Base class for sending requests to the Wistia API.

    Note: any sub-classes will still need to override the :attr:`API_ENDPOINT`

    """
    # Default to the value specified via the environment
    _API_TOKEN = WISTIA_API_TOKEN

    # Maximum results per page; also documented in the link below
    #   https://wistia.com/support/developers/data-api#paging
    _MAX_PER_PAGE = 100

    # This attribute keeps a running count of the total API requests made.
    #
    # The current rate limit for the Wistia API is 600 requests / min as
    # documented in the link below. Use `request_count()` to retrieve the
    # number of API requests made, and any custom application logic to sleep
    # when the request limit is reached. Don't forget to reset the running
    # total via `reset_request_count()`.
    #   https://wistia.com/support/developers/data-api#rate
    _REQUEST_COUNT = 0

    @classmethod
    def configure(cls, api_token):
        """Sets the API token used to authenticate requests to the Wistia API."""
        cls._API_TOKEN = api_token

    @classmethod
    def request_count(cls):
        """Return the running count of API requests to the Wistia API."""
        return cls._REQUEST_COUNT

    @classmethod
    def reset_request_count(cls):
        """Reset (clear) the running count of API requests to the Wistia API."""
        cls._REQUEST_COUNT = 0

    @classmethod
    def session(cls, additional_status_force_list: Optional[List[int]] = None) -> Session:
        """
        Return a new :class:`requests.Session` object.

        `additional_status_force_list` is an optional list of additional HTTP
        response status codes to retry on, in additional to the
        `DEFAULT_STATUS_FORCE_LIST`.

        """
        return cls._get_session(additional_status_force_list)

    @classmethod
    def get_page(cls, url, data_key=None, max_per_page=_MAX_PER_PAGE, **kwargs):
        """
        Makes an HTTP GET request to the Wistia API. If we get back
        ``max_per_page`` results or more, this indicates there are more results
        available, so we will pass the ``page`` parameter to retrieve all the
        results for an API request.

        Used primarily for `list` methods in the Wistia API, as described below:
          https://wistia.com/support/developers/data-api#paging_and_sorting_responses

        :raises HTTPError: Raised for any 4xx or 5xx errors.
        :raises ConnectionError: Raised for any request timeouts or connection errors.
        """
        data = []
        page = 1

        page_data = cls._request_page(url, **kwargs)
        if data_key:
            page_data = page_data[data_key]
        data.extend(page_data)

        while len(page_data) >= max_per_page:
            page += 1
            page_data = cls._request_page(url, page, **kwargs)
            if data_key:
                page_data = page_data[data_key]
            data.extend(page_data)

        return data

    @classmethod
    def _increment_count_decorator(cls, func):
        """
        Returns a decorator which wraps a function `func` to increment the
        :attr:`_REQUEST_COUNT` attribute on each function call.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cls._REQUEST_COUNT += 1
            return func(*args, **kwargs)

        return wrapper

    @classmethod
    def _get_session(cls, additional_status_force_list=None) -> Session:
        """
        Return the :class:`requests.Session` object for an API request.
        """
        session = cls._create_session(additional_status_force_list)
        session.request = cls._increment_count_decorator(session.request)

        return session

    @classmethod
    def _create_session(cls, additional_status_force_list=None):
        """
        Create and return a new :class:`request.Session` object, using `HTTP
        Basic` authentication as described here:
          https://wistia.com/support/developers/data-api#authentication

        In this implementation, the Session object automatically retries
        for common server-side error codes, and prefixes the url in all API
        requests with the :attr:`API_ENDPOINT` attribute.
        """
        session = SessionWithRetry(
            auth=('api', cls._API_TOKEN),
            additional_status_force_list=additional_status_force_list)

        return prefix_url_session(cls.API_ENDPOINT, session)

    @classmethod
    def _request_page(cls, url, page=None, **kwargs) -> Dict[str, Any]:
        """
        Requests a single page from the the Wistia API.
        """
        params = (kwargs.pop('params', None) or {}).copy()
        if page:
            params['page'] = page

        r = cls._get_session().request('GET', url, params=params, **kwargs)
        r.raise_for_status()

        return r.json()
