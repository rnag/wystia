"""
Configs and settings for Wistia API
"""
from .constants import WISTIA_ACCOUNT


class WistiaConfig:

    API_URL = 'https://api.wistia.com/v1/'
    UPLOAD_URL = 'https://upload.wistia.com/'
    EMBED_URL = 'https://fast.wistia.com/embed/'

    PROJECTS_URL = 'projects.json'
    PROJECTS_SHOW_URL = 'projects/{project_id}.json'
    PROJECTS_COPY_URL = 'projects/{project_id}/copy.json'
    MEDIAS_URL = 'medias.json'
    MEDIAS_SHOW_URL = 'medias/{media_id}.json'
    MEDIAS_COPY_URL = 'medias/{media_id}/copy.json'
    MEDIAS_STATS_URL = 'medias/{media_id}/stats.json'
    CUSTOMIZATION_URL = 'medias/{media_id}/customizations.json'
    CAPTIONS_ORDER_URL = 'medias/{media_id}/captions/purchase.json'
    ALL_CAPTIONS_URL = 'medias/{media_id}/captions.json'
    LANG_CAPTIONS_URL = 'medias/{media_id}/captions/{lang_code}.json'

    MEDIAS_EMBED_URL = 'medias/{media_id}.json'

    @classmethod
    def wistia_url(cls, video_id, account_name=WISTIA_ACCOUNT):
        """Construct the wistia media Url given a video id"""
        return 'https://{account_name}.wistia.com/medias/{video_id}'.format(
            account_name=account_name, video_id=video_id)
