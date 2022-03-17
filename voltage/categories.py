from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import CategoryPayload
    from .internals import CacheHandler
    from .channel import Channel

class Category:
    """
    A class that represents a Voltage category.

    Attributes
    ----------
    name: :class:`str`
        The name of the category.
    description: :class:`str`
        The name of the category.
    channels: List[:class:`Channel`]
        A list of all channels in the category.
    """
    __slots__ = ('name', 'id', 'channel_ids', 'cache')
    def __init__(self, data: CategoryPayload, cache: CacheHandler):
        self.name = data['title']
        self.id = data['id']
        self.channel_ids = data['channels']
        self.cache = cache

    @property
    def channels(self) -> list[Channel]:
        return [self.cache.get_channel(id) for id in self.channel_ids]

    def __repr__(self):
        return f'<Category {self.name}>'

    def __str__(self):
        return self.name
