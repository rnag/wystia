"""
Project-specific constants
"""

__all__ = ['LOG_LEVEL',
           'WISTIA_ACCOUNT',
           'WISTIA_API_TOKEN',
           'RAISE_ON_UNKNOWN_KEY']

import os

from dataclass_wizard.utils.type_conv import as_bool


# Library Log Level
LOG_LEVEL = os.getenv('WISTIA_LOG_LEVEL', 'WARNING').upper()

# This is also the wistia.com sub-domain where videos are hosted
WISTIA_ACCOUNT = os.getenv('WISTIA_ACCOUNT', 'REPLACE-ME')

# Wistia API token
WISTIA_API_TOKEN = os.getenv('WISTIA_API_TOKEN')

# Whether to raise when an unknown JSON key is encountered in the
# de-serialization process; default to true.
RAISE_ON_UNKNOWN_KEY = as_bool(os.getenv('RAISE_ON_UNKNOWN_KEY', True))
