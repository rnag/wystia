"""
Project-specific constants
"""

__all__ = ['LOG_LEVEL',
           'WISTIA_ACCOUNT',
           'WISTIA_API_TOKEN']

import os


# Library Log Level
LOG_LEVEL = os.getenv('WISTIA_LOG_LEVEL', 'WARNING').upper()

# This is also the wistia.com sub-domain where videos are hosted
WISTIA_ACCOUNT = os.getenv('WISTIA_ACCOUNT', 'REPLACE-ME')

# Wistia API token
WISTIA_API_TOKEN = os.getenv('WISTIA_API_TOKEN')
