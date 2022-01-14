"""
Project-specific exception classes
"""
__all__ = ['WistiaError',
           'ContentIsEmpty',
           'NoSuchProject',
           'NoSuchMedia',
           'VideoHasCaptions',
           'UploadFailed']

from requests import Response

from .log import LOG
from .utils.response import format_error


class WistiaError(Exception):
    """
    Base exception class for errors raised by this library.

    """
    ERR_STATUS = 400

    def __init__(self, message, **log_kwargs):
        self.message = message
        self.code = self.__class__.__name__

        super(WistiaError, self).__init__(self.message)

        if log_kwargs:
            field_vals = [f'{k}={v}' for k, v in log_kwargs.items()]
            message = f'{message.rstrip(".")}. {", ".join(field_vals)}'

        LOG.error('%s: %s', self.code, message)

    def response(self):
        """Formats an error object and returns an AWS Lambda Proxy response."""
        return format_error(self.message, self.code, self.ERR_STATUS)


class ContentIsEmpty(WistiaError):

    def __init__(self):
        msg = 'The specified file content in the request is empty.'
        super(ContentIsEmpty, self).__init__(msg)


class NoSuchProject(WistiaError):

    def __init__(self, project_id):
        msg = 'Project does not exist, or was deleted from Wistia.'
        super(NoSuchProject, self).__init__(msg, project_id=project_id)


class NoSuchMedia(WistiaError):

    def __init__(self, media_id):
        msg = 'Video (or media) does not exist, or was deleted from Wistia.'
        super(NoSuchMedia, self).__init__(msg, media_id=media_id)


class VideoHasCaptions(WistiaError):

    def __init__(self, video_id):
        msg = 'English captions already exist for the Wistia video.'
        super(VideoHasCaptions, self).__init__(msg, video_id=video_id)


class UploadFailed(WistiaError):

    def __init__(self, r: Response):
        msg = 'Failure calling the Wistia Upload API.'
        super(UploadFailed, self).__init__(
            msg, status=r.status_code, text=r.text, reason=r.reason)
