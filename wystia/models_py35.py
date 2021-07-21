__all__ = ['LanguageCode',
           'MediaType',
           'SortBy',
           'SortDir',
           'VideoStatus',
           'VideoData',
           'VideoEmbedData',
           'UploadResponse']

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Union, Any

from .log import LOG
from .utils.parse import get_srt_duration, as_bool, as_int, as_datetime


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


class PropertyHelper:

    @classmethod
    def property_name_to_getter(cls, only_settable=True):
        """
        Return a mapping of instance property method name to the getter method
        for the property. Note that this excludes any un-settable properties
        (i.e. ones which don't define a setter method) by default.

        Credits: https://stackoverflow.com/a/47433706/10237506
        """
        return_dict = {}
        for name in dir(cls):
            obj = getattr(cls, name)
            if isinstance(obj, property):
                if obj.fset is None and only_settable:
                    continue
                return_dict[name] = obj.__get__

        return return_dict

    def set_property_values(self, source: Dict[str, Any]):
        """
        Set (or update) all settable instance properties, with variables in a
        source dictionary object.

        Also sets sensible defaults for instance properties, in case no
        mapping is defined in the source dict.
        """
        for name in self.property_name_to_getter():
            if name in source:
                setattr(self, name, source[name])
            else:
                setattr(self, name, getattr(self, name, None))

    def get_property_values(self, only_settable=True,
                            check_value=lambda x: x is not None):
        """
        Returns a mapping of property name to its current value. By default,
        only includes settable properties whose values are not None.

        """
        vars = self.property_name_to_getter(only_settable)
        return {attr: getter(self) for attr, getter in vars.items()
                if check_value(getter(self))}

    def __repr__(self):
        """
        Construct a default `__repr__` method in the format that the Python
        `dataclasses` module would return.
        """
        vars = self.property_name_to_getter()
        values = ['{}={!r}'.format(f, fget(self)) for f, fget in vars.items()]

        return '%s(%s)' % (self.__class__.__qualname__, ', '.join(values))


class VideoData(PropertyHelper):

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

        self.status = kwargs.pop('status', 'not_found')

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
                'VideoData: Video (%s) is missing a required field in '
                'get_video response',
                kwargs.get('hashed_id'), exc_info=e)

        # Video titles seem to include encoded characters like '&amp;' in the
        # response, but not in the title displayed on the Wistia video page.
        self.name = kwargs.pop('name', '').replace('&amp;', '&')

        self.set_property_values(kwargs)

    @property
    def hashed_id(self) -> str:
        return self._hashed_id

    @hashed_id.setter
    def hashed_id(self, hashed_id: str):
        self._hashed_id = hashed_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def project_id(self) -> str:
        return self._project_id

    @project_id.setter
    def project_id(self, project_id: str):
        self._project_id = project_id

    @property
    def created(self) -> datetime:
        return self._created

    @created.setter
    def created(self, created: Union[datetime, str]):
        self._created = as_datetime(created)

    @property
    def updated(self) -> datetime:
        return self._updated

    @updated.setter
    def updated(self, updated: Union[datetime, str]):
        self._updated = as_datetime(updated)

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    def duration(self, duration: float):
        self._duration = duration

    @property
    def status(self) -> VideoStatus:
        return self._status

    @status.setter
    def status(self, status: Union[VideoStatus, str]):
        if isinstance(status, str):
            status = VideoStatus(status)

        self._status = status

    @property
    def has_audio_description(self) -> bool:
        return self._has_audio_description

    @has_audio_description.setter
    def has_audio_description(self, has_audio_description: Optional[bool]):
        self._has_audio_description = as_bool(has_audio_description)

    @property
    def captions_enabled(self) -> bool:
        return self._captions_enabled

    @captions_enabled.setter
    def captions_enabled(self, captions_enabled: Optional[bool]):
        self._captions_enabled = as_bool(captions_enabled, None)

    @property
    def overlay_text(self) -> str:
        return self._overlay_text

    @overlay_text.setter
    def overlay_text(self, overlay_text: str):
        self._overlay_text = overlay_text

    @property
    def caption_duration(self) -> Optional[float]:
        return self._caption_duration

    @caption_duration.setter
    def caption_duration(self, caption_duration: Optional[float]):
        self._caption_duration = caption_duration

    @property
    def num_captions(self) -> Optional[int]:
        return self._num_captions

    @num_captions.setter
    def num_captions(self, num_captions: Optional[int]):
        self._num_captions = num_captions

    @property
    def ad_disabled(self) -> bool:
        return self._ad_disabled

    @ad_disabled.setter
    def ad_disabled(self, ad_disabled: Optional[bool]):
        self._ad_disabled = as_bool(ad_disabled)

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

    def process_captions(self, captions: List[Dict]):
        """
        Process the response from the `Captions: Index` API for the video.

        Sets the following attributes on the object:
            - `num_captions`
            - `caption_duration`

        Ref: https://wistia.com/support/developers/data-api#captions_index
        """
        if not captions:
            return

        caption_durations = []
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
        return_dict = self.get_property_values()

        return_dict['status'] = self.status.value
        for attr in ('created', 'updated'):
            val = getattr(self, attr)
            if val:
                return_dict[attr] = val.isoformat()

        return return_dict

    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)

        obj.status = d.pop('status')

        for attr in ('created', 'updated'):
            val = d.pop(attr)
            if val:
                setattr(obj, attr, as_datetime(val, raise_=True))

        obj.set_property_values(d)

        return obj


