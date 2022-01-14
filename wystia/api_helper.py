"""
Utility functions for interacting with the Wistia API.
"""
from __future__ import annotations

from requests import HTTPError

from .api_data import WistiaDataApi
from .config import WistiaConfig
from .errors import NoSuchProject
from .log import LOG
from .models import (Container, Project, Video,
                     Customizations, Plugin, CaptionsV1)


class WistiaHelper:
    """
    Helper class for interacting with Wistia API and Wistia videos, which
    further simplifies any calls. This assumes that :class:`WistiaApi` has
    been configured as needed with the API token.

    """

    @staticmethod
    def is_archived_video(video_name: str) -> bool:
        """
        Check if this is an archived video which is automatically created by
        Wistia.

        In that case, we shouldn't order captions for it, since it's a copy of
        a video that was replaced with new media.

        Source: https://wistia.com/learn/product-updates/improved-library-management-tools  # noqa: E501
        """
        return '[Archived' in video_name and video_name[-1] == ']'

    @classmethod
    def video_exists(cls, video_id: str) -> bool:
        """
        Check if a video exists on Wistia.
        """
        status = WistiaDataApi.session().head(
            WistiaConfig.MEDIAS_SHOW_URL.format(media_id=video_id)
        ).status_code

        return not (status == 404)

    @classmethod
    def update_video_name(
        cls,
        video_id: str,
        video_title: str
    ) -> Video:
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

        return customizations.plugin.captions_v1.on is True

    @classmethod
    def enable_captions(
        cls,
        video_id: str,
        on_by_default: bool = False
    ):
        """
        Enable captions on a Wistia video.
        """
        data = Customizations(
            plugin=Plugin(
                captions_v1=CaptionsV1(
                    on_by_default=on_by_default,
                    on=True
                )
            )
        )

        return WistiaDataApi.update_customizations(video_id, data)

    @classmethod
    def enable_ad(cls, video_id: str):
        """
        Enable audio descriptions on a Wistia video.
        """
        data = Customizations(audio_description_is_required=True)

        return WistiaDataApi.update_customizations(video_id, data)

    @classmethod
    def enable_captions_and_ad(
        cls,
        video_id: str,
        on_by_default: bool = False
    ):
        """
        Enable captions and AD on a Wistia video.
        """
        data = Customizations(
            plugin=Plugin(
                captions_v1=CaptionsV1(
                    on_by_default=on_by_default,
                    on=True
                )
            ),
            audio_description_is_required=True
        )

        return WistiaDataApi.update_customizations(video_id, data)

    @classmethod
    def disable_captions_and_ad(
        cls,
        video_id: str,
        on_by_default: bool = False
    ):
        """
        Disable captions and AD on a Wistia video.
        """
        data = Customizations(
            plugin=Plugin(
                captions_v1=CaptionsV1(
                    on_by_default=on_by_default,
                    on=False
                )
            ),
            audio_description_is_required=False
        )

        return WistiaDataApi.update_customizations(video_id, data)

    @classmethod
    def customize_video_on_wistia(
        cls,
        video_id: str,
        player_color: str
    ):
        """Set commonly used customization options for a media on Wistia."""
        customizations = {'playerColor': player_color}

        r = WistiaDataApi.session().put(
            WistiaConfig.CUSTOMIZATION_URL.format(media_id=video_id),
            json=customizations
        )

        try:
            r.raise_for_status()
        except HTTPError:
            LOG.error('Wistia Customizations API. status=%d text=%s',
                      r.status_code, r.text)
            raise

        LOG.info('[%s] Wistia: Customize Video success', r.elapsed)
        return r.json()

    @classmethod
    def project_details(
        cls,
        project_id: str,
        projects: Container[Project] | None = None
    ) -> Project:
        """Retrieve details on a Wistia project.

        The optional parameter `projects` contains info on all projects in
        the Wistia account, such as a response from the `Projects:list` API.

        :raises NoSuchProject: If the project doesn't exist on Wistia
        """
        if not projects:
            projects = WistiaDataApi.list_all_projects()

        for p in projects:
            if p.hashed_id == project_id:
                project = p
                break
        else:
            raise NoSuchProject(project_id)

        return project
