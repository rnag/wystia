from __future__ import annotations

from functools import partial

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .requests_config import (
    DEFAULT_MAX_RETRIES, DEFAULT_BACKOFF_FACTOR, DEFAULT_STATUS_FORCE_LIST)


class SessionWithRetry(Session):
    """
    Extend the :class:`request.Session` class to provide support for HTTP
    retries (in cases of timeout or other server-side errors)
    """
    def __init__(self, auth=None,
                 num_retries=DEFAULT_MAX_RETRIES,
                 backoff_factor=DEFAULT_BACKOFF_FACTOR,
                 additional_status_force_list: list[int] | None = None):

        super().__init__()
        self.auth = auth

        status_force_list = DEFAULT_STATUS_FORCE_LIST
        # Retry on additional status codes (ex. HTTP 400) if needed
        if additional_status_force_list:
            status_force_list.extend(additional_status_force_list)

        retry_strategy = Retry(
            read=0,
            total=num_retries,
            status_forcelist=status_force_list,
            allowed_methods=["HEAD", "GET", "PUT", "POST", "DELETE",
                             "OPTIONS", "TRACE"],
            backoff_factor=backoff_factor
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.mount("https://", adapter)
        self.mount("http://", adapter)


def prefix_url_session(prefix: str, session=None) -> Session:
    """
    Returns a :class:`requests.Session` object which makes all HTTP requests
    against a base API endpoint.

    https://stackoverflow.com/a/53140699/10237506
    """
    prefix = prefix.rstrip('/') + '/'

    def new_request(prefix, f, method, url, *args, **kwargs):
        return f(method, prefix + url.lstrip('/'), *args, **kwargs)

    if session is None:
        session = requests.Session()

    session.request = partial(new_request, prefix, session.request)
    return session
