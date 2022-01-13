from __future__ import annotations

from requests import Session

from .api_base import _BaseWistiaApi
from .config import WistiaConfig
from .errors import NoSuchMedia
from .models import VideoEmbedData


class WistiaEmbedApi(_BaseWistiaApi):
    """
    Helper class to interact with the Wistia Media Embed API (docs below)
      https://wistia.com/support/developers/embed-options

    """
    _API_ENDPOINT = WistiaConfig.EMBED_URL

    @classmethod
    def _get_session(cls, additional_status_force_list=None) -> Session:
        """
        Override to not wrap with the decorator that increments the
        :attr:`_REQUEST_COUNT` attribute, since it's not confirmed whether the
        Wistia Data API rate limitations apply in the case of this endpoint.
        """
        return cls._create_session(additional_status_force_list)

    @classmethod
    def get_data(cls, video_id: str) -> VideoEmbedData:
        """
        Get media embed data for a Wistia video using the endpoint to the
        `.jsonp` file

        """
        r = cls.session().get(
            WistiaConfig.MEDIAS_EMBED_URL.format(media_id=video_id))
        r.raise_for_status()

        data = r.json()
        if 'error' in data:
            # Wistia Embed response contains an error object like below:
            #   {'error': True, 'iframe': True}
            raise NoSuchMedia(video_id)

        return VideoEmbedData.from_dict(data.get('media', {}))

    @classmethod
    def asset_url(cls, video_id: str | None = None,
                  media_data: VideoEmbedData | None = None,
                  asset_type='original') -> str | None:
        """
        Get the media asset url stored on Wistia, by default for the
        "original" video.

        Note: one of `video_id` or `media_data` must be specified.

        Note that Wistia also has separate asset url's for various resolutions
        on each video.

        """
        if media_data is None:
            media_data = cls.get_data(video_id)

        mp4_url = None
        for asset in media_data.assets:
            if asset.type == asset_type:
                url = asset.url
                mp4_url = url.replace('.bin', '/file.mp4', 1)

        return mp4_url

    @classmethod
    def num_assets(cls, video_id: str | None = None,
                   media_data: VideoEmbedData | None = None,
                   asset_type='mp4_alternate_audio') -> int:
        """
        Return the total number of assets (by default, AD files) associated
        with a Wistia video.

        """
        if media_data is None:
            media_data = cls.get_data(video_id)

        asset_count = 0
        for asset in media_data.assets:
            if asset.type == asset_type:
                asset_count += 1

        return asset_count
