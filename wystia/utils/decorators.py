"""
Decorator utilities
"""
import functools
from requests.exceptions import ConnectionError as RequestsConnectionError


def retry_on_connection_error(func=None, max_retries=5):
    """
    Decorator to automatically retry a function when a `ConnectionError` (such
    as a Broken Pipe error) is raised.
    """
    def decorate_func(f):
        @functools.wraps(f)
        def new_func(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return f(*args, **kwargs)
                except RequestsConnectionError:
                    retries += 1
                except Exception:
                    # Unexpected error, raise the message so it shows up
                    raise

            raise Exception('Maximum retries exceeded')

        return new_func

    return decorate_func(func) if func else decorate_func
