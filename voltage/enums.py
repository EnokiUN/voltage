import enum


class EmbedType(enum.Enum):
    """
    An enum which represents a Embed's type.
    """

    website = "Website"
    image = "Image"
    text = "Text"
    none = "None"


class SortType(enum.Enum):
    """
    An enum which represents the sort type for fetching messages.
    """

    latest = "Latest"
    oldest = "Oldest"
    relevance = "Relevance"


class ChannelType(enum.Enum):
    """
    An enum which represents the channel type.
    """

    text_channel = "TextChannel"
    voice_channel = "VoiceChannel"
    group = "Group"
    direct_message = "DirectMessage"
    saved_message = "SavedMessage"


class AssetType(enum.Enum):
    """
    An enum which represents the type of an asset.
    """

    image = "Image"
    video = "Video"
    audio = "Audio"
    file = "File"
    text = "Text"


class PresenseType(enum.Enum):
    """
    An enum which represents the type of a presense.
    """

    busy = "Busy"
    idle = "Idle"
    online = "Online"
    invisible = "Invisible"
