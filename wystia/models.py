__all__ = ['LanguageCode',
           'MediaType',
           'SortBy',
           'SortDir',
           'VideoStatus',
           'VideoData',
           'VideoEmbedData',
           'UploadResponse']

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Union

from .log import LOG
from .utils.parse import get_srt_duration


class LanguageCode(Enum):
    """
    The 3-character Language Codes for Wistia, as specified by ISO-639-2.
    """
    CHINESE = 'chi'
    ENGLISH = 'eng'
    FRENCH = 'fre'
    GERMAN = 'ger'
    ITALIAN = 'ita'
    SPANISH = 'spa'
    JAPANESE = 'jpn'


class MediaType(Enum):
    """
    Wistia Media Types, as documented in the link below:
      https://wistia.com/support/developers/data-api#medias_response

    """
    VIDEO = 'Video'
    AUDIO = 'Audio'
    IMAGE = 'Image'
    PDF = 'PdfDocument'
    WORD = 'MicrosoftOfficeDocument'
    SWF = 'Swf'
    UNKNOWN = 'UnknownType'


class SortBy(Enum):
    """
    The name of the field to sort by. Defaults to sorting by Project ID.
      https://wistia.com/support/developers/data-api#sorting

    """
    NAME = 'name'
    CREATED = 'created'
    UPDATED = 'updated'


class SortDir(Enum):
    """
    Specifies the direction of the sort, defaults to ASC (ascending) order.
      https://wistia.com/support/developers/data-api#sorting

    """
    DESC = 0
    ASC = 1


class VideoStatus(Enum):

    # the file has been fully processed and is ready for embedding and viewing
    READY = 'ready'
    # the file is actively being processed
    PROCESSING = 'processing'
    # the file is waiting in the queue to be processed
    QUEUED = 'queued'
    # the file was unable to be processed (usually a format or size error)
    FAILED = 'failed'
    # custom enum member, indicates that video was taken down from Wistia
    # this is not part of the Wistia API
    NOT_FOUND = 'not_found'


@dataclass(init=False)
class VideoData:

    hashed_id: str
    name: str
    project_id: str
    created: datetime
    updated: datetime
    duration: float
    status: VideoStatus
    has_audio_description: bool

    # Not included in GET '/v1/medias' response, but technically
    # still part of video metadata.
    captions_enabled: bool = None
    overlay_text: str = None
    caption_duration: Optional[float] = None
    num_captions: int = 0
    ad_disabled: bool = False

    def __init__(self, assets=None, **kwargs):
        """
        Parses an API response from `Medias: List` or `Projects: Show`
        """
        if kwargs.pop('type') != 'Video':
            return

        for asset in assets or []:
            if asset['type'] == 'AlternateAudioFile':
                self.has_audio_description = True
                break
        else:
            self.has_audio_description = False

        self.status = VideoStatus(kwargs.pop('status'))
        self.created = datetime.fromisoformat(
            kwargs.pop('created'))
        self.updated = datetime.fromisoformat(
            kwargs.pop('updated'))

        project_data = kwargs.pop('project', None)
        if project_data:
            self.set_project(project_data['hashed_id'])
        else:
            self.set_project('')

        try:
            self.duration = kwargs.pop('duration')
        except KeyError as e:
            # There are rare cases when 'duration' field is missing from
            # response. This usually also means video is inaccessible from the
            # webpage, so we might need to contact Wistia Support to resolve
            # the issue.
            self.status = VideoStatus.FAILED
            self.duration = 0.0
            LOG.exception(
                f'VideoData: Video ({kwargs.get("hashed_id")}) is missing a '
                'required field in get_video response', exc_info=e)

        # Video titles seem to include encoded characters like '&amp;' in the
        # response, but not in the title displayed on the Wistia video page.
        self.name = kwargs.pop('name', '').replace('&amp;', '&')

        vars = self.__annotations__
        for var, value in kwargs.items():
            if var in vars:
                setattr(self, var, value)

    @classmethod
    def load_video(cls, video_id: str) -> 'VideoData':
        """
        Retrieve video data from Wistia and return a new :class:`VideoData`
        object.
        """
        from .api_data import WistiaDataApi
        obj = cls(**WistiaDataApi.get_video(video_id))
        return obj

    @classmethod
    def list_for_project(cls, project_id: str) -> List['VideoData']:
        """
        List videos for a Wistia project.
        """
        from .api_data import WistiaDataApi
        videos = []
        for v in WistiaDataApi.list_project(project_id):
            vd = VideoData(**v)
            vd.set_project(project_id)
            videos.append(vd)

        return videos

    @property
    def has_captions(self) -> bool:
        """
        Indicates whether the Wistia video has a captions file.
        """
        return self.caption_duration is not None

    def set_project(self, project_id: str):
        """Set the `project_id` attribute on the object."""
        self.project_id = project_id

    def process_captions(self, captions: Dict):
        """
        Process the response from the `Captions: Index` API for the video.

        Sets the following attributes on the object:
            - `num_captions`
            - `caption_duration`

        Ref: https://wistia.com/support/developers/data-api#captions_index
        """
        if not captions:
            return

        caption_durations: List[float] = []
        for caption in captions:
            # lc = LanguageCode(caption['language'])
            captions_end_seconds = get_srt_duration(caption['text'])

            caption_durations.append(captions_end_seconds)

        self.num_captions = len(caption_durations)
        self.caption_duration = caption_durations[0]

    def process_customizations(self, customizations):
        """
        Process the response from the `Customizations: Show` API for the video.

        Sets the following attributes on the object:
            - `ad_disabled`
            - `captions_enabled`
            - `overlay_text`

        Ref: https://wistia.com/support/developers/data-api#customizations_show
        """

        # Check if ad is explicitly disabled
        ad_disabled = customizations.get(
            'audioDescriptionIsRequired', '').lower() == 'false'
        overlay_text = customizations.get('plugin', {}).get(
            'thumbnailTextOverlay-v2', {}).get('text') or ''

        self.ad_disabled = ad_disabled
        self.captions_enabled = (customizations.get('plugin', {})
                                 .get('captions-v1', {})
                                 .get('on', 'false')).upper() == 'TRUE'
        self.overlay_text = overlay_text.strip()

    def dict(self):
        return_dict = {attr: value for attr, value in self.__dict__.items()
                       if value is not None}

        return_dict['status'] = self.status.value
        for attr in ('created', 'updated'):
            val = getattr(self, attr)
            if val:
                return_dict[attr] = val.isoformat()

        return return_dict

    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)

        obj.status = VideoStatus(d.pop('status'))

        for attr in ('created', 'updated'):
            val = d.pop(attr)
            if val:
                setattr(obj, attr, datetime.fromisoformat(val))

        vars = obj.__annotations__
        for var, value in d.items():
            if var in vars:
                setattr(obj, var, value)

        return obj


