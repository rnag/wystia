"""
Config for retries using the `requests` library
"""


# Default timeout for requests
DEFAULT_TIMEOUT = 60

# Default backoff factor to use for the exponential backoff algorithm;
# Note that the first retry will happen immediately.
#
# For example, if the backoff factor is 1, then after the first retry,
# we will sleep using the following seconds between retries:
#     [2, 4, 8, 16, 32 ...]
DEFAULT_BACKOFF_FACTOR = 1

# Default max retries before giving up.
DEFAULT_MAX_RETRIES = 7

# Maximum backoff time.
BACKOFF_MAX = 120

# Set of HTTP status codes that we should force a retry on
DEFAULT_STATUS_FORCE_LIST = [429, 500, 502, 503, 504]
