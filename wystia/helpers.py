"""
Utility functions for interacting with the Wistia API.
"""


class WistiaHelper:
    """
    Helper class for interacting with Wistia API and Wistia videos, which
    further simplifies any calls. This assumes that :class:`WistiaApi` has
    been configured as needed with the API token.

    """

    @staticmethod
    def is_archived_video(video_name: str):
        """
        Check if this is an archived video which is automatically created by Wistia.

        In that case, we shouldn't order captions for it, since it's a copy of a video
        that was replaced with new media.

        Source: https://wistia.com/learn/product-updates/improved-library-management-tools
        """
        return '[Archived' in video_name and video_name[-1] == ']'