class VideoEmbedData(PropertyHelper):

    def __init__(self, **kwargs):
        """
        Parses a response from `WistiaEmbedApi.get_data`
        """
        if kwargs.pop('type') != 'Video':
            return

        self.hashed_id = kwargs['hashedId']
        self.created = kwargs['createdAt']

        customizations = kwargs.get('embed_options') or {}
        self.captions_enabled = (customizations
                                 .get('plugin', {})
                                 .get('captions-v1', {}).get('on') == 'true')
        self.ad_enabled = (customizations
                           .get('audioDescriptionIsRequired', '') != 'false')
        self.num_captions = len(kwargs.get('captions', []))

        assets = kwargs.get('assets') or []
        for asset in assets:
            if asset['type'] == 'original':
                self.source_url = asset['url'].replace('.bin', '/file.mp4', 1)
            if asset['type'] == 'alternate_audio':
                self.has_audio_description = True
                self.ad_url = asset['url'].replace('.bin', '/file.mp3', 1)

        # Copy over defaults and fields with expected names
        self.set_property_values(kwargs)

    @property
    def hashed_id(self) -> str:
        return self._hashed_id

    @hashed_id.setter
    def hashed_id(self, hashed_id: str):
        self._hashed_id = hashed_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def created(self) -> datetime:
        return self._created

    @created.setter
    def created(self, created: Union[datetime, str]):
        self._created = as_datetime(created)

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    def duration(self, duration: float):
        self._duration = duration

    @property
    def captions_enabled(self) -> bool:
        return self._captions_enabled

    @captions_enabled.setter
    def captions_enabled(self, captions_enabled: bool):
        self._captions_enabled = as_bool(captions_enabled)

    @property
    def ad_enabled(self) -> bool:
        return self._ad_enabled

    @ad_enabled.setter
    def ad_enabled(self, ad_enabled: bool):
        self._ad_enabled = as_bool(ad_enabled)

    @property
    def source_url(self) -> str:
        return self._source_url

    @source_url.setter
    def source_url(self, source_url: str):
        self._source_url = source_url

    @property
    def ad_url(self) -> Optional[str]:
        return self._ad_url

    @ad_url.setter
    def ad_url(self, ad_url: Optional[str]):
        self._ad_url = ad_url

    @property
    def has_audio_description(self) -> bool:
        return self._has_audio_description

    @has_audio_description.setter
    def has_audio_description(self, has_audio_description: bool):
        self._has_audio_description = as_bool(has_audio_description)

    @property
    def num_captions(self) -> int:
        return self._num_captions

    @num_captions.setter
    def num_captions(self, num_captions: int):
        self._num_captions = as_int(num_captions)

    @classmethod
    def load_video(cls, video_id: str) -> 'VideoEmbedData':
        """
        Retrieve video embed data from Wistia and return a new
        :class:`VideoEmbedData` object.

        """
        from .api_embed import WistiaEmbedApi
        obj = cls(**WistiaEmbedApi.get_data(video_id))
        return obj


class UploadResponse(PropertyHelper):
    """
    Represents a response from the Wistia Upload API

    Example response format:
      https://wistia.com/support/developers/upload-api#response-format
    """

    def __init__(self, **kwargs):
        self.set_property_values(kwargs)

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id_: Optional[int]):
        self._id = as_int(id_)

    @property
    def hashed_id(self) -> str:
        return self._hashed_id

    @hashed_id.setter
    def hashed_id(self, hashed_id: str):
        self._hashed_id = hashed_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, type_: str):
        self._type = type_

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, description: Optional[str]):
        self._description = description

    @property
    def created(self) -> datetime:
        return self._created

    @created.setter
    def created(self, created: Union[datetime, str]):
        self._created = as_datetime(created)

    @property
    def updated(self) -> datetime:
        return self._updated

    @updated.setter
    def updated(self, updated: Union[datetime, str]):
        self._updated = as_datetime(updated)

    @property
    def progress(self) -> float:
        return self._progress

    @progress.setter
    def progress(self, progress: float):
        self._progress = progress

    @property
    def status(self) -> VideoStatus:
        return self._status

    @status.setter
    def status(self, status: Union[VideoStatus, str]):
        if isinstance(status, str):
            status = VideoStatus(status)

        self._status = status

    @property
    def thumbnail(self) -> Dict[str, Union[int, str]]:
        return self._thumbnail

    @thumbnail.setter
    def thumbnail(self, thumbnail: Dict[str, Union[int, str]]):
        self._thumbnail = thumbnail

    @property
    def duration(self) -> Optional[float]:
        return self._duration

    @duration.setter
    def duration(self, duration: Optional[float]):
        self._duration = duration
