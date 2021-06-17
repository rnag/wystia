"""
Utility functions for interacting with the Wistia API.
"""
from requests import HTTPError

from .api_data import WistiaDataApi
from .config import WistiaConfig
from .log import LOG


class WistiaHelper:
    """
    Helper class for interacting with Wistia API and Wistia videos, which
    further simplifies any calls. This assumes that :class:`WistiaApi` has
    been configured as needed with the API token.

    """

    @staticmethod
    def is_archived_video(video_name: str):
        """
        Check if this is an archived video which is automatically created by
        Wistia.

        In that case, we shouldn't order captions for it, since it's a copy of
        a video that was replaced with new media.

        Source: https://wistia.com/learn/product-updates/improved-library-management-tools  # noqa: E501
        """
        return '[Archived' in video_name and video_name[-1] == ']'

    @classmethod
    def video_exists(cls, video_id):
        """
        Check if a video exists on Wistia.
        """
        status = WistiaDataApi.session().head(
            WistiaConfig.MEDIAS_SHOW_URL.format(media_id=video_id)
        ).status_code

        return not (status == 404)

    @classmethod
    def update_video_name(cls, video_id: str, video_title: str):
        """Update the title for a Wistia video."""
        return WistiaDataApi.update_video(video_id, video_title)

    @classmethod
    def has_captions_enabled(cls, video_id: str) -> bool:
        """
        Check if a video has captions available in the player settings.

        :return: A boolean indicating if the video player has captions
          available.
        """
        customizations = WistiaDataApi.get_customizations(video_id)

        return (customizations.get('plugin', {})
                .get('captions-v1', {})
                .get('on', 'false')).upper() == 'TRUE'

    @classmethod
    def enable_captions(cls, video_id, on_by_default=False):
        """
        Enable captions on a Wistia video.
        """
        obd_value = str(on_by_default).lower()
        data = {
            "plugin": {
                "captions-v1": {
                    "language": "", "onByDefault": obd_value, "on": "true"
                }
            }
        }

        return WistiaDataApi.update_customizations(video_id, data)

    @classmethod
    def enable_ad(cls, video_id):
        """
        Enable audio descriptions on a Wistia video.
        """
        data = {
            "audioDescriptionIsRequired": "true"
        }

        return WistiaDataApi.update_customizations(video_id, data)

    @classmethod
    def enable_captions_and_ad(cls, video_id, on_by_default=False):
        """
        Enable captions and AD on a Wistia video.
        """
        obd_value = str(on_by_default).lower()
        data = {
            "plugin": {
                "captions-v1": {
                    "language": "", "onByDefault": obd_value, "on": "true"
                }
            },
            "audioDescriptionIsRequired": "true"
        }

        return WistiaDataApi.update_customizations(video_id, data)

    @classmethod
    def disable_captions_and_ad(cls, video_id, on_by_default=False):
        """
        Disable captions and AD on a Wistia video.
        """
        obd_value = str(on_by_default).lower()
        data = {
            "plugin": {
                "captions-v1": {
                    "language": "", "onByDefault": obd_value, "on": "false"
                }
            },
            "audioDescriptionIsRequired": "false"
        }

        return WistiaDataApi.update_customizations(video_id, data)

    @classmethod
    def customize_video_on_wistia(cls, video_id: str, player_color: str):
        """Set commonly used customization options for a media on Wistia."""
        customizations = {'playerColor': player_color}

        r = WistiaDataApi.session().put(
            WistiaConfig.CUSTOMIZATION_URL.format(media_id=video_id),
            json=customizations)

        try:
            r.raise_for_status()
        except HTTPError:
            LOG.error('Wistia Customizations API. status=%d text=%s',
                      r.status_code, r.text)
            raise

        LOG.info(f'[{r.elapsed}] Wistia: Customize Video success')
        return r.json()
