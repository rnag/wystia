from wystia import WistiaApi
from wystia.constants import WISTIA_API_TOKEN


wistia_token = 'REPLACE-ME'

# Set up Wistia API token, only if currently not specified
# in the environment.
if WISTIA_API_TOKEN is None:
    WistiaApi.configure(wistia_token)