@dataclass(init=False)
class VideoEmbedData:

    hashed_id: str
    name: str
    created: datetime
    duration: float
    # status: VideoStatus
    captions_enabled: bool
    ad_enabled: bool

    # Not included in GET '/v1/medias' response, but technically
    # still part of video metadata.
    source_url: str
    ad_url: Optional[str] = None
    has_audio_description: bool = False
    num_captions: int = 0

    def __init__(self, **kwargs):
        """
        Parses a response from `WistiaEmbedApi.get_data`
        """
        if kwargs.pop('type') != 'Video':
            return

        self.hashed_id = kwargs['hashedId']
        self.name = kwargs['name']
        self.created = datetime.fromtimestamp(kwargs['createdAt'])
        self.duration = kwargs['duration']

        customizations = kwargs.get('embed_options') or {}
        self.captions_enabled = (customizations
                                 .get('plugin', {})
                                 .get('captions-v1', {}).get('on') == 'true')
        self.ad_enabled = (customizations
                           .get('audioDescriptionIsRequired') != 'false')
        self.num_captions = len(kwargs.get('captions', []))

        assets = kwargs.get('assets') or []
        for asset in assets:
            if asset['type'] == 'original':
                self.source_url = asset['url'].replace('.bin', '/file.mp4', 1)
            if asset['type'] == 'alternate_audio':
                self.has_audio_description = True
                self.ad_url = asset['url'].replace('.bin', '/file.mp3', 1)

    @classmethod
    def load_video(cls, video_id: str) -> 'VideoEmbedData':
        """
        Retrieve video embed data from Wistia and return a new
        :class:`VideoEmbedData` object.

        """
        from .api_embed import WistiaEmbedApi
        obj = cls(**WistiaEmbedApi.get_data(video_id))
        return obj


@dataclass(init=False)
class UploadResponse:
    """
    Represents a response from the Wistia Upload API

    Example response format:
      https://wistia.com/support/developers/upload-api#response-format
    """
    id: int
    hashed_id: str
    name: str
    type: str
    description: Optional[str]
    created: datetime
    updated: datetime
    progress: float
    status: str
    thumbnail: Dict[str, Union[int, str]]
    duration: Optional[float] = None

    # noinspection PyTypeChecker
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        # Convert known datetime attributes to :class:`datetime` objects
        try:
            self.created = datetime.fromisoformat(self.created)
            self.updated = datetime.fromisoformat(self.updated)
        except (TypeError, ValueError, AttributeError):
            pass
