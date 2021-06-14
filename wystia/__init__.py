"""
A Python wrapper library for the Wistia API


Docs:
    - https://wistia.com/support/developers/data-api
    - https://wistia.com/support/developers/upload-api
    - https://wistia.com/support/developers/embed-options

"""
__all__ = ['WistiaDataApi',
           'WistiaEmbedApi',
           'WistiaUploadApi']

import logging

from .data_api import WistiaDataApi
from .embed_api import WistiaEmbedApi
from .upload_api import WistiaUploadApi


__author__ = 'Ritvik Nag'
__email__ = 'rv.kvetch@gmail.com'
__version__ = '0.1.0'


# Set up logging to ``/dev/null`` like a library is supposed to.
#   https://docs.python.org/3.8/howto/logging.html#configuring-logging-for-a-library
logging.getLogger('wystia').addHandler(logging.NullHandler())
