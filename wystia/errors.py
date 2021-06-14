"""
Project-specific exception classes
"""
__all__ = ['WistiaError',
           'NoSuchProject',
           'NoSuchVideo',
           'NoVideoCaptions',
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

        LOG.error(f'{self.code}: {message}')

    def response(self):
        """Formats an error object and returns an AWS Lambda Proxy response."""
        return format_error(self.message, self.code, self.ERR_STATUS)


class NoSuchProject(WistiaError):

    def __init__(self, video_id):
        msg = 'Project does not exist, or was deleted from Wistia.'
        super(NoSuchProject, self).__init__(msg, video_id=video_id)


class NoSuchVideo(WistiaError):

    def __init__(self, video_id):
        msg = 'Video does not exist, or was deleted from Wistia.'
        super(NoSuchVideo, self).__init__(msg, video_id=video_id)


class NoVideoCaptions(WistiaError):

    def __init__(self, video_id):
        msg = 'No captions exist for the Wistia video.'
        super(NoVideoCaptions, self).__init__(msg, video_id=video_id)


class UploadFailed(WistiaError):

    def __init__(self, r: Response):
        msg = 'Failure calling the Wistia Upload API.'
        super(UploadFailed, self).__init__(
            msg, status=r.status_code, text=r.text, reason=r.reason)
