from __future__ import annotations

__all__ = ['LanguageCode',
           'MediaType',
           'SortBy',
           'SortDir',
           'VideoStatus',
           'Container',
           'Project',
           'Media',
           'Video',
           'VideoStats',
           'VideoEmbedData',
           'UploadResponse']

import json
import pprint
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Generic, Iterator, Iterable, Any

from dataclass_wizard import JSONWizard, json_field
from dataclass_wizard.abstractions import W
from dataclass_wizard.type_def import Encoder

from .constants import RAISE_ON_UNKNOWN_KEY
from .log import LOG
from .utils.decorators import cached_property
from .utils.metaclasses import display_with_pformat
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


class Container(list, Generic[W]):
    """
    List wrapper around a list of :class:`JSONWizard` (or a sub-class)
    instances.
    """
    __slots__ = ('_model', )

    def __init__(self, data_model: type[W], seq: Iterable[W] = ()):
        super().__init__(seq)
        self._model = data_model

    def __iter__(self) -> Iterator[W]:
        return super().__iter__()

    def __str__(self):
        """Control the value displayed when print(self) is called."""
        return pprint.pformat(self)

    def to_json(self, encoder: Encoder = json.dumps, **encoder_kwargs) -> str:
        """Convert the list of instances to a JSON string."""
        # noinspection PyArgumentList
        return self._model.list_to_json(
            self,
            encoder=encoder,
            **encoder_kwargs
        )

    def to_pretty_json(self, encoder: Encoder = json.dumps) -> str:
        """Convert the list of instances to a *prettified* JSON string."""
        return self.to_json(indent=2, encoder=encoder)


#########################
#   Data API - Models   #
#########################

@dataclass
class Project(JSONWizard, metaclass=display_with_pformat):
    """
    Project dataclass
    """
    class _(JSONWizard.Meta):
        raise_on_unknown_json_key = RAISE_ON_UNKNOWN_KEY

    hashed_id: str
    id: int
    name: str
    media_count: int
    created: datetime
    updated: datetime
    anonymous_can_upload: bool
    anonymous_can_download: bool
    public: bool
    public_id: str
    description: str | None


@dataclass
class Media(JSONWizard, metaclass=display_with_pformat):
    """
    Media dataclass

    """
    class _(JSONWizard.Meta):
        raise_on_unknown_json_key = RAISE_ON_UNKNOWN_KEY

    hashed_id: str
    id: int
    name: str
    description: str
    type: MediaType
    created: datetime
    updated: datetime
    progress: float
    thumbnail: Thumbnail
    section: str | None = None
    duration: float | None = None

    status: VideoStatus = VideoStatus.NOT_FOUND


@dataclass
class Thumbnail:
    """
    Thumbnail dataclass

    """
    url: str
    width: int
    height: int


@dataclass
class Asset:
    """
    Asset dataclass

    """
    url: str
    file_size: int
    content_type: str
    type: str
    width: int | None = None
    height: int | None = None


@dataclass
class Video(Media, JSONWizard, metaclass=display_with_pformat):
    """
    Video dataclass

    """
    class _(JSONWizard.Meta):
        raise_on_unknown_json_key = RAISE_ON_UNKNOWN_KEY

    duration: float = 0.0
    project: ProjectInfo = None
    assets: list[Asset] = field(default_factory=list)
    embed_code: str = json_field('', repr=False, dump=False, default=None)

    # Not included in GET '/v1/medias' response, but technically
    # still part of video metadata.
    has_audio_description: bool = False
    captions_enabled: bool | None = None
    overlay_text: str | None = None
    caption_duration: float | None = None
    num_captions: int | None = None
    ad_disabled: bool | None = None

    def __post_init__(self):
        # Media (video) titles seem to include encoded characters
        # like '&amp;' in the response, but not in the title displayed
        # on the Wistia project page.
        self.name = self.name.replace('&amp;', '&')

        if self.type is not MediaType.VIDEO:
            return

        for asset in self.assets:
            if asset.type == 'AlternateAudioFile':
                self.has_audio_description = True
                break

        if not self.duration:
            # There are rare cases when 'duration' field is missing from
            # response. This usually also means video is inaccessible from the
            # webpage, so we might need to contact Wistia Support to resolve
            # the issue.
            self.status = VideoStatus.FAILED
            self.duration = 0.0
            LOG.error(
                f'Video ({self.hashed_id}) is missing a required field '
                'in get_video response')

    @cached_property
    def project_id(self) -> str:
        """Return the project's hashed id."""
        return self.project.hashed_id if self.project else ''

    @classmethod
    def load_video(cls, video_id: str) -> Video:
        """
        Retrieve video data from Wistia and return a new :class:`Video`
        object.
        """
        from .api_data import WistiaDataApi

        return WistiaDataApi.get_video(video_id)

    @classmethod
    def list_for_project(cls, project_id: str) -> list[Video]:
        """
        List videos for a Wistia project.
        """
        from .api_data import WistiaDataApi

        videos: Container[Video] = WistiaDataApi.list_project(
            project_id,
            model_cls=Video
        )

        for v in videos:
            v.project = ProjectInfo(project_id)

        return videos

    @property
    def has_captions(self) -> bool:
        """
        Indicates whether the Wistia video has a captions file.
        """
        return self.caption_duration is not None

    def process_captions(self, captions: list[dict]):
        """
        Process the response from the `Captions: Index` API for the video.

        Sets the following attributes on the object:
            - `num_captions`
            - `caption_duration`

        Ref: https://wistia.com/support/developers/data-api#captions_index
        """
        if not captions:
            return

        caption_durations: list[float] = []
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


