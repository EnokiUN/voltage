from __future__ import annotations
from types import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import CategoryPayload
    from .internals import CacheHandler
    from .channel import Channel

class Category:
    def __init__(self, data: CategoryPayload, cache: CacheHandler):
        self.name = data['title']
        self.id = data['id']
        self.channel_ids = data['channels']
        self.cache = cache

    @property
    def channels(self) -> list[Channel]:
        return [self.cache.get_channel(id) for id in self.channel_ids]
