from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .file import FilePayload


# Almost ripped out from https://github.com/revoltchat/revolt.py/blob/master/revolt/types/embed.py


class YoutubeEmbedPayload(TypedDict):
    type: Literal["Youtube"]
    id: str
    timestamp: NotRequired[str]


class TwitchEmbedPayload(TypedDict):
    type: Literal["Twitch"]
    id: str
    content_type: Literal["Channel", "Video", "Clip"]


class SpotifyEmbedPayload(TypedDict):
    type: Literal["Spotify"]
    id: str
    content_type: Literal["Track", "Album", "Playlist"]


class SoundCloudEmbedPayload(TypedDict):
    type: Literal["SoundCloud"]


class BandcampEmbedPayload(TypedDict):
    type: Literal["Bandcamp"]
    id: str
    content_type: str


SpecialWebsiteEmbedPayload = Union[
    YoutubeEmbedPayload, TwitchEmbedPayload, SpotifyEmbedPayload, SoundCloudEmbedPayload, BandcampEmbedPayload
]


class JanuaryImagePayload(TypedDict):
    url: str
    width: int
    height: int
    size: Literal["Large", "Preview"]


class JanuaryVideoPayload(TypedDict):
    url: str
    width: int
    height: int


class WebsiteEmbedPayload(TypedDict):
    type: Literal["Website"]
    url: NotRequired[str]
    special: NotRequired[SpecialWebsiteEmbedPayload]
    title: NotRequired[str]
    description: NotRequired[str]
    image: NotRequired[JanuaryImagePayload]
    video: NotRequired[JanuaryVideoPayload]
    site_name: NotRequired[str]
    icon_url: NotRequired[str]
    colour: NotRequired[str]


class ImageEmbedPayload(TypedDict):  # TODO? idk
    type: Literal["Image"]


class TextEmbedPayload(TypedDict):
    type: Literal["Text"]
    title: NotRequired[str]
    description: NotRequired[str]
    url: NotRequired[str]
    media: NotRequired[FilePayload]
    icon_url: NotRequired[str]
    colour: NotRequired[str]


class NoneEmbed(TypedDict):
    type: Literal["None"]


EmbedPayload = Union[WebsiteEmbedPayload, ImageEmbedPayload, TextEmbedPayload, NoneEmbed]


class SendableEmbedPayload(TypedDict):
    type: Literal["Text"]
    title: NotRequired[str]
    description: NotRequired[str]
    url: NotRequired[str]
    media: NotRequired[str]
    icon_url: NotRequired[str]
    colour: NotRequired[str]