@dataclass
class ProjectInfo:
    """
    Project dataclass

    """
    hashed_id: str
    id: int = None
    name: str = None


@dataclass
class VideoStats(JSONWizard, metaclass=display_with_pformat):
    """
    VideoStats dataclass

    """
    class _(JSONWizard.Meta):
        raise_on_unknown_json_key = RAISE_ON_UNKNOWN_KEY

    id: int
    hashed_id: str
    name: str
    stats: Stats


@dataclass
class Stats(metaclass=display_with_pformat):
    """
    Stats dataclass

    """
    page_loads: int
    visitors: int
    percent_of_visitors_clicking_play: int
    plays: int
    average_percent_watched: int


###########################
#   Upload API - Models   #
###########################

@dataclass
class UploadResponse(JSONWizard, metaclass=display_with_pformat):
    """
    Represents a response from the Wistia Upload API

    Example response format:
      https://wistia.com/support/developers/upload-api#response-format
    """
    class _(JSONWizard.Meta):
        raise_on_unknown_json_key = RAISE_ON_UNKNOWN_KEY

    hashed_id: str
    id: int
    name: str
    type: str
    description: str | None
    created: datetime
    updated: datetime
    progress: float
    thumbnail: Thumbnail
    duration: float | None = None
    status: VideoStatus = VideoStatus.QUEUED


############################
#   Media Embed - Models   #
############################

@dataclass
class VideoEmbedData(JSONWizard, metaclass=display_with_pformat):
    """
    VideoEmbedData dataclass

    """
    class _(JSONWizard.Meta):
        raise_on_unknown_json_key = RAISE_ON_UNKNOWN_KEY
        skip_defaults = True

    hashed_id: str
    name: str
    created_at: datetime
    duration: float
    assets: list[EmbedAsset]
    project_id: int
    stats: EmbedStats
    distillery_url: str
    account_key: str
    media_key: str
    type: str
    media_type: str
    progress: float
    status: int
    branding: bool
    enable_customer_logo: bool
    seo_description: str
    preload_preference: Any
    flash_player_url: str
    show_about: bool
    first_embed_for_account: bool
    first_share_for_account: bool
    keyframe_align: bool
    use_media_data_host_logic: bool
    tracking_transmit_interval: int
    # Annotating this field as a generic `dict` type for now, because
    # I've not seen this feature used before.
    integrations: dict
    # integrations: Integrations
    hls_enabled: bool
    embed_options: EmbedOptions
    captions: list[Caption] = field(default_factory=list)
    transcript: Transcript | None = None

    # Not included in GET '/v1/medias' response, but technically
    # still part of video metadata.
    source_url: str = ''
    ad_url: str | None = None
    has_audio_description: bool = False

    def __post_init__(self):
        for asset in self.assets:
            if asset.type == 'original':
                self.source_url = asset.url.replace('.bin', '/file.mp4', 1)
            if asset.type == 'alternate_audio':
                self.has_audio_description = True
                self.ad_url = asset.url.replace('.bin', '/file.mp3', 1)

    @cached_property
    def captions_enabled(self) -> bool:
        return self.embed_options.plugin.captions_v1.on is True

    @cached_property
    def ad_enabled(self) -> bool:
        return self.embed_options.audio_description_is_required

    @cached_property
    def num_captions(self) -> int:
        return len(self.captions)

    @classmethod
    def load_video(cls, video_id: str) -> VideoEmbedData:
        """
        Retrieve video embed data from Wistia and return a new
        :class:`VideoEmbedData` object.

        """
        from .api_embed import WistiaEmbedApi

        return WistiaEmbedApi.get_data(video_id)


