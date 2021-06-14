from typing import Optional, Dict, Any

from requests import HTTPError

from .base_api import _BaseWistiaApi
from .config.wistia import WistiaConfig
from .errors import *
from .log import LOG
from .models import LanguageCode


class WistiaDataApi(_BaseWistiaApi):
    """
    Helper class to interact with the Wistia Data API (docs below)
      https://wistia.com/support/developers/data-api

    """
    API_ENDPOINT = WistiaConfig.API_URL

    @classmethod
    def get_videos_for_project(cls, project_id, sort_by=None):
        """Get videos for a Wistia project.

        Defaults to sorting by Project ID. You can pass the`sort_by` argument
        to sort by the following acceptable values:
            name, created, updated

        :raises NoSuchProject: If the project does not exist on Wistia
        """
        params = {'project_id': project_id}
        if sort_by:
            params['sort_by']: sort_by

        try:
            data = cls.get_page(
                WistiaConfig.MEDIAS_URL, params=params)
        except HTTPError as e:
            raise NoSuchProject(project_id) if cls._has_resp_status(e, 404) else e

        return data

    @classmethod
    def list_project(cls, project_id, sort_by=None, per_page=500):
        """
        Get all videos for a Wistia project, via the `Projects#show` API:
          https://wistia.com/support/developers/data-api#projects_show

        Defaults to sorting by Project ID. You can pass the`sort_by` argument
        to sort by the following acceptable values:
            name, created, updated

        :raises NoSuchProject: If the project does not exist on Wistia
        """
        params = {'project_id': project_id}
        if sort_by:
            params['sort_by']: sort_by

        try:
            data = cls.get_page(
                WistiaConfig.PROJECTS_SHOW_URL.format(project_id=project_id),
                data_key='medias', max_per_page=per_page, params=params)
        except HTTPError as e:
            raise NoSuchProject(project_id) if cls._has_resp_status(e, 404) else e

        return data

    @classmethod
    def get_video(cls, video_id):
        """
        Get information on a Wistia video.

        :raises NoSuchVideo: If the video does not exist on Wistia
        """
        r = cls.session().get(
            WistiaConfig.MEDIAS_SHOW_URL.format(media_id=video_id))

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise NoSuchVideo(video_id) if cls._has_resp_status(e, 404) else e

        return r.json()

    @classmethod
    def update_video_name(cls, video_id, video_title):
        """Update the title for a Wistia video."""
        data = {'name': video_title}

        r = cls.session().put(
            WistiaConfig.MEDIAS_SHOW_URL.format(media_id=video_id),
            data=data)
        r.raise_for_status()

        return r.json()

    @classmethod
    def video_exists(cls, video_id):
        """
        Check if a video exists on Wistia.
        """
        status = cls.session().head(
            WistiaConfig.MEDIAS_SHOW_URL.format(media_id=video_id)
        ).status_code

        return not (status == 404)

    @classmethod
    def copy_video_to_project(cls, video_id: str, dest_project_id: str):
        """Copy a video to a separate project."""
        data = {'project_id': dest_project_id}

        r = cls.session().post(
            WistiaConfig.MEDIAS_COPY_URL.format(media_id=video_id), json=data)
        r.raise_for_status()

        return r.json()

    @classmethod
    def get_captions(cls, video_id, lang_code: Optional[LanguageCode] = None):
        """
        Get captions on a Wistia video.
        """
        if lang_code:
            url = WistiaConfig.LANG_CAPTIONS_URL.format(
                media_id=video_id, lang_code=lang_code.value)
        else:
            url = WistiaConfig.ALL_CAPTIONS_URL.format(
                media_id=video_id)

        r = cls.session().get(url)

        try:
            r.raise_for_status()
        except HTTPError:
            if lang_code and 400 <= r.status_code < 500:
                return {}
            else:
                raise

        return r.json()

    @classmethod
    def replace_captions(cls, video_id, lang_code: LanguageCode, srt_contents=None, srt_file=None):
        """
        Update captions for a given language on a Wistia video.
        """
        put_kwargs = {'json': {'caption_file': srt_contents}}

        r = cls.session().put(
            WistiaConfig.LANG_CAPTIONS_URL.format(
                media_id=video_id, lang_code=lang_code.value), **put_kwargs)

        try:
            r.raise_for_status()
        except HTTPError:
            if r.status_code != 404:
                raise
            # Captions don't exist for the specified language
            # Ref: https://wistia.com/support/developers/data-api#the-response-27
            LOG.warning('%s: No captions on video, will attempt to add them. lang_code=%s',
                        video_id, lang_code.value)
            cls.add_captions(video_id, lang_code, srt_contents)

    @classmethod
    def add_captions(cls, video_id, lang_code: LanguageCode, srt_contents=None):
        """
        Add new captions for a given language on a Wistia video.

        Note that this always add new captions, regardless of whether captions
        already exist for the language. Please use :func:`replace_captions`
        if we need to update captions for a language instead.

        """
        post_kwargs = {'json': {'language': lang_code.value,
                                'caption_file': srt_contents}}

        r = cls.session().post(
            WistiaConfig.ALL_CAPTIONS_URL.format(
                media_id=video_id), **post_kwargs)
        r.raise_for_status()

    @classmethod
    def customize_video_on_wistia(cls, video_id: str, player_color: str):
        """Set commonly used customization options for a media on Wistia."""
        customizations = {'playerColor': player_color}

        try:
            r = cls.update_customizations(video_id, customizations, raw_resp=True)
        except HTTPError as e:
            r = e.response
            LOG.error('Wistia Customizations API. status=%d text=%s', r.status_code, r.text)
            raise

        LOG.info(f'[{r.elapsed}] Wistia: Customize Video success')
        return r.json()

    @classmethod
    def set_customizations(cls, video_id: str, customizations: Dict[str, Any],
                           raw_resp=False):
        """Overwrites the customizations for a media on Wistia"""
        r = cls.session().post(WistiaConfig.CUSTOMIZATION_URL.format(
            media_id=video_id), json=customizations)
        r.raise_for_status()

        return r if raw_resp else r.json()

    @classmethod
    def update_customizations(cls, video_id: str, customizations: Dict[str, Any],
                              raw_resp=False):
        """Updates the customizations for a media on Wistia"""
        r = cls.session().put(WistiaConfig.CUSTOMIZATION_URL.format(
            media_id=video_id), json=customizations)
        r.raise_for_status()

        return r if raw_resp else r.json()

    @classmethod
    def enable_captions(cls, video_id, on_by_default=False):
        """
        Enable captions on a Wistia video.
        """
        obd_value = str(on_by_default).lower()
        data = {
            "plugin": {
                "captions-v1": {"language": "", "onByDefault": obd_value, "on": "true"}
            }
        }

        return cls.update_customizations(video_id, data)

    @classmethod
    def enable_ad(cls, video_id):
        """
        Enable audio descriptions on a Wistia video.
        """
        data = {
            "audioDescriptionIsRequired": "true"
        }

        return cls.update_customizations(video_id, data)

    @classmethod
    def disable_captions_and_ad(cls, video_id, on_by_default=False):
        """
        Disable captions and AD on a Wistia video.
        """
        obd_value = str(on_by_default).lower()
        data = {
            "plugin": {
                "captions-v1": {"language": "", "onByDefault": obd_value, "on": "false"}
            },
            "audioDescriptionIsRequired": "false"
        }

        return cls.update_customizations(video_id, data)

    @classmethod
    def get_customizations(cls, video_id):
        r = cls.session().get(WistiaConfig.CUSTOMIZATION_URL.format(media_id=video_id))
        r.raise_for_status()

        return r.json()

    @classmethod
    def delete_video(cls, video_id) -> bool:
        """
        Deletes a video from Wistia.

        :return: A boolean indicating whether the video was successfully deleted.
        """
        r = cls.session().delete(
            WistiaConfig.MEDIAS_SHOW_URL.format(media_id=video_id))

        success = r.status_code == 200
        if not success:
            LOG.error('Wistia Delete Video API. status=%d text=%s',
                      r.status_code, r.text)

        return success

    @classmethod
    def has_captions_enabled(cls, video_id: str) -> bool:
        """
        Check if a video has captions available in the player settings.

        :return: A boolean indicating if the video player has captions available.
        """
        customizations = cls.get_customizations(video_id)

        return (customizations.get('plugin', {})
                .get('captions-v1', {})
                .get('on', 'false')).upper() == 'TRUE'
