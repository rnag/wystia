from __future__ import annotations

import os.path
from typing import Any

from requests import HTTPError
from requests_toolbelt import MultipartEncoder

from .api_base import _BaseWistiaApi
from .config import WistiaConfig
from .errors import UploadFailed
from .log import LOG
from .models import UploadResponse
from .utils.decorators import retry_on_connection_error


class WistiaUploadApi(_BaseWistiaApi):
    """
    Helper class to interact with the Wistia Upload API (docs below)
      https://wistia.com/support/developers/upload-api

    """
    _API_ENDPOINT = WistiaConfig.UPLOAD_URL

    @classmethod
    def upload_file(
        cls,
        file_path: str,
        project_id: str | None = None,
        title: str | None = None,
        description: str | None = None,
        contact_id: int | None = None,
        max_retries=5
    ) -> UploadResponse:
        """
        Uploads a video file (given an absolute file path) to Wistia,
        and returns the hashed ID of the newly hosted video.

        Docs:
          https://wistia.com/support/developers/upload-api#the-request

        :param file_path: The path of the video file to upload.
        :param project_id: The hashed id of the project to upload media into.
          If omitted, a new project will be created and uploaded to.
        :param title: Optional display name for the video. If omitted, the
          filename will be used instead.
        :param description: Optional description for the video.
        :param contact_id: A Wistia contact id, an integer value. If omitted,
          it will default to the contact_id of the account’s owner.
        :param max_retries: Maximum number of retries, in case we run into a
          `BrokenPipeError` while uploading the video; defaults to 5.
        :raises UploadFailed: In case the upload operation fails; also logs
          error details from the Upload API response.

        """
        file_data = {'file': open(file_path, 'rb'),
                     'name': title or os.path.basename(file_path),
                     'access_token': cls._API_TOKEN}
        if project_id:
            file_data['project_id'] = project_id
        if description:
            file_data['description'] = description
        if contact_id:
            file_data['contact_id'] = contact_id

        # Works around a :class:`OverflowError` that is usually raised by the
        # `requests` library when uploading large files (>2GB).
        m = MultipartEncoder(fields=file_data)

        upload_func = retry_on_connection_error(
            cls._upload_url_or_file_to_wistia, max_retries=max_retries)
        data = upload_func(m, {'Content-Type': m.content_type})

        return UploadResponse.from_dict(data)

    @classmethod
    def upload_link(
        cls,
        url: str,
        project_id: str | None = None,
        title: str | None = None,
        description: str | None = None,
        contact_id: int | None = None
    ) -> UploadResponse:
        """
        Uploads a public video link to Wistia, and returns the hashed ID of the
        newly hosted video.

        Docs:
          https://wistia.com/support/developers/upload-api#the-request

        :param url: A public, downloadable link for the video.
        :param project_id: The hashed id of the project to upload media into.
          If omitted, a new project will be created and uploaded to.
        :param title: Optional display name for the video. If omitted, the
          filename will be used instead.
        :param description: Optional description for the video.
        :param contact_id: A Wistia contact id, an integer value. If omitted,
          it will default to the contact_id of the account’s owner.
        :raises UploadFailed: In case the upload operation fails; also logs
          error details from the Upload API response.

        """
        file_data = {'url': url,
                     'name': title or os.path.basename(url),
                     'access_token': cls._API_TOKEN}
        if project_id:
            file_data['project_id'] = project_id
        if description:
            file_data['description'] = description
        if contact_id:
            file_data['contact_id'] = contact_id

        data = cls._upload_url_or_file_to_wistia(file_data)

        return UploadResponse.from_dict(data)

    @classmethod
    def _upload_url_or_file_to_wistia(
            cls, data, headers=None) -> dict[str, Any]:
        """
        Passes a URL or a file to the Wistia Upload API.
        """
        # Make the API request to upload the video
        LOG.debug('Uploading to Wistia...')
        r = cls._get_session().request(
            'POST', '/', data=data, headers=headers)
        try:
            # Confirm the request was a success
            r.raise_for_status()
        except HTTPError:
            # Raise an error with the response details
            raise UploadFailed(r)

        LOG.info('Upload successful, completed in %s', r.elapsed)
        return r.json()