@dataclass
class Transcript:
    video_id: str


@dataclass
class Details:
    """
    Details dataclass

    """
    audio_description: bool | None = None
    language_metadata: LanguageMetadata | None = None


@dataclass
class EmbedAsset:
    """
    EmbedAsset dataclass

    """
    type: str
    slug: str
    display_name: str
    bitrate: int
    public: bool
    status: int
    progress: float
    url: str
    created_at: datetime
    details: Details = field(default_factory=Details)
    size: int | None = None
    ext: str = ''
    metadata: Metadata | None = None
    container: str | None = None
    codec: str | None = None
    segment_duration: int | None = None
    opt_vbitrate: int | None = None
    width: int | None = None
    height: int | None = None


@dataclass
class LanguageMetadata:
    name: str
    native_name: str
    right_to_left: bool


@dataclass
class Metadata:
    """
    Metadata dataclass

    """
    aspect_ratio: float | None = None
    av_stream_metadata: str | None = None
    average_bitrate: int | None = None
    early_max_bitrate: int | None = None
    frame_width: int | None = None
    frame_height: int | None = None
    frame_count: int | None = None
    max_bitrate: int | None = None
    served_by_media_api: int | None = None


@dataclass
class EmbedStats:
    """
    Stats dataclass

    """
    load_count: int
    play_count: int
    unique_load_count: int
    unique_play_count: int
    average_engagement: float


@dataclass
class Integrations:
    """
    Integrations dataclass

    TODO we don't use this feature, so no idea what goes here
    """
    pass


@dataclass
class Caption:
    """
    Caption dataclass

    """
    language: str
    text: str


@dataclass
class EmbedOptions:
    """
    EmbedOptions dataclass

    """
    volume_control: bool
    fullscreen_button: bool
    controls_visible_on_load: bool
    player_color: str
    bpb_time: bool
    plugin: Plugin
    vulcan: bool
    playsinline: bool
    video_quality: str = ''
    audio_description_is_required: bool = False
    branding: bool | None = None
    chapters_on: bool | None = None
    show_customer_logo: bool | None = None
    auto_play: bool | None = None
    silent_auto_play: bool | None = None
    play_button: bool | None = None
    small_play_button: bool | None = None
    playbar: bool | None = None
    settings_control: bool | None = None
    playback_rate_control: bool | None = None
    quality_control: bool | None = None
    end_video_behavior: str | None = None
    thumbnail_alt_text: str | None = None
    unaltered_still_image_asset: UnalteredStillImageAsset | None = None
    still_url: str | None = None
    spherical: bool | None = None


@dataclass
class CaptionsV1:
    """
    CaptionsV1 dataclass

    """
    on_by_default: bool = False
    is_async: bool = json_field('async', default=False)
    language: str = ''
    on: bool | None = None


@dataclass
class Plugin:
    """
    Plugin dataclass

    """
    captions_v1: CaptionsV1 = field(default_factory=CaptionsV1)
    midroll_link_v1: MidrollLinkV1 | None = None
    chapters: Chapters | None = None
    share: Share | None = None


@dataclass
class MidrollLinkV1:
    """
    MidrollLinkV1 dataclass

    """
    links: list[Link]
    on: bool


@dataclass
class Link:
    """
    Link dataclass

    """
    name: str
    time: int
    duration: int
    text: str
    url: str
    conversion_opportunity_id: int
    conversion_opportunity_key: str


@dataclass
class Chapters:
    """
    Chapters dataclass

    """
    visible_on_load: bool
    chapter_list: list[ChapterList]
    on: bool


@dataclass
class ChapterList:
    """
    ChapterList dataclass

    """
    id: int
    title: str
    time: float
    deleted: bool


@dataclass
class Share:
    """
    Share dataclass

    """
    channels: str
    page_title: str
    page_url: str
    tweet_text: str
    override_url: bool
    on: bool
    conversion_opportunity_key: str
    download_type: str | None = None


@dataclass
class UnalteredStillImageAsset:
    """
    UnalteredStillImageAsset dataclass

    """
    url: str
    width: int | None = None
    height: int | None = None
