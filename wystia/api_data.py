from __future__ import annotations

from typing import TypeVar

from requests import HTTPError

from .api_base import _BaseWistiaApi
from .config import WistiaConfig
from .errors import *
from .log import LOG
from .models import *
from .utils.parse import resolve_contents


T = TypeVar('T')


class WistiaDataApi(_BaseWistiaApi):
    """
    Helper class to interact with the Wistia Data API (docs below)
      https://wistia.com/support/developers/data-api

    Fully implements the following sections in the API documentation:

        - Paging and Sorting Responses
        - Projects
        - Medias
        - Customizations
        - Captions

    """
    _API_ENDPOINT = WistiaConfig.API_URL

    # --------------------------
    # -       PROJECTS         -
    # --------------------------

    @classmethod
    def list_all_projects(
        cls,
        sort_by: SortBy | None = None,
        sort_dir: SortDir | None = None,
        per_page=_BaseWistiaApi._MAX_PER_PAGE
    ) -> Container[Project]:
        """
        Retrieve a list of Projects in the account, via the
        `Projects:list` API:
          https://wistia.com/support/developers/data-api#projects_list

        Defaults to sorting by Project ID. You can pass the`sort_by` argument
        to sort by another value.

        :raises NoSuchProject: If the project does not exist on Wistia
        """
        params = {}
        if sort_by:
            params['sort_by'] = sort_by.value
        if sort_dir:
            params['sort_direction'] = sort_dir.value

        try:
            data = cls.list_page(
                WistiaConfig.PROJECTS_URL,
                data_model=Project,
                per_page=per_page,
                params=params
            )
        except HTTPError:
            raise

        return data

    @classmethod
    def list_project(
        cls,
        project_id: str,
        sort_by: SortBy | None = None,
        sort_dir: SortDir | None = None,
        per_page=500,
        model_cls: type[T] = Media,
    ) -> Container[T | Media]:
        """
        Get all medias (generally videos) for a Wistia project, via the
        `Projects#show` API:
          https://wistia.com/support/developers/data-api#projects_show

        Defaults to sorting by Project ID. You can pass the`sort_by` argument
        to sort by another value.

        :raises NoSuchProject: If the project does not exist on Wistia
        """
        params = {'project_id': project_id}
        if sort_by:
            params['sort_by'] = sort_by.value
        if sort_dir:
            params['sort_direction'] = sort_dir.value

        try:
            data = cls.list_page(
                WistiaConfig.PROJECTS_SHOW_URL.format(project_id=project_id),
                data_model=model_cls,
                data_key='medias',
                per_page=per_page,
                params=params
            )
        except HTTPError as e:
            raise NoSuchProject(project_id) \
                if cls._has_resp_status(e, 404) else e

        return data

    @classmethod
    def create_project(
        cls,
        project_name: str | None = None,
        admin_email: str | None = None,
        public_upload: bool | None = None,
        public_download: bool | None = None,
        public: bool | None = None
    ) -> Project:
        """
        Create a new project in your account, via the `Projects:create` API:
          https://wistia.com/support/developers/data-api#projects_create

        """
        params = {'name': project_name}
        if admin_email:
            params['adminEmail'] = admin_email
        if public_upload is not None:
            params['anonymousCanUpload'] = 1 if public_upload else 0
        if public_download is not None:
            params['anonymousCanDownload'] = 1 if public_download else 0
        if public is not None:
            params['public'] = 1 if public else 0

        r = cls.session().post(
            WistiaConfig.PROJECTS_URL,
            params=params
        )
        r.raise_for_status()

        return Project.from_dict(r.json())

    @classmethod
    def update_project(
        cls, project_id: str,
        project_name: str | None = None,
        public_upload: bool | None = None,
        public_download: bool | None = None,
        public: bool | None = None
    ) -> Project:
        """
        Update an existing project in your account, via the
        `Projects:update` API:
          https://wistia.com/support/developers/data-api#projects_update

        """
        params = {}
        if project_name:
            params['name'] = project_name
        if public_upload is not None:
            params['anonymousCanUpload'] = 1 if public_upload else 0
        if public_download is not None:
            params['anonymousCanDownload'] = 1 if public_download else 0
        if public is not None:
            params['public'] = 1 if public else 0

        r = cls.session().put(
            WistiaConfig.PROJECTS_SHOW_URL.format(project_id=project_id),
            params=params
        )
        r.raise_for_status()

        return Project.from_dict(r.json())

    @classmethod
    def delete_project(cls, project_id: str):
        """
        Delete a project in your account, via the `Projects:delete` API:
          https://wistia.com/support/developers/data-api#projects_delete

        :return: A boolean indicating whether the video was successfully
          deleted.
        """
        return cls.handle_delete(
            WistiaConfig.PROJECTS_SHOW_URL.format(project_id=project_id)
        )

    @classmethod
    def copy_project(
        cls,
        project_id: str,
        admin_email: str | None = None
    ) -> Project:
        """
        Copies an existing project in your account, including all media and
        sections, via the `Projects:copy` API:
          https://wistia.com/support/developers/data-api#projects_copy

        """
        params = {}
        if admin_email:
            params['adminEmail'] = admin_email

        r = cls.session().post(
            WistiaConfig.PROJECTS_COPY_URL.format(project_id=project_id),
            params=params
        )
        r.raise_for_status()

        return Project.from_dict(r.json())

    # --------------------------
    # -        MEDIAS          -
    # --------------------------

    @classmethod
    def list_videos(
        cls,
        project_id: str | None = None,
        video_name: str | None = None,
        media_type: MediaType | None = MediaType.VIDEO,
        video_id: str | None = None,
        sort_by: SortBy | None = None,
        sort_dir: SortDir | None = None
    ) -> Container[Video]:
        """
        Get all videos for a Wistia project or by other criteria, via the
        `Medias#list` API:
          https://wistia.com/support/developers/data-api#medias_list

        Defaults to sorting by Project ID. You can pass the`sort_by` argument
        to sort by another value.

        :raises NoSuchProject: If the project does not exist on Wistia
        """
        return cls.list_medias(
            project_id=project_id,
            media_name=video_name,
            media_type=media_type,
            media_id=video_id,
            sort_by=sort_by,
            sort_dir=sort_dir,
            model_cls=Video
        )

    @classmethod
    def list_medias(
        cls,
        project_id: str | None = None,
        media_name: str | None = None,
        media_type: MediaType | None = None,
        media_id: str | None = None,
        sort_by: SortBy | None = None,
        sort_dir: SortDir | None = None,
        model_cls: type[T] = Media
    ) -> Container[T | Media]:
        """
        Get all medias for a Wistia project or by other criteria, via the
        `Medias#list` API:
          https://wistia.com/support/developers/data-api#medias_list

        Defaults to sorting by Project ID. You can pass the`sort_by` argument
        to sort by another value.

        :raises NoSuchProject: If the project does not exist on Wistia
        """
        params = {}
        if project_id:
            params['project_id'] = project_id
        if media_name:
            params['name'] = media_name
        if media_type:
            params['type'] = media_type.value
        if media_id:
            params['hashed_id'] = media_id
        if sort_by:
            params['sort_by'] = sort_by.value
        if sort_dir:
            params['sort_direction'] = sort_dir.value

        try:
            data = cls.list_page(
                WistiaConfig.MEDIAS_URL,
                data_model=model_cls,
                params=params
            )
        except HTTPError as e:
            raise NoSuchProject(project_id) \
                if cls._has_resp_status(e, 404) else e

        return data

    @classmethod
    def get_video(
        cls,
        video_id: str,
        model_cls: type[T] = Video
    ) -> T | Video:
        """
        Get information on a Wistia video, via the `Medias#show` API:
          https://wistia.com/support/developers/data-api#medias_show

        :raises NoSuchMedia: If the video does not exist on Wistia
        """
        r = cls.session().get(
            WistiaConfig.MEDIAS_SHOW_URL.format(media_id=video_id)
        )

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise NoSuchMedia(video_id) if cls._has_resp_status(e, 404) else e

        return model_cls.from_dict(r.json())

    @classmethod
    def get_media(cls, media_id: str) -> Media:
        """
        Get information on a Wistia media, via the `Medias#show` API:
          https://wistia.com/support/developers/data-api#medias_show

        :raises NoSuchMedia: If the media does not exist on Wistia
        """
        return cls.get_video(media_id, model_cls=Media)

    @classmethod
    def update_video(
        cls,
        video_id: str,
        video_name: str | None = None,
        video_desc: str | None = None,
        thumbnail_media_id: str | None = None
    ) -> Video:
        """
        Updates attributes on a video, via the `Medias#update` API:
          https://wistia.com/support/developers/data-api#medias_update

        :param video_id: The hashed id of the video on Wistia.
        :param video_name: An optional new name for the video.
        :param video_desc: An optional new description for this video. Accepts
          plain text or markdown.
        :param thumbnail_media_id: The Wistia hashed ID of an image that will
          replace the still that’s displayed before the player starts playing.
        :raises NoSuchMedia: If the video does not exist on Wistia
        """
        return cls.update_media(
            media_id=video_id,
            media_name=video_name,
            media_desc=video_desc,
            thumbnail_media_id=thumbnail_media_id,
            model_cls=Video
        )

    @classmethod
    def update_media(
        cls,
        media_id: str,
        media_name: str | None = None,
        media_desc: str | None = None,
        thumbnail_media_id: str | None = None,
        model_cls: type[T] = Media
    ) -> T | Media:
        """
        Updates attributes on a media (generally a video), via the
        `Medias#update` API:
          https://wistia.com/support/developers/data-api#medias_update

        :param media_id: The hashed id of the media on Wistia.
        :param media_name: An optional new name for the media.
        :param media_desc: An optional new description for this media. Accepts
          plain text or markdown.
        :param thumbnail_media_id: The Wistia hashed ID of an image that will
          replace the still that’s displayed before the player starts playing.
        :param model_cls: The model class to load the response data into.
        :raises NoSuchMedia: If the media does not exist on Wistia
        """
        data = {}
        if media_name:
            data['name'] = media_name
        if media_desc:
            data['description'] = media_desc
        if thumbnail_media_id:
            data['new_still_media_id'] = thumbnail_media_id

        r = cls.session().put(
            WistiaConfig.MEDIAS_SHOW_URL.format(media_id=media_id),
            data=data
        )

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise NoSuchMedia(media_id) if cls._has_resp_status(e, 404) else e

        return model_cls.from_dict(r.json())

    @classmethod
    def delete_media(cls, media_id: str):
        """
        Deletes a media (generally a video) from Wistia, via the
        `Medias#delete` API:
          https://wistia.com/support/developers/data-api#medias_delete

        :return: A boolean indicating whether the video was successfully
          deleted.
        """
        return cls.handle_delete(
            WistiaConfig.MEDIAS_SHOW_URL.format(media_id=media_id)
        )

    # Alias
    delete_video = delete_media

    @classmethod
    def copy_video(
        cls,
        video_id: str,
        dest_project_id: str | None = None,
        owner: str | None = None,
        model_cls: type[T] = Video
    ) -> T | Video:
        """
        Copy a video, optionally to another project, via the `Medias#copy` API:
          https://wistia.com/support/developers/data-api#medias_copy

        :raises NoSuchMedia: If the video does not exist on Wistia
        :raises NoSuchProject: If the project does not exist on Wistia
        """
        data = {}
        if dest_project_id:
            data['project_id'] = dest_project_id
        if owner:
            data['owner'] = owner

        r = cls.session().post(
            WistiaConfig.MEDIAS_COPY_URL.format(media_id=video_id),
            json=data
        )

        try:
            r.raise_for_status()
        except HTTPError as e:
            if cls._has_resp_status(e, 404):
                if dest_project_id and dest_project_id in r.text:
                    # Project does not exist
                    raise NoSuchProject(dest_project_id)
                # Video does not exist
                raise NoSuchMedia(video_id)
            else:
                raise e

        return model_cls.from_dict(r.json())

    @classmethod
    def copy_media(
        cls,
        media_id: str,
        dest_project_id: str | None = None,
        owner: str | None = None
    ) -> Media:
        """
        Copy a media, optionally to another project, via the `Medias#copy` API:
          https://wistia.com/support/developers/data-api#medias_copy

        :raises NoSuchMedia: If the media does not exist on Wistia
        :raises NoSuchProject: If the project does not exist on Wistia
        """
        return cls.copy_video(
            media_id,
            dest_project_id,
            owner,
            model_cls=Media
        )

    @classmethod
    def get_stats_for_video(cls, video_id: str) -> VideoStats:
        """
        Get aggregated tracking stats on a Wistia video, via the
        `Medias#stats` API:
          https://wistia.com/support/developers/data-api#medias_stats

        :raises NoSuchMedia: If the video does not exist on Wistia
        """
        r = cls.session().get(
            WistiaConfig.MEDIAS_STATS_URL.format(media_id=video_id))

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise NoSuchMedia(video_id) if cls._has_resp_status(e, 404) else e

        return VideoStats.from_dict(r.json())

    # --------------------------
    # -     CUSTOMIZATIONS     -
    # --------------------------

    @classmethod
    def get_customizations(cls, video_id: str) -> Customizations:
        """
        Get customizations for a video on Wistia, via the
        `Customizations#show` API:
          https://wistia.com/support/developers/data-api#customizations_show

        :raises NoSuchMedia: If the video does not exist on Wistia
        """
        r = cls.session().get(
            WistiaConfig.CUSTOMIZATION_URL.format(media_id=video_id))

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise NoSuchMedia(video_id) if cls._has_resp_status(e, 404) else e

        return Customizations.from_dict(r.json())

    @classmethod
    def create_customizations(
        cls,
        video_id: str,
        customizations: Customizations
    ) -> Customizations:
        """
        Overwrites the customizations for a video on Wistia, via the
        `Customizations#create` API:
          https://wistia.com/support/developers/data-api#customizations_create

        :return: The new customizations on the video
        :raises NoSuchMedia: If the video does not exist on Wistia
        """
        r = cls.session().post(
            WistiaConfig.CUSTOMIZATION_URL.format(media_id=video_id),
            json=customizations.to_dict()
        )

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise NoSuchMedia(video_id) if cls._has_resp_status(e, 404) else e

        return Customizations.from_dict(r.json())

    @classmethod
    def update_customizations(
        cls,
        video_id: str,
        customizations: Customizations
    ) -> Customizations:
        """
        Updates the customizations for a video on Wistia, via the
        `Customizations#update` API:
          https://wistia.com/support/developers/data-api#customizations_update

        :return: The new customizations on the video
        :raises NoSuchMedia: If the video does not exist on Wistia
        """
        r = cls.session().put(
            WistiaConfig.CUSTOMIZATION_URL.format(media_id=video_id),
            json=customizations.to_dict()
        )

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise NoSuchMedia(video_id) if cls._has_resp_status(e, 404) else e

        return Customizations.from_dict(r.json())

    @classmethod
    def delete_customizations(cls, video_id: str):
        """
        Deletes the customizations for a video on Wistia, via the
        `Customizations#delete` API:
          https://wistia.com/support/developers/data-api#customizations_delete

        """
        return cls.handle_delete(
            WistiaConfig.CUSTOMIZATION_URL.format(media_id=video_id))

    # --------------------------
    # -       CAPTIONS         -
    # --------------------------

    @classmethod
    def list_captions(cls, video_id: str) -> Container[VideoCaptions]:
        """
        Retrieves all the captions on a Wistia video, via the
        `Captions#index` API:
          https://wistia.com/support/developers/data-api#captions_index

        The text of the captions will be in SRT format.

        :raises NoSuchMedia: If the video does not exist on Wistia.
        """
        r = cls.session().get(
            WistiaConfig.ALL_CAPTIONS_URL.format(media_id=video_id))

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise NoSuchMedia(video_id) if r.status_code == 404 else e

        return VideoCaptions.from_list(r.json())

    @classmethod
    def get_captions(
        cls,
        video_id: str,
        lang_code: LanguageCode
    ) -> VideoCaptions | None:
        """
        Retrieves the captions for a specific language on a Wistia video,
        via the `Captions#show` API:
          https://wistia.com/support/developers/data-api#captions_show

        The text of the captions will be in SRT format. If no captions exist
        for the specified language, a `None` value is returned.
        """
        r = cls.session().get(
            WistiaConfig.LANG_CAPTIONS_URL.format(
                media_id=video_id,
                lang_code=lang_code.value
            )
        )

        try:
            r.raise_for_status()
        except HTTPError:
            if r.status_code == 404:
                return None
            else:
                # Unexpected error
                raise

        return VideoCaptions.from_dict(r.json())

    @classmethod
    def create_captions(
        cls,
        video_id: str,
        lang_code: LanguageCode | None = None,
        srt_contents: str | None = None,
        srt_file: str | None = None
    ) -> None:
        """
        Create new captions for a given language on a Wistia video, via the
        `Captions#create` API:
          https://wistia.com/support/developers/data-api#captions_create

        Note that this always add new captions, regardless of whether captions
        already exist for the language. Please use :meth:`update_captions`
        if we need to replace captions for a language instead.

        :param video_id: The Wistia video to add the new captions for.
        :param lang_code: An optional ISO-639–2 language code for the file. If
          left unspecified, the language code will be detected automatically.
        :param srt_contents: The caption text in SRT format.
        :param srt_file: The path to an SRT file.
        :raises ContentIsEmpty: If one of `srt_contents` or `srt_file` is not
          provided.
        """
        data = {'caption_file': resolve_contents(srt_file, srt_contents)}
        if lang_code is not None:
            data['language'] = lang_code.value

        r = cls.session().post(
            WistiaConfig.ALL_CAPTIONS_URL.format(media_id=video_id),
            json=data
        )

        # check if the request was a success
        r.raise_for_status()

        # add an explicit return value
        return None

    @classmethod
    def update_captions(
        cls,
        video_id: str,
        lang_code: LanguageCode,
        srt_contents: str | None = None,
        srt_file: str | None = None
    ) -> None:
        """
        Replace captions for a given language on a Wistia video, via the
        `Captions#update` API:
          https://wistia.com/support/developers/data-api#captions_update

        **Note**: it is generally safer to call this method instead of
        :meth:`create_captions`, which always adds new captions for a given
        language; this method falls back to :meth:`create_captions` in case
        captions don't exist for the specified language.

        :param video_id: The Wistia video to add the new captions for.
        :param lang_code: An ISO-639–2 language code for the file. If
          left unspecified, the language code will be detected automatically.
        :param srt_contents: The caption text in SRT format.
        :param srt_file: The path to an SRT file.
        :raises ContentIsEmpty: If one of `srt_contents` or `srt_file` is not
          provided.
        """
        srt_contents = resolve_contents(srt_file, srt_contents)
        data = {'caption_file': srt_contents}

        r = cls.session().put(
            WistiaConfig.LANG_CAPTIONS_URL.format(
                media_id=video_id, lang_code=lang_code.value),
            json=data)

        # check if the request was a success
        try:
            r.raise_for_status()
        except HTTPError:
            if r.status_code != 404:
                raise
            # Captions don't exist for the specified language
            # Ref: https://wistia.com/support/developers/data-api#the-response-27  # noqa: E501
            LOG.info(
                '%s: No captions on video, will attempt to add them. '
                'lang_code=%s', video_id, lang_code.value)
            cls.create_captions(video_id, lang_code, srt_contents)

        # add an explicit return value
        return None

    @classmethod
    def delete_captions(
        cls,
        video_id: str,
        lang_code: LanguageCode
    ):
        """
        Deletes the captions for a video on Wistia, via the
        `Captions#delete` API:
          https://wistia.com/support/developers/data-api#captions_delete

        """
        return cls.handle_delete(
            WistiaConfig.LANG_CAPTIONS_URL.format(
                media_id=video_id,
                lang_code=lang_code.value
            )
        )

    @classmethod
    def order_captions(
        cls,
        video_id: str,
        automated: bool = False,
        rush: bool = True,
        automatically_enable: bool = True
    ) -> None:
        """
        Purchase English captions on a Wistia video, via the
        `Captions#purchase` API:
          https://wistia.com/support/developers/data-api#captions_purchase

        :param video_id: The hashed id of the video to order captions for.
        :param automated: Set to true to order computer-generated
          captions ($0.25/minute) or false to order human-generated
          captions ($2.50/minute).
          Defaults to false.
        :param rush: Set to true to enable a rush order (one business day
          turnaround, $4.00/minute), or false to retain the standard four
          business day turnaround for human-generated captions ($2.50/minute).
          Defaults to true.
        :param automatically_enable: Set to true to automatically enable
          captions for the video as soon as the order is ready or false to
          hold the captions for review before manually enabling them.
          Defaults to true.
        :raises VideoHasCaptions: If English captions already exist for
          the video.
        :raises NoSuchMedia: If the video does not exist.

        """
        params = {
            'automated': automated,
            'rush': rush,
            'automatically_enable': automatically_enable
        }

        r = cls.session().post(
            WistiaConfig.CAPTIONS_ORDER_URL.format(media_id=video_id),
            params=params
        )

        try:
            r.raise_for_status()
        except HTTPError:
            # Ref: https://wistia.com/support/developers/data-api#the-response-29  # noqa: E501
            if r.status_code == 400:
                raise VideoHasCaptions(video_id)
            elif r.status_code == 404:
                raise NoSuchMedia(video_id)
            else:
                raise

        return None
