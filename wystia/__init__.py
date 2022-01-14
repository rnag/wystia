"""
A Python wrapper library for the Wistia API


Docs:
    - https://wistia.com/support/developers/data-api
    - https://wistia.com/support/developers/upload-api
    - https://wistia.com/support/developers/embed-options

"""
__all__ = ['WistiaApi',
           'WistiaDataApi',
           'WistiaEmbedApi',
           'WistiaUploadApi',
           'WistiaHelper']

import logging

from .api_data import WistiaDataApi
from .api_embed import WistiaEmbedApi
from .api_upload import WistiaUploadApi
from .api_helper import WistiaHelper


# A handy alias in case it comes in useful to anyone :-)
WistiaApi = WistiaDataApi


__author__ = 'Ritvik Nag'
__email__ = 'rv.kvetch@gmail.com'
__version__ = '1.0.0'


# Set up logging to ``/dev/null`` like a library is supposed to.
#   https://docs.python.org/3.8/howto/logging.html#configuring-logging-for-a-library
logging.getLogger('wystia').addHandler(logging.NullHandler())
